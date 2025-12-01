#!/bin/bash

# PostgreSQL Setup Script for TradeX
# This script helps set up the PostgreSQL database

set -e

echo "🚀 TradeX PostgreSQL Setup"
echo "=========================="
echo ""

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "❌ PostgreSQL is not running!"
    echo "   Starting PostgreSQL..."
    brew services start postgresql@15
    sleep 2
fi

echo "✅ PostgreSQL is running"
echo ""

# Check if database exists
if psql -lqt | cut -d \| -f 1 | grep -qw tradex; then
    echo "⚠️  Database 'tradex' already exists"
    read -p "   Do you want to drop and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Dropping existing database..."
        dropdb tradex
        echo "   Creating new database..."
        createdb tradex
        echo "✅ Database 'tradex' created"
    else
        echo "✅ Using existing database 'tradex'"
    fi
else
    echo "📦 Creating database 'tradex'..."
    createdb tradex
    echo "✅ Database 'tradex' created"
fi

echo ""
echo "📋 Database connection info:"
echo "   Host: localhost"
echo "   Database: tradex"
echo "   User: $(whoami)"
echo ""
echo "🔗 Connection string for .env file:"
echo "   DATABASE_URL=postgresql+asyncpg://localhost/tradex"
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update your .env file with the DATABASE_URL above"
echo "2. Install Python dependencies: pip install -r requirements.txt"
echo "3. Run the server: python3 main.py"
echo ""

