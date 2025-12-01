"""
Stock Data Endpoints
Uses multiple free APIs with flexible rate limits:
1. Finnhub (primary) - 60 calls/minute
2. Alpha Vantage (fallback) - 5 calls/minute
3. Yahoo Finance via yfinance (last resort)
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Tuple
import httpx
from datetime import datetime, timedelta
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from app.core.config import settings

# Try to import yfinance and pandas, fallback to None if not available
try:
    import yfinance as yf
    import pandas as pd
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    pd = None

logger = logging.getLogger("tradex")

# Thread pool for running synchronous yfinance calls
_executor = ThreadPoolExecutor(max_workers=5)

router = APIRouter()

# In-memory cache for stock data (TTL: 60 seconds)
_cache: Dict[str, Tuple[dict, datetime]] = {}
CACHE_TTL = 60  # seconds
STALE_CACHE_TTL = 3600  # 1 hour - return stale cache if within this time

# API Keys (optional - some APIs work without keys)
FINNHUB_API_KEY = getattr(settings, 'FINNHUB_API_KEY', '') or ''
ALPHA_VANTAGE_API_KEY = getattr(settings, 'ALPHA_VANTAGE_API_KEY', '') or ''


def _get_cached_data(cache_key: str, allow_stale: bool = False) -> Optional[dict]:
    """Get data from cache if it's still valid, optionally return stale cache"""
    if cache_key in _cache:
        data, timestamp = _cache[cache_key]
        age = datetime.utcnow() - timestamp
        
        # Return fresh cache
        if age < timedelta(seconds=CACHE_TTL):
            return data
        
        # Return stale cache if allowed and not too old
        if allow_stale and age < timedelta(seconds=STALE_CACHE_TTL):
            return data
        
        # Cache too old, remove it
        if age >= timedelta(seconds=STALE_CACHE_TTL):
            del _cache[cache_key]
    
    return None


def _set_cached_data(cache_key: str, data: dict):
    """Store data in cache"""
    _cache[cache_key] = (data, datetime.utcnow())


