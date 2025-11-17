# Trading Signal Analyzer v0.93

**Advanced Technical Analysis Tool for Day Trading - Stocks, FOREX & Crypto**

A Python-based multi-asset scanner and technical analysis tool with NEW aggressive 5 Pillars momentum criteria, VWAP bands, MACD indicators, and Dark Flow institutional analysis to identify optimal entry and exit points across stocks, FOREX pairs, and cryptocurrencies.  If you find this useful, or just feel generous, [buy me a coffee.](https://buymeacoffee.com/savowood)

![License](https://img.shields.io/badge/license-GPL%20v3-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Version](https://img.shields.io/badge/version-0.93-green.svg)

---

## ⚠️ DISCLAIMER

**THIS SOFTWARE IS FOR EDUCATIONAL PURPOSES ONLY**

Trading stocks, FOREX, cryptocurrencies, options, and other securities involves **substantial risk** and can result in **significant financial losses**. This software is provided as an educational tool and technical analysis aid only.

- **NOT financial advice** - Consult a licensed financial advisor before trading
- **NOT investment advice** - You are solely responsible for your trading decisions  
- **NO WARRANTIES** - Author assumes no liability for any losses incurred
- **Past performance does not guarantee future results**

**USE AT YOUR OWN RISK. ONLY TRADE WITH MONEY YOU CAN AFFORD TO LOSE.**

---

## 🎯 Features

### Multi-Asset Scanning
- **Stock Scanner** - Momentum stocks using the 5 Pillars methodology
- **FOREX Scanner** - Top 10 major currency pairs (24/5 trading)
- **Crypto Scanner** - Top 20 active cryptocurrencies (24/7 trading)
- **Dark Flow Scanner** - Institutional volume profile analysis (NEW in v0.93)

### Stock Scanner (NEW 5 Pillars - v0.93)
- Scans NASDAQ, NYSE, or all US markets
- **NEW aggressive momentum criteria:**
  1. **Up 10%+ on the day** (active intraday momentum)
  2. **500% relative volume** (5x average - institutional interest)
  3. **News event detected** (catalyst moving stock higher)
  4. **Price range $2-$20** (default, configurable)
  5. **Under 20M shares float** (squeeze potential)
- **Configurable price ranges:**
  - Default: $2-$20 (recommended)
  - Penny stocks: $0.10-$2.00
  - Sub-penny: $0.0001-$0.10
  - Mid-cap: $20-$100
  - Custom: User-defined
- **Enhanced display** with low float indicators (⭐) and catalyst strength
- **Quality over quantity** - fewer, higher-probability setups
- **Delisting detection** - Automatically filters out inactive stocks

### FOREX Scanner
- Scans top 10 major FOREX pairs:
  - **Majors**: EUR/USD, GBP/USD, USD/JPY, USD/CHF
  - **Commodity currencies**: AUD/USD, NZD/USD, USD/CAD
  - **Crosses**: EUR/GBP, EUR/JPY, GBP/JPY
- Shows current price, changes, and volatility
- 24/5 market coverage

### Cryptocurrency Scanner
- Scans top 20 highly active cryptocurrencies:
  - BTC, ETH, BNB, SOL, XRP, ADA, DOGE, and more
- Displays hour%, day%, and week% changes
- Activity scoring based on volume and volatility
- 24/7 market coverage

### Dark Flow Scanner (NEW in v0.93)
- **Institutional volume profile analysis**
- Detects key price levels where institutions are active
- Identifies volume clusters (dark pool activity)
- Finds unusual volume spikes
- Detects price gaps and their significance
- **Works with stocks and major ETFs** (SPY, QQQ, IWM, DIA)
- Shows support/resistance levels based on institutional activity
- Provides bullish/bearish bias based on volume distribution

**Dark Flow Features:**
- Volume profile analysis with 20 price bins
- Key institutional levels ranked by trading activity
- Unusual volume detection (2+ standard deviations)
- Price gap identification and classification
- Active level alerts (within 0.5% of current price)
- Optimized for major ETFs where institutional activity is highest

### Technical Analysis
- **VWAP (Volume Weighted Average Price)** with 1σ and 2σ bands
- **SMA + ATR** bands for FOREX/crypto (when volume data unavailable)
- **MACD** (Moving Average Convergence Divergence) with crossover detection
- **Automatic entry/exit point calculation**
- **Risk/Reward ratio optimization** (default 3:1, customizable)
- **Position relative to VWAP bands** (overbought/oversold zones)
- Works across all asset types: stocks, FOREX, and crypto

### User-Friendly Interface
- Interactive menu system
- Multiple analysis timeframes (scalping, intraday, short-term, medium-term, long-term)
- Analyze scanned assets or manual entries
- Save scan results for repeated analysis
- Adjust settings on the fly

---

## 📋 Requirements

- Python 3.8 or higher
- Internet connection (for real-time data)

### Dependencies
```bash
pip install yfinance pandas numpy tradingview-screener
```

---

## 🚀 Installation

### Option 1: Clone from GitHub
```bash
git clone https://github.com/savowood/trading-signal-analyzer.git
cd trading-signal-analyzer
pip install -r requirements.txt
```

### Option 2: Direct Download
1. Download `trading_signal_analyzer.py`
2. Install dependencies:
   ```bash
   pip install yfinance pandas numpy tradingview-screener
   ```

---

## 💻 Usage

### Basic Usage
```bash
python trading_signal_analyzer.py
```

### First Run
1. **Accept Disclaimer** - You must accept terms and conditions
2. **Set Risk/Reward Ratio** - Default is 3:1, can be customized
3. **Choose Timeframe** - Scalping (1m), Intraday (5m), Short-term (1h), Medium-term (1d), or Long-term (1wk)

### Main Menu Options

**1. Run Momentum Scanner (stocks)**
- Scans markets for momentum setups
- Shows top candidates with scores
- Select stocks to analyze

**2. Scan FOREX pairs (top 10)**
- Scans major currency pairs
- Shows price movements and volatility
- 24/5 trading opportunities

**3. Scan Cryptocurrencies (top 20)**
- Scans most active cryptocurrencies
- Activity-based ranking
- 24/7 trading opportunities

**4. Dark Flow Scanner (institutional levels)**
- Analyze volume profile for institutional activity
- Scan major ETFs (SPY, QQQ, IWM, DIA) or custom tickers
- Identify key support/resistance from volume clusters
- Detect unusual volume and price gaps
- See where "smart money" is active

**5. Analyze from Last Scan**
- Reuse previous scan results
- Quick analysis without rescanning
- Works with stocks, FOREX, or crypto

**6. Enter Ticker Manually**
- Analyze specific assets
- Supports stocks, FOREX, and crypto
- Comma-separated for multiple tickers

**7. Change Risk/Reward Ratio**
- Adjust profit targets
- Common ratios: 2:1, 3:1, 5:1

**8. Change Timeframe**
- Switch between scalping/intraday/short/medium/long-term analysis

**9. Quit**
- Clean exit with final disclaimer

---

## 📊 Example Output

### Stock Analysis
```
📊 TRADING ANALYSIS: NVDA
💰 CURRENT PRICE: $892.50
📈 VWAP: $888.20 (+0.48%)
📍 Position: Between VWAP and 1σ (Upper)

📉 VWAP BANDS:
   +2σ: $905.30
   +1σ: $896.75
   VWAP: $888.20
   -1σ: $879.65
   -2σ: $871.10

📊 MACD:
   MACD Line: 2.3456
   Signal Line: 1.8923
   Histogram: 0.4533
   🔥 BULLISH CROSSOVER!

🎯 TRADING RECOMMENDATION
🟢 DIRECTION: LONG (STRONG signal)

📍 ENTRY POINT: $888.20
   Reason: Wait for pullback to VWAP

🛑 STOP LOSS: $883.77
   Risk: $4.43 (0.50%)

🎯 TAKE PROFIT: $901.49
   Reward: $13.29 (1.49%)

⚖️ RISK/REWARD: 3.00:1
   3:1 ratio is appropriate
```

### Dark Flow Scanner Output
```
🌊 DARK FLOW ANALYSIS: SPY
════════════════════════════════════════════════════════════════════════════════

💰 CURRENT PRICE: $485.23
📊 TODAY'S OPEN: $482.10
📈 TODAY'S RANGE: $481.50 - $486.75

🟢 BIAS: BULLISH

🎯 KEY INSTITUTIONAL LEVELS (Volume Clusters):
   1. $485.50 (+0.06%) ⭐ ACTIVE
   2. $483.20 (-0.42%) ⬇️  SUPPORT
   3. $487.30 (+0.43%) ⬆️  RESISTANCE
   4. $481.80 (-0.71%) ⬇️  SUPPORT
   5. $488.90 (+0.76%) ⬆️  RESISTANCE

🌊 DARK FLOW SIGNALS:
   • VOLUME_CLUSTER at $485.50

📊 UNUSUAL VOLUME ACTIVITY:
   • 2024-11-15 10:30: $484.50 - 3.2x avg
   • 2024-11-15 13:15: $485.80 - 2.8x avg

⚡ PRICE GAPS:
   • UP: $482.10 → $483.45 (1.28%)

⭐ MAJOR ETF - Prime candidate for signature prints

════════════════════════════════════════════════════════════════════════════════
💡 Volume clusters show institutional accumulation/distribution levels
════════════════════════════════════════════════════════════════════════════════
```

### FOREX Scanner Output
```
💱 FOREX PAIRS - TOP 10 MAJOR PAIRS
═══════════════════════════════════════════════════════════════════════════════

#    Pair         Price        Change%    Week%      Volatility%
───────────────────────────────────────────────────────────────────────────────
1    EUR/USD      1.0876       🟢 +0.15%  +1.23%     2.45%
2    GBP/USD      1.2654       🔴 -0.08%  -0.87%     2.18%
3    USD/JPY      149.2300     🟢 +0.22%  +2.14%     3.21%
```

### Crypto Scanner Output
```
₿ CRYPTOCURRENCIES - TOP 20 ACTIVE COINS
═══════════════════════════════════════════════════════════════════════════════

#    Name            Price           Hour%      Day%       Week%      Activity
───────────────────────────────────────────────────────────────────────────────
1    Bitcoin         $43,256.78      🟢 +0.45%  +2.34%    +8.76%     87.6
2    Ethereum        $2,287.45       🚀 +0.89%  +5.12%    +12.34%    156.2
3    Solana          $98.76          🟢 +0.34%  +1.23%    +15.67%    245.3
```

---

## 🎓 Methodology

### 5 Pillars of Day Trading
This software implements the "5 Pillars of Day Trading" methodology for stock selection, based on research from trading strategies that identify stocks with:
- High probability momentum setups
- Sufficient liquidity for day trading
- Volatility for profit potential
- Recent catalyst for price movement
- Technical pattern confirmation

**Learn more:**
- Educational resources on day trading strategies
- Technical analysis fundamentals

### Dark Flow Scanner Methodology
The Dark Flow Scanner uses **volume profile analysis** to detect institutional activity:

**How It Works:**
1. **Volume Profile Creation** - Divides price range into 20 bins and aggregates volume at each level
2. **Key Level Identification** - Finds price levels with highest trading activity (institutional accumulation/distribution)
3. **Unusual Volume Detection** - Identifies volume spikes 2+ standard deviations above average
4. **Gap Analysis** - Detects price gaps over 1% and classifies them
5. **Bias Determination** - Calculates bullish/bearish bias from price vs. open

**Use Cases:**
- Identify where institutions are building positions (support levels)
- Find resistance where institutions may be distributing (selling)
- Spot "signature prints" - large block orders in major ETFs
- Confirm technical analysis with volume validation
- Find optimal entry points near institutional levels

**Best Practices:**
- Focus on major ETFs (SPY, QQQ, IWM, DIA) for clearest signals
- Volume clusters within 0.5% of current price are most actionable
- Combine with VWAP/MACD analysis for highest-probability setups
- Unusual volume often precedes major price moves

### Technical Analysis
The technical analysis implementation (VWAP, MACD, SMA+ATR) is original work by the author:

**VWAP Bands:**
- VWAP = Volume Weighted Average Price
- Standard deviation bands show support/resistance
- Price position indicates overbought/oversold conditions

**SMA + ATR Bands:**
- Used for FOREX/crypto when volume data unavailable
- 20-period Simple Moving Average
- ATR-based bands (1x and 2x ATR)
- Automatically detected and applied

**MACD:**
- 12/26/9 default settings
- Crossovers signal potential entries
- Histogram shows momentum strength

---

## 🛠️ Configuration

### Timeframe Options

| Timeframe | Period | Interval | Best For |
|-----------|--------|----------|----------|
| Scalping | 1 day | 1 minute | Ultra-short term, quick trades |
| Intraday | 5 days | 5 minutes | Day trading, same-day entries/exits |
| Short-term | 1 month | 1 hour | Swing trading, multi-day holds |
| Medium-term | 3 months | 1 day | Position trading, weeks to months |
| Long-term | 1 year | 1 week | Investment trading, months to year |

### Risk/Reward Ratios

| Ratio | Description | Use Case |
|-------|-------------|----------|
| 2:1 | Conservative | High probability setups |
| 3:1 | Balanced | Default, most trades |
| 5:1 | Aggressive | Strong momentum, wider stops |

### Asset Types

| Asset Type | Format | Example |
|------------|--------|---------|
| Stocks | TICKER | AAPL, TSLA, NVDA |
| FOREX | PAIR=X | EURUSD=X, GBPUSD=X |
| Crypto | SYMBOL-USD | BTC-USD, ETH-USD |

---

## 🤝 Contributing

This project is open source under GPL v3. **All contributions are welcome!**

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines
- Follow existing code style (type hints, docstrings)
- Add comments for complex logic
- Test thoroughly before submitting
- Update README/CHANGELOG if adding features

**Important:** Per GPL v3, all modifications must be shared back to the community.

---

## 📝 License

This project is licensed under the **GNU General Public License v3.0**.

**What this means:**
- ✅ Free to use, modify, and distribute
- ✅ Commercial use allowed
- ✅ Must disclose source code
- ✅ Modifications must use GPL v3
- ✅ No warranty provided

See the [LICENSE](LICENSE) file for full details.

---

## 👤 Author

**Michael Johnson**
- GitHub: [@savowood](https://github.com/savowood)
- Project: [Trading Signal Analyzer](https://github.com/savowood/trading-signal-analyzer)

---

## 🙏 Acknowledgments

- **Trading Community** - For the 5 Pillars of Day Trading methodology
- **TradingView** - Screener API for market data
- **Yahoo Finance** - Historical price data via yfinance
- **Open Source Community** - For Python libraries and tools

---

## 📚 Educational Resources

### Recommended Learning
- [TradingView Education](https://www.tradingview.com/education/)
- [Investopedia Trading Basics](https://www.investopedia.com/trading-4427765)
- [Babypips FOREX School](https://www.babypips.com/learn/forex) (for FOREX)
- [CoinMarketCap Learn](https://coinmarketcap.com/alexandria) (for crypto)

### Dark Flow & Volume Profile
- Volume profile is a chartist technique for finding value areas
- Dark pools are private exchanges where institutional orders execute
- Volume clusters indicate areas where price may find support/resistance
- Combine with technical analysis for confirmation

### Risk Management
- Never risk more than 1-2% of account per trade
- Always use stop losses
- Paper trade before using real money
- Understand position sizing
- Have a trading plan
- Be aware of market hours and liquidity

### Market Hours
- **Stocks**: 9:30 AM - 4:00 PM ET (Mon-Fri)
- **FOREX**: 24 hours, 5 days/week (Sun 5 PM - Fri 5 PM ET)
- **Crypto**: 24 hours, 7 days/week

---

## ⚡ Troubleshooting

### Common Issues

**"TradingView screener not available"**
```bash
pip install tradingview-screener
```

**"Could not analyze [ticker]"**
- Check ticker symbol is correct (use proper format)
- Ensure internet connection
- Some assets may have insufficient data
- FOREX tickers need =X suffix (e.g., EURUSD=X)
- Crypto tickers need -USD suffix (e.g., BTC-USD)

**"No stocks/pairs/crypto found in scan"**
- Markets may be quiet
- Try different market selection
- Adjust timeframe
- Check internet connection

**Dark Flow Scanner Issues**
- Works best with liquid assets (stocks with high volume)
- Major ETFs (SPY, QQQ, IWM, DIA) provide clearest signals
- Requires at least 10 data points for volume profile
- Some assets may have insufficient historical data

**Rate Limiting**
- Yahoo Finance may throttle requests
- Wait a few minutes between large scans
- Use scanner results multiple times (option 5)

**FOREX/Crypto Data Issues**
- Some pairs may have limited historical data
- Try different timeframes
- Ensure correct ticker format
- System automatically switches to SMA+ATR when volume unavailable

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/savowood/trading-signal-analyzer/issues)
- **Discussions:** [GitHub Discussions](https://github.com/savowood/trading-signal-analyzer/discussions)
- **Pull Requests:** [GitHub PRs](https://github.com/savowood/trading-signal-analyzer/pulls)

---

## 🔮 Roadmap

**Current Version (v0.93):**
- ✅ NEW aggressive 5 Pillars momentum criteria
- ✅ Configurable price ranges ($2-$20 default)
- ✅ 500% relative volume filter (5x average)
- ✅ Low float detection (<20M shares)
- ✅ Multi-asset support (stocks, FOREX, crypto)
- ✅ Dark Flow Scanner (institutional levels)
- ✅ 5 timeframe options
- ✅ VWAP + MACD analysis
- ✅ SMA + ATR for FOREX/crypto

**Planned Features (v0.94+):**
- [ ] RSI and Bollinger Bands indicators
- [ ] Export analysis to CSV/PDF
- [ ] Trade journaling/logging
- [ ] Enhanced pattern recognition
- [ ] Dark Flow alerts for level breaks

**Planned for v1.0:**
- [ ] Backtesting engine
- [ ] Performance metrics and statistics
- [ ] Alert system for setups
- [ ] Multi-timeframe analysis view
- [ ] Real-time scanning mode
- [ ] Paper trading simulation

**Future Considerations:**
- [ ] GUI interface (optional)
- [ ] Mobile app companion
- [ ] Community sharing of setups
- [ ] Advanced charting integration
- [ ] Machine learning price predictions
- [ ] Options trading support
- [ ] Dark Flow pattern recognition (signature print detection)

---

## ⭐ Star History

If you find this tool useful, please consider giving it a star on GitHub!

---

## 📈 Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and release notes.

**Latest Updates (v0.93):**
- **NEW aggressive 5 Pillars** - Up 10%+, 5x volume, catalyst, $2-$20, <20M float
- **Configurable price ranges** - 5 presets + custom option
- **Enhanced momentum filtering** - Quality over quantity
- **Low float indicators** - Squeeze potential detection
- **Catalyst strength classification** - STRONG/MODERATE/PRESENT
- **Improved scanner display** - Sorted by best setups first
- **Dark Flow Scanner** - Institutional volume profile analysis
- **SMA + ATR bands** - For FOREX/crypto without volume data

---

## 📄 Legal

**Copyright (C) 2025 Michael Johnson**

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

---

## ⚠️ Important Notes

### Dark Flow Trading
- Volume clusters indicate institutional activity areas
- High volume at price level = strong support/resistance
- Unusual volume spikes often precede significant moves
- Major ETFs (SPY, QQQ) show clearest institutional patterns
- Always confirm with technical analysis (VWAP/MACD)

### FOREX Trading
- FOREX markets are highly leveraged
- Currency pairs can be affected by global events
- Always be aware of economic calendar events
- Understand pip values and lot sizes

### Cryptocurrency Trading
- Crypto markets are extremely volatile
- 24/7 trading with no circuit breakers
- Regulatory environment is evolving
- Consider exchange risks and wallet security
- Never invest more than you can afford to lose

### General Trading Advice
- This tool provides technical analysis only
- Fundamental analysis is also important
- Market conditions change constantly
- No system guarantees profits
- Risk management is crucial

---

**Built with ❤️ for the trading community**

*Remember: The best trade is the one you don't take when conditions aren't right.*
