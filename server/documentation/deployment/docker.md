# Docker Deployment Guide

Complete guide for deploying TradeX Server using Docker and Docker Compose.

## Overview

TradeX Server includes Docker support for easy deployment and containerization. This guide covers building, running, and deploying the server using Docker.

## Prerequisites

- Docker Desktop installed (or Docker Engine + Docker Compose)
- Docker version 20.10+
- Docker Compose version 2.0+

## Quick Start

### Using Docker Compose (Recommended)

```bash
cd server

# Copy environment file
cp .env.example .env
# Edit .env with your credentials

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Manual Docker Build

### Build Image

```bash
cd server
docker build -t tradex-server .
```

### Run Container

```bash
docker run -d \
  --name tradex-server \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  tradex-server
```

## Docker Compose Configuration

The `docker-compose.yml` file includes:

- **Service**: `tradex-server`
- **Port**: 8000 (mapped to host)
- **Environment**: Loaded from `.env` file
- **Volumes**: Logs directory mounted
- **Health Check**: Automatic health monitoring
- **Restart Policy**: `unless-stopped`

### Customize docker-compose.yml

```yaml
version: '3.8'

services:
  tradex-server:
    build: .
    container_name: tradex-server
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./tradex.db:/app/tradex.db  # If using SQLite
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## Environment Variables

Create a `.env` file with your configuration:

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/tradex

# Twitter API
TWITTER_BEARER_TOKEN=your_token
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_secret

# Alpaca Trading
ALPACA_API_KEY=your_key
ALPACA_API_SECRET=your_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Trading Configuration
TRADING_ENABLED=false
TRADING_SYMBOL=TSLA
MAX_POSITION_SIZE=1000.0
```

## Docker with PostgreSQL

### Option 1: External PostgreSQL

If PostgreSQL is running on the host or another container:

```yaml
services:
  tradex-server:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - postgres
    networks:
      - tradex-network

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: tradex
      POSTGRES_USER: tradex_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - tradex-network

volumes:
  postgres_data:

networks:
  tradex-network:
    driver: bridge
```

Update `.env`:
```env
DATABASE_URL=postgresql+asyncpg://tradex_user:secure_password@postgres:5432/tradex
```

### Option 2: Host PostgreSQL

If PostgreSQL is on the host machine:

```yaml
services:
  tradex-server:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

Update `.env`:
```env
DATABASE_URL=postgresql+asyncpg://user:password@host.docker.internal:5432/tradex
```

## Production Deployment

### 1. Build Production Image

```bash
docker build -t tradex-server:latest .
```

### 2. Tag for Registry

```bash
docker tag tradex-server:latest your-registry/tradex-server:v1.0.0
```

### 3. Push to Registry

```bash
docker push your-registry/tradex-server:v1.0.0
```

### 4. Deploy

```bash
# Pull image
docker pull your-registry/tradex-server:v1.0.0

# Run with production settings
docker run -d \
  --name tradex-server \
  -p 8000:8000 \
  --env-file .env.production \
  --restart unless-stopped \
  your-registry/tradex-server:v1.0.0
```

## Dockerfile Details

The Dockerfile includes:

- **Base Image**: Python 3.12-slim
- **Working Directory**: `/app`
- **Dependencies**: Installed from `requirements.txt`
- **Application Code**: Copied to container
- **Port**: 8000 exposed
- **Health Check**: Built-in health monitoring
- **Non-root User**: Runs as non-privileged user (recommended for production)

## Health Checks

The container includes automatic health checks:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"
```

Monitor health:
```bash
docker ps  # Shows health status
docker inspect tradex-server | grep Health
```

## Logging

Logs are written to `/app/logs` in the container. Mount this directory:

```yaml
volumes:
  - ./logs:/app/logs
```

View logs:
```bash
# Docker Compose
docker-compose logs -f tradex-server

# Docker
docker logs -f tradex-server
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs tradex-server

# Check container status
docker ps -a

# Inspect container
docker inspect tradex-server
```

### Database Connection Issues

```bash
# Test database connection from container
docker exec -it tradex-server python -c "from app.db.database import engine; print(engine)"
```

### Port Already in Use

```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Host:Container
```

### Permission Issues

```bash
# Fix log directory permissions
chmod -R 755 logs/
```

## Security Best Practices

1. **Use Secrets Management**: Don't commit `.env` files
2. **Non-root User**: Run container as non-root (already configured)
3. **Network Isolation**: Use Docker networks
4. **Resource Limits**: Set CPU and memory limits
5. **Regular Updates**: Keep base images updated

### Example with Resource Limits

```yaml
services:
  tradex-server:
    build: .
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

## Multi-Stage Build (Advanced)

For smaller production images:

```dockerfile
# Build stage
FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t tradex-server:${{ github.sha }} .
      - name: Push to registry
        run: |
          docker tag tradex-server:${{ github.sha }} your-registry/tradex-server:latest
          docker push your-registry/tradex-server:latest
```

## Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

### Container Stats

```bash
docker stats tradex-server
```

## Backup and Restore

### Backup Database

```bash
# If using PostgreSQL in Docker
docker exec postgres pg_dump -U tradex_user tradex > backup.sql
```

### Restore Database

```bash
docker exec -i postgres psql -U tradex_user tradex < backup.sql
```

## Next Steps

- [Quick Start Guide](../getting-started/quick-start.md) - Local development
- [PostgreSQL Setup](../setup/postgresql-setup.md) - Database configuration
- [API Reference](../api-reference/endpoints.md) - API documentation

