# Changelog

All notable changes to Trading Signal Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.98] - 2025-12-01

### Fixed
- **Column Alignment in All Display Outputs** - Corrected misaligned columns across multiple displays
  - Fixed Dark Flow Scanner display - Score, Bias, RelVol, and Change% now align properly
  - Fixed Cryptocurrency display - Hour%, Day%, Week%, and Activity columns now align correctly
  - Fixed 5 Pillars display - Score, Today%, RelVol, and Float(M) columns now align properly
  - Fixed FOREX display - Change%, Week%, and Volatility% columns now align correctly
  - Properly accounted for emojis (🔥, 🟢, 🔴, ⭐) in column width calculations
  - Added spacing before "x" in RelVol values (e.g., "10.8 x" instead of "10.8x")
  - All percentage signs and suffixes now properly included in formatted strings

### Changed
- **Dark Flow Scanner Menu Order** - Reorganized for better workflow
  - Market-wide Dark Flow scan moved to first option (was second)
  - Major ETFs scan moved to second option (was first)
  - Manual ticker entry remains in third position
  - Provides quicker access to the most powerful scanning feature

### Added
- **Quick Quit Option ('q')** - Added to all menus for faster navigation
  - Main menu: Press 'q' to quit application (alternative to option 11)
  - Momentum Scanner: 'q' returns to main menu from market and price selection
  - Dark Flow Scanner: 'q' returns to main menu from all sub-menus
  - Timeframe selection: 'q' cancels and returns to main menu
  - All input prompts updated to show 'q' option
  - Improves user experience with quick exit capability

### Technical
- Updated version number to 0.98 in script
- All `.lower()` calls added to input handling for case-insensitive 'q' detection
- Column width adjustments maintain consistency across different data types

---

## [0.97] - 2025-01-27

### Added
- **Extended Trading Hours Support** - Comprehensive pre-market and after-hours analysis
  - Pre-market analysis (4:00 AM - 9:30 AM ET)
  - After-hours analysis (4:00 PM - 8:00 PM ET)
  - Extended hours price change calculations vs. last regular market close
  - Volume tracking for pre-market and after-hours sessions
  - High/low range displays for each extended session
  - Timezone-aware session detection and separation
  - Green/red emoji indicators for price direction (🟢/🔴/⚪)
- **Enhanced Data Collection** - All stock data fetching now includes extended hours
  - `analyze_stock()` uses `prepost=True` for comprehensive data
  - `check_multi_timeframe()` includes extended hours in trend analysis
  - `analyze_institutional_levels()` tracks extended hours volume patterns
- **Smart Display Integration** - Extended hours info shown in analysis output
  - Displays after current price in recommendation view
  - Formatted volume with thousands separators
  - Price ranges adapt to stock price level (penny stocks, crypto, etc.)
  - Only shown for stocks (not forex/crypto which trade 24/7)

### Why This Feature?
Extended hours trading provides critical insights:
- **Pre-market momentum** - See institutional positioning before market open
- **After-hours reactions** - Track immediate response to earnings and news
- **Better timing** - Make more informed entry/exit decisions with complete data
- **Volume analysis** - Understand institutional activity outside regular hours

---

## [0.96] - 2025-01-27

