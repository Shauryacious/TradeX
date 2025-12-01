"""
Tweet Endpoints
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.db.models import Tweet
from app.services.twitter_service import TwitterService
from app.services.reddit_service import RedditService

router = APIRouter()

# Global service instances (initialized on first use)
_twitter_service: Optional[TwitterService] = None
_reddit_service: Optional[RedditService] = None


def get_twitter_service() -> TwitterService:
    """Get or create TwitterService instance"""
    global _twitter_service
    if _twitter_service is None:
        _twitter_service = TwitterService()
    return _twitter_service


def get_reddit_service() -> RedditService:
    """Get or create RedditService instance"""
    global _reddit_service
    if _reddit_service is None:
        _reddit_service = RedditService()
    return _reddit_service


class TweetResponse(BaseModel):
    """Tweet response model"""
    id: int
    tweet_id: str
    author_username: str
    content: str
    created_at: datetime
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    processed: bool
    created_at_db: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[TweetResponse])
async def get_tweets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    author: Optional[str] = None,
    sentiment: Optional[str] = Query(None, regex="^(positive|negative|neutral)$"),
    db: AsyncSession = Depends(get_db),
):
    """Get tweets with optional filtering"""
    query = select(Tweet).order_by(desc(Tweet.created_at_db))
    
    if author:
        query = query.where(Tweet.author_username == author)
    
    if sentiment:
        query = query.where(Tweet.sentiment_label == sentiment)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    tweets = result.scalars().all()
    
    return tweets


class FetchTweetsRequest(BaseModel):
    """Request model for fetching tweets"""
    username: str
    max_results: int = 10


class FetchTweetsResponse(BaseModel):
    """Response model for fetching tweets"""
    success: bool
    message: str
    tweets_fetched: int
    tweets_saved: int
    tweets_skipped: int
    tweets: List[TweetResponse]
    status_messages: List[str]


@router.post("/fetch", response_model=FetchTweetsResponse)
async def fetch_tweets_from_twitter(
    request: FetchTweetsRequest,
    db: AsyncSession = Depends(get_db),
    twitter_service: TwitterService = Depends(get_twitter_service),
    reddit_service: RedditService = Depends(get_reddit_service),
):
    """
    Fetch tweets from Twitter API for a given username and save them to the database.
    Returns progress information about what's happening.
    """
    status_messages = []
    tweets_fetched = 0
    tweets_saved = 0
    tweets_skipped = 0
    saved_tweets = []
    
    try:
        # Step 1: Validate username
        username = request.username.strip().lstrip('@')
        if not username:
            raise HTTPException(status_code=400, detail="Username cannot be empty")
        
        status_messages.append(f"Starting to fetch tweets for @{username}...")
        
        # Step 2: Get user ID
        status_messages.append(f"Looking up user ID for @{username}...")
        user_id, error_type = await twitter_service.get_user_id(username)
        
        if not user_id:
            # Provide specific error messages based on error type
            if error_type == 'no_credentials':
                status_messages.append("❌ Twitter API credentials not configured")
                status_messages.append("Please configure Twitter API credentials in your .env file:")
                status_messages.append("- TWITTER_BEARER_TOKEN (recommended)")
                status_messages.append("- Or TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET")
                status_messages.append("See documentation: server/documentation/setup/api-credentials.md")
                
                return FetchTweetsResponse(
                    success=False,
                    message="Twitter API credentials are not configured. Please add your Twitter API credentials to the .env file.",
                    tweets_fetched=0,
                    tweets_saved=0,
                    tweets_skipped=0,
                    tweets=[],
                    status_messages=status_messages
                )
            elif error_type == 'rate_limit':
                status_messages.append("⚠️ Twitter API rate limit exceeded")
                status_messages.append("Switching to Reddit API (free alternative)...")
                
                # Try Reddit as a free fallback
                reddit_service = get_reddit_service()
                status_messages.append(f"Fetching Reddit posts related to @{username}...")
                
                try:
                    reddit_posts = await reddit_service.get_posts_for_username(username, request.max_results)
                    
                    if reddit_posts:
                        status_messages.append(f"✅ Found {len(reddit_posts)} Reddit posts")
                        status_messages.append("Saving Reddit posts to database...")
                        
                        # Convert Reddit posts to tweet format and save
                        for idx, post_data in enumerate(reddit_posts, 1):
                            try:
                                status_messages.append(f"Processing Reddit post {idx}/{len(reddit_posts)}...")
                                
                                # Check if post already exists
                                result = await db.execute(
                                    select(Tweet).where(Tweet.tweet_id == post_data["tweet_id"])
                                )
                                existing_tweet = result.scalar_one_or_none()
                                
                                if existing_tweet:
                                    tweets_skipped += 1
                                    saved_tweets.append(TweetResponse(
                                        id=existing_tweet.id,
                                        tweet_id=existing_tweet.tweet_id,
                                        author_username=existing_tweet.author_username,
                                        content=existing_tweet.content,
                                        created_at=existing_tweet.created_at,
                                        sentiment_score=existing_tweet.sentiment_score,
                                        sentiment_label=existing_tweet.sentiment_label,
                                        processed=existing_tweet.processed,
                                        created_at_db=existing_tweet.created_at_db,
                                    ))
                                else:
                                    # Save new post (this includes sentiment analysis)
                                    tweet = await twitter_service.save_tweet(db, post_data)
                                    tweets_saved += 1
                                    tweets_fetched += 1
                                    saved_tweets.append(TweetResponse(
                                        id=tweet.id,
                                        tweet_id=tweet.tweet_id,
                                        author_username=tweet.author_username,
                                        content=tweet.content,
                                        created_at=tweet.created_at,
                                        sentiment_score=tweet.sentiment_score,
                                        sentiment_label=tweet.sentiment_label,
                                        processed=tweet.processed,
                                        created_at_db=tweet.created_at_db,
                                    ))
                            except Exception as e:
                                status_messages.append(f"Error processing Reddit post {idx}: {str(e)}")
                        
                        status_messages.append("✅ Reddit posts fetched and saved successfully!")
                        
                        return FetchTweetsResponse(
                            success=True,
                            message=f"Twitter API rate limited. Fetched {tweets_fetched} Reddit posts instead. Saved {tweets_saved} new, skipped {tweets_skipped} existing.",
                            tweets_fetched=tweets_fetched,
                            tweets_saved=tweets_saved,
                            tweets_skipped=tweets_skipped,
                            tweets=saved_tweets,
                            status_messages=status_messages
                        )
                    else:
                        status_messages.append("❌ No Reddit posts found")
                        status_messages.append("Twitter API rate limit exceeded and no Reddit alternatives found.")
                        status_messages.append("Please wait 15 minutes and try again, or check your Twitter Developer Portal.")
                        
                        return FetchTweetsResponse(
                            success=False,
                            message=f"Twitter API rate limit exceeded and no Reddit alternatives found. Please wait 15 minutes and try again.",
                            tweets_fetched=0,
                            tweets_saved=0,
                            tweets_skipped=0,
                            tweets=[],
                            status_messages=status_messages
                        )
                except Exception as e:
                    status_messages.append(f"❌ Error fetching from Reddit: {str(e)}")
                    status_messages.append("Twitter API rate limit exceeded. Please wait 15 minutes and try again.")
                    
                    return FetchTweetsResponse(
                        success=False,
                        message=f"Twitter API rate limit exceeded. Reddit fallback also failed. Please wait 15 minutes and try again.",
                        tweets_fetched=0,
                        tweets_saved=0,
                        tweets_skipped=0,
                        tweets=[],
                        status_messages=status_messages
                    )
            elif error_type == 'auth_error':
                status_messages.append("❌ Twitter API authentication failed")
                status_messages.append("Your Twitter API credentials are invalid or expired.")
                status_messages.append("Please check:")
                status_messages.append("1. Bearer Token is valid and not expired")
                status_messages.append("2. OAuth credentials are correct")
                status_messages.append("3. App permissions are set to 'Read' in Twitter Developer Portal")
                status_messages.append("4. Regenerate credentials if needed")
                
                return FetchTweetsResponse(
                    success=False,
                    message="Twitter API authentication failed. Please check your API credentials in the .env file.",
                    tweets_fetched=0,
                    tweets_saved=0,
                    tweets_skipped=0,
                    tweets=[],
                    status_messages=status_messages
                )
            elif error_type == 'not_found':
                status_messages.append(f"❌ User @{username} not found on Twitter")
                status_messages.append("This could mean:")
                status_messages.append("1. The username is incorrect")
                status_messages.append("2. The account has been suspended or deleted")
                status_messages.append("3. The account is private")
                
                return FetchTweetsResponse(
                    success=False,
                    message=f"User @{username} not found on Twitter. Please verify the username is correct.",
                    tweets_fetched=0,
                    tweets_saved=0,
                    tweets_skipped=0,
                    tweets=[],
                    status_messages=status_messages
                )
            else:
                status_messages.append("⚠️ Unable to fetch user information")
                status_messages.append("This could be due to:")
                status_messages.append("1. Twitter API rate limit exceeded (try again later)")
                status_messages.append("2. Username doesn't exist or is incorrect")
                status_messages.append("3. Twitter API credentials need to be configured")
                status_messages.append("4. Network connectivity issues")
                
                return FetchTweetsResponse(
                    success=False,
                    message=f"Unable to fetch tweets for @{username}. Please check the username and try again later.",
                    tweets_fetched=0,
                    tweets_saved=0,
                    tweets_skipped=0,
                    tweets=[],
                    status_messages=status_messages
                )
        
        status_messages.append(f"Found user ID: {user_id}")
        
        # Step 3: Fetch tweets from Twitter
        status_messages.append(f"Fetching up to {request.max_results} recent tweets from Twitter API...")
        tweet_data_list = await twitter_service.get_recent_tweets(username, request.max_results)
        tweets_fetched = len(tweet_data_list)
        
        if tweets_fetched == 0:
            status_messages.append(f"No tweets found for @{username}")
            return FetchTweetsResponse(
                success=True,
                message=f"No tweets found for @{username}",
                tweets_fetched=0,
                tweets_saved=0,
                tweets_skipped=0,
                tweets=[],
                status_messages=status_messages
            )
        
        status_messages.append(f"Successfully fetched {tweets_fetched} tweet(s) from Twitter")
        
        # Step 4: Save tweets to database with sentiment analysis
        status_messages.append("Saving tweets to database and analyzing sentiment...")
        
        for idx, tweet_data in enumerate(tweet_data_list, 1):
            try:
                status_messages.append(f"Processing tweet {idx}/{tweets_fetched}...")
                
                # Check if tweet already exists
                result = await db.execute(
                    select(Tweet).where(Tweet.tweet_id == tweet_data["tweet_id"])
                )
                existing_tweet = result.scalar_one_or_none()
                
                if existing_tweet:
                    tweets_skipped += 1
                    status_messages.append(f"Tweet {idx} already exists in database, skipping...")
                    saved_tweets.append(TweetResponse(
                        id=existing_tweet.id,
                        tweet_id=existing_tweet.tweet_id,
                        author_username=existing_tweet.author_username,
                        content=existing_tweet.content,
                        created_at=existing_tweet.created_at,
                        sentiment_score=existing_tweet.sentiment_score,
                        sentiment_label=existing_tweet.sentiment_label,
                        processed=existing_tweet.processed,
                        created_at_db=existing_tweet.created_at_db,
                    ))
                else:
                    # Save new tweet (this includes sentiment analysis)
                    tweet = await twitter_service.save_tweet(db, tweet_data)
                    tweets_saved += 1
                    status_messages.append(
                        f"Tweet {idx} saved with sentiment: {tweet.sentiment_label or 'neutral'}"
                    )
                    saved_tweets.append(TweetResponse(
                        id=tweet.id,
                        tweet_id=tweet.tweet_id,
                        author_username=tweet.author_username,
                        content=tweet.content,
                        created_at=tweet.created_at,
                        sentiment_score=tweet.sentiment_score,
                        sentiment_label=tweet.sentiment_label,
                        processed=tweet.processed,
                        created_at_db=tweet.created_at_db,
                    ))
            except Exception as e:
                status_messages.append(f"Error processing tweet {idx}: {str(e)}")
                # Continue with next tweet
        
        status_messages.append("✅ Tweet fetching and saving completed!")
        
        return FetchTweetsResponse(
            success=True,
            message=f"Successfully fetched {tweets_fetched} tweet(s). Saved {tweets_saved} new, skipped {tweets_skipped} existing.",
            tweets_fetched=tweets_fetched,
            tweets_saved=tweets_saved,
            tweets_skipped=tweets_skipped,
            tweets=saved_tweets,
            status_messages=status_messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        status_messages.append(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch tweets: {str(e)}"
        )


@router.get("/stats/summary")
async def get_tweet_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get tweet statistics"""
    from sqlalchemy import func
    
    # Total tweets
    total_result = await db.execute(select(func.count(Tweet.id)))
    total_tweets = total_result.scalar()
    
    # Sentiment distribution
    sentiment_result = await db.execute(
        select(Tweet.sentiment_label, func.count(Tweet.id))
        .group_by(Tweet.sentiment_label)
    )
    sentiment_dist = {row[0] or "unknown": row[1] for row in sentiment_result.all()}
    
    # By author
    author_result = await db.execute(
        select(Tweet.author_username, func.count(Tweet.id))
        .group_by(Tweet.author_username)
    )
    author_dist = {row[0]: row[1] for row in author_result.all()}
    
    return {
        "total_tweets": total_tweets,
        "sentiment_distribution": sentiment_dist,
        "author_distribution": author_dist,
    }


@router.get("/{tweet_id}", response_model=TweetResponse)
async def get_tweet(
    tweet_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific tweet by ID"""
    result = await db.execute(
        select(Tweet).where(Tweet.tweet_id == tweet_id)
    )
    tweet = result.scalar_one_or_none()
    
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    
    return tweet

