# TradeX Client

React + Vite + TypeScript + Tailwind CSS frontend for the TradeX trading platform.

## Features

1. **Fetch Tweets** - Fetch and display latest tweets from Elon Musk and Tesla
2. **Stock Data** - View Tesla stock data with interactive charts
3. **Sentiment Analysis** - Analyze sentiment of fetched tweets
4. **Trade Execution** - Execute trades based on sentiment analysis results

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file (optional):
```env
VITE_API_BASE_URL=http://localhost:8000
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Chart library for stock data visualization
- **Axios** - HTTP client for API requests

## Project Structure

```
src/
  components/        # React components
    TweetList.tsx           # Tweet fetching and display
    StockChart.tsx          # Stock data and charts
    SentimentAnalysis.tsx   # Sentiment analysis results
    TradeExecution.tsx      # Trade execution
  services/         # API service layer
    api.ts                  # API client and types
  App.tsx           # Main application component
  main.tsx          # Application entry point
  index.css         # Tailwind CSS imports
```

## Usage Flow

1. Click "Fetch Tweets" to load tweets from Elon Musk and Tesla
2. Click "Fetch Stock Data" to view Tesla stock information and charts
3. Click "Run Analysis" to perform sentiment analysis on the fetched tweets
4. Click "Execute Trade" to execute a trade based on the sentiment analysis results

## API Integration

The client communicates with the TradeX backend API running on `http://localhost:8000` by default.

Endpoints used:
- `GET /api/v1/tweets/` - Fetch tweets
- `POST /api/v1/trades/execute` - Execute trades
- Stock data is fetched from Yahoo Finance API (public, no key required)
