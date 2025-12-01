"""
Health Check Endpoints
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with service status"""
    from app.core.config import settings
    from app.services.twitter_service import TwitterService
    from app.services.trading_service import TradingService
    
    twitter_service = TwitterService()
    trading_service = TradingService()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "twitter": {
                "configured": bool(settings.TWITTER_BEARER_TOKEN),
                "monitoring": twitter_service.is_monitoring,
            },
            "trading": {
                "configured": bool(settings.ALPACA_API_KEY),
                "enabled": settings.TRADING_ENABLED,
            },
        },
    }

