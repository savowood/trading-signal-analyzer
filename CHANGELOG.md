# Changelog

All notable changes to Trading Signal Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.93] - 2025-01-XX

### Changed - NEW 5 PILLARS CRITERIA
**Complete overhaul of momentum scanner with new, more aggressive criteria:**

#### NEW 5 Pillars:
1. **Up 10%+ on the day** (was: any price movement)
   - Filters for strong intraday momentum
   - Only shows stocks actively moving UP
   - Catches momentum early in the day

2. **500% relative volume (5x average)** (was: 2x average)
   - Much stronger volume requirement
   - Indicates significant institutional interest
   - Filters out low-conviction moves

3. **News event moving stock higher** (was: any catalyst)
   - Catalyst detection via extreme moves + volume
   - Strong/moderate/present classification
   - Indicates fundamental driver behind move

4. **Price range $2-$20** (was: $0.0001-$20)
   - Default changed to $2-$20 for better liquidity
   - Configurable with 5 preset ranges + custom option
   - Eliminates most penny stocks by default
   - Sub-penny and penny options still available

5. **Under 20M shares float** (was: under 100M)
   - Much tighter float requirement
   - Optimized for squeeze potential
   - Filters for low-float runners

### Added
- **Price range configuration menu** with presets:
  - Default: $2-$20 (recommended)
  - Penny stocks: $0.10-$2.00
  - Sub-penny: $0.0001-$0.10
  - Mid-cap: $20-$100
  - Custom: User-defined range
- **Enhanced scanner output** showing:
  - Low float indicator (⭐)
  - Today's % change (primary sort)
  - Catalyst strength (STRONG/MODERATE/PRESENT)
  - Clearer 5 Pillars explanation in header
- **Improved filtering**:
  - Minimum 3 of 5 pillars required (was: 2 of 5)
  - Sort by score then today's % move
  - Up to 100 results scanned (was: 50)

### Changed
- Scanner now sorts by **biggest movers today** (was: highest relative volume)
- Default price range is **$2-$20** (was: $0.0001-$20)
- Minimum pillars met: **3 of 5** (was: 2 of 5)
- Scanner criteria much more aggressive for momentum plays
- Display format updated for new criteria

### Why These Changes?
The new 5 Pillars are designed to catch **active momentum plays** with:
- Strong intraday movement (already up 10%+)
- Explosive volume (5x average)
- Fundamental catalyst (news/event driving move)
- Good liquidity ($2-$20 range)
- Squeeze potential (low float <20M)

This eliminates most noise and focuses on high-probability momentum setups.

---

## [0.92] - 2025-01-XX

### Added
- **FOREX Scanner** - Scan top 10 major FOREX pairs
  - EUR/USD, GBP/USD, USD/JPY, USD/CHF (majors)
  - AUD/USD, NZD/USD, USD/CAD (commodity currencies)
  - EUR/GBP, EUR/JPY, GBP/JPY (crosses)
  - Displays price, change%, week%, and volatility
  - 24/5 market coverage
- **Cryptocurrency Scanner** - Scan top 20 highly active cryptocurrencies
  - BTC, ETH, BNB, SOL, XRP, ADA, DOGE, and more
  - Displays hour%, day%, week% changes
  - Activity scoring based on volume and volatility
  - 24/7 market coverage
- **Unified Scanner Interface** - Choose from stocks, FOREX, or crypto
  - All scanners accessible from main menu
  - Consistent selection interface across asset types
  - Stores last scan results for quick re-analysis
  - Smart formatting for different asset classes
- **Enhanced Manual Entry** - Examples provided for stocks, FOREX, and crypto formats
- **SMA + ATR Bands** - Alternative to VWAP for assets without volume data
  - Automatically detects if volume data is available
  - Uses 20-period SMA with ATR-based bands for FOREX/crypto
  - Uses VWAP with standard deviation bands for stocks
  - Seamless switching between indicators

### Changed
- Main menu expanded from 6 to 8 options
- Generic `choose_from_scan()` function replaces stock-specific version
- Updated menu numbering to accommodate new features
- Version number updated to 0.92
- Technical analysis now adapts to asset type (VWAP for stocks, SMA+ATR for FOREX/crypto)

### Fixed
- Typo in calculate_entry_exit function (lower_2sd → lower_2std)
- **FOREX and crypto analysis now works correctly** - Previously showed NaN values due to missing volume data
- Volume detection added to automatically choose appropriate indicators
- Display function now shows correct indicator type (VWAP vs SMA)

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
- Removed named references to Ross Cameron from user-facing text (kept in code comments for attribution)

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

### Planned for v0.93
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
