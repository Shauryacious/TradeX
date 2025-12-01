#!/bin/bash

# TradeX Server - Stop Script
# Stops the running TradeX server

set -e

# Find and kill the server process by name
SERVER_PID=$(pgrep -f "python.*main.py" || true)

# Also check for processes using port 8000
PORT_PID=$(lsof -ti:8000 2>/dev/null || true)

if [ -z "$SERVER_PID" ] && [ -z "$PORT_PID" ]; then
    echo "ℹ️  TradeX server is not running"
    exit 0
fi

echo "🛑 Stopping TradeX Server..."

# Use PORT_PID if SERVER_PID is empty, or use SERVER_PID
if [ -n "$SERVER_PID" ]; then
    echo "   Found process: $SERVER_PID"
    TARGET_PID="$SERVER_PID"
elif [ -n "$PORT_PID" ]; then
    echo "   Found process using port 8000: $PORT_PID"
    TARGET_PID="$PORT_PID"
else
    TARGET_PID=""
fi

if [ -n "$TARGET_PID" ]; then
    # Try graceful shutdown first (SIGTERM)
    kill -TERM "$TARGET_PID" 2>/dev/null || true
    
    # Wait a bit for graceful shutdown
    sleep 2
    
    # Check if process is still running
    if pgrep -p "$TARGET_PID" > /dev/null 2>&1 || lsof -ti:8000 > /dev/null 2>&1; then
        echo "   Process still running, forcing shutdown..."
        kill -9 "$TARGET_PID" 2>/dev/null || true
        sleep 1
    fi
fi

# Verify it's stopped
if pgrep -f "python.*main.py" > /dev/null || lsof -ti:8000 > /dev/null 2>&1; then
    echo "❌ Failed to stop server"
    exit 1
else
    echo "✅ Server stopped successfully"
fi

