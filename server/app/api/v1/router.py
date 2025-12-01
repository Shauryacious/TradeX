"""
API Router
Main router for API endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import tweets, trades, positions, health, stocks

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(tweets.router, prefix="/tweets", tags=["tweets"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(positions.router, prefix="/positions", tags=["positions"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])

