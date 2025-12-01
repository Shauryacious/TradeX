# TradeX Server Scripts

Utility scripts for managing the TradeX server.

## Available Scripts

### `start.sh`
Starts the TradeX server.

**Usage:**
```bash
./scripts/start.sh
```

**Features:**
- Activates virtual environment if present
- Checks for .env file
- Verifies PostgreSQL is running
- Checks if server is already running
- Creates logs directory
- Starts the server

### `stop.sh`
Stops the running TradeX server.

**Usage:**
```bash
./scripts/stop.sh
```

**Features:**
- Finds the server process
- Attempts graceful shutdown (SIGTERM)
- Forces shutdown if needed (SIGKILL)
- Verifies server is stopped

### `restart.sh`
Restarts the TradeX server (stops then starts).

**Usage:**
```bash
./scripts/restart.sh
```

**Features:**
- Stops the server
- Waits briefly
- Starts the server

## Quick Reference

```bash
# Start server
./scripts/start.sh

# Stop server
./scripts/stop.sh

# Restart server
./scripts/restart.sh

# Check if server is running
pgrep -f "python.*main.py"
```

## Notes

- All scripts can be run from the `server` directory
- Scripts automatically handle virtual environment activation
- Server logs are written to `logs/tradex.log`
- The server runs on `http://localhost:8000` by default

