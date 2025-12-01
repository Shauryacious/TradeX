"""
TradeX Server - Main Application Entry Point
Production-ready FastAPI server for Twitter-based trading bot
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.db.database import init_db, close_db
from app.services.trading_service import TradingService
from app.services.twitter_service import TwitterService

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    logger.info("Starting TradeX server...")
    await init_db()
    
    # Initialize services
    twitter_service = TwitterService()
    trading_service = TradingService()
    
    # Start background tasks
    await twitter_service.start_monitoring()
    
    logger.info("TradeX server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down TradeX server...")
    await twitter_service.stop_monitoring()
    await close_db()
    logger.info("TradeX server shut down complete")


# Create FastAPI application
app = FastAPI(
    title="TradeX API",
    description="Twitter-based trading bot API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TradeX API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TradeX API",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )

