# Polygon.io / Massive Integration Guide

## Overview

The Trading Signal Analyzer now supports **optional** integration with **Polygon.io** (now rebranded as **Massive**) for professional-grade market data. This provides significant enhancements over the default yfinance data source.

> **📝 Note:** Polygon.io rebranded to Massive in 2024. The API, SDK, and functionality remain **identical** - only the branding changed. All references to "Polygon" still work perfectly.

## 🚀 Benefits of Polygon Integration

### **Enhanced Pressure Cooker Scanner:**
- ✅ **More reliable short interest data** - Better squeeze detection
- ✅ **Professional options flow** - Real gamma squeeze signals
- ✅ **News integration** - Automated catalyst detection
- ✅ **Better fundamentals** - More accurate float and shares data

### **Enhanced Dark Flow Scanner:**
- ✅ **Block trade detection** - See institutional whale orders (10k+ shares)
- ✅ **Dark pool vs lit volume** - Identify hidden accumulation
- ✅ **Tick-by-tick data** - Better volume profile analysis
- ✅ **Time & sales** - See actual order flow

### **General Improvements:**
- ✅ **Real-time or delayed data** (depending on your plan)
- ✅ **Better reliability** - Official exchange data, not scraping
- ✅ **Higher rate limits** - Faster scans
- ✅ **Professional SLA** - Better uptime than free sources

## 📦 Installation

### 1. Install Polygon SDK

```bash
# Install the Polygon Python client
pip install polygon-api-client

# Or if you already installed requirements.txt, you're all set!
pip install -r requirements.txt
```

### 2. Get a Polygon/Massive API Key

