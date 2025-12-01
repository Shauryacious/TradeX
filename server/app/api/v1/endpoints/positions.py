"""
Position Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.db.models import Position
from app.services.trading_service import TradingService

router = APIRouter()


class PositionResponse(BaseModel):
    """Position response model"""
    id: int
    symbol: str
    quantity: float
    average_price: float
    current_price: Optional[float]
    unrealized_pnl: Optional[float]
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[PositionResponse])
async def get_positions(
    db: AsyncSession = Depends(get_db),
):
    """Get all current positions"""
    trading_service = TradingService()
    await trading_service.update_positions(db)
    
    result = await db.execute(select(Position))
    positions = result.scalars().all()
    
    return positions


@router.get("/{symbol}", response_model=PositionResponse)
async def get_position(
    symbol: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific position by symbol"""
    trading_service = TradingService()
    await trading_service.update_positions(db)
    
    result = await db.execute(
        select(Position).where(Position.symbol == symbol)
    )
    position = result.scalar_one_or_none()
    
    if not position:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Position not found")
    
    return position

