"""
Twitter Service
Handles Twitter API interactions and tweet monitoring
"""

import asyncio
import os
import ssl
import certifi
from typing import List, Optional, Dict
from datetime import datetime, timezone
from tweepy.asynchronous import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import TwitterAPIError
from app.db.models import Tweet
from app.services.sentiment_service import SentimentService

logger = setup_logging()

# Set SSL certificate file for aiohttp (used by tweepy)
# Must be set before any aiohttp imports
cert_path = certifi.where()
os.environ['SSL_CERT_FILE'] = cert_path
os.environ['REQUESTS_CA_BUNDLE'] = cert_path
os.environ['CURL_CA_BUNDLE'] = cert_path

# Also set for Python's ssl module
ssl._create_default_https_context = ssl._create_unverified_context


class TwitterService:
    """Service for Twitter API interactions"""
    
    def __init__(self):
        """Initialize Twitter client"""
        # Check if we have the minimum required credentials
        has_bearer = bool(settings.TWITTER_BEARER_TOKEN and len(settings.TWITTER_BEARER_TOKEN) >= 50)
        has_oauth = bool(
            settings.TWITTER_API_KEY and settings.TWITTER_API_SECRET and
            settings.TWITTER_ACCESS_TOKEN and settings.TWITTER_ACCESS_TOKEN_SECRET
        )
        
        if not has_bearer and not has_oauth:
            logger.error(
                "Twitter API credentials not properly configured. "
                "You need either a Bearer Token (50+ chars) or OAuth 1.0a credentials (API Key, Secret, Access Token, Access Token Secret)."
            )
        elif not has_bearer:
            logger.warning(
                f"Twitter Bearer Token appears invalid (length: {len(settings.TWITTER_BEARER_TOKEN) if settings.TWITTER_BEARER_TOKEN else 0} chars). "
                "Some endpoints may require OAuth 1.0a instead."
            )
        elif not has_oauth:
            logger.warning(
                "Twitter OAuth 1.0a credentials not fully configured. "
                "Some endpoints may require OAuth 1.0a authentication."
            )
        
        # Initialize client with all available credentials
        # tweepy will use Bearer Token when available, fall back to OAuth 1.0a if needed
        # wait_on_rate_limit=False to prevent blocking - we'll handle rate limits gracefully
        self.client = AsyncClient(
            bearer_token=settings.TWITTER_BEARER_TOKEN if has_bearer else None,
            consumer_key=settings.TWITTER_API_KEY if has_oauth else None,
            consumer_secret=settings.TWITTER_API_SECRET if has_oauth else None,
            access_token=settings.TWITTER_ACCESS_TOKEN if has_oauth else None,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET if has_oauth else None,
            wait_on_rate_limit=False,  # Don't block on rate limits - handle gracefully
        )
        
        self.sentiment_service = SentimentService()
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        self._has_bearer = has_bearer
        self._has_oauth = has_oauth
    
    async def _test_authentication(self):
        """Test Twitter API authentication"""
        try:
            # Try to get a known user to test auth
            test_user = await self.client.get_user(username="twitter")
            if test_user and test_user.data:
                logger.info("Twitter API authentication successful")
            else:
                logger.warning("Twitter API authentication test returned no data")
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate limit" in error_msg.lower() or "Too Many Requests" in error_msg:
                logger.warning(
                    "Twitter API rate limit exceeded. Authentication test skipped. "
                    "The server will continue to run and retry later. "
                    "Rate limits reset periodically - check your Twitter API usage in the developer portal."
                )
            elif "401" in error_msg or "Unauthorized" in error_msg:
                logger.error(
                    "Twitter API authentication failed. Please check:\n"
                    "1. Bearer Token is valid and not expired (regenerate if needed)\n"
                    "2. OAuth 1.0a credentials are correct (API Key, Secret, Access Token, Access Token Secret)\n"
                    "3. App permissions are set to 'Read' in Twitter Developer Portal\n"
                    f"Error: {e}"
                )
            else:
                logger.warning(f"Twitter API authentication test failed: {e}")
    
    async def get_user_id(self, username: str) -> tuple:
        """
        Get user ID from username
        Returns: (user_id, error_type)
        error_type can be: 'rate_limit', 'auth_error', 'not_found', 'no_credentials', 'unknown'
        """
        # Check if credentials are configured
        if not self._has_bearer and not self._has_oauth:
            logger.error("Twitter API credentials not configured")
            return None, 'no_credentials'
        
        try:
            # Try with username first
            try:
                user = await self.client.get_user(username=username)
                if user and user.data:
                    return user.data.id, None
            except Exception as e1:
                # If that fails, try with @ prefix
                try:
                    username_clean = username.lstrip('@')
                    user = await self.client.get_user(username=username_clean)
                    if user and user.data:
                        return user.data.id, None
                except Exception as e2:
                    error_msg1 = str(e1)
                    error_msg2 = str(e2)
                    # Check for rate limit errors (429)
                    if "429" in error_msg1 or "rate limit" in error_msg1.lower() or "Too Many Requests" in error_msg1:
                        logger.warning(f"Twitter API rate limit exceeded for {username}")
                        return None, 'rate_limit'
                    # Check for authentication errors (401)
                    elif "401" in error_msg1 or "Unauthorized" in error_msg1 or "Invalid" in error_msg1:
                        logger.error(f"Twitter API authentication failed for {username}: {e1}")
                        return None, 'auth_error'
                    # Check for not found (404)
                    elif "404" in error_msg1 or "Not Found" in error_msg1:
                        logger.warning(f"User @{username} not found on Twitter")
                        return None, 'not_found'
                    else:
                        logger.error(f"Failed to get user ID for {username}: {e1}")
                        return None, 'unknown'
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate limit" in error_msg.lower() or "Too Many Requests" in error_msg:
                logger.warning(f"Twitter API rate limit exceeded for {username}")
                return None, 'rate_limit'
            elif "401" in error_msg or "Unauthorized" in error_msg or "Invalid" in error_msg:
                logger.error(f"Twitter API authentication failed for {username}: {e}")
                return None, 'auth_error'
            elif "404" in error_msg or "Not Found" in error_msg:
                logger.warning(f"User @{username} not found on Twitter")
                return None, 'not_found'
            else:
                logger.error(f"Failed to get user ID for {username}: {e}")
                return None, 'unknown'
        
        return None, 'unknown'
    
    async def get_recent_tweets(self, username: str, max_results: int = 10) -> List[Dict]:
        """Get recent tweets from a user"""
        try:
            user_id, error_type = await self.get_user_id(username)
            if not user_id:
                return []
            
            tweets = await self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=["created_at", "text", "public_metrics"],
            )
            
            if not tweets.data:
                return []
            
            return [
                {
                    "tweet_id": str(tweet.id),
                    "author_username": username,
                    "content": tweet.text,
                    "created_at": tweet.created_at,
                }
                for tweet in tweets.data
            ]
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate limit" in error_msg.lower() or "Too Many Requests" in error_msg:
                logger.warning(f"Twitter API rate limit exceeded for {username}. Will retry later.")
                return []  # Return empty list instead of raising error
            logger.error(f"Failed to get tweets for {username}: {e}")
            raise TwitterAPIError(f"Failed to fetch tweets: {e}")
    
    async def save_tweet(self, session: AsyncSession, tweet_data: Dict) -> Tweet:
        """Save tweet to database without sentiment analysis"""
        try:
            # Check if tweet already exists
            result = await session.execute(
                select(Tweet).where(Tweet.tweet_id == tweet_data["tweet_id"])
            )
            existing_tweet = result.scalar_one_or_none()
            
            if existing_tweet:
                return existing_tweet
            
            # Convert timezone-aware datetime to timezone-naive UTC
            # Twitter API returns timezone-aware datetimes, but database expects timezone-naive
            created_at = tweet_data["created_at"]
            if created_at and hasattr(created_at, 'tzinfo') and created_at.tzinfo is not None:
                # Convert to UTC and remove timezone info
                created_at = created_at.astimezone(timezone.utc).replace(tzinfo=None)
            
            # Create new tweet without sentiment analysis
            tweet = Tweet(
                tweet_id=tweet_data["tweet_id"],
                author_username=tweet_data["author_username"],
                content=tweet_data["content"],
                created_at=created_at,
                sentiment_score=None,
                sentiment_label=None,
                processed=False,
            )
            
            session.add(tweet)
            await session.commit()
            await session.refresh(tweet)
            
            logger.info(f"Saved tweet {tweet_data['tweet_id']} (sentiment analysis will be done later)")
            return tweet
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to save tweet: {e}")
            raise
    
    async def check_new_tweets(self, session: AsyncSession):
        """Check for new tweets from monitored users"""
        try:
            for username in settings.MONITORED_USERS:
                try:
                    tweets = await self.get_recent_tweets(username, max_results=settings.TWEETS_PER_USER)
                    for tweet_data in tweets:
                        await self.save_tweet(session, tweet_data)
                    await asyncio.sleep(1)  # Rate limit protection
                except TwitterAPIError as e:
                    # If it's a rate limit error, we already logged it and returned empty list
                    # Just continue to next user
                    if "rate limit" in str(e).lower() or "429" in str(e):
                        continue
                    raise
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate limit" in error_msg.lower():
                logger.warning("Twitter API rate limit exceeded. Will retry on next check interval.")
            else:
                logger.error(f"Error checking new tweets: {e}")
    
    async def start_monitoring(self):
        """Start background monitoring task"""
        if self.is_monitoring:
            logger.warning("Monitoring already started")
            return
        
        # Test authentication before starting monitoring
        if self._has_bearer or self._has_oauth:
            await self._test_authentication()
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Twitter monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring task"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Close the Twitter client's aiohttp session to clean up connections
        try:
            # tweepy AsyncClient uses aiohttp under the hood
            # Access the session through the client's _session attribute
            if hasattr(self.client, '_session') and self.client._session:
                if not self.client._session.closed:
                    await self.client._session.close()
            # Alternative: try accessing through client.client.session
            elif hasattr(self.client, 'client') and hasattr(self.client.client, 'session'):
                session = self.client.client.session
                if session and not session.closed:
                    await session.close()
        except Exception as e:
            logger.warning(f"Error closing Twitter client session: {e}")
        
        logger.info("Twitter monitoring stopped")
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        from app.db.database import AsyncSessionLocal
        
        while self.is_monitoring:
            try:
                async with AsyncSessionLocal() as session:
                    await self.check_new_tweets(session)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            await asyncio.sleep(settings.TWEET_CHECK_INTERVAL)

