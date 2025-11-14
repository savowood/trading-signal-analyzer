# Changelog

All notable changes to Trading Signal Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.91] - 2025-01-XX

### Added
- **Five trading timeframes** instead of three:
  - Scalping (1 day, 1-minute intervals)
  - Intraday (5 days, 5-minute intervals) 
  - Short-term (1 month, 1-hour intervals)
  - Medium-term (3 months, 1-day intervals)
  - Long-term (1 year, 1-week intervals)
- **Sub-penny stock support** - Now scans and displays stocks from $0.0001 to $20
- **Smart price formatting** - Automatically adjusts decimal places based on stock price:
  - 6 decimals for prices under $0.01
  - 4 decimals for prices $0.01-$0.10
  - 3 decimals for prices $0.10-$1.00
  - 2 decimals for prices $1.00+
- **Delisting detection** - Automatically filters out likely delisted stocks based on:
  - Ticker suffix indicators (Q, E, D)
  - Zero or extremely low volume
  - Extremely low market capitalization
  - Suspiciously low prices with no activity
- **CHANGELOG.md** - Version history and release notes

### Fixed
- Timeframe change menu now shows all 5 options consistently
- Scanner price range filter updated to include sub-penny stocks ($0.0001 minimum)
- VWAP bands and entry/exit points now format with appropriate decimals for sub-penny stocks

### Changed
- Updated scanner to scan from $0.0001 instead of $1.00 minimum
- Improved display formatting for scanner results table
- Enhanced precision in all price-related calculations

---

## [0.9] - 2025-01-XX

### Added
- **Initial release** of Trading Signal Analyzer
- Integrated Ross Cameron 5 Pillars Scanner
  - Relative Volume filter (2x+ average)
  - Float filter (under 100M shares)
  - Price range filter ($1-$20)
  - Catalyst detection (10%+ movement)
  - Pattern recognition (breakout/consolidation)
- **Technical Analysis Engine**
  - VWAP calculation with 1σ and 2σ bands
  - MACD indicator with crossover detection
  - Automatic entry/exit point calculation
- **Risk Management**
  - Configurable risk/reward ratios (default 3:1)
  - Smart stop loss placement
  - Take profit optimization
  - Risk/reward ratio recommendations
- **Interactive Menu System**
  - Run scanner for momentum setups
  - Analyze from previous scan results
  - Manual ticker entry
  - Change risk/reward ratio on the fly
  - Change timeframe dynamically
- **Three Initial Timeframes**
  - Intraday (5 days, 5-minute intervals)
  - Short-term (1 month, 1-hour intervals)
  - Medium-term (3 months, 1-day intervals)
- **Legal & Compliance**
  - GPL v3 open source license
  - Comprehensive financial disclaimer
  - User acceptance required at startup
  - Exit disclaimer with risk reminders
- **Documentation**
  - README.md with installation and usage instructions
  - Requirements.txt for dependency management
  - Inline code documentation with docstrings
  - Type hints for better code clarity

### Features
- Real-time market data from TradingView screener
- Historical data from Yahoo Finance (yfinance)
- Support for NASDAQ, NYSE, and combined US markets
- Position analysis relative to VWAP bands
- MACD bullish/bearish signal strength classification
- Session persistence (scan results, settings)
- Batch analysis of multiple stocks
- Formatted output with emojis and clear structure

### Technical
- Python 3.8+ support
- Dependencies: yfinance, pandas, numpy, tradingview-screener
- Modular class-based architecture
- Type-annotated functions
- Comprehensive error handling
- Clean separation of concerns

---

## Release Notes

### Version Numbering
- **Major.Minor.Patch** format (Semantic Versioning)
- Major: Breaking changes or significant feature additions
- Minor: New features, backwards compatible
- Patch: Bug fixes, small improvements

### Compatibility
- **Python**: 3.8 or higher required
- **Operating Systems**: Windows, macOS, Linux
- **Internet**: Required for real-time data

### Known Issues
See [GitHub Issues](https://github.com/savowood/trading-signal-analyzer/issues) for current known issues and feature requests.

---

## Upcoming Features (Roadmap)

### Planned for v0.92
- [ ] Enhanced pattern recognition algorithms
- [ ] Additional technical indicators (RSI, Bollinger Bands)
- [ ] Export analysis results to CSV
- [ ] Trading journal integration

### Planned for v1.0
- [ ] Backtesting engine
- [ ] Performance metrics and statistics
- [ ] Alert system for setups
- [ ] Multi-timeframe analysis view
- [ ] Real-time scanning mode
- [ ] Paper trading simulation

### Future Considerations
- [ ] GUI interface (optional)
- [ ] Mobile app companion
- [ ] Community sharing of setups
- [ ] Advanced charting integration
- [ ] Machine learning price predictions

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

All contributions must comply with GPL v3 license requirements.

---

## Support

- **Bug Reports**: [GitHub Issues](https://github.com/savowood/trading-signal-analyzer/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/savowood/trading-signal-analyzer/discussions)
- **Questions**: [GitHub Discussions Q&A](https://github.com/savowood/trading-signal-analyzer/discussions/categories/q-a)

---

**Author**: Michael Johnson (@savowood)  
**License**: GPL v3  
**Repository**: https://github.com/savowood/trading-signal-analyzer