async def _fetch_finnhub_quote(symbol: str) -> dict:
    """
    Fetch current stock quote from Finnhub API
    Free tier: 60 calls/minute, no API key required for basic usage
    """
    symbol_upper = symbol.upper()
    
    # Finnhub API endpoint
    url = f"https://finnhub.io/api/v1/quote"
    params = {"symbol": symbol_upper}
    
    # Add API key if available (optional for free tier)
    if FINNHUB_API_KEY:
        params["token"] = FINNHUB_API_KEY
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 429:
                raise HTTPException(
                    status_code=429,
                    detail="Finnhub API rate limit exceeded. Please try again in a moment."
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Check if symbol is valid (Finnhub returns all zeros for invalid symbols)
            if data.get("c") == 0 and data.get("o") == 0 and data.get("h") == 0:
                raise HTTPException(status_code=404, detail=f"Stock symbol {symbol_upper} not found")
            
            current_price = data.get("c")  # Current price
            previous_close = data.get("pc")  # Previous close
            high = data.get("h")  # High
            low = data.get("l")  # Low
            open_price = data.get("o")  # Open
            
            if current_price is None or current_price == 0:
                raise HTTPException(status_code=404, detail=f"Stock symbol {symbol_upper} not found")
            
            # Build response in same format as other APIs
            return {
                "chart": {
                    "result": [{
                        "meta": {
                            "regularMarketPrice": float(current_price),
                            "previousClose": float(previous_close) if previous_close else float(current_price),
                            "regularMarketVolume": 0,  # Finnhub quote doesn't include volume
                            "regularMarketDayHigh": float(high) if high else float(current_price),
                            "regularMarketDayLow": float(low) if low else float(current_price),
                            "regularMarketOpen": float(open_price) if open_price else float(current_price),
                        },
                        "timestamp": [int(datetime.utcnow().timestamp())],
                        "indicators": {
                            "quote": [{
                                "close": [float(current_price)],
                                "volume": [0],
                            }]
                        }
                    }]
                }
            }
    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Finnhub API request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Finnhub API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching from Finnhub for {symbol_upper}: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error fetching data from Finnhub: {str(e)}")


async def _fetch_alpha_vantage_quote(symbol: str) -> dict:
    """
    Fetch current stock quote from Alpha Vantage API
    Free tier: 5 calls/minute, 500 calls/day - requires API key (free to get)
    """
    symbol_upper = symbol.upper()
    
    if not ALPHA_VANTAGE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Alpha Vantage API key not configured. Get a free key at https://www.alphavantage.co/support/#api-key"
        )
    
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol_upper,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 429:
                raise HTTPException(
                    status_code=429,
                    detail="Alpha Vantage API rate limit exceeded (5 calls/minute). Please try again in a moment."
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                raise HTTPException(status_code=404, detail=f"Stock symbol {symbol_upper} not found")
            
            if "Note" in data:
                # Rate limit message
                raise HTTPException(
                    status_code=429,
                    detail="Alpha Vantage API rate limit exceeded. Please try again in a moment."
                )
            
            quote = data.get("Global Quote", {})
            if not quote:
                raise HTTPException(status_code=404, detail=f"Stock symbol {symbol_upper} not found")
            
            current_price = quote.get("05. price")
            previous_close = quote.get("08. previous close")
            high = quote.get("03. high")
            low = quote.get("04. low")
            open_price = quote.get("02. open")
            volume = quote.get("06. volume", "0")
            
            if not current_price or current_price == "None":
                raise HTTPException(status_code=404, detail=f"Stock symbol {symbol_upper} not found")
            
            # Build response in same format as other APIs
            return {
                "chart": {
                    "result": [{
                        "meta": {
                            "regularMarketPrice": float(current_price),
                            "previousClose": float(previous_close) if previous_close and previous_close != "None" else float(current_price),
                            "regularMarketVolume": int(volume) if volume and volume != "None" else 0,
                            "regularMarketDayHigh": float(high) if high and high != "None" else float(current_price),
                            "regularMarketDayLow": float(low) if low and low != "None" else float(current_price),
                            "regularMarketOpen": float(open_price) if open_price and open_price != "None" else float(current_price),
                        },
                        "timestamp": [int(datetime.utcnow().timestamp())],
                        "indicators": {
                            "quote": [{
                                "close": [float(current_price)],
                                "volume": [int(volume) if volume and volume != "None" else 0],
                            }]
                        }
                    }]
                }
            }
    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Alpha Vantage API request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Alpha Vantage API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching from Alpha Vantage for {symbol_upper}: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error fetching data from Alpha Vantage: {str(e)}")


def _fetch_yahoo_data_via_yfinance_sync(symbol: str, days: int = 30) -> dict:
    """
    Synchronous function to fetch data using yfinance library
    This runs in a thread pool since yfinance is synchronous
    Uses history method primarily (more reliable, less rate-limited) with info as fallback
    """
    try:
        symbol_upper = symbol.upper()
        ticker = yf.Ticker(symbol_upper)
        
        # Determine period for historical data
        if days <= 5:
            period = "5d"
        elif days <= 30:
            period = "1mo"
        elif days <= 90:
            period = "3mo"
        elif days <= 180:
            period = "6mo"
        else:
            period = "1y"
        
        # Use history method first (more reliable and less rate-limited)
        hist = ticker.history(period=period)
        
        if hist.empty:
            # If history fails, try info as last resort
            try:
                logger.debug(f"History empty for {symbol_upper}, trying info")
                info = ticker.info
                if not info or len(info) == 0:
                    raise ValueError(f"Stock symbol {symbol_upper} not found or no data available")
                
                current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
                previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose") or current_price
                volume = info.get("volume") or info.get("regularMarketVolume", 0)
                day_high = info.get("dayHigh") or info.get("regularMarketDayHigh") or current_price
                day_low = info.get("dayLow") or info.get("regularMarketDayLow") or current_price
                day_open = info.get("open") or info.get("regularMarketOpen") or current_price
                
                if current_price is None:
                    raise ValueError(f"Stock symbol {symbol_upper} not found or no data available")
                
                # Create minimal chart data
                timestamps = [int(datetime.utcnow().timestamp())]
                closes = [current_price]
                volumes = [volume]
                
            except Exception as info_error:
                error_msg = str(info_error)
                # Check if it's a rate limit error
                if "429" in error_msg or "rate" in error_msg.lower() or "too many" in error_msg.lower():
                    logger.warning(f"Rate limited when fetching info for {symbol_upper}")
                    raise ValueError(f"Rate limited: {error_msg}")
                raise ValueError(f"Stock symbol {symbol_upper} not found or no data available: {error_msg}")
        else:
            # Get the most recent data points from history
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest
            
            current_price = float(latest["Close"])
            previous_close = float(previous["Close"])
            volume = int(latest["Volume"]) if not pd.isna(latest["Volume"]) else 0
            day_high = float(latest["High"]) if not pd.isna(latest["High"]) else current_price
            day_low = float(latest["Low"]) if not pd.isna(latest["Low"]) else current_price
            day_open = float(latest["Open"]) if not pd.isna(latest["Open"]) else current_price
            
            # Prepare chart data from history
            timestamps = [int(ts.timestamp()) for ts in hist.index]
            closes = [float(x) if not pd.isna(x) else None for x in hist["Close"].tolist()]
            volumes = [int(x) if not pd.isna(x) else 0 for x in hist["Volume"].tolist()]
        
        # Build response in same format as API
        return {
            "chart": {
                "result": [{
                    "meta": {
                        "regularMarketPrice": float(current_price),
                        "previousClose": float(previous_close) if previous_close else float(current_price),
                        "regularMarketVolume": int(volume),
                        "regularMarketDayHigh": float(day_high),
                        "regularMarketDayLow": float(day_low),
                        "regularMarketOpen": float(day_open),
                    },
                    "timestamp": timestamps,
                    "indicators": {
                        "quote": [{
                            "close": closes,
                            "volume": volumes,
                        }]
                    }
                }]
            }
        }
    except ValueError as e:
        error_msg = str(e)
        # Check if it's a rate limit error
        if "rate" in error_msg.lower() or "429" in error_msg or "too many" in error_msg.lower():
            logger.warning(f"Rate limited when fetching {symbol}: {error_msg}")
            raise ValueError(f"Rate limited: Please try again in a few moments")
        logger.warning(f"yfinance fetch failed for {symbol}: {error_msg}")
        raise ValueError(f"yfinance error: {error_msg}")
    except Exception as e:
        error_msg = str(e)
        # Check for rate limiting in exception message
        if "429" in error_msg or "rate" in error_msg.lower() or "too many" in error_msg.lower():
            logger.warning(f"Rate limited when fetching {symbol}: {error_msg}")
            raise ValueError(f"Rate limited: Please try again in a few moments")
        logger.error(f"Unexpected error in yfinance fetch for {symbol}: {error_msg}", exc_info=True)
        raise ValueError(f"yfinance error: {error_msg}")


async def _fetch_yahoo_data_via_yfinance(symbol: str, days: int = 30) -> dict:
    """
    Fetch data using yfinance library (more reliable than direct API calls)
    Runs the synchronous yfinance call in a thread pool
    """
    if not YFINANCE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="yfinance library not available. Please install it: pip install yfinance"
        )
    
    try:
        if not pd:
            raise HTTPException(
                status_code=503,
                detail="pandas library not available. Please install it: pip install pandas"
            )
        
        # Run the synchronous yfinance call in a thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor,
            _fetch_yahoo_data_via_yfinance_sync,
            symbol,
            days
        )
        return result
    except ValueError as e:
        # Convert ValueError to appropriate HTTPException
        error_msg = str(e)
        logger.warning(f"yfinance ValueError for {symbol}: {error_msg}")
        if "rate" in error_msg.lower() or "429" in error_msg or "too many" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="Yahoo Finance API rate limit exceeded. Please try again in a few moments."
            )
        if "not found" in error_msg.lower() or "no data" in error_msg.lower():
            raise HTTPException(status_code=404, detail=f"Stock symbol {symbol} not found")
        # Re-raise as ValueError to be handled by caller
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"yfinance fetch error for {symbol}: {error_msg}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"Error fetching data: {error_msg}")


