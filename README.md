# Trading Signal Analyzer v0.92

**Advanced Technical Analysis Tool for Day Trading - Stocks, FOREX & Crypto**

A Python-based multi-asset scanner and technical analysis tool that combines the 5 Pillars of Day Trading methodology with VWAP bands and MACD indicators to identify optimal entry and exit points across stocks, FOREX pairs, and cryptocurrencies.

![License](https://img.shields.io/badge/license-GPL%20v3-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Version](https://img.shields.io/badge/version-0.92-green.svg)

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
- **Stock Scanner** - Momentum stocks using the 5 Pillars methodology losely based on Ross Cameron's pillars
- **FOREX Scanner** - Top 10 major currency pairs (24/5 trading)
- **Crypto Scanner** - Top 20 active cryptocurrencies (24/7 trading)

### Stock Scanner (5 Pillars)
- Scans NASDAQ, NYSE, or all US markets
- Filters stocks based on the **5 Pillars of Day Trading**:
  1. Strong Relative Volume (2x+ average)
  2. Float under 100 million shares
  3. Price range $0.0001-$20 (includes sub-penny stocks)
  4. Recent catalyst (10%+ price movement)
  5. Chart pattern (breakout or consolidation)
- **Sub-penny stock support** - Displays accurate pricing for stocks under $0.01
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

### Technical Analysis
- **VWAP (Volume Weighted Average Price)** with 1σ and 2σ bands
- **MACD** (Moving Average Convergence Divergence) with crossover detection
- **SMA(20) with ATR bands** (When volume data isn't available for VWAP)
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
You may need to use python3 instead of just python on some systems.  Consult your man pages on how to make an alias.

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

**4. Analyze from Last Scan**
- Reuse previous scan results
- Quick analysis without rescanning
- Works with stocks, FOREX, or crypto

**5. Enter Ticker Manually**
- Analyze specific assets
- Supports stocks, FOREX, and crypto
- Comma-separated for multiple tickers

**6. Change Risk/Reward Ratio**
- Adjust profit targets
- Common ratios: 2:1, 3:1, 5:1

**7. Change Timeframe**
- Switch between scalping/intraday/short/medium/long-term analysis

**8. Quit**
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
This is losely based on the five pillars from Warrior Trading and Ross Cameron.  It is NOT the same.

**Learn more:**
- Educational resources on day trading strategies
- Technical analysis fundamentals

### Technical Analysis
The technical analysis implementation (VWAP, MACD) is original work by the author:

**VWAP Bands:**
- VWAP = Volume Weighted Average Price
- Standard deviation bands show support/resistance
- Price position indicates overbought/oversold conditions

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

- **Warrior Trading, Ross Cameron, and the entire Trading Community** - For the 5 Pillars of Day Trading methodology
- **Joovier** - The YouTuber who shared a ton of knowledge in his multi-hour videos
- **My AMAZING girlfriend** - For making me get off my butt and finally start doing this
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
- [Warrior Trading and Ross Cameron](https://www.warriortrading.com/)
- [Ross Cameron's YouTube Channel](https://www.youtube.com/@DaytradeWarrior)
- [Joovier's YouTube channel](https://www.youtube.com/@JooviersGems)


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

**Rate Limiting**
- Yahoo Finance may throttle requests
- Wait a few minutes between large scans
- Use scanner results multiple times (option 4)

**FOREX/Crypto Data Issues**
- Some pairs may have limited historical data
- Try different timeframes
- Ensure correct ticker format

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/savowood/trading-signal-analyzer/issues)
- **Discussions:** [GitHub Discussions](https://github.com/savowood/trading-signal-analyzer/discussions)
- **Pull Requests:** [GitHub PRs](https://github.com/savowood/trading-signal-analyzer/pulls)

---

## 🔮 Roadmap

**Current Version (v0.92):**
- ✅ Multi-asset support (stocks, FOREX, crypto)
- ✅ 5 timeframe options
- ✅ Sub-penny stock support
- ✅ VWAP + MACD analysis

**Planned Features (v0.93+):**
- [ ] RSI and Bollinger Bands indicators
- [ ] Export analysis to CSV/PDF
- [ ] Trade journaling/logging
- [ ] Enhanced pattern recognition

**Planned for v1.0:**
- [ ] Backtesting engine
- [ ] Performance metrics and statistics
- [ ] Alert system for setups
- [ ] Multi-timeframe analysis view
- [ ] Real-time scanning mode
- [ ] Paper trading simulation

**Future Considerations:**
- [ ] GUI (optional)
- [ ] Mobile app companion
- [ ] Community sharing of setups
- [ ] Advanced charting integration
- [ ] Machine learning price predictions
- [ ] Options trading support

---

## ⭐ Star History

If you find this tool useful, please consider giving it a star on GitHub!

---

## 📈 Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and release notes.

**Latest Updates (v0.92):**
- Added FOREX scanner for top 10 currency pairs
- Added cryptocurrency scanner for top 20 coins
- Enhanced menu system with 8 options
- Unified asset selection interface
- Smart formatting for different asset types

---

## 📄 Legal

**Copyright (C) 2025 Michael Johnson**

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

---

## ⚠️ Important Notes

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
