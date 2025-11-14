# Trading Signal Analyzer v0.91

**Advanced Technical Analysis Tool for Day Trading**

A Python-based stock scanner and technical analysis tool that combines Ross Cameron's 5 Pillars of Day Trading methodology with VWAP bands and MACD indicators to identify optimal entry and exit points.

![License](https://img.shields.io/badge/license-GPL%20v3-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Version](https://img.shields.io/badge/version-0.91-green.svg)

---

## ⚠️ DISCLAIMER

**THIS SOFTWARE IS FOR EDUCATIONAL PURPOSES ONLY**

Trading stocks, options, and other securities involves **substantial risk** and can result in **significant financial losses**. This software is provided as an educational tool and technical analysis aid only.

- **NOT financial advice** - Consult a licensed financial advisor before trading
- **NOT investment advice** - You are solely responsible for your trading decisions  
- **NO WARRANTIES** - Author assumes no liability for any losses incurred
- **Past performance does not guarantee future results**

**USE AT YOUR OWN RISK. ONLY TRADE WITH MONEY YOU CAN AFFORD TO LOSE.**

---

## 🎯 Features

### Ross Cameron Scanner
- Scans NASDAQ, NYSE, or all US markets
- Filters stocks based on the **5 Pillars of Day Trading**:
  1. Strong Relative Volume (2x+ average)
  2. Float under 100 million shares
  3. Price range $0.0001-$20 (includes sub-penny stocks)
  4. Recent catalyst (10%+ price movement)
  5. Chart pattern (breakout or consolidation)
- **Sub-penny stock support** - Displays accurate pricing for stocks under $0.01

### Technical Analysis
- **VWAP (Volume Weighted Average Price)** with 1σ and 2σ bands
- **MACD** (Moving Average Convergence Divergence) with crossover detection
- **Automatic entry/exit point calculation**
- **Risk/Reward ratio optimization** (default 3:1, customizable)
- **Position relative to VWAP bands** (overbought/oversold zones)

### User-Friendly Interface
- Interactive menu system
- Multiple analysis timeframes (intraday, short-term, medium-term)
- Analyze scanned stocks or manual entries
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

**1. Run Ross Cameron Scanner**
- Scans markets for momentum setups
- Shows top candidates with scores
- Select stocks to analyze

**2. Analyze from Last Scan**
- Reuse previous scan results
- Quick analysis without rescanning

**3. Enter Ticker Manually**
- Analyze specific stocks
- Comma-separated for multiple tickers

**4. Change Risk/Reward Ratio**
- Adjust profit targets
- Common ratios: 2:1, 3:1, 5:1

**5. Change Timeframe**
- Switch between scalping/intraday/short/medium/long-term analysis

**6. Quit**
- Clean exit with final disclaimer

---

## 📊 Example Output

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

---

## 🎓 Methodology

### Ross Cameron's 5 Pillars
This software implements the stock selection methodology taught by Ross Cameron at [Warrior Trading](https://www.warriortrading.com/). The 5 Pillars identify stocks with:
- High probability momentum setups
- Sufficient liquidity for day trading
- Volatility for profit potential
- Recent catalyst for price movement
- Technical pattern confirmation

**Learn more:**
- [Warrior Trading YouTube](https://www.youtube.com/c/WarriorTrading)
- [Ross Cameron's Trading Strategies](https://www.warriortrading.com/day-trading-strategies)

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
- Update README if adding features

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

- **Ross Cameron** - For the 5 Pillars of Day Trading methodology
- **Warrior Trading** - Educational resources and trading community
- **TradingView** - Screener API for market data
- **Yahoo Finance** - Historical price data via yfinance

---

## 📚 Educational Resources

### Recommended Learning
- [Warrior Trading Free Course](https://www.warriortrading.com/free-day-trading-course)
- [TradingView Education](https://www.tradingview.com/education/)
- [Investopedia Trading Basics](https://www.investopedia.com/trading-4427765)

### Risk Management
- Never risk more than 1-2% of account per trade
- Always use stop losses
- Paper trade before using real money
- Understand position sizing
- Have a trading plan

---

## ⚡ Troubleshooting

### Common Issues

**"TradingView screener not available"**
```bash
pip install tradingview-screener
```

**"Could not analyze [ticker]"**
- Check ticker symbol is correct
- Ensure internet connection
- Some stocks may have insufficient data

**"No stocks found in scan"**
- Markets may be quiet
- Try different market selection
- Adjust timeframe

**Rate Limiting**
- Yahoo Finance may throttle requests
- Wait a few minutes between large scans
- Use scanner results multiple times (option 2)

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/savowood/trading-signal-analyzer/issues)
- **Discussions:** [GitHub Discussions](https://github.com/savowood/trading-signal-analyzer/discussions)
- **Pull Requests:** [GitHub PRs](https://github.com/savowood/trading-signal-analyzer/pulls)

---

## 🔮 Roadmap

**Planned Features (v1.0+):**
- [ ] Backtesting engine
- [ ] Trade journaling/logging
- [ ] Multiple timeframe analysis
- [ ] Additional technical indicators (RSI, Stochastic)
- [ ] Alert system for setups
- [ ] Export analysis to CSV/PDF
- [ ] GUI interface (optional)
- [ ] Real-time scanning mode

---

## ⭐ Star History

If you find this tool useful, please consider giving it a star on GitHub!

---

## 📄 Legal

**Copyright (C) 2025 Michael Johnson**

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

---

**Built with ❤️ for the trading community**

*Remember: The best trade is the one you don't take when conditions aren't right.*
