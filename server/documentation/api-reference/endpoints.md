# API Reference

Complete API endpoint documentation for TradeX Server.

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Authentication

Currently, the API does not require authentication. For production deployments, implement authentication middleware.

## Endpoints

### Health Check

#### `GET /health`
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "TradeX API"
}
```

#### `GET /api/v1/health/detailed`
Detailed health check with service status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-30T15:00:00.000000",
  "services": {
    "twitter": {
      "configured": true,
      "monitoring": true
    },
    "trading": {
      "configured": true,
      "enabled": false
    }
  }
}
```

### Tweets

#### `GET /api/v1/tweets/`
Get all tweets with optional filtering and pagination.

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100, max: 1000) - Number of records to return
- `author` (string, optional) - Filter by author username
- `sentiment` (string, optional) - Filter by sentiment: `positive`, `negative`, or `neutral`

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/tweets/?author=elonmusk&sentiment=positive&limit=10"
```

**Response:**
```json
[
  {
    "id": 1,
    "tweet_id": "1234567890",
    "author_username": "elonmusk",
    "content": "Great news!",
    "created_at": "2025-11-30T10:00:00",
    "sentiment_score": 0.75,
    "sentiment_label": "positive",
    "processed": false,
    "created_at_db": "2025-11-30T10:05:00"
  }
]
```

#### `GET /api/v1/tweets/{tweet_id}`
Get a specific tweet by Twitter tweet ID.

**Path Parameters:**
- `tweet_id` (string) - Twitter tweet ID

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/tweets/1234567890"
```

**Response:**
```json
{
  "id": 1,
  "tweet_id": "1234567890",
  "author_username": "elonmusk",
  "content": "Great news!",
  "created_at": "2025-11-30T10:00:00",
  "sentiment_score": 0.75,
  "sentiment_label": "positive",
  "processed": false,
  "created_at_db": "2025-11-30T10:05:00"
}
```

#### `GET /api/v1/tweets/stats/summary`
Get tweet statistics.

**Response:**
```json
{
  "total_tweets": 150,
  "sentiment_distribution": {
    "positive": 45,
    "negative": 30,
    "neutral": 75
  },
  "author_distribution": {
    "elonmusk": 50,
    "Tesla": 60,
    "realDonaldTrump": 40
  }
}
```

### Trades

#### `GET /api/v1/trades/`
Get all trades with optional filtering and pagination.

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100, max: 1000) - Number of records to return
- `symbol` (string, optional) - Filter by stock symbol
- `status` (string, optional) - Filter by status: `pending`, `filled`, `cancelled`, `rejected`

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/trades/?symbol=TSLA&status=filled&limit=20"
```

**Response:**
```json
[
  {
    "id": 1,
    "symbol": "TSLA",
    "side": "buy",
    "quantity": 10,
    "price": 250.50,
    "order_id": "order_123",
    "status": "filled",
    "tweet_id": 1,
    "sentiment_score": 0.75,
    "reason": "Sentiment-based trade: 0.75",
    "created_at": "2025-11-30T10:10:00"
  }
]
```

#### `GET /api/v1/trades/{trade_id}`
Get a specific trade by ID.

**Path Parameters:**
- `trade_id` (int) - Trade ID

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/trades/1"
```

#### `GET /api/v1/trades/stats/summary`
Get trade statistics.

**Response:**
```json
{
  "total_trades": 25,
  "status_distribution": {
    "filled": 20,
    "pending": 3,
    "cancelled": 2
  },
  "side_distribution": {
    "buy": 15,
    "sell": 10
  },
  "total_volume": 125000.50
}
```

### Positions

#### `GET /api/v1/positions/`
Get all current positions.

**Response:**
```json
[
  {
    "id": 1,
    "symbol": "TSLA",
    "quantity": 10,
    "average_price": 250.50,
    "current_price": 255.00,
    "unrealized_pnl": 45.00,
    "updated_at": "2025-11-30T15:00:00"
  }
]
```

#### `GET /api/v1/positions/{symbol}`
Get position for a specific symbol.

**Path Parameters:**
- `symbol` (string) - Stock symbol (e.g., TSLA)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/positions/TSLA"
```

**Response:**
```json
{
  "id": 1,
  "symbol": "TSLA",
  "quantity": 10,
  "average_price": 250.50,
  "current_price": 255.00,
  "unrealized_pnl": 45.00,
  "updated_at": "2025-11-30T15:00:00"
}
```

## Error Responses

### 404 Not Found
```json
{
  "detail": "Tweet not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently, there are no rate limits implemented. For production, consider implementing rate limiting middleware.

## Response Format

All successful responses return JSON. Error responses also return JSON with a `detail` field.

## Pagination

Endpoints that support pagination use `skip` and `limit` query parameters:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100, max: 1000)

## Filtering

Endpoints support filtering via query parameters. Multiple filters can be combined.

## Examples

### Get Recent Positive Tweets from Elon Musk

```bash
curl "http://localhost:8000/api/v1/tweets/?author=elonmusk&sentiment=positive&limit=5&skip=0"
```

### Get All Filled TSLA Trades

```bash
curl "http://localhost:8000/api/v1/trades/?symbol=TSLA&status=filled"
```

### Get Current TSLA Position

```bash
curl "http://localhost:8000/api/v1/positions/TSLA"
```

## Testing with cURL

```bash
# Health check
curl http://localhost:8000/health

# Get tweets
curl http://localhost:8000/api/v1/tweets/

# Get trade stats
curl http://localhost:8000/api/v1/trades/stats/summary
```

## Testing with Python

```python
import requests

base_url = "http://localhost:8000"

# Get tweets
response = requests.get(f"{base_url}/api/v1/tweets/")
tweets = response.json()

# Get trade stats
response = requests.get(f"{base_url}/api/v1/trades/stats/summary")
stats = response.json()
```

## Next Steps

- [Quick Start Guide](../getting-started/quick-start.md) - Get started
- [PostgreSQL Setup](../setup/postgresql-setup.md) - Database configuration
- [Docker Deployment](../deployment/docker.md) - Production deployment

