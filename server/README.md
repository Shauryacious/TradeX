# TradeX Server

Production-ready FastAPI server for Twitter-based trading bot.

## Features

- **FastAPI** with async/await support
- **SQLAlchemy** with async database operations
- **Twitter API** integration for real-time tweet monitoring
- **Sentiment Analysis** using VADER and transformer models
- **Alpaca Trading API** integration for automated trading
- **Production-ready** with logging, error handling, and Docker support

## Tech Stack

- **Framework**: FastAPI 0.115.0
- **Database**: SQLAlchemy 2.0 with PostgreSQL (async)
- **Twitter**: Tweepy 5.0.0
- **Trading**: Alpaca Trade API 3.1.1
- **Sentiment**: VADER + Transformers (RoBERTa)
- **Python**: 3.12+

## Project Structure

```
server/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/     # API endpoints
│   │       └── router.py      # Main router
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   ├── logging.py         # Logging setup
│   │   └── exceptions.py      # Custom exceptions
│   ├── db/
│   │   ├── database.py        # Database connection
│   │   └── models.py         # Database models
│   └── services/
│       ├── twitter_service.py      # Twitter API service
│       ├── sentiment_service.py    # Sentiment analysis
│       └── trading_service.py      # Trading operations
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
└── .env.example            # Environment variables template
```

## 📚 Documentation

For detailed documentation, see the [documentation directory](./documentation/README.md):
- [Quick Start Guide](./documentation/getting-started/quick-start.md)
- [PostgreSQL Setup](./documentation/setup/postgresql-setup.md)
- [API Reference](./documentation/api-reference/endpoints.md)
- [Docker Deployment](./documentation/deployment/docker.md)

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required environment variables:
- `TWITTER_BEARER_TOKEN` - Twitter API Bearer Token
- `TWITTER_API_KEY` - Twitter API Key
- `TWITTER_API_SECRET` - Twitter API Secret
- `TWITTER_ACCESS_TOKEN` - Twitter Access Token
- `TWITTER_ACCESS_TOKEN_SECRET` - Twitter Access Token Secret
- `ALPACA_API_KEY` - Alpaca API Key (for paper trading)
- `ALPACA_API_SECRET` - Alpaca API Secret

### 3. Run the Server

```bash
# Development mode
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the API

- **API Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

## Docker Setup

### Build and Run

```bash
# Build image
docker build -t tradex-server .

# Run container
docker run -p 8000:8000 --env-file .env tradex-server

# Or use docker-compose
docker-compose up -d
```

## API Endpoints

### Health
- `GET /health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health with service status

### Tweets
- `GET /api/v1/tweets/` - Get all tweets (with pagination and filters)
- `GET /api/v1/tweets/{tweet_id}` - Get specific tweet
- `GET /api/v1/tweets/stats/summary` - Tweet statistics

### Trades
- `GET /api/v1/trades/` - Get all trades
- `GET /api/v1/trades/{trade_id}` - Get specific trade
- `GET /api/v1/trades/stats/summary` - Trade statistics

### Positions
- `GET /api/v1/positions/` - Get all positions
- `GET /api/v1/positions/{symbol}` - Get position for symbol

## Configuration

Key configuration options in `.env`:

- `TRADING_ENABLED` - Enable/disable trading (safety: default `false`)
- `MAX_POSITION_SIZE` - Maximum position size in dollars
- `RISK_PERCENTAGE` - Risk percentage per trade
- `SENTIMENT_THRESHOLD_POSITIVE` - Positive sentiment threshold
- `SENTIMENT_THRESHOLD_NEGATIVE` - Negative sentiment threshold
- `MONITORED_USERS` - Comma-separated list of Twitter usernames
- `TWEET_CHECK_INTERVAL` - Interval in seconds to check for new tweets

## Safety Features

- **Trading disabled by default** - Set `TRADING_ENABLED=true` to enable
- **Paper trading** - Uses Alpaca paper trading by default
- **Position sizing** - Automatic risk management
- **Rate limiting** - Built-in rate limit handling for Twitter API

## Development

### Code Formatting

```bash
# Format code
black .

# Lint code
ruff check .
```

### Testing

```bash
# Run tests
pytest
```

## Production Deployment

1. Set `ENVIRONMENT=production` in `.env`
2. Set `DEBUG=false`
3. Use a production database (PostgreSQL recommended)
4. Set up proper logging and monitoring
5. Use a reverse proxy (nginx) in front of the application
6. Set up SSL/TLS certificates

## License

See main project README for license information.

