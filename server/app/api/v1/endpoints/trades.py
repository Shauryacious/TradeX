"""
Trade Endpoints
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.db.models import Trade
from app.services.trading_service import TradingService

router = APIRouter()


class TradeResponse(BaseModel):
    """Trade response model"""
    id: int
    symbol: str
    side: str
    quantity: float
    price: float
    order_id: Optional[str]
    status: str
    tweet_id: Optional[int]
    sentiment_score: Optional[float]
    reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[TradeResponse])
async def get_trades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get trades with optional filtering"""
    query = select(Trade).order_by(desc(Trade.created_at))
    
    if symbol:
        query = query.where(Trade.symbol == symbol)
    
    if status:
        query = query.where(Trade.status == status)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    trades = result.scalars().all()
    
    return trades


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific trade by ID"""
    result = await db.execute(
        select(Trade).where(Trade.id == trade_id)
    )
    trade = result.scalar_one_or_none()
    
    if not trade:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Trade not found")
    
    return trade


@router.get("/stats/summary")
async def get_trade_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get trade statistics"""
    from sqlalchemy import func
    
    # Total trades
    total_result = await db.execute(select(func.count(Trade.id)))
    total_trades = total_result.scalar()
    
    # By status
    status_result = await db.execute(
        select(Trade.status, func.count(Trade.id))
        .group_by(Trade.status)
    )
    status_dist = {row[0]: row[1] for row in status_result.all()}
    
    # By side
    side_result = await db.execute(
        select(Trade.side, func.count(Trade.id))
        .group_by(Trade.side)
    )
    side_dist = {row[0]: row[1] for row in side_result.all()}
    
    # Total volume
    volume_result = await db.execute(
        select(func.sum(Trade.quantity * Trade.price))
    )
    total_volume = volume_result.scalar() or 0
    
    return {
        "total_trades": total_trades,
        "status_distribution": status_dist,
        "side_distribution": side_dist,
        "total_volume": float(total_volume),
    }


class TradeRequest(BaseModel):
    """Trade request model"""
    symbol: str
    sentiment_score: float
    tweet_id: Optional[int] = None
    reason: Optional[str] = None


@router.post("/execute", response_model=TradeResponse)
async def execute_trade(
    trade_request: TradeRequest,
    db: AsyncSession = Depends(get_db),
):
    """Execute a trade based on sentiment analysis"""
    trading_service = TradingService()
    
    try:
        trade = await trading_service.execute_trade(
            session=db,
            symbol=trade_request.symbol,
            sentiment_score=trade_request.sentiment_score,
            tweet_id=trade_request.tweet_id,
            reason=trade_request.reason,
        )
        
        if trade is None:
            raise HTTPException(
                status_code=400,
                detail="Trade execution failed. Check if trading is enabled and sentiment is strong enough."
            )
        
        return trade
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trade execution error: {str(e)}")

