# Enhanced Dark Flow Scanner - Integration Guide

## Overview

The Enhanced Dark Flow Scanner adds **market-wide scanning capability** to find stocks with institutional accumulation patterns, not just analyze individual tickers.

---

## What's New

### Before (v0.93):
- ❌ Only analyzed tickers you manually entered
- ❌ No market scanning for Dark Flow signals
- ❌ Had to guess which stocks had institutional activity

### After (Enhanced):
- ✅ **Scans entire market** for Dark Flow signals
- ✅ **Ranks stocks** by institutional accumulation strength (0-100 score)
- ✅ **Filters for breakout candidates** with volume clusters and unusual activity
- ✅ Provides **list of actionable stocks** ready for detailed analysis

---

## New Features

### 1. Market-Wide Dark Flow Scanning

Scans 100+ stocks and scores them based on:

**Scoring System (0-100 points):**
- **Active volume clusters** (institutions at current price): +30 points
- **Unusual volume events** (smart money entry): +20 points  
- **Bullish bias + consolidation** (coiling for breakout): +20 points
- **Key levels creating squeeze**: +15 points
- **Gap filling patterns** (accumulation): +15 points

**Score Interpretation:**
- 80-100: 🔥🔥🔥 STRONG - High probability institutional setup
- 60-79: 🔥🔥 MODERATE - Good institutional interest
- 50-59: 🔥 WEAK - Some institutional activity

### 2. Intelligent Filtering

Pre-filters stocks before deep analysis:
- Price range: $5-$100 (configurable)
- Minimum volume: 1M+ average daily
- Relative volume: 1.5x+ average
- Price change: -5% to +15% (not overextended)

### 3. Detailed Signal Breakdown

For each stock found:
- **Dark Flow Score**: Overall strength (0-100)
- **Bias**: Bullish/Bearish based on price vs. open
- **Signals**: Count of volume clusters + unusual volume + gaps
- **RelVol**: Current volume vs. average
- **Change%**: Today's price change

---

## How It Works

### Step 1: Market Scan
```python
scanner.scan_market_for_dark_flow(
    market_choice='1',    # US stocks
    min_price=5.0,        # $5 minimum
    max_price=100.0,      # $100 maximum
    min_volume=1_000_000  # 1M+ avg volume
)
```

### Step 2: Volume Profile Analysis
For each candidate stock:
1. Downloads 5 days of hourly data
2. Creates 20-bin volume profile
3. Identifies key price levels with highest volume
4. Detects unusual volume spikes (2+ std dev)
5. Finds price gaps being filled

### Step 3: Dark Flow Scoring
Calculates 0-100 score based on:
- **Volume clusters near current price** → Institutions active HERE
- **Unusual volume** → Smart money entering
- **Tight consolidation** → Coiling for move
- **Levels above/below** → Squeeze setup
- **Gap patterns** → Institutional filling

### Step 4: Ranking & Display
- Sorts by Dark Flow score (highest first)
- Shows top candidates in formatted table
- Allows selection for detailed analysis

---

## Integration into Main App

### Option A: Replace Existing Dark Flow Scanner

In `trading_signal_analyzer.py`, replace the `DarkFlowScanner` class with `EnhancedDarkFlowScanner` and update Option 4 menu:

```python
elif main_choice == '4':
    print("\n" + "=" * 70)
    print("🌊 DARK FLOW SCANNER")
    print("=" * 70)
    print("\nDetect institutional accumulation patterns")
    print("\nOptions:")
    print("1. Scan major ETFs (SPY, QQQ, IWM, DIA)")
    print("2. Scan market for Dark Flow signals")  # NEW
    print("3. Enter ticker(s) manually")
    
    df_choice = input("\nEnter choice (1-3): ").strip()
    
    if df_choice == '2':
        # NEW: Market-wide scan
        # [Add market scanning logic here]
```

### Option B: Add as Separate Feature

Add new menu option (Option 5) to keep both scanners:

```python
print("\n4. Dark Flow Scanner (institutional levels)")
print("5. Dark Flow Market Scan (find breakout stocks)")  # NEW
print("6. Analyze from last scan results")
# etc...
```

---

## Usage Example

### Running Market Scan:

