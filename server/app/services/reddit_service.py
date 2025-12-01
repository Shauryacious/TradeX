"""
Reddit Service
Free alternative to Twitter API for fetching social media content
Uses Reddit's public API (no authentication required)
"""

import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timezone
from app.core.logging import setup_logging

logger = setup_logging()


class RedditService:
    """Service for Reddit API interactions (free, no auth required)"""
    
    BASE_URL = "https://www.reddit.com"
    
    # Map Twitter usernames to Reddit subreddits
    USERNAME_TO_SUBREDDIT = {
        "elonmusk": ["r/elonmusk", "r/tesla", "r/SpaceX", "r/teslainvestorsclub"],
        "tesla": ["r/tesla", "r/teslainvestorsclub", "r/RealTesla"],
    }
    
    def __init__(self):
        """Initialize Reddit service"""
        logger.info("Reddit service initialized (free, no authentication required)")
    
    async def get_posts_from_subreddit(self, subreddit: str, limit: int = 10) -> List[Dict]:
        """
        Get recent posts from a subreddit
        Args:
            subreddit: Subreddit name (with or without r/ prefix)
            limit: Number of posts to fetch (max 100)
        Returns:
            List of post dictionaries
        """
        try:
            # Remove r/ prefix if present
            subreddit_clean = subreddit.lstrip("r/")
            url = f"{self.BASE_URL}/r/{subreddit_clean}/new.json?limit={min(limit, 100)}"
            
            headers = {
                "User-Agent": "TradeX/1.0 (Educational Project)"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = []
                        
                        if "data" in data and "children" in data["data"]:
                            for child in data["data"]["children"]:
                                post_data = child.get("data", {})
                                
                                # Convert Reddit post to tweet-like format
                                posts.append({
                                    "tweet_id": f"reddit_{post_data.get('id', '')}",
                                    "author_username": post_data.get("author", "unknown"),
                                    "content": post_data.get("title", "") + "\n\n" + post_data.get("selftext", ""),
                                    "created_at": datetime.fromtimestamp(
                                        post_data.get("created_utc", 0),
                                        tz=timezone.utc
                                    ),
                                    "source": "reddit",
                                    "subreddit": subreddit_clean,
                                    "score": post_data.get("score", 0),
                                    "url": f"https://reddit.com{post_data.get('permalink', '')}",
                                })
                        
                        logger.info(f"Fetched {len(posts)} posts from r/{subreddit_clean}")
                        return posts
                    else:
                        logger.warning(f"Reddit API returned status {response.status} for r/{subreddit_clean}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit}: {e}")
            return []
    
    async def get_posts_for_username(self, username: str, limit: int = 10) -> List[Dict]:
        """
        Get posts related to a Twitter username by searching relevant subreddits
        Args:
            username: Twitter username (e.g., "elonmusk")
            limit: Number of posts per subreddit
        Returns:
            List of post dictionaries
        """
        all_posts = []
        
        # Get relevant subreddits for this username
        subreddits = self.USERNAME_TO_SUBREDDIT.get(username.lower(), [f"r/{username}"])
        
        # Fetch from each subreddit
        for subreddit in subreddits:
            try:
                posts = await self.get_posts_from_subreddit(subreddit, limit)
                all_posts.extend(posts)
            except Exception as e:
                logger.warning(f"Failed to fetch from {subreddit}: {e}")
                continue
        
        # Sort by creation date (newest first)
        all_posts.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Return top N posts
        return all_posts[:limit]
    
    async def search_posts(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search Reddit for posts matching a query
        Args:
            query: Search query
            limit: Number of results
        Returns:
            List of post dictionaries
        """
        try:
            url = f"{self.BASE_URL}/search.json"
            params = {
                "q": query,
                "limit": min(limit, 100),
                "sort": "new"
            }
            
            headers = {
                "User-Agent": "TradeX/1.0 (Educational Project)"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = []
                        
                        if "data" in data and "children" in data["data"]:
                            for child in data["data"]["children"]:
                                post_data = child.get("data", {})
                                
                                posts.append({
                                    "tweet_id": f"reddit_{post_data.get('id', '')}",
                                    "author_username": post_data.get("author", "unknown"),
                                    "content": post_data.get("title", "") + "\n\n" + post_data.get("selftext", ""),
                                    "created_at": datetime.fromtimestamp(
                                        post_data.get("created_utc", 0),
                                        tz=timezone.utc
                                    ),
                                    "source": "reddit",
                                    "subreddit": post_data.get("subreddit", ""),
                                    "score": post_data.get("score", 0),
                                    "url": f"https://reddit.com{post_data.get('permalink', '')}",
                                })
                        
                        return posts
                    else:
                        return []
        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
            return []

