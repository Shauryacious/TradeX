#!/bin/bash

# TradeX Server - Restart Script
# Stops and starts the TradeX server

set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🔄 Restarting TradeX Server..."
echo ""

# Stop the server
"$SCRIPT_DIR/stop.sh"

# Wait a moment
sleep 2

# Start the server
"$SCRIPT_DIR/start.sh"