```
🌊 DARK FLOW SCANNER
════════════════════════════════════════════════════════════════════════════════

Detect institutional accumulation patterns

Options:
1. Scan major ETFs (SPY, QQQ, IWM, DIA)
2. Scan market for Dark Flow signals
3. Enter ticker(s) manually

Enter choice (1-3): 2

Select market:
1. US Stocks (NASDAQ + NYSE) - RECOMMENDED
2. NASDAQ only
3. NYSE only
Enter choice (1-3): 1

Price range (default $5-$100):
Min price (or Enter for $5): 10
Max price (or Enter for $100): 50

🌊 Scanning market for Dark Flow signals...
   Filters: $10.00-$50.00, 1,000,000+ avg volume
   Analyzing 100 candidates for Dark Flow signals...
✅ Found 12 stocks with Dark Flow signals
```

### Results Display:

```
🌊 DARK FLOW SCANNER - MARKET-WIDE RESULTS
════════════════════════════════════════════════════════════════════════════════

Stocks with institutional accumulation patterns:
════════════════════════════════════════════════════════════════════════════════

#    Ticker   Price      Score   Bias        Signals   RelVol   Change%
────────────────────────────────────────────────────────────────────────────────
1    XYZ      $28.45     85/100 🔥🔥🔥  🟢 BULLISH   5         3.2x     +2.34%
2    ABC      $15.67     78/100 🔥🔥   🟢 BULLISH   4         2.8x     +1.87%
3    DEF      $42.30     72/100 🔥🔥   🟢 BULLISH   3         2.1x     +0.54%
4    GHI      $19.85     68/100 🔥🔥   🟢 BULLISH   4         2.5x     +1.23%
5    JKL      $33.21     61/100 🔥🔥   🟢 BULLISH   2         1.9x     -0.42%
────────────────────────────────────────────────────────────────────────────────

🔥 Score: 80+ = STRONG | 60-79 = MODERATE | 50-59 = WEAK
💡 Signals = Volume clusters + Unusual volume + Gaps
🌊 Dark Flow indicates institutional accumulation/distribution
════════════════════════════════════════════════════════════════════════════════

📋 SELECT STOCKS FOR DETAILED ANALYSIS
Enter numbers (e.g., 1,2,3) or 'all' or 'skip':
Your selection: 1,2

[Shows detailed Dark Flow analysis for XYZ and ABC...]
```

---

## Technical Details

### Volume Profile Algorithm

```python
def _create_volume_profile(df, bins=20):
    """
    Divides price range into 20 bins
    Aggregates volume at each price level
    Identifies where institutions traded most
    """
    price_range = df['Close'].max() - df['Close'].min()
    bin_size = price_range / bins
    
    # Group by price bin, sum volume
    volume_profile = df.groupby('price_bin').agg({
        'Volume': 'sum',
        'Close': 'mean'
    })
    
    # Sort by volume (highest = institutional levels)
    return volume_profile.sort_values('volume', ascending=False)
```

### Dark Flow Score Calculation

```python
def _calculate_dark_flow_score(analysis, row):
    """
    Scores institutional activity strength
    
    Returns 0-100 score based on:
    - Volume clusters at current price (30 pts)
    - Unusual volume events (20 pts)
    - Bullish consolidation (20 pts)
    - Squeeze setup (15 pts)
    - Gap filling (15 pts)
    """
    score = 0
    
    # Active clusters (within 0.5% of price)
    if has_active_volume_clusters:
        score += 30
    
    # Unusual volume (2+ std dev spikes)
    if unusual_volume_count >= 3:
        score += 20
    
    # Consolidation (tight range)
    if is_consolidating:
        score += 20
    
    # Squeeze (levels above and below)
    if has_squeeze_setup:
        score += 15
    
    # Gap filling
    if filling_gap_bullishly:
        score += 15
    
    return min(score, 100)
```

---

## What This Finds

### Example: Strong Dark Flow Signal (Score 85/100)

**Ticker: XYZ at $28.45**

**Why Score is High:**
1. ✅ **Volume cluster at $28.50** (+30) - Institutions active RIGHT HERE
2. ✅ **3 unusual volume spikes** (+20) - Smart money entering
3. ✅ **Tight 2% range, bullish** (+20) - Consolidating for breakout
4. ✅ **Resistance at $29, support at $28** (+15) - Squeeze setup
5. ✅ **Filled gap from $27.50** (+15) - Institutions bought the dip

**What This Means:**
- Institutions are accumulating at current level
- Price consolidating tightly = energy building
- Volume confirms smart money interest
- Setup for potential breakout above $29

