#!/bin/bash

# TradeX Server - Start Script
# Starts the TradeX server

set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVER_DIR="$(dirname "$SCRIPT_DIR")"

# Change to server directory
cd "$SERVER_DIR"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Copy .env.example to .env and configure your settings"
    echo ""
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Set SSL certificate paths (fix for macOS SSL issues)
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())" 2>/dev/null)
export REQUESTS_CA_BUNDLE="$SSL_CERT_FILE"

# Check if PostgreSQL is running
if ! pg_isready -q 2>/dev/null; then
    echo "⚠️  Warning: PostgreSQL might not be running"
    echo "   Start it with: brew services start postgresql@15"
    echo ""
fi

# Check if server is already running (by process name)
if pgrep -f "python.*main.py" > /dev/null; then
    echo "⚠️  Server is already running!"
    echo "   Use ./scripts/stop.sh to stop it first"
    exit 1
fi

# Check if port 8000 is already in use
PORT_PID=$(lsof -ti:8000 2>/dev/null || true)
if [ -n "$PORT_PID" ]; then
    echo "⚠️  Port 8000 is already in use by process $PORT_PID"
    echo "   Attempting to stop the process..."
    kill -TERM "$PORT_PID" 2>/dev/null || true
    sleep 2
    # Check if still running and force kill if needed
    if lsof -ti:8000 > /dev/null 2>&1; then
        kill -9 "$PORT_PID" 2>/dev/null || true
        sleep 1
    fi
    # Final check
    if lsof -ti:8000 > /dev/null 2>&1; then
        echo "❌ Failed to free port 8000. Please stop the process manually:"
        echo "   lsof -ti:8000 | xargs kill -9"
        exit 1
    else
        echo "✅ Port 8000 is now free"
    fi
fi

echo "🚀 Starting TradeX Server..."
echo "   Server directory: $SERVER_DIR"
echo "   Logs: $SERVER_DIR/logs/tradex.log"
echo ""

# Start the server
python3 main.py

