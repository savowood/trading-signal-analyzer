# 🔑 API Setup Guide - Enhanced Pressure Cooker

This guide walks you through getting **FREE API keys** for the Enhanced Pressure Cooker scanner.

---

## 📰 **NewsAPI** (Free - Catalyst Detection)

NewsAPI provides news articles for catalyst detection.

### **Free Tier Limits**:
- ✅ 100 requests per day
- ✅ News from last 30 days
- ✅ All sources included

### **How to Get API Key**:

1. **Go to**: https://newsapi.org/

2. **Click "Get API Key"** (top right)

3. **Create account**:
   - Enter your name
   - Enter your email
   - Choose "Individual" plan
   - Click "Submit"

4. **Check your email** for verification

5. **Copy your API key** from the dashboard

6. **Add to settings**:
   ```bash
   nano ~/.trading_analyzer
   ```

   Add your key:
   ```json
   {
     "api_keys": {
       "newsapi": "YOUR_API_KEY_HERE"
     }
   }
   ```

### **Example Key Format**:
```
12345678901234567890123456789012
```
(32 characters)

---

## 🤖 **Reddit API** (Free - Social Sentiment)

Reddit API lets you track mentions on WallStreetBets and other subreddits.

### **Free Tier Limits**:
- ✅ 60 requests per minute
- ✅ Unlimited daily requests
- ✅ Full access to all subreddits

### **How to Get API Key**:

