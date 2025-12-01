"""
Application Configuration
Loads settings from environment variables with sensible defaults
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # CORS settings
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173"
    
    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://localhost/tradex"
    
    # Twitter API settings
    TWITTER_BEARER_TOKEN: str = ""
    TWITTER_API_KEY: str = ""
    TWITTER_API_SECRET: str = ""
    TWITTER_ACCESS_TOKEN: str = ""
    TWITTER_ACCESS_TOKEN_SECRET: str = ""
    
    # Trading API settings
    ALPACA_API_KEY: str = ""
    ALPACA_API_SECRET: str = ""
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"  # Paper trading by default
    
    # Stock Data API settings (optional - APIs work without keys but with better rate limits with keys)
    FINNHUB_API_KEY: str = ""  # Get free key at https://finnhub.io/register
    ALPHA_VANTAGE_API_KEY: str = ""  # Get free key at https://www.alphavantage.co/support/#api-key
    
    # Trading settings
    TRADING_SYMBOL: str = "TSLA"
    TRADING_ENABLED: bool = False  # Safety: disabled by default
    MAX_POSITION_SIZE: float = 1000.0  # Maximum position size in dollars
    RISK_PERCENTAGE: float = 1.0  # Risk 1% of capital per trade
    
    # Sentiment analysis settings
    SENTIMENT_THRESHOLD_POSITIVE: float = 0.3
    SENTIMENT_THRESHOLD_NEGATIVE: float = -0.3
    
    # Monitoring settings
    # Note: With 100 posts/month limit, recommended settings:
    # - TWEET_CHECK_INTERVAL: 21600 (6 hours) or 43200 (12 hours)
    # - TWEETS_PER_USER: 1
    # - MONITORED_USERS: 1-2 users max
    # Example: 2 users × 1 tweet × 4 checks/day = 8 posts/day = ~240/month (still over, adjust as needed)
    MONITORED_USERS: Union[str, List[str]] = "elonmusk,Tesla,realDonaldTrump"
    TWEET_CHECK_INTERVAL: int = 21600  # seconds (6 hours default to conserve API quota - 100 posts/month limit)
    TWEETS_PER_USER: int = 1  # Number of tweets to fetch per user per check (1 = most conservative)
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/tradex.log"
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("MONITORED_USERS", mode="before")
    @classmethod
    def parse_monitored_users(cls, v):
        """Parse comma-separated monitored users"""
        if isinstance(v, str):
            return [user.strip() for user in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


def clear_settings_cache():
    """Clear the settings cache to reload from .env file"""
    get_settings.cache_clear()


# Global settings instance
settings = get_settings()