**Option A: Free Tier (Limited)**
1. Go to [polygon.io](https://polygon.io) **OR** [massive.io](https://massive.io) (same company, both work)
2. Sign up for a free account
3. Get your API key from the dashboard

> **💡 Tip:** Both websites work - they redirect to the same backend. Use whichever you prefer!

**Limitations of Free Tier:**
- ⚠️ Delayed data (15+ minutes)
- ⚠️ Low rate limits (5 requests/minute)
- ⚠️ No real-time data
- **Verdict:** Better than nothing, but yfinance might be more useful

**Option B: Starter Plan ($29-49/month) - RECOMMENDED**
- ✅ End-of-day data
- ✅ Moderate rate limits
- ✅ Historical data access
- ✅ News integration
- **Best for:** Daily Pressure Cooker scans and research

**Option C: Developer Plan ($99-199/month)**
- ✅ Real-time data (15 sec delay)
- ✅ Higher rate limits
- ✅ Options chains
- ✅ Better for intraday scanning
- **Best for:** Active trading with frequent scans

**Option D: Advanced Plan ($299-999+/month)**
- ✅ True real-time tick data
- ✅ Unlimited API calls
- ✅ Full options data with Greeks
- ✅ Block trade data
- **Best for:** Professional day trading

### 3. Configure Your API Key

Add your Polygon API key to the settings file:

```bash
# Edit the settings file
nano ~/.trading_analyzer
# or
code ~/.trading_analyzer
```

Add your API key to the `api_keys` section:

```json
{
  "api_keys": {
    "polygon": "YOUR_POLYGON_API_KEY_HERE",
    "newsapi": null,
    "reddit_client_id": null,
    "reddit_client_secret": null
  }
}
```

**Example:**
```json
{
  "api_keys": {
    "polygon": "abc123XYZ789yourActualKeyHere",
    "newsapi": null
  },
  "cache_settings": {
    "scan_results": 900
  }
}
```

### 4. Restart the Analyzer

```bash
# Restart the trading analyzer to load new settings
python -m trading_analyzer
```

You should see:
```
Loading settings...
✅ Loaded custom settings from ~/.trading_analyzer
✅ Polygon.io integration active
```

## 🎯 How It Works

The analyzer uses an **intelligent hybrid provider** that:

1. **Tries Polygon first** (if API key configured)
2. **Falls back to yfinance** if:
   - No Polygon key configured
   - Polygon API returns an error
   - Data not available in your Polygon plan
   - Rate limit exceeded

**This means:** The analyzer will always work, even if Polygon is unavailable!

## 📊 What Data Comes from Where

### **With Polygon API Key:**

| Data Type | Source | Why? |
|-----------|--------|------|
| Real-time quotes | **Polygon** | Faster, more reliable |
| Historical OHLCV | **Polygon** | Official exchange data |
| News/catalysts | **Polygon** | Integrated news feed |
| Block trades | **Polygon only** | Requires tick data |
| Short interest | **yfinance** | More comprehensive |
| Float/fundamentals | **yfinance** | Better coverage |
| Options chains | **yfinance** | Currently better for options |

### **Without Polygon API Key:**

| Data Type | Source |
|-----------|--------|
| All data | **yfinance** |

The scanners automatically adapt to use the best available source!

## 🔧 New Features Enabled

### 1. **Block Trade Detection (Dark Flow Scanner)**

When Polygon is enabled, the Dark Flow scanner can detect large institutional orders:

```
🐋 BLOCK TRADES DETECTED:
   • 2024-01-15 14:23:45 - $45.67 - 25,000 shares (DARK POOL)
   • 2024-01-15 14:25:12 - $45.71 - 15,000 shares (NYSE)
   • 2024-01-15 14:27:33 - $45.69 - 30,000 shares (DARK POOL)

   Dark Pool vs Lit Ratio: 55% dark | 45% lit
   → Institutional accumulation pattern detected
```

### 2. **Enhanced News Integration (Pressure Cooker)**

```
📰 RECENT CATALYSTS:
   • [2 hours ago] "Company announces earnings beat"
   • [1 day ago] "Short seller report released"
   • [3 days ago] "FDA approval expected soon"

   Catalyst Score: +15 points
```

### 3. **Real-time Quote Updates**

Faster scans with more current data (depending on your plan tier).

## 🧪 Testing Your Integration

### Check if Polygon is Working:

Run a scan and look for these indicators:

```
✅ Polygon.io integration active
📊 Using Polygon for market data
🔄 Fallback to yfinance for short interest
```

### View Data Source Statistics:

After running scans, check the statistics:

```python
# In the analyzer
from trading_analyzer.data.hybrid_provider import get_hybrid_provider

provider = get_hybrid_provider()
provider.print_stats()
```

Output:
```
📊 DATA PROVIDER STATISTICS
============================================================
Polygon Available:      ✅ Yes
Total Data Requests:    150
Polygon Calls:          120
Polygon Success Rate:   95.0%
YFinance Fallbacks:     30
============================================================
```

## 💡 Tips & Best Practices

### **1. Start with Free/Starter Tier**
- Test the integration with free or starter plan
- Upgrade only if you need real-time data

### **2. Monitor Your Usage**
- Check Polygon dashboard for API usage
- Stay within your plan's rate limits
- The analyzer respects rate limits automatically

### **3. Use Hybrid Approach**
- Let the analyzer choose best source
- Don't worry about fallbacks - it's automatic

### **4. Best Value Plans:**
- **Research/Learning:** Free yfinance (no Polygon needed)
- **Daily Scanning:** Polygon Starter ($29-49/month)
- **Intraday Trading:** Polygon Developer ($99-199/month)
- **Professional:** Polygon Advanced ($299+/month)

## 🐛 Troubleshooting

### **"Polygon initialization failed"**
- Check your API key is correct
- Verify key is active in Polygon dashboard
- Check internet connection

### **"Using yfinance fallback"**
- Normal! This means Polygon data wasn't available for that request
- Could be: rate limit, data not in your plan, or API error
- Analyzer continues working with yfinance

### **"Rate limit exceeded"**
- You've hit your Polygon plan's limit
- Analyzer automatically falls back to yfinance
- Consider upgrading plan or waiting for limit reset

### **No block trades showing up:**
- Block trade detection requires tick data
- Only available in higher-tier Polygon plans
- Falls back to regular volume analysis

## 🔄 About the Polygon → Massive Rebrand

**Q: Why does the code say "Polygon" but the company is now "Massive"?**

A: Polygon.io rebranded to Massive in 2024, but **technically nothing changed:**

| What | Still the Same? |
|------|----------------|
| Python package name | ✅ `polygon-api-client` |
| Import statements | ✅ `from polygon import RESTClient` |
| API endpoints | ✅ `api.polygon.io` |
| Your API keys | ✅ Work on both sites |
| Documentation | ✅ polygon.io/docs still active |
| Pricing/plans | ✅ Same structure |

**Bottom line:** The rebrand is **marketing only**. All technical aspects are identical. Your API key from either site works the same way.

## 📚 Additional Resources

- **Polygon Documentation:** https://polygon.io/docs (still active)
- **Massive Website:** https://massive.io (new branding)
- **API Reference:** https://polygon.io/docs/stocks/getting-started
- **Pricing:** https://polygon.io/pricing or https://massive.io/pricing

## ⚠️ Important Notes

1. **Polygon is OPTIONAL** - The analyzer works perfectly fine without it
2. **Automatic fallback** - Never breaks if Polygon is unavailable
3. **No vendor lock-in** - Can disable anytime by removing API key
4. **Free tier limitations** - Free tier has very limited usefulness
5. **Best for active traders** - Most value if scanning multiple times per day

## 🎯 Recommended Setup

**For Most Users:**
```json
{
  "api_keys": {
    "polygon": null  // Use free yfinance
  }
}
```

**For Serious Traders:**
```json
{
  "api_keys": {
    "polygon": "your_starter_or_developer_key"  // $29-199/month
  }
}
```

---

**Questions?** Check the main README or open an issue on GitHub.

**Happy Trading!** 🚀📈
