"""
Trading Service
Handles trading operations via Alpaca API
"""

from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import TradingAPIError
from app.db.models import Trade, Position, Tweet

logger = setup_logging()

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logger.warning("Alpaca trading API not available. Trading features will be disabled.")


class TradingService:
    """Service for trading operations"""
    
    def __init__(self):
        """Initialize trading client"""
        if not ALPACA_AVAILABLE:
            logger.warning("Alpaca package not installed. Trading features disabled.")
            self.client = None
        elif not settings.ALPACA_API_KEY or not settings.ALPACA_API_SECRET:
            logger.warning(
                "Alpaca API credentials not configured. "
                "Please set ALPACA_API_KEY and ALPACA_API_SECRET in your .env file"
            )
            self.client = None
        elif len(settings.ALPACA_API_KEY) < 10 or len(settings.ALPACA_API_SECRET) < 10:
            logger.warning(
                f"Alpaca API credentials appear invalid (key length: {len(settings.ALPACA_API_KEY)}, "
                f"secret length: {len(settings.ALPACA_API_SECRET)}). Please check your .env file."
            )
            self.client = None
        else:
            try:
                self.client = TradingClient(
                    api_key=settings.ALPACA_API_KEY,
                    secret_key=settings.ALPACA_API_SECRET,
                    paper=True if "paper" in settings.ALPACA_BASE_URL else False,
                )
                # Test the connection
                account = self.client.get_account()
                logger.info(
                    f"Trading client initialized successfully. "
                    f"Account status: {account.status}, "
                    f"Buying power: ${float(account.buying_power):,.2f}"
                )
            except Exception as e:
                error_msg = str(e)
                if "401" in error_msg or "Unauthorized" in error_msg or "invalid" in error_msg.lower():
                    logger.error(
                        f"Alpaca API authentication failed. Please verify your API keys are correct. Error: {e}"
                    )
                else:
                    logger.error(f"Failed to initialize trading client: {e}")
                self.client = None
    
    def _calculate_position_size(self, sentiment_score: float) -> float:
        """
        Calculate position size based on sentiment and risk management
        
        Args:
            sentiment_score: Sentiment score from -1 to 1
            
        Returns:
            Position size in dollars
        """
        # Base position size on sentiment strength
        sentiment_strength = abs(sentiment_score)
        
        # Scale position size based on sentiment strength
        # Stronger sentiment = larger position (up to max)
        position_size = min(
            settings.MAX_POSITION_SIZE * sentiment_strength,
            settings.MAX_POSITION_SIZE,
        )
        
        return round(position_size, 2)
    
    async def execute_trade(
        self,
        session: AsyncSession,
        symbol: str,
        sentiment_score: float,
        tweet_id: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Optional[Trade]:
        """
        Execute a trade based on sentiment
        
        Args:
            session: Database session
            symbol: Stock symbol to trade
            sentiment_score: Sentiment score (-1 to 1)
            tweet_id: Associated tweet ID
            reason: Reason for the trade
            
        Returns:
            Trade object if successful
        """
        if not settings.TRADING_ENABLED:
            logger.warning("Trading is disabled. Set TRADING_ENABLED=true to enable.")
            return None
        
        if not self.client:
            logger.error("Trading client not initialized")
            return None
        
        try:
            # Determine trade side based on sentiment
            if sentiment_score > settings.SENTIMENT_THRESHOLD_POSITIVE:
                side = OrderSide.BUY
            elif sentiment_score < settings.SENTIMENT_THRESHOLD_NEGATIVE:
                side = OrderSide.SELL
            else:
                logger.info(f"Sentiment {sentiment_score} is neutral, skipping trade")
                return None
            
            # Get current price
            account = self.client.get_account()
            buying_power = float(account.buying_power)
            
            # Calculate position size
            position_size_dollars = self._calculate_position_size(abs(sentiment_score))
            
            # Check if we have enough buying power
            if side == OrderSide.BUY and position_size_dollars > buying_power:
                logger.warning(f"Insufficient buying power. Need ${position_size_dollars}, have ${buying_power}")
                position_size_dollars = buying_power * 0.95  # Use 95% of available
            
            # Get current price to calculate quantity
            # Note: In production, use market data API
            # For now, we'll use a placeholder
            current_price = 250.0  # Placeholder - should fetch from market data API
            quantity = int(position_size_dollars / current_price)
            
            if quantity < 1:
                logger.warning(f"Position size too small: ${position_size_dollars}")
                return None
            
            # Create market order
            market_order_data = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=side,
                time_in_force=TimeInForce.DAY,
            )
            
            # Submit order
            order = self.client.submit_order(order_data=market_order_data)
            
            # Save trade to database
            trade = Trade(
                symbol=symbol,
                side=side.value.lower(),
                quantity=quantity,
                price=current_price,  # Will be updated when order fills
                order_id=order.id,
                status="pending",
                tweet_id=tweet_id,
                sentiment_score=sentiment_score,
                reason=reason or f"Sentiment-based trade: {sentiment_score:.2f}",
            )
            
            session.add(trade)
            await session.commit()
            await session.refresh(trade)
            
            logger.info(f"Trade executed: {side.value} {quantity} {symbol} at ${current_price}")
            return trade
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to execute trade: {e}")
            raise TradingAPIError(f"Trade execution failed: {e}")
    
    async def get_positions(self, session: AsyncSession) -> list[Position]:
        """Get current positions from database"""
        try:
            result = await session.execute(select(Position))
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
    
    async def update_positions(self, session: AsyncSession):
        """Update positions from trading account"""
        if not self.client:
            return
        
        try:
            positions = self.client.get_all_positions()
            
            for pos in positions:
                # Update or create position in database
                result = await session.execute(
                    select(Position).where(Position.symbol == pos.symbol)
                )
                db_position = result.scalar_one_or_none()
                
                if db_position:
                    db_position.quantity = float(pos.qty)
                    db_position.average_price = float(pos.avg_entry_price)
                    db_position.current_price = float(pos.current_price)
                    db_position.unrealized_pnl = float(pos.unrealized_pl)
                else:
                    db_position = Position(
                        symbol=pos.symbol,
                        quantity=float(pos.qty),
                        average_price=float(pos.avg_entry_price),
                        current_price=float(pos.current_price),
                        unrealized_pnl=float(pos.unrealized_pl),
                    )
                    session.add(db_position)
            
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to update positions: {e}")

