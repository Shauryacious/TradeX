import axios, { AxiosError } from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Retry logic for rate-limited requests
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second base delay

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Request interceptor for retry logic
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as InternalAxiosRequestConfig & { _retry?: boolean; _retryCount?: number };
    
    // Don't retry on connection refused errors (server not running)
    const isConnectionRefused = 
      error.code === 'ECONNREFUSED' || 
      error.message?.includes('ERR_CONNECTION_REFUSED') ||
      error.message?.includes('Network Error');
    
    // Only retry on 429 (rate limit) or temporary network errors (not connection refused)
    if (
      (error.response?.status === 429 || (!error.response && !isConnectionRefused)) &&
      config &&
      !config._retry &&
      (config._retryCount || 0) < MAX_RETRIES
    ) {
      config._retry = true;
      config._retryCount = (config._retryCount || 0) + 1;
      
      // Exponential backoff: 1s, 2s, 4s
      const delay = RETRY_DELAY * Math.pow(2, (config._retryCount || 1) - 1);
      
      if (error.response?.status === 429) {
        console.log(`Rate limited. Retrying in ${delay}ms... (attempt ${config._retryCount}/${MAX_RETRIES})`);
      } else {
        console.log(`Network error. Retrying in ${delay}ms... (attempt ${config._retryCount}/${MAX_RETRIES})`);
      }
      
      await sleep(delay);
      
      return api(config);
    }
    
    return Promise.reject(error);
  }
);

export interface Tweet {
  id: number;
  tweet_id: string;
  author_username: string;
  content: string;
  created_at: string;
  sentiment_score: number | null;
  sentiment_label: string | null;
  processed: boolean;
  created_at_db: string;
}

export interface Trade {
  id: number;
  symbol: string;
  side: string;
  quantity: number;
  price: number;
  order_id: string | null;
  status: string;
  tweet_id: number | null;
  sentiment_score: number | null;
  reason: string | null;
  created_at: string;
}

export interface Position {
  id: number;
  symbol: string;
  quantity: number;
  average_price: number;
  current_price: number;
  unrealized_pnl: number;
  updated_at: string;
}

export interface StockData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  previousClose: number;
  timestamp: string;
  stale?: boolean; // Indicates if data is from cache
  message?: string; // Optional message about data freshness
}

export interface TradeRequest {
  symbol: string;
  sentiment_score: number;
  tweet_id?: number;
  reason?: string;
}

// Tweets API
export const fetchTweets = async (author?: string, limit: number = 10): Promise<Tweet[]> => {
  const params: Record<string, string | number> = { limit };
  if (author) {
    params.author = author;
  }
  const response = await api.get('/api/v1/tweets/', { params });
  return response.data;
};

// Fetch tweets from Twitter API
export interface FetchTweetsResponse {
  success: boolean;
  message: string;
  tweets_fetched: number;
  tweets_saved: number;
  tweets_skipped: number;
  tweets: Tweet[];
  status_messages: string[];
}

export const fetchTweetsFromTwitter = async (
  username: string,
  maxResults: number = 10
): Promise<FetchTweetsResponse> => {
  const response = await api.post('/api/v1/tweets/fetch', {
    username,
    max_results: maxResults,
  });
  return response.data;
};

// Stock Data API (using backend proxy to avoid CORS issues)
export const fetchStockData = async (symbol: string = 'TSLA'): Promise<StockData> => {
  try {
    const response = await api.get(`/api/v1/stocks/data/${symbol}`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<{ detail?: string }>;
      
      if (axiosError.response?.status === 429) {
        const errorMessage = axiosError.response.data?.detail || 
          'Rate limit exceeded. Please wait a moment and try again.';
        throw new Error(errorMessage);
      }
      
      if (axiosError.response?.status === 404) {
        throw new Error(`Stock symbol "${symbol}" not found.`);
      }
      
      if (axiosError.response?.status === 503 || axiosError.response?.status === 504) {
        throw new Error('Service temporarily unavailable. Please try again in a moment.');
      }
      
      if (!axiosError.response) {
        // Connection refused or network error
        if (axiosError.code === 'ECONNREFUSED' || 
            axiosError.message.includes('ERR_CONNECTION_REFUSED') ||
            axiosError.message.includes('Network Error')) {
          throw new Error('Cannot connect to server. Please make sure the server is running on http://localhost:8000');
        }
        throw new Error('Network error. Please check your connection and try again.');
      }
      
      throw new Error(axiosError.response.data?.detail || 'Failed to fetch stock data.');
    }
    
    console.error('Error fetching stock data:', error);
    throw error instanceof Error ? error : new Error('An unexpected error occurred.');
  }
};

// Get stock historical data for chart
export interface ChartDataPoint {
  date: string;
  price: number;
  volume: number;
}

export const fetchStockHistory = async (symbol: string = 'TSLA', days: number = 30): Promise<ChartDataPoint[]> => {
  try {
    const response = await api.get(`/api/v1/stocks/history/${symbol}`, {
      params: { days },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<{ detail?: string }>;
      
      if (axiosError.response?.status === 429) {
        const errorMessage = axiosError.response.data?.detail || 
          'Rate limit exceeded. Please wait a moment and try again.';
        throw new Error(errorMessage);
      }
      
      if (axiosError.response?.status === 404) {
        throw new Error(`Historical data for "${symbol}" not found.`);
      }
      
      if (axiosError.response?.status === 503 || axiosError.response?.status === 504) {
        throw new Error('Service temporarily unavailable. Please try again in a moment.');
      }
      
      if (!axiosError.response) {
        // Connection refused or network error
        if (axiosError.code === 'ECONNREFUSED' || 
            axiosError.message.includes('ERR_CONNECTION_REFUSED') ||
            axiosError.message.includes('Network Error')) {
          throw new Error('Cannot connect to server. Please make sure the server is running on http://localhost:8000');
        }
        throw new Error('Network error. Please check your connection and try again.');
      }
      
      throw new Error(axiosError.response.data?.detail || 'Failed to fetch stock history.');
    }
    
    console.error('Error fetching stock history:', error);
    throw error instanceof Error ? error : new Error('An unexpected error occurred.');
  }
};

// Execute trade
export const executeTrade = async (tradeRequest: TradeRequest): Promise<Trade> => {
  const response = await api.post('/api/v1/trades/execute', tradeRequest);
  return response.data;
};

// Get positions
export const fetchPositions = async (): Promise<Position[]> => {
  const response = await api.get('/api/v1/positions/');
  return response.data;
};

// Get trades
export const fetchTrades = async (symbol?: string): Promise<Trade[]> => {
  const params: Record<string, string> = {};
  if (symbol) {
    params.symbol = symbol;
  }
  const response = await api.get('/api/v1/trades/', { params });
  return response.data;
};

// Analyze tweets sentiment
export interface AnalyzeTweetsRequest {
  tweet_ids: number[];
}

export interface AnalyzeTweetsResponse {
  success: boolean;
  message: string;
  analyzed_count: number;
  tweets: Tweet[];
}

export const analyzeTweets = async (
  tweetIds: number[]
): Promise<AnalyzeTweetsResponse> => {
  const response = await api.post('/api/v1/tweets/analyze', {
    tweet_ids: tweetIds,
  });
  return response.data;
};

