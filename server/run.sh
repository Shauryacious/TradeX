#!/bin/bash

# TradeX Server Startup Script

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the server
python3 main.py