async def _fetch_yahoo_data_via_api(symbol: str, days: int = 30, max_retries: int = 3) -> dict:
    """
    Fetch data from Yahoo Finance API with retry logic (fallback method)
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol.upper()}?interval=1d&range={days}d"
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                
                # If we get rate limited, wait and retry
                if response.status_code == 429:
                    wait_time = (2 ** attempt) * 2  # Exponential backoff: 2s, 4s, 8s
                    if attempt < max_retries - 1:
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise HTTPException(
                            status_code=429,
                            detail="Yahoo Finance API rate limit exceeded. Please try again in a few moments."
                        )
                
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
            raise HTTPException(status_code=504, detail="Request to Yahoo Finance timed out")
        except httpx.RequestError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
            raise HTTPException(status_code=503, detail=f"Network error: {str(e)}")
    
    raise HTTPException(status_code=500, detail="Failed to fetch data after retries")


async def _fetch_stock_data(symbol: str, days: int = 30) -> dict:
    """
    Fetch stock data using multiple APIs with fallback chain:
    1. Finnhub (60 calls/minute) - fastest and most reliable
    2. Alpha Vantage (5 calls/minute) - good fallback
    3. Yahoo Finance via yfinance - last resort
    """
    symbol_upper = symbol.upper()
    
    # Try Finnhub first (best rate limits: 60 calls/minute)
    try:
        logger.debug(f"Trying Finnhub for {symbol_upper}")
        return await _fetch_finnhub_quote(symbol_upper)
    except HTTPException as e:
        if e.status_code == 404:
            raise  # Don't fallback for 404
        if e.status_code == 429:
            logger.warning(f"Finnhub rate limited for {symbol_upper}, trying Alpha Vantage")
        else:
            logger.warning(f"Finnhub failed for {symbol_upper}: {str(e)}, trying Alpha Vantage")
    except Exception as e:
        logger.warning(f"Finnhub error for {symbol_upper}: {str(e)}, trying Alpha Vantage")
    
    # Try Alpha Vantage (5 calls/minute)
    try:
        logger.debug(f"Trying Alpha Vantage for {symbol_upper}")
        return await _fetch_alpha_vantage_quote(symbol_upper)
    except HTTPException as e:
        if e.status_code == 404:
            raise  # Don't fallback for 404
        if e.status_code == 429:
            logger.warning(f"Alpha Vantage rate limited for {symbol_upper}, trying yfinance")
        elif e.status_code == 503 and "API key not configured" in str(e.detail):
            logger.info(f"Alpha Vantage not configured for {symbol_upper}, trying yfinance")
        else:
            logger.warning(f"Alpha Vantage failed for {symbol_upper}: {str(e)}, trying yfinance")
    except Exception as e:
        logger.warning(f"Alpha Vantage error for {symbol_upper}: {str(e)}, trying yfinance")
    
    # Fallback to yfinance (last resort - often rate limited)
    if YFINANCE_AVAILABLE:
        try:
            logger.debug(f"Trying yfinance for {symbol_upper}")
            return await _fetch_yahoo_data_via_yfinance(symbol_upper, days)
        except HTTPException as e:
            if e.status_code == 404:
                raise  # Don't fallback for 404
            if e.status_code == 429:
                raise  # Don't fallback for rate limits, let endpoint handle stale cache
            logger.warning(f"yfinance failed for {symbol_upper}: {str(e)}")
        except ValueError as e:
            error_msg = str(e)
            if "rate" in error_msg.lower() or "429" in error_msg or "too many" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="All stock data APIs rate limited. Please try again in a few moments."
                )
            if "not found" in error_msg.lower() or "no data" in error_msg.lower():
                raise HTTPException(status_code=404, detail=f"Stock symbol {symbol_upper} not found")
            logger.warning(f"yfinance ValueError for {symbol_upper}: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate" in error_msg.lower() or "too many" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="All stock data APIs rate limited. Please try again in a few moments."
                )
            logger.warning(f"yfinance error for {symbol_upper}: {error_msg}")
    
    # Final fallback to direct Yahoo Finance API
    try:
        logger.debug(f"Trying direct Yahoo Finance API for {symbol_upper}")
        return await _fetch_yahoo_data_via_api(symbol_upper, days)
    except HTTPException as e:
        if e.status_code == 404 or e.status_code == 429:
            raise  # Don't modify 404 or 429 errors
        raise


@router.get("/data/{symbol}")
async def get_stock_data(symbol: str):
    """
    Get current stock data for a symbol
    Proxies request to Yahoo Finance API with caching
    Returns stale cache if rate limited
    """
    symbol_upper = symbol.upper()
    cache_key = f"data_{symbol_upper}"
    
    logger.info(f"Fetching stock data for {symbol_upper}")
    
    # Check cache first (fresh)
    cached = _get_cached_data(cache_key, allow_stale=False)
    if cached:
        logger.debug(f"Returning cached data for {symbol_upper}")
        return cached
    
    try:
        # Fetch data using multiple APIs with fallback
        logger.debug(f"Fetching fresh data for {symbol_upper}")
        data = await _fetch_stock_data(symbol_upper, days=30)
        
        if not data.get("chart") or not data["chart"].get("result") or len(data["chart"]["result"]) == 0:
            logger.warning(f"No chart data returned for {symbol_upper}")
            raise HTTPException(status_code=404, detail=f"Stock symbol {symbol_upper} not found")
        
        result = data["chart"]["result"][0]
        meta = result.get("meta", {})
        
        current_price = meta.get("regularMarketPrice")
        previous_close = meta.get("previousClose")
        
        logger.debug(f"Data for {symbol_upper}: price={current_price}, previousClose={previous_close}")
        
        if current_price is None:
            logger.warning(f"Current price is None for {symbol_upper}")
            raise HTTPException(status_code=404, detail=f"Incomplete data for symbol {symbol_upper}: current price not available")
        
        if previous_close is None:
            logger.warning(f"Previous close is None for {symbol_upper}, using current price")
            previous_close = current_price
        
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
        
        response_data = {
            "symbol": symbol_upper,
            "price": current_price,
            "change": change,
            "changePercent": change_percent,
            "volume": meta.get("regularMarketVolume", 0),
            "high": meta.get("regularMarketDayHigh", current_price),
            "low": meta.get("regularMarketDayLow", current_price),
            "open": meta.get("regularMarketOpen", current_price),
            "previousClose": previous_close,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Cache the response
        _set_cached_data(cache_key, response_data)
        logger.info(f"Successfully fetched and cached data for {symbol_upper}")
        
        return response_data
    except HTTPException as e:
        # If rate limited, try to return stale cache
        if e.status_code == 429:
            stale_cache = _get_cached_data(cache_key, allow_stale=True)
            if stale_cache:
                logger.info(f"Rate limited for {symbol_upper}, returning stale cache")
                stale_cache["stale"] = True  # Mark as stale
                stale_cache["message"] = "Rate limited - showing cached data"
                return stale_cache
        logger.error(f"HTTPException for {symbol_upper}: {e.status_code} - {e.detail}")
        raise
    except ValueError as e:
        # Handle ValueError from yfinance (usually means symbol not found)
        error_msg = str(e)
        logger.error(f"ValueError for {symbol_upper}: {error_msg}")
        if "not found" in error_msg.lower() or "no data" in error_msg.lower():
            raise HTTPException(status_code=404, detail=f"Stock symbol {symbol_upper} not found")
        # Try stale cache before failing
        stale_cache = _get_cached_data(cache_key, allow_stale=True)
        if stale_cache:
            logger.warning(f"Error fetching {symbol_upper}, returning stale cache: {error_msg}")
            stale_cache["stale"] = True
            stale_cache["message"] = f"Error fetching fresh data - showing cached data: {error_msg}"
            return stale_cache
        raise HTTPException(status_code=404, detail=f"Stock symbol {symbol_upper} not found: {error_msg}")
    except Exception as e:
        # On any other error, try stale cache
        error_msg = str(e)
        logger.error(f"Unexpected error fetching {symbol_upper}: {error_msg}", exc_info=True)
        stale_cache = _get_cached_data(cache_key, allow_stale=True)
        if stale_cache:
            logger.warning(f"Error fetching {symbol_upper}, returning stale cache: {error_msg}")
            stale_cache["stale"] = True
            stale_cache["message"] = f"Error fetching fresh data - showing cached data: {error_msg}"
            return stale_cache
        raise HTTPException(status_code=500, detail=f"Internal error: {error_msg}")


@router.get("/history/{symbol}")
async def get_stock_history(symbol: str, days: int = 30):
    """
    Get historical stock data for a symbol
    Proxies request to Yahoo Finance API with caching
    Returns stale cache if rate limited
    
    Args:
        symbol: Stock symbol (e.g., TSLA)
        days: Number of days of history to fetch (default: 30)
    """
    if days < 1 or days > 365:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 365")
    
    symbol_upper = symbol.upper()
    cache_key = f"history_{symbol_upper}_{days}"
    
    # Check cache first (fresh)
    cached = _get_cached_data(cache_key, allow_stale=False)
    if cached:
        return cached
    
    try:
        # Fetch data using multiple APIs with fallback
        data = await _fetch_stock_data(symbol_upper, days=days)
        
        if not data.get("chart") or not data["chart"].get("result") or len(data["chart"]["result"]) == 0:
            raise HTTPException(status_code=404, detail=f"Stock symbol {symbol} not found")
        
        result = data["chart"]["result"][0]
        timestamps = result.get("timestamp", [])
        quotes = result.get("indicators", {}).get("quote", [{}])[0]
        
        if not timestamps or not quotes:
            raise HTTPException(status_code=404, detail=f"No historical data available for symbol {symbol}")
        
        chart_data = []
        for i, timestamp in enumerate(timestamps):
            if i < len(quotes.get("close", [])) and quotes["close"][i] is not None:
                chart_data.append({
                    "date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d"),
                    "price": quotes["close"][i],
                    "volume": quotes.get("volume", [0])[i] if i < len(quotes.get("volume", [])) else 0,
                })
        
        # Cache the response
        _set_cached_data(cache_key, chart_data)
        
        return chart_data
    except HTTPException as e:
        # If rate limited, try to return stale cache
        if e.status_code == 429:
            stale_cache = _get_cached_data(cache_key, allow_stale=True)
            if stale_cache:
                logger.info(f"Rate limited for {symbol_upper} history, returning stale cache")
                return stale_cache
        raise
    except Exception as e:
        # On any other error, try stale cache
        stale_cache = _get_cached_data(cache_key, allow_stale=True)
        if stale_cache:
            logger.warning(f"Error fetching {symbol_upper} history, returning stale cache: {str(e)}")
            return stale_cache
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

