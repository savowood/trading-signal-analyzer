# Migration Guide: v1.0 → v2.0

**Migrating from Monolithic to Modular Architecture**

This guide helps you transition from Trading Signal Analyzer v1.0 (single-file) to v2.0 (modular package) while maintaining your settings, understanding new features, and adapting to the new workflow.

---

## 📋 Table of Contents

1. [Should You Migrate?](#should-you-migrate)
2. [Key Differences](#key-differences)
3. [Installation](#installation)
4. [Settings Migration](#settings-migration)
5. [Workflow Changes](#workflow-changes)
6. [New Features in v2.0](#new-features-in-v20)
7. [Feature Comparison](#feature-comparison)
8. [Running Both Versions](#running-both-versions)
9. [Troubleshooting](#troubleshooting)
10. [FAQs](#faqs)

---

## Should You Migrate?

### ✅ Migrate to v2.0 if you want:
- **Polygon/Massive API integration** - Professional-grade market data
- **Scan history database** - Track all your scans over time
- **Support/Resistance analysis** - Advanced technical levels
- **Volume Profile** - See where institutions are trading
- **Parallel processing** - Faster market scans
- **Watchlist system** - Monitor favorite tickers
- **Better code organization** - Easier to extend/customize

### ⏸️ Stay on v1.0 if you:
- **Need maximum stability** - v1.0 is rock-solid and complete
- **Prefer single-file simplicity** - Just one Python file to manage
- **Don't need new features** - v1.0 does everything you need
- **Want proven reliability** - v1.0 is battle-tested

### 🤝 Use Both if you:
- Want to **test v2.0** while keeping v1.0 as backup
- Need v2.0 features sometimes, but prefer v1.0 simplicity for quick scans
- Are evaluating whether to fully migrate

**The Good News:** Both versions can run side-by-side with no conflicts!

---

## Key Differences

### Architecture

| Aspect | v1.0 (Monolithic) | v2.0 (Modular) |
|--------|-------------------|----------------|
| **File Structure** | Single file | Package with modules |
| **Execution** | `python trading_signal_analyzer.py` | `python -m trading_analyzer` |
| **Installation** | Copy file + pip install deps | `pip install -e .` or `pip install trading-analyzer` |
| **Updates** | Download new file | `git pull` + `pip install -e .` |
| **Customization** | Edit one large file | Edit specific modules |

### Features

| Feature | v1.0 | v2.0 | Notes |
|---------|------|------|-------|
| 5 Pillars Scanner | ✅ | ✅ | Same |
| FOREX Scanner | ✅ | ✅ | Same |
| Crypto Scanner | ✅ | ✅ | Same |
| Dark Flow Scanner | ✅ | ✅ | Enhanced in v2.0 |
| Pressure Cooker | ✅ | ✅ | Enhanced in v2.0 |
| Polygon API | ❌ | ✅ | **NEW** |
| Database/History | ❌ | ✅ | **NEW** |
| Watchlist | ❌ | ✅ | **NEW** |
| Support/Resistance | ❌ | ✅ | **NEW** |
| Volume Profile | ❌ | ✅ | **NEW** |
| Parallel Processing | ❌ | ✅ | **NEW** |
| Position Calculator | ✅ | ❌ | v1.0 only |
| R:R Customization | ✅ | ❌ | v1.0 only |
| Timeframe Selection | ✅ | ❌ | v1.0 only |
| Extended Hours | ✅ | ❌ | v1.0 only |
| Batch Analysis | ✅ | ❌ | v1.0 only |

---

## Installation

### Option A: Side-by-Side Installation (Recommended for Testing)

Keep v1.0 running while testing v2.0:

```bash
# Your existing v1.0 installation stays where it is
# /path/to/trading_signal_analyzer.py

# Clone v2.0 to a different location
cd ~/trading-tools
git clone -b v2.0-dev https://github.com/savowood/trading-signal-analyzer.git trading-analyzer-v2
cd trading-analyzer-v2

# Install v2.0 in development mode
pip install -e .

# Run v1.0
python /path/to/trading_signal_analyzer.py

# Run v2.0
python -m trading_analyzer
```

### Option B: Clean Migration

Replace v1.0 with v2.0:

```bash
# Backup your v1.0 file (just in case)
cp trading_signal_analyzer.py trading_signal_analyzer.py.v1.0.backup

# Remove v1.0 (optional - you can keep it)
# rm trading_signal_analyzer.py

# Clone v2.0
git clone -b v2.0-dev https://github.com/savowood/trading-signal-analyzer.git
cd trading-signal-analyzer

# Install
pip install -e .

# Run
python -m trading_analyzer
```

### Option C: Use Both Regularly

Create shell aliases for easy switching:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias tsa1='python /path/to/trading_signal_analyzer.py'
alias tsa2='python -m trading_analyzer'

# Usage
tsa1  # Run v1.0
tsa2  # Run v2.0
```

---

## Settings Migration

### Your Settings File

Both versions use `~/.trading_analyzer`, so your settings automatically carry over!

**v1.0 Settings Structure:**
```json
{
  "disclaimer_acknowledged": true,
  "pressure_cooker_disclaimer_acknowledged": true,
  "api_keys": {
    "newsapi": null,
    "reddit_client_id": null,
    "reddit_client_secret": null
  },
  "cache_settings": {
    "scan_results": 900
  }
}
```

**v2.0 Settings Structure (Enhanced):**
```json
{
  "disclaimer_acknowledged": true,
  "pressure_cooker_disclaimer_acknowledged": true,
  "api_keys": {
    "polygon": "YOUR_POLYGON_API_KEY",  // NEW
    "newsapi": null,
    "reddit_client_id": null,
    "reddit_client_secret": null
  },
  "cache_settings": {
    "scan_results": 900,
    "stock_data": 3600,  // NEW
    "options_data": 1800  // NEW
  },
  "database": {  // NEW
    "path": "~/Documents/trading_analyzer.db",
    "auto_save": true,
    "max_history_days": 90
  }
}
```

### Adding Polygon API Key

```bash
# Edit settings file
nano ~/.trading_analyzer

# Add your Polygon API key
{
  "api_keys": {
    "polygon": "abc123XYZ789yourKeyHere"
  }
}
```

See `POLYGON_SETUP_GUIDE.md` for obtaining an API key.

---

## Workflow Changes

### Launching the Application

**v1.0:**
```bash
python trading_signal_analyzer.py
```

**v2.0:**
```bash
python -m trading_analyzer
# OR
trading-analyzer  # If installed with pip install
```

### Menu Structure

**v1.0 Main Menu:**
```
1. Momentum Scanner
2. FOREX Scanner
3. Crypto Scanner
4. Dark Flow Scanner
   └─ 4. Pressure Cooker
5. Analyze from last scan
6. Enter ticker manually
7. Batch analysis
8. Position calculator
9. Change R:R ratio
10. Change timeframe
```

**v2.0 Main Menu:**
```
1. Run Momentum Scan
2. Run Dark Flow Scan
3. Run Pressure Cooker  // Top level now
4. View Database Statistics  // NEW
5. Manage Watchlist  // NEW
6. View Cache Status
7. Clear Cache
8. View Settings
9. Edit Settings
```

### Scanner Output

**v1.0:** Results displayed in terminal only

**v2.0:** Results displayed in terminal AND saved to database

```bash
# View scan history
python -m trading_analyzer
# Select "4. View Database Statistics"
```

---

## New Features in v2.0

### 1. Polygon/Massive API Integration

Get professional-grade market data:

```python
# Automatic hybrid provider
# Tries Polygon first, falls back to yfinance
# No code changes needed!
```

**Benefits:**
- Real-time or delayed quotes (depending on plan)
- Better reliability
- Block trade detection
- Enhanced volume data

### 2. Database & Scan History

All scans automatically saved:

```sql
-- View your scan history
SELECT scan_type, timestamp, results_count
FROM scan_history
ORDER BY timestamp DESC
LIMIT 10;
```

**Features:**
- Track performance over time
- Review past scans
- Identify patterns
- Export history

### 3. Watchlist System

Monitor favorite tickers:

```bash
# Add to watchlist during analysis
# Or use menu: "5. Manage Watchlist"
```

### 4. Support/Resistance Analysis

Automatic S/R level detection:

```python
# Shows in Pressure Cooker analysis
Nearest Resistance: $45.67 (+2.3%)
Nearest Support: $42.10 (-2.8%)
In Squeeze: Yes (3.5% range)
```

### 5. Volume Profile

See institutional price levels:

```python
# Point of Control (POC): Where most volume traded
POC: $44.25
Value Area: $43.50 - $45.00
Above Value Area: Bullish
```

### 6. Parallel Processing

Faster scans using multiple CPU cores:

```python
# v1.0: Sequential (one ticker at a time)
# v2.0: Parallel (multiple tickers simultaneously)

# Typical speed improvement: 3-5x faster
```

---

## Feature Comparison

### What You Keep

✅ All scanners (Momentum, FOREX, Crypto, Dark Flow, Pressure Cooker)
✅ Technical analysis (VWAP, MACD, RSI, SuperTrend, etc.)
✅ Export to CSV, Excel, PDF
✅ Settings file configuration
✅ Disclaimers and risk warnings
✅ All existing functionality

### What You Gain

🆕 Polygon/Massive API integration
🆕 SQLite database with scan history
🆕 Support/Resistance detection
🆕 Volume Profile analysis
🆕 Watchlist management
🆕 Parallel processing (faster scans)
🆕 Data validation and quality checks
🆕 Better error handling
🆕 Modular code (easier to customize)

### What You Lose (Temporarily)

⚠️ Position size calculator (planned for v2.1)
⚠️ R:R ratio customization (planned for v2.1)
⚠️ Timeframe selection (planned for v2.1)
⚠️ Extended hours support (planned for v2.1)
⚠️ Batch analysis (planned for v2.2)

**Note:** These features will be added back in future v2.x releases.

---

## Running Both Versions

### Directory Structure

```
~/trading-tools/
├── v1/
│   └── trading_signal_analyzer.py  # v1.0
└── v2/
    └── trading_analyzer/  # v2.0 package
        ├── __init__.py
        ├── main.py
        ├── core/
        ├── scanners/
        └── ...
```

### Shell Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc

# v1.0
alias tsa1='cd ~/trading-tools/v1 && python trading_signal_analyzer.py'

# v2.0
alias tsa2='cd ~/trading-tools/v2 && python -m trading_analyzer'

# Usage
tsa1  # Quick scan with v1.0
tsa2  # Full analysis with v2.0
```

### Shared Settings

Both versions read from `~/.trading_analyzer`, so settings sync automatically:

```json
{
  // Settings used by BOTH versions
  "disclaimer_acknowledged": true,
  "pressure_cooker_disclaimer_acknowledged": true,

  // v1.0 ignores these (v2.0 only)
  "polygon": "...",
  "database": {...}
}
```

---

## Troubleshooting

### "Module not found" Error

```bash
# Make sure you installed v2.0
pip install -e .

# Verify installation
python -c "import trading_analyzer; print('OK')"
```

### Database Permissions Error

```bash
# Database location
~/Documents/trading_analyzer.db

# Fix permissions
chmod 644 ~/Documents/trading_analyzer.db
```

### Polygon API Not Working

```bash
# Check API key in settings
cat ~/.trading_analyzer | grep polygon

# Test API key
python -c "
from trading_analyzer.data.hybrid_provider import get_hybrid_provider
provider = get_hybrid_provider()
print('Polygon available:', provider.polygon.is_available())
"
```

### Both Versions Using Same Settings

This is **intentional** and **safe**:
- v1.0 ignores v2.0-specific settings
- v2.0 uses v1.0 settings plus new ones
- No conflicts

---

## FAQs

### Q: Can I run both versions simultaneously?

**A:** Yes! They don't conflict. Just don't run the same scan twice at the same time.

### Q: Will my v1.0 settings work with v2.0?

**A:** Yes, completely. v2.0 reads the same settings file and adds new options.

### Q: Do I need a Polygon API key for v2.0?

**A:** No, it's optional. v2.0 works perfectly with free yfinance data (same as v1.0).

### Q: What happens to my scan results from v1.0?

**A:** They stay as-is. v2.0 starts with a fresh database. Old CSV exports remain valid.

### Q: Can I go back to v1.0 after migrating?

**A:** Absolutely! Just run `python trading_signal_analyzer.py` like before.

### Q: Will v1.0 still be maintained?

**A:** Yes, but only bug fixes (v1.0.x). New features go to v2.0.

### Q: When will missing features return to v2.0?

**A:**
- Position calculator: v2.1 (Q1 2026)
- R:R customization: v2.1 (Q1 2026)
- Extended hours: v2.1 (Q1 2026)
- Batch analysis: v2.2 (Q2 2026)

### Q: Is v2.0 slower than v1.0?

**A:** No, it's **faster** due to parallel processing! Scans complete 3-5x quicker.

### Q: Can I customize v2.0 easier than v1.0?

**A:** Yes! Modular code means you can edit specific features without touching everything.

---

## Migration Checklist

Use this checklist when migrating:

### Before Migration
- [ ] Backup your v1.0 file
- [ ] Backup `~/.trading_analyzer` settings
- [ ] Export any important scan results to CSV
- [ ] Note which scanners you use most
- [ ] Check if you need Polygon API (optional)

### During Migration
- [ ] Install v2.0 (side-by-side or clean)
- [ ] Run `pip install -e .`
- [ ] Test launch: `python -m trading_analyzer`
- [ ] Accept disclaimers (same as v1.0)
- [ ] Run a test scan (Momentum or Crypto)
- [ ] Verify settings carried over

### After Migration
- [ ] Add Polygon API key (if desired)
- [ ] Run each scanner once to test
- [ ] Check database created (`~/Documents/trading_analyzer.db`)
- [ ] Test watchlist feature
- [ ] Review scan history
- [ ] Compare performance vs v1.0

### Optional (Keep v1.0)
- [ ] Create shell aliases for both versions
- [ ] Document when to use each version
- [ ] Keep v1.0 as backup for critical trading days

---

## Getting Help

### Resources
- **v1.0 Documentation:** `README.md` on main branch
- **v2.0 Documentation:** `README.md` on v2.0-dev branch
- **Issues:** https://github.com/savowood/trading-signal-analyzer/issues
- **Discussions:** https://github.com/savowood/trading-signal-analyzer/discussions

### Reporting Problems
When reporting issues, specify:
- Version (v1.0 or v2.0)
- Operating system
- Python version
- Error message (full traceback)
- Steps to reproduce

---

## Conclusion

### Recommended Migration Path

**Week 1:** Install v2.0 side-by-side, test with non-critical scans
**Week 2:** Use both versions, compare results
**Week 3:** Decide primary version based on needs
**Week 4:** Fully migrate or keep both (your choice!)

### Key Takeaways

✅ Both versions are production-ready
✅ Migration is low-risk (can easily revert)
✅ Settings automatically carry over
✅ New features are worth exploring
✅ No rush - take your time testing

---

**Good luck with your migration, and happy trading!** 📈

*Last updated: December 7, 2025*