**Trading Strategy:**
- Entry: Near $28.50 (institutional level)
- Stop: Below $27.80 (support level)
- Target: $30.50+ (breakout above resistance)
- Risk/Reward: 3:1+

---

## Advantages Over Manual Analysis

### Without Dark Flow Scanner:
1. Check 100+ stocks manually ❌
2. Calculate volume profiles by hand ❌
3. Guess where institutions are active ❌
4. Miss unusual volume events ❌
5. No systematic scoring ❌

### With Enhanced Dark Flow Scanner:
1. Scans 100+ stocks automatically ✅
2. Calculates volume profiles ✅
3. Identifies institutional levels ✅
4. Detects unusual volume ✅
5. Ranks by setup quality ✅

**Time Saved:** Hours → Minutes

---

## Best Practices

### 1. Price Range Selection
- **$10-$50**: Best liquidity + institutional interest
- **$5-$20**: More volatility, penny-ish stocks
- **$50-$100**: Lower volatility, bigger caps

### 2. Score Interpretation
- **80-100**: Primary watchlist (strong setups)
- **60-79**: Secondary watchlist (good setups)
- **50-59**: Monitor, needs confirmation

### 3. Combining with Other Scans
```python
# Example workflow:
1. Run Momentum Scanner (5 Pillars)
2. Run Dark Flow Scanner
3. Find overlaps → HIGHEST PROBABILITY

If stock appears in BOTH:
- Has momentum (5 Pillars)
- Has institutional backing (Dark Flow)
- = PRIME CANDIDATE
```

### 4. When to Use
- **Pre-market**: Scan for day's candidates
- **Mid-day**: Find stocks consolidating
- **After hours**: Plan tomorrow's trades
- **Weekly**: Find swing trade setups

---

## Files Included

1. **enhanced_dark_flow_scanner.py** - Main implementation
   - `EnhancedDarkFlowScanner` class
   - `scan_market_for_dark_flow()` method
   - Scoring algorithms
   - Display functions

2. **DARK_FLOW_INTEGRATION_GUIDE.md** (this file)
   - Integration instructions
   - Usage examples
   - Technical details

3. **updated_README.md**
   - Dark Flow documentation added
   - Feature descriptions
   - Example outputs

---

## Testing

### Quick Test:
```python
from enhanced_dark_flow_scanner import EnhancedDarkFlowScanner

scanner = EnhancedDarkFlowScanner()

# Scan US market, $10-$50 range
results = scanner.scan_market_for_dark_flow(
    market_choice='1',
    min_price=10.0,
    max_price=50.0
)

# Display results
from enhanced_dark_flow_scanner import display_dark_flow_scan_results
display_dark_flow_scan_results(results)
```

### Expected Output:
- List of 5-20 stocks with Dark Flow signals
- Scores ranging 50-100
- Mostly bullish bias stocks
- Mix of signals (clusters, volume, gaps)

---

## Future Enhancements

### Possible Additions:
- [ ] **Real-time alerts** when stocks hit Dark Flow levels
- [ ] **Historical backtesting** of Dark Flow signals
- [ ] **Sector clustering** (which sectors have most Dark Flow)
- [ ] **Dark Flow + 5 Pillars** combined scanner
- [ ] **Signature print detection** (specific institutional patterns)
- [ ] **Export to CSV** for spreadsheet analysis
- [ ] **Visualization** (volume profile charts)

---

## Troubleshooting

### "No Dark Flow signals found"
- Market may be quiet (low volume day)
- Try wider price range ($5-$100)
- Lower minimum volume threshold
- Try different market (NASDAQ vs NYSE)

### "Scanner too slow"
- Reduce scan limit from 100 to 50 stocks
- Narrow price range
- Increase minimum volume filter
- Scan only NASDAQ or NYSE, not both

### "Scores all low (50-60)"
- Normal on quiet market days
- Wait for higher volume days
- Check if market is trending (better signals in trends)
- Focus on top scores regardless of absolute value

---

## Summary

The Enhanced Dark Flow Scanner transforms the original single-ticker analysis tool into a **market-wide scanning system** that:

✅ Finds stocks with institutional accumulation
✅ Ranks them by Dark Flow signal strength  
✅ Provides actionable list of breakout candidates
✅ Saves hours of manual analysis time
✅ Increases probability of successful trades

**Result:** You now have a systematic way to find where "smart money" is accumulating positions, giving you an edge in identifying high-probability setups BEFORE they break out.

---

**Ready to find institutional accumulation patterns! 🌊**
