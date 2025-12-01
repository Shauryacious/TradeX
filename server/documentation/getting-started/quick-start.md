# Quick Start Guide - PostgreSQL Setup

## ✅ Current Status
- ✅ PostgreSQL 15 is installed and running
- ✅ Database `tradex` already exists
- ✅ Code updated to use PostgreSQL

## 🚀 Quick Setup (3 Steps)

### Step 1: Install Python Dependencies
```bash
cd server
pip install -r requirements.txt
```

This will install `asyncpg` (PostgreSQL async driver) instead of `aiosqlite`.

### Step 2: Configure Environment
```bash
# Copy example file
cp .env.example .env

# Edit .env and set your DATABASE_URL (already configured for local)
# The default connection string should work:
DATABASE_URL=postgresql+asyncpg://localhost/tradex
```

### Step 3: Run the Server
```bash
python3 main.py
```

The server will automatically create all tables on first run!

## 🔍 Verify Database Connection

```bash
# Test connection
psql -d tradex

# Check tables (after running server once)
psql -d tradex -c "\dt"
```

## 📝 What Changed

1. **requirements.txt**: Replaced `aiosqlite` with `asyncpg`
2. **config.py**: Default `DATABASE_URL` now uses PostgreSQL
3. **.env.example**: Updated with PostgreSQL connection string

## 🛠️ Manual Database Setup (if needed)

If you need to recreate the database:

```bash
# Run the setup script
./setup_postgres.sh

# Or manually:
dropdb tradex
createdb tradex
```

## 📚 Full Documentation

See [PostgreSQL Setup Guide](../setup/postgresql-setup.md) for detailed setup instructions and troubleshooting.

