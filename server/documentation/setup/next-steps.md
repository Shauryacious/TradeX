# Next Steps After Twitter API Setup

Congratulations! You've completed the Twitter API setup. Here's what to do next.

## ✅ What You've Completed

- ✅ Twitter Developer Account created
- ✅ API credentials obtained
- ✅ Credentials added to `.env` file

## 🚀 Next Steps

### 1. Test Your Server

Start the server to verify everything works:

```bash
cd /Users/shauryaagrawal/Desktop/TradeX/server
./scripts/start.sh
```

**What to look for:**
- ✅ "Twitter monitoring started" (success)
- ❌ "Twitter Bearer Token not configured" (check .env file)
- ❌ Connection errors (check credentials)

### 2. Verify Twitter Connection

Once the server is running:

1. **Check the logs:**
   ```bash
   tail -f logs/tradex.log
   ```

2. **Look for:**
   - ✅ "Twitter monitoring started"
   - ✅ No connection errors
   - ⚠️ Rate limit warnings (normal if you hit limits)

3. **Test API endpoints:**
   - Visit: http://localhost:8000/api/docs
   - Try: `GET /api/v1/tweets/` to see if tweets are being collected

### 3. Set Up Alpaca Trading API (Optional)

If you want to enable trading:

1. **Follow the guide:**
   - See: `documentation/setup/api-credentials.md`
   - Section: "Alpaca Trading API Credentials"

2. **Get Alpaca credentials:**
   - Sign up at: https://alpaca.markets/
   - Use **Paper Trading** for testing (free, no real money)

3. **Add to .env:**
   ```env
   ALPACA_API_KEY=your_alpaca_key
   ALPACA_API_SECRET=your_alpaca_secret
   ```

4. **Enable trading** (after thorough testing):
   ```env
   TRADING_ENABLED=true
   ```

### 4. Connect to Database in pgAdmin

View your data:

1. **Open pgAdmin 4**
2. **Connect to TradeX database:**
   - Host: `localhost`
   - Port: `5432`
   - Database: `tradex`
   - Username: `shauryaagrawal`
3. **Explore tables:**
   - `tweets` - Collected tweets
   - `trades` - Executed trades
   - `positions` - Current positions

### 5. Monitor Your Bot

**Check what's happening:**
- View tweets: http://localhost:8000/api/v1/tweets/
- View trades: http://localhost:8000/api/v1/trades/
- View positions: http://localhost:8000/api/v1/positions/
- Health check: http://localhost:8000/health

## 🔍 Troubleshooting

### Twitter API Not Working

**Error: "Twitter Bearer Token not configured"**
- Check `.env` file has all 5 Twitter credentials
- Make sure no "your_*" placeholders remain
- Restart server after updating `.env`

**Error: "Rate limit exceeded"**
- You've hit Twitter's rate limits
- Wait 15 minutes and try again
- Consider upgrading to paid tier

**Error: "Forbidden" or "Unauthorized"**
- Check app permissions (should be "Read")
- Verify OAuth 1.0a is enabled
- Regenerate tokens if needed

### Server Won't Start

**Port 8000 already in use:**
```bash
./scripts/stop.sh  # Stop existing server
./scripts/start.sh  # Start fresh
```

**Database connection errors:**
- Verify PostgreSQL is running: `brew services list | grep postgresql`
- Check database exists: `psql -l | grep tradex`

## 📊 What Happens Next

Once running, your bot will:

1. **Monitor Twitter** - Check for new tweets every 60 seconds (configurable)
2. **Analyze Sentiment** - Process tweets with VADER + RoBERTa models
3. **Store Data** - Save tweets and sentiment to PostgreSQL
4. **Make Trading Decisions** - If trading is enabled (currently disabled for safety)

## 🎯 Quick Commands

```bash
# Start server
./scripts/start.sh

# Stop server
./scripts/stop.sh

# Restart server
./scripts/restart.sh

# View logs
tail -f logs/tradex.log

# Check if running
pgrep -f "python.*main.py"
```

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/api/docs
- **Full Setup Guide**: `documentation/setup/api-credentials.md`
- **PostgreSQL Guide**: `documentation/setup/postgresql-setup.md`
- **API Reference**: `documentation/api-reference/endpoints.md`

## ⚠️ Important Reminders

1. **Trading is disabled by default** - Set `TRADING_ENABLED=true` only after testing
2. **Use paper trading first** - Test with Alpaca paper trading before live trading
3. **Monitor your bot** - Check logs regularly
4. **Keep credentials secure** - Never commit `.env` to git
5. **Respect rate limits** - Twitter and Alpaca have rate limits

---

**Ready to start?** Run `./scripts/start.sh` and visit http://localhost:8000/api/docs!