### Added
- **Automatic Update Checker** - Checks for new releases on application launch
  - Queries GitHub releases API for latest version
  - Semantic version comparison (handles 0.95, 0.96, 1.0, etc.)
  - Non-blocking with 2-second timeout (won't delay app startup)
  - Prominent notification with download link when update available
  - Silently fails if network unavailable or API rate-limited
  - Shows version comparison: Current vs. Latest

### Technical
- Uses GitHub API endpoint: `/repos/savowood/trading-signal-analyzer/releases/latest`
- Parses version tags (strips 'v' prefix if present)
- Proper semantic version comparison with padding
- Graceful error handling for network issues

---

## [0.95] - 2025-01-26

### Added
- **RSI Indicator (14-period)** - Classic momentum oscillator
  - Overbought detection (RSI > 70)
  - Oversold detection (RSI < 30)
  - Neutral zone identification
  - Displayed in analysis output with status
- **SuperTrend Indicator** - ATR-based trend following system
  - 10-period ATR with 3.0 multiplier
  - Dynamic support/resistance levels
  - Bullish/bearish trend detection (🟢/🔴 indicators)
  - Upper and lower band calculations
- **Volume Confirmation Analysis** - Validates signals with volume data
  - Relative volume ratio vs. 20-period average
  - Strong confirmation (2x+ volume)
  - Moderate confirmation (1.5x-2x volume)
  - Weak/no confirmation (< 1.5x volume)
- **EMA 9/20 Crossover Signals** - Fast/slow moving average system
  - Bullish crossover detection (9 crosses above 20)
  - Bearish crossunder detection (9 crosses below 20)
  - Current EMA values displayed
  - Signal strength integration
- **Multi-Timeframe Trend Confirmation** - Analyzes 3 timeframes simultaneously
  - 1-hour trend (20-period EMA)
  - 4-hour trend (20-period EMA)
  - Daily trend (50-period EMA)
  - Bullish/bearish/mixed alignment detection
  - Counts bullish trends across timeframes
  - Different periods for crypto vs. stocks
- **Signal Strength Scoring System** - Comprehensive 0-100 score with letter grades
  - Grade A (90-100): Excellent setup, all indicators aligned
  - Grade B (80-89): Strong setup, most indicators positive
  - Grade C (70-79): Good setup, favorable conditions
  - Grade D (60-69): Marginal setup, mixed signals
  - Grade F (< 60): Poor setup, unfavorable conditions
  - Scoring factors:
    - VWAP position (40 points max)
    - MACD signals (20 points max)
    - RSI levels (15 points max)
    - Volume confirmation (10 points max)
    - Multi-timeframe alignment (15 points max)
- **Position Sizing Calculator** - Risk-based position management
  - Account size input
  - Risk percentage per trade (default 1%)
  - Automatic share calculation based on stop loss
  - Dollar risk amount display
  - Portfolio percentage allocation
- **CSV Export for Batch Analysis** - Save analysis results to file
  - All key metrics exported
  - Timestamp included
  - Suitable for further analysis or record keeping
- **Crypto-Specific Parameter Adjustments** - Optimized for cryptocurrency volatility
  - Different multi-timeframe periods
  - Adjusted for 24/7 trading
  - Higher volatility accommodation

### Changed
- Signal recommendation now includes comprehensive scoring
- Entry/exit calculations factor in multiple indicators
- Analysis output expanded with new indicator sections
- More granular signal strength classification

---

## [0.94] - 2025-01-25

### Fixed
- **VWAP Bands Corrected** - Now use 2σ and 3σ (instead of 1σ and 2σ)
  - Upper bands: +2σ and +3σ from VWAP
  - Lower bands: -2σ and -3σ from VWAP
  - Updated all display text to reflect correct bands
  - More accurate extreme zone detection
- **Stock Scanner Price Filter** - Now properly enforced
  - Minimum price: 90% of lower bound (prevents edge cases)
  - Better filtering of stocks near price boundaries
  - Reduced false positives from delisted stocks
- **Cryptocurrency Scanner** - Now fully dynamic
  - Fetches real-time data from CoinGecko API
  - No more hardcoded ticker lists
  - Automatically gets top cryptocurrencies by market cap
  - Handles API failures gracefully
  - Shows trading volume and market cap
- **Removed Delisted/Inactive Crypto Tickers** - Clean dataset
  - Removed deprecated tokens
  - Removed low-volume/dead projects
  - Focus on actively traded cryptocurrencies

### Changed
- VWAP zone descriptions updated throughout codebase
- Scanner output shows "2σ" and "3σ" labels
- Crypto scanner more reliable with dynamic data

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
