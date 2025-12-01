# PostgreSQL Setup Guide for TradeX Server

## Step-by-Step Setup Instructions

### Step 1: Check PostgreSQL Installation ✅
PostgreSQL is already installed on your system (version 15).

### Step 2: Start PostgreSQL Service

```bash
# Start PostgreSQL service
brew services start postgresql@15

# Or if you prefer to run it manually (without auto-start on boot)
pg_ctl -D /opt/homebrew/var/postgresql@15 start
```

**Verify it's running:**
```bash
brew services list | grep postgresql
# Should show: postgresql@15 started
```

### Step 3: Create Database and User

```bash
# Connect to PostgreSQL (default user is your macOS username)
psql postgres

# Once connected, run these SQL commands:
```

**In the PostgreSQL prompt, run:**

```sql
-- Create database
CREATE DATABASE tradex;

-- Create user (optional, you can use your default user)
CREATE USER tradex_user WITH PASSWORD 'your_secure_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE tradex TO tradex_user;

-- Connect to the new database
\c tradex

-- Exit
\q
```

**Or use a single command:**
```bash
createdb tradex
```

### Step 4: Update Python Dependencies

The code has been updated to use `asyncpg` instead of `aiosqlite`. Install it:

```bash
cd server
pip install asyncpg
# Or reinstall all dependencies
pip install -r requirements.txt
```

### Step 5: Update Environment Variables

Edit your `.env` file:

```bash
cd server
cp .env.example .env
nano .env  # or use your preferred editor
```

**Update the DATABASE_URL:**
```env
# Option 1: Using default macOS user (simplest)
DATABASE_URL=postgresql+asyncpg://$(whoami)@localhost/tradex

# Option 2: Using created user
DATABASE_URL=postgresql+asyncpg://tradex_user:your_secure_password_here@localhost/tradex

# Option 3: If you need to specify port (default is 5432)
DATABASE_URL=postgresql+asyncpg://tradex_user:password@localhost:5432/tradex
```

**For macOS, the simplest connection string is:**
```env
DATABASE_URL=postgresql+asyncpg://localhost/tradex
```

### Step 6: Test Database Connection

```bash
# Test connection from command line
psql -d tradex

# If successful, you'll see:
# tradex=#
# Type \q to exit
```

### Step 7: Run the Server

```bash
cd server
python3 main.py
```

The server will automatically create all necessary tables on first run.

### Step 8: Verify Tables Were Created

```bash
psql -d tradex

# In PostgreSQL prompt:
\dt

# Should show:
#  public | positions
#  public | trades
#  public | tweets
```

## Troubleshooting

### PostgreSQL Service Not Starting

```bash
# Check logs
tail -f /opt/homebrew/var/log/postgresql@15.log

# Restart service
brew services restart postgresql@15
```

### Connection Refused

```bash
# Check if PostgreSQL is listening
lsof -i :5432

# Should show postgres process
```

### Permission Denied

If you get permission errors, you might need to:
```bash
# Check PostgreSQL data directory permissions
ls -la /opt/homebrew/var/postgresql@15

# Or recreate the database cluster (WARNING: deletes all data)
rm -rf /opt/homebrew/var/postgresql@15
initdb /opt/homebrew/var/postgresql@15
```

### Database Already Exists

If the database already exists:
```bash
# Drop and recreate (WARNING: deletes all data)
dropdb tradex
createdb tradex
```

## Quick Reference Commands

```bash
# Start PostgreSQL
brew services start postgresql@15

# Stop PostgreSQL
brew services stop postgresql@15

# Restart PostgreSQL
brew services restart postgresql@15

# Check status
brew services list | grep postgresql

# Connect to database
psql -d tradex

# List all databases
psql -l

# List all tables in current database
psql -d tradex -c "\dt"
```

## Production Notes

For production deployments:
1. Use a strong password for the database user
2. Consider using connection pooling (pgBouncer)
3. Set up regular backups
4. Configure SSL connections
5. Use environment-specific database names (e.g., `tradex_prod`, `tradex_dev`)