1. **Create Reddit account** (if you don't have one):
   - Go to: https://www.reddit.com/
   - Click "Sign Up"

2. **Go to Reddit Apps page**:
   - Visit: https://www.reddit.com/prefs/apps

3. **Create an application**:
   - Scroll to bottom
   - Click "create another app..."
   - Fill out form:
     - **name**: "Trading Analyzer" (or any name)
     - **App type**: Select **"script"**
     - **description**: "Personal trading scanner"
     - **about url**: (leave blank)
     - **redirect uri**: http://localhost:8080
   - Click "create app"

4. **Copy your credentials**:
   - **client_id**: Text under "personal use script" (14 characters)
   - **client_secret**: Text next to "secret" (27 characters)

5. **Add to settings**:
   ```bash
   nano ~/.trading_analyzer
   ```

   Add both keys:
   ```json
   {
     "api_keys": {
       "reddit_client_id": "YOUR_CLIENT_ID",
       "reddit_client_secret": "YOUR_CLIENT_SECRET"
     }
   }
   ```

### **Example Format**:
```json
{
  "reddit_client_id": "aBcD1234eFgH56",
  "reddit_client_secret": "xYz789aBcDeFgHiJkLmNoPqR"
}
```

---

## ✅ **Verify Your Setup**

After adding the API keys, restart your trading analyzer:

```bash
python -m trading_analyzer
```

Select option **3** (Enhanced Pressure Cooker) and run a scan. You should see:

```
📊 Analyzing technicals for TICKER...
🔍 Checking options flow for TICKER...
📰 Detecting catalysts for TICKER...      ← Should work if NewsAPI key valid
💬 Analyzing social sentiment for TICKER... ← Should work if Reddit keys valid
```

---

## 🔍 **Troubleshooting**

### **NewsAPI Not Working?**

**Error**: `401 Unauthorized` or `Invalid API key`

**Solutions**:
1. Check your API key in `~/.trading_analyzer` has no extra spaces
2. Verify you verified your email with NewsAPI
3. Try generating a new key from NewsAPI dashboard

**Error**: `429 Too Many Requests`

**Solution**: You've exceeded 100 requests/day. Wait until tomorrow or upgrade to paid plan ($449/mo).

---

### **Reddit API Not Working?**

**Error**: `401 Invalid credentials`

**Solutions**:
1. Make sure you selected **"script"** type (NOT "web app")
2. Check both `client_id` and `client_secret` are correct
3. Verify no extra quotes or spaces in settings file

**Error**: `403 Forbidden`

**Solution**: Your Reddit account is too new (must be >24 hours old). Wait a day.

---

## 💰 **Upgrade Options (Optional)**

While the free tiers work great, here are paid options for power users:

### **NewsAPI Pro** ($449/month)
- Unlimited requests
- Real-time news
- More sources
- Not necessary for casual use

### **Reddit Premium** (Free for API)
- Reddit API is actually free even for power users
- No need to upgrade

---

## 📋 **Complete Settings Example**

Here's what your `~/.trading_analyzer` should look like with all keys:

```json
{
  "_comment": "Trading Analyzer User Settings",
  "disclaimer_acknowledged": true,
  "pressure_cooker_disclaimer_acknowledged": true,

  "api_keys": {
    "finviz": "c907b012-f86d-4493-ba77-9e6d13df38ba",
    "newsapi": "12345678901234567890123456789012",
    "reddit_client_id": "aBcD1234eFgH56",
    "reddit_client_secret": "xYz789aBcDeFgHiJkLmNoPqR",
    "tradingview": "",
    "polygon": "",
    "alphavantage": ""
  },

  "cache_settings": {
    "scan_results": 900,
    "microcap_list": 14400,
    "stock_data": 300
  },

  "rate_limit": {
    "workers": 3,
    "delay_every": 10,
    "delay_ms": 100,
    "batch_size": 500
  },

  "pillars": {
    "change": {
      "threshold": 10.0,
      "weight": 0.2
    },
    "rel_vol": {
      "threshold": 5.0,
      "weight": 0.2
    },
    "float": {
      "threshold": 20.0,
      "weight": 0.2
    },
    "price_range": {
      "min": 2.0,
      "max": 20.0,
      "weight": 0.2
    }
  },

  "min_score": 50,
  "max_results_display": 50
}
```

---

## 🚀 **What You Get With These APIs**

### **Without APIs** (Basic Mode):
```
SETUP SCORE: 72/100 🔥🔥
Float: 2.3M | Short%: 25% | RelVol: 5.2x
```

### **With All APIs** (Enhanced Mode):
```
SETUP SCORE: 87/100 🔥🔥🔥

🔥 SQUEEZE FUNDAMENTALS:
   Float: 2.3M | Short%: 25% | Days to Cover: 8.3

📊 TECHNICAL SETUP:
   RSI: 28 ✅ OVERSOLD
   MACD: ✅ BULLISH CROSSOVER
   Setup Stage: READY TO BREAK

🎯 CATALYST DETECTED:
   ✅ FDA Approval Expected (12 news articles)
   ✅ Unusual options activity (C/P ratio: 4.2)
   ✅ Trending on WSB (47 mentions, bullish)

📈 KEY FACTORS:
   • Ultra-Low Float
   • RSI Oversold
   • Catalyst: FDA/Biotech
   • Setup Ready to Break
```

**Much more powerful!** 🎯

---

## ⏱️ **How Long Does Setup Take?**

- **NewsAPI**: 2 minutes
- **Reddit API**: 3-5 minutes
- **Total**: ~5-7 minutes

**Well worth it for the enhanced analysis!**

---

## 📞 **Support**

If you have issues:

1. **NewsAPI Support**: https://newsapi.org/contact
2. **Reddit API Docs**: https://www.reddit.com/dev/api
3. **Trading Analyzer Issues**: Check settings file for typos

---

## 🎓 **Best Practices**

1. **Don't share API keys**: Keep them private in your `~/.trading_analyzer` file
2. **Monitor usage**: NewsAPI is limited to 100/day - use wisely
3. **Respect rate limits**: Don't scan hundreds of tickers at once
4. **Backup your settings**: `cp ~/.trading_analyzer ~/.trading_analyzer.backup`

---

**You're all set!** 🚀

Run Enhanced Pressure Cooker and start finding high-probability squeeze setups!
