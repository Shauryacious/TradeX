# API Credentials Setup Guide

Complete step-by-step guide to obtain API credentials for Twitter and Alpaca Trading.

## Table of Contents

1. [Twitter API Credentials](#twitter-api-credentials)
2. [Alpaca Trading API Credentials](#alpaca-trading-api-credentials)
3. [Adding Credentials to .env](#adding-credentials-to-env)

---

## Twitter API Credentials

### Step 1: Create Twitter Developer Account

1. **Go to Twitter Developer Portal**
   - Visit: https://developer.twitter.com/
   - Click **"Sign up"** or **"Apply"**

2. **Sign in with your Twitter account**
   - Use your existing Twitter account or create one

3. **Apply for Developer Access**
   - Click **"Apply for a developer account"**
   - Select **"Hobbyist"** or **"Making a bot"** (free tier)
   - Fill out the application form:
     - **What use case are you interested in?** → Select "Making a bot"
     - **Will you make Twitter content available to a government entity?** → Answer as appropriate
     - **Will you make Twitter content available to a government entity?** → Answer as appropriate
   - Accept the terms and conditions
   - Submit your application

4. **Wait for Approval**
   - Usually takes a few minutes to 24 hours
   - You'll receive an email when approved

### Step 2: Create a Project and App

1. **Access Developer Portal**
   - Go to: https://developer.twitter.com/en/portal/dashboard
   - Sign in with your Twitter account

2. **Create a Project**
   - Click **"Create Project"**
   - Enter project name: `TradeX` (or any name)
   - Select use case: **"Making a bot"**
   - Enter project description
   - Click **"Next"**

3. **Create an App**
   - Enter app name: `TradeX Bot` (or any name)
   - Click **"Next"**
   - Review and click **"Create App"**

### Step 3: Get API Credentials

1. **Navigate to Your App**
   - Go to: https://developer.twitter.com/en/portal/projects-and-apps
   - Click on your app name

2. **Get API Keys and Tokens**
   - Click on **"Keys and tokens"** tab
   - You'll see:
     - **API Key** (also called Consumer Key)
     - **API Key Secret** (also called Consumer Secret)
     - **Bearer Token** (click "Regenerate" if needed)

3. **Generate Access Tokens**
   - Scroll down to **"Access Token and Secret"**
   - Click **"Generate"**
   - **IMPORTANT**: Copy these immediately - they won't be shown again!
   - You'll get:
     - **Access Token**
     - **Access Token Secret**

4. **Set App Permissions**
   - Go to **"Settings"** tab
   - Under **"App permissions"**, select:
     - **Read** (for reading tweets)
     - **Read and Write** (if you want to post tweets)
   - Click **"Save"**

### Step 4: Enable OAuth 1.0a (if needed)

1. **Go to Settings**
   - In your app settings, find **"User authentication settings"**
   - Click **"Set up"**

2. **Configure OAuth**
   - **App permissions**: Read (or Read and Write)
   - **Type of App**: Web App, Automated App or Bot
   - **App info**:
     - **Callback URI / Redirect URL**: `http://localhost:3000` (or any URL)
     - **Website URL**: `http://localhost:3000` (or your website)
   - Click **"Save"**

### Step 5: Copy Your Credentials

You should now have:
- ✅ **API Key** (Consumer Key)
- ✅ **API Key Secret** (Consumer Secret)
- ✅ **Bearer Token**
- ✅ **Access Token**
- ✅ **Access Token Secret**

**⚠️ Important Security Notes:**
- Never share these credentials publicly
- Never commit them to git
- Keep them secure
- Regenerate if compromised

---

## Alpaca Trading API Credentials

### Step 1: Create Alpaca Account

1. **Go to Alpaca Website**
   - Visit: https://alpaca.markets/
   - Click **"Get Started"** or **"Sign Up"**

2. **Sign Up**
   - Enter your email address
   - Create a password
   - Verify your email

3. **Complete Profile**
   - Fill in your personal information
   - Answer trading experience questions
   - Accept terms and conditions

### Step 2: Choose Account Type

**Option A: Paper Trading (Recommended for Testing)**
- Free, no real money
- Perfect for testing and development
- Same API as live trading
- Go to: https://app.alpaca.markets/paper/dashboard/overview

**Option B: Live Trading**
- Requires account funding
- Real money trading
- Only use after thorough testing
- Go to: https://app.alpaca.markets/dashboard/overview

### Step 3: Get API Credentials

1. **Access API Dashboard**
   - Log in to Alpaca
   - Go to: https://app.alpaca.markets/paper/dashboard/overview (for paper trading)
   - Or: https://app.alpaca.markets/dashboard/overview (for live trading)

2. **Navigate to API Keys**
   - Click on your profile/account menu (top right)
   - Select **"Your API Keys"** or **"API Keys"**
   - Or go directly to: https://app.alpaca.markets/paper/dashboard/overview (paper) or https://app.alpaca.markets/dashboard/overview (live)

3. **Generate API Keys**
   - Click **"Generate New Key"** or **"Create New Key"**
   - Enter a name: `TradeX Bot` (or any name)
   - Select permissions:
     - **Trading** (required)
     - **Market Data** (optional, for real-time quotes)
   - Click **"Generate"**

4. **Copy Your Credentials**
   - **API Key ID** (also called Key ID)
   - **Secret Key** (click "Show" to reveal)
   - **⚠️ Copy the Secret Key immediately** - it won't be shown again!

5. **Note the Base URL**
   - **Paper Trading**: `https://paper-api.alpaca.markets`
   - **Live Trading**: `https://api.alpaca.markets`

### Step 4: Verify Your Account (for Live Trading)

If using live trading:
1. Complete identity verification (KYC)
2. Link a bank account
3. Fund your account (minimum varies)

---

## Adding Credentials to .env

### Step 1: Open .env File

```bash
cd /Users/shauryaagrawal/Desktop/TradeX/server
nano .env
# or use your preferred editor (VS Code, vim, etc.)
```

### Step 2: Add Twitter Credentials

Replace the placeholder values:

```env
# Twitter API Credentials
TWITTER_BEARER_TOKEN=your_actual_bearer_token_here
TWITTER_API_KEY=your_actual_api_key_here
TWITTER_API_SECRET=your_actual_api_secret_here
TWITTER_ACCESS_TOKEN=your_actual_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_actual_access_token_secret_here
```

**Example:**
```env
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAMLheAAAAAAA0%2BuSeid%2BULvsea4JtiGRiSDSJSI%3DEUifiRBkKG5E2XzMDjRfl76ZC9Ub0wnz4XsNiRVBChTYbJcE3F
TWITTER_API_KEY=abc123xyz789
TWITTER_API_SECRET=def456uvw012
TWITTER_ACCESS_TOKEN=1234567890-abcdefghijklmnopqrstuvwxyz
TWITTER_ACCESS_TOKEN_SECRET=abcdefghijklmnopqrstuvwxyz1234567890
```

### Step 3: Add Alpaca Credentials

Replace the placeholder values:

```env
# Alpaca Trading API Credentials
ALPACA_API_KEY=your_actual_alpaca_key_id_here
ALPACA_API_SECRET=your_actual_alpaca_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

**Example:**
```env
ALPACA_API_KEY=PK1234567890ABCDEF
ALPACA_API_SECRET=abc123def456ghi789jkl012mno345pqr678stu
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

### Step 4: Enable Trading (Optional)

If you want to enable trading (after thorough testing):

```env
TRADING_ENABLED=true
```

**⚠️ Warning**: Only enable trading after:
- Testing thoroughly with paper trading
- Understanding the risks
- Having proper risk management in place

### Step 5: Save and Restart

1. **Save the .env file**
2. **Restart the server**:
   ```bash
   ./scripts/stop.sh
   ./scripts/start.sh
   ```

---

## Verification

### Test Twitter API

```bash
# The server will automatically test Twitter API on startup
# Check logs for any errors:
tail -f logs/tradex.log
```

### Test Alpaca API

The server will test Alpaca API on startup. Check logs for:
- ✅ "Trading client initialized" (success)
- ❌ "Alpaca API credentials not configured" (missing credentials)

---

## Troubleshooting

### Twitter API Issues

**Error: "Invalid or expired token"**
- Regenerate your Bearer Token
- Check that Access Tokens are generated
- Verify OAuth 1.0a is enabled

**Error: "Rate limit exceeded"**
- You've hit Twitter's rate limits
- Wait 15 minutes and try again
- Consider upgrading to paid tier for higher limits

**Error: "Forbidden"**
- Check app permissions (should be Read or Read and Write)
- Verify OAuth settings are configured

### Alpaca API Issues

**Error: "Invalid API key"**
- Double-check you copied the full key (no spaces)
- Verify you're using the correct base URL (paper vs live)
- Make sure keys are for the correct environment (paper/live)

**Error: "Account not found"**
- Complete account verification
- Ensure account is properly set up

---

## Security Best Practices

1. **Never commit .env to git** ✅ (already in .gitignore)
2. **Use environment variables in production**
3. **Rotate keys regularly**
4. **Use different keys for development and production**
5. **Limit API key permissions** (principle of least privilege)
6. **Monitor API usage** for unusual activity
7. **Use paper trading** for development and testing

---

## Quick Reference

### Twitter Developer Portal
- Dashboard: https://developer.twitter.com/en/portal/dashboard
- Projects: https://developer.twitter.com/en/portal/projects-and-apps
- Documentation: https://developer.twitter.com/en/docs

### Alpaca
- Paper Trading Dashboard: https://app.alpaca.markets/paper/dashboard/overview
- Live Trading Dashboard: https://app.alpaca.markets/dashboard/overview
- API Documentation: https://alpaca.markets/docs/

---

## Next Steps

After adding credentials:
1. Restart the server: `./scripts/restart.sh`
2. Check logs: `tail -f logs/tradex.log`
3. Test API endpoints: http://localhost:8000/api/docs
4. Verify database connection in pgAdmin

---

## Support

- **Twitter API Support**: https://twittercommunity.com/
- **Alpaca Support**: https://alpaca.markets/support
- **TradeX Issues**: Check project documentation

