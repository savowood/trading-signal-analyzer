# Trading Signal Analyzer v0.93 - Dark Flow Scanner Integration Instructions

## Overview

These instructions will guide you through updating trading_signal_analyzer.py to include the Enhanced Dark Flow Scanner with market-wide scanning capability.

---

## Step 1: Replace Dark Flow Scanner Class

**Location:** Find the `DarkFlowScanner` class (around line 1100-1250 in original v0.93)

**Action:** Replace the entire `DarkFlowScanner` class with the enhanced version below:

```python
class DarkFlowScanner:
    """
    Enhanced Dark Flow Scanner - Detects institutional dark pool activity using volume profile
    Now includes market-wide scanning capability
    """
    
    def __init__(self):
        self.major_etfs = ['SPY', 'QQQ', 'IWM', 'DIA']
    
    def scan_market_for_dark_flow(self, market_choice: str = '1', min_price: float = 5.0, 
                                   max_price: float = 100.0, min_volume: float = 1_000_000) -> List[Dict]:
        """
        Scan entire market for stocks with Dark Flow signals
        
        Looks for:
        - Volume clusters near current price (institutional levels)
        - Unusual volume spikes (smart money entry)
        - Price consolidation near institutional levels
        - Gaps being filled by institutional buying
        
        Args:
            market_choice: Market selection ('1' for US, '3' NASDAQ, '4' NYSE)
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_volume: Minimum average daily volume
            
        Returns:
            List of stocks with Dark Flow signals ranked by strength
        """
        if not TRADINGVIEW_AVAILABLE:
            print("❌ TradingView screener not available")
            return []
        
        try:
            print("🌊 Scanning market for Dark Flow signals...")
            print(f"   Filters: ${min_price:.2f}-${max_price:.2f}, {min_volume:,.0f}+ avg volume")
            
            # Build query
            q = Query()
            
            if market_choice == '3':
                q = q.set_markets('america').where(col('exchange') == 'NASDAQ')
            elif market_choice == '4':
                q = q.set_markets('america').where(col('exchange') == 'NYSE')
            else:
                q = q.set_markets('america')
            
            # Apply filters
            q = q.where(col('close').between(min_price, max_price))
            q = q.where(col('volume') >= min_volume)
            q = q.where(col('change').between(-5, 15))  # Not too extended
            
            # Select fields
            q = q.select(
                'name', 'close', 'volume', 'change', 'change_from_open',
                'Perf.W', 'Perf.1M', 'relative_volume_10d_calc',
                'average_volume_10d_calc', 'high', 'low', 'open'
            ).order_by('volume', ascending=False).limit(100)
            
            # Execute
            count, df = q.get_scanner_data()
            
            if df is None or df.empty:
                print("⚠️  No stocks found matching criteria")
                return []
            
            print(f"   Analyzing {len(df)} candidates for Dark Flow signals...")
            
            results = []
            
            for _, row in df.iterrows():
                try:
                    ticker = row['name']
                    
                    # Quick pre-filter
                    rel_vol = float(row.get('relative_volume_10d_calc') or 0)
                    if rel_vol < 1.5:  # Need at least 1.5x volume
                        continue
                    
                    # Analyze for Dark Flow signals
                    analysis = self.analyze_institutional_levels(ticker, period="5d")
                    
                    if not analysis:
                        continue
                    
                    # Score the Dark Flow signals
                    score = self._calculate_dark_flow_score(analysis, row)
                    
                    if score >= 50:  # Minimum score threshold
                        results.append({
                            'Ticker': ticker,
                            'Price': analysis['current_price'],
                            'Score': score,
                            'Bias': analysis['bias'],
                            'KeyLevels': len(analysis['key_levels']),
                            'UnusualVol': len(analysis['unusual_volume']),
                            'Signals': len(analysis['signals']),
                            'RelVol': rel_vol,
                            'Change%': float(row.get('change') or 0),
                            'Analysis': analysis  # Store full analysis
                        })
                    
                except Exception as e:
                    continue
            
            # Sort by Dark Flow score
            results.sort(key=lambda x: x['Score'], reverse=True)
            
            print(f"✅ Found {len(results)} stocks with Dark Flow signals")
            return results
            
        except Exception as e:
            print(f"❌ Dark Flow scan error: {e}")
            return []
    
    def _calculate_dark_flow_score(self, analysis: Dict, row: pd.Series) -> float:
        """
        Calculate Dark Flow signal strength score (0-100)
        
        Scoring criteria:
        - Active volume clusters (near current price): +30 points
        - Unusual volume events: +20 points
        - Bullish bias with consolidation: +20 points
        - Key levels above/below price (squeeze setup): +15 points
        - Gap filling by institutions: +15 points
        """
        score = 0.0
        current_price = analysis['current_price']
        
        # 1. Active volume clusters
        active_clusters = [s for s in analysis['signals'] if s['type'] == 'VOLUME_CLUSTER']
        if active_clusters:
            score += 30
        elif analysis['key_levels']:
            closest_level = min(analysis['key_levels'], key=lambda x: abs(x - current_price))
            distance_pct = abs(closest_level - current_price) / current_price
            if distance_pct < 0.02:
                score += 20
        
        # 2. Unusual volume
        unusual_vol_count = len(analysis['unusual_volume'])
        if unusual_vol_count >= 3:
            score += 20
        elif unusual_vol_count >= 1:
            score += 10
        
        # 3. Bullish consolidation
        if analysis['bias'] == 'BULLISH':
            today_range = analysis['today_high'] - analysis['today_low']
            range_pct = today_range / current_price
            if range_pct < 0.03:
                score += 20
            elif range_pct < 0.05:
                score += 10
        
        # 4. Squeeze setup
        if len(analysis['key_levels']) >= 3:
            levels_above = [l for l in analysis['key_levels'] if l > current_price]
            levels_below = [l for l in analysis['key_levels'] if l < current_price]
            
            if levels_above and levels_below:
                nearest_resistance = min(levels_above)
                nearest_support = max(levels_below)
                squeeze_range = nearest_resistance - nearest_support
                squeeze_pct = squeeze_range / current_price
                
                if squeeze_pct < 0.05:
                    score += 15
                elif squeeze_pct < 0.10:
                    score += 8
        
        # 5. Gap filling
        if analysis['gaps']:
            recent_gap = analysis['gaps'][-1]
            gap_direction = recent_gap['direction']
            
            if gap_direction == 'DOWN' and analysis['bias'] == 'BULLISH':
                score += 15
            elif gap_direction == 'UP' and analysis['bias'] == 'BULLISH':
                score += 8
        
        return min(score, 100)
        
    def analyze_institutional_levels(self, ticker: str, period: str = "5d") -> Optional[Dict]:
        """Analyze volume profile to detect institutional activity levels"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval="1h")
            
            if df.empty or len(df) < 10:
                return None
            
            current_price = df['Close'].iloc[-1]
            today_open = df['Open'].iloc[-5] if len(df) >= 5 else df['Open'].iloc[0]
            today_high = df['High'].tail(24).max() if len(df) >= 24 else df['High'].max()
            today_low = df['Low'].tail(24).min() if len(df) >= 24 else df['Low'].min()
            
            # Create volume profile
            volume_profile = self._create_volume_profile(df)
            key_levels = self._find_key_levels(volume_profile, current_price)
            
            # Detect signals
            signals = []
            for level in key_levels[:3]:
                if abs(current_price - level) / current_price < 0.005:
                    signals.append({
                        'type': 'VOLUME_CLUSTER',
                        'level': level,
                        'distance': ((level - current_price) / current_price) * 100
                    })
            
            unusual_volume = self._detect_unusual_volume(df)
            gaps = self._detect_gaps(df)
            
            bias = "BULLISH" if current_price > today_open else "BEARISH"
            bias_emoji = "🟢" if bias == "BULLISH" else "🔴"
            
            return {
                'ticker': ticker,
                'current_price': current_price,
                'today_open': today_open,
                'today_high': today_high,
                'today_low': today_low,
                'bias': bias,
                'bias_emoji': bias_emoji,
                'key_levels': key_levels[:5],
                'signals': signals,
                'unusual_volume': unusual_volume,
                'gaps': gaps,
                'is_major_etf': ticker in self.major_etfs
            }
        except Exception as e:
            return None
    
    def _create_volume_profile(self, df: pd.DataFrame, bins: int = 20) -> pd.DataFrame:
        """Create volume profile"""
        price_range = df['Close'].max() - df['Close'].min()
        if price_range == 0:
            return pd.DataFrame()
        
        bin_size = price_range / bins
        df['price_bin'] = ((df['Close'] - df['Close'].min()) / bin_size).astype(int)
        
        volume_profile = df.groupby('price_bin').agg({
            'Volume': 'sum',
            'Close': 'mean'
        }).reset_index()
        
        volume_profile.columns = ['bin', 'volume', 'price']
        volume_profile = volume_profile.sort_values('volume', ascending=False)
        
        return volume_profile
    
    def _find_key_levels(self, volume_profile: pd.DataFrame, current_price: float) -> List[float]:
        """Find key price levels"""
        if volume_profile.empty:
            return []
        top_levels = volume_profile.head(10)['price'].tolist()
        top_levels.sort(key=lambda x: abs(x - current_price))
        return top_levels
    
    def _detect_unusual_volume(self, df: pd.DataFrame) -> List[Dict]:
        """Detect unusual volume"""
        avg_volume = df['Volume'].mean()
        std_volume = df['Volume'].std()
        
        unusual = []
        for idx, row in df.iterrows():
            if row['Volume'] > avg_volume + (2 * std_volume):
                unusual.append({
                    'time': idx,
                    'price': row['Close'],
                    'volume': row['Volume'],
                    'ratio': row['Volume'] / avg_volume
                })
        
        return unusual[-5:] if len(unusual) > 5 else unusual
    
    def _detect_gaps(self, df: pd.DataFrame) -> List[Dict]:
        """Detect price gaps"""
        gaps = []
        for i in range(1, len(df)):
            prev_close = df['Close'].iloc[i-1]
            curr_open = df['Open'].iloc[i]
            gap_pct = abs(curr_open - prev_close) / prev_close
            
            if gap_pct > 0.01:
                gaps.append({
                    'time': df.index[i],
                    'gap_from': prev_close,
                    'gap_to': curr_open,
                    'gap_pct': gap_pct * 100,
                    'direction': 'UP' if curr_open > prev_close else 'DOWN'
                })
        
        return gaps
```

---

## Step 2: Add Dark Flow Scan Results Display Function

**Location:** After the `display_dark_flow_analysis()` function

**Action:** Add this new function:

```python
def display_dark_flow_scan_results(results: List[Dict]):
    """Display Dark Flow market scan results"""
    print("\n" + "=" * 100)
    print("🌊 DARK FLOW SCANNER - MARKET-WIDE RESULTS")
    print("=" * 100)
    print("\nStocks with institutional accumulation patterns:")
    print("=" * 100)
    
    if not results:
        print("No Dark Flow signals found")
        return
    
    print(f"\n{'#':<4} {'Ticker':<8} {'Price':<10} {'Score':<7} {'Bias':<10} "
          f"{'Signals':<9} {'RelVol':<8} {'Change%':<9}")
    print("-" * 100)
    
    for idx, stock in enumerate(results, 1):
        bias_emoji = "🟢" if stock['Bias'] == "BULLISH" else "🔴"
        
        # Score emoji
        if stock['Score'] >= 80:
            score_emoji = "🔥🔥🔥"
        elif stock['Score'] >= 60:
            score_emoji = "🔥🔥"
        else:
            score_emoji = "🔥"
        
        price_str = f"${stock['Price']:.2f}"
        
        print(f"{idx:<4} {stock['Ticker']:<8} {price_str:<10} "
              f"{stock['Score']}/100 {score_emoji:<4} {bias_emoji} {stock['Bias']:<8} "
              f"{stock['Signals']:<9} {stock['RelVol']:<7.1f}x {stock['Change%']:>+7.2f}%")
    
    print("-" * 100)
    print("\n🔥 Score: 80+ = STRONG | 60-79 = MODERATE | 50-59 = WEAK")
    print("💡 Signals = Volume clusters + Unusual volume + Gaps")
    print("🌊 Dark Flow indicates institutional accumulation/distribution")
    print("=" * 100)
```

---

## Step 3: Update Main Menu - Option 4

**Location:** In the `main()` function, find the Dark Flow Scanner option (Option 4)

**Action:** Replace the entire Option 4 block with:

```python
        # Dark Flow Scanner
        elif main_choice == '4':
            print("\n" + "=" * 70)
            print("🌊 DARK FLOW SCANNER")
            print("=" * 70)
            print("\nDetect institutional accumulation patterns")
            print("\nOptions:")
            print("1. Scan major ETFs (SPY, QQQ, IWM, DIA)")
            print("2. Scan market for Dark Flow signals")  # NEW OPTION
            print("3. Enter ticker(s) manually")
            
            df_choice = input("\nEnter choice (1-3): ").strip()
            
            if df_choice == '2':
                # NEW FEATURE: Market-wide Dark Flow scan
                print("\nSelect market:")
                print("1. US Stocks (NASDAQ + NYSE) - RECOMMENDED")
                print("2. NASDAQ only")
                print("3. NYSE only")
                market_choice = input("Enter choice (1-3): ").strip()
                
                if market_choice == '2':
                    market = '3'
                elif market_choice == '3':
                    market = '4'
                else:
                    market = '1'
                
                # Price range
                print("\nPrice range (default $5-$100):")
                min_input = input("Min price (or Enter for $5): ").strip()
                max_input = input("Max price (or Enter for $100): ").strip()
                
                min_price = float(min_input) if min_input else 5.0
                max_price = float(max_input) if max_input else 100.0
                
                # Create scanner and scan market
                dark_flow = DarkFlowScanner()
                results = dark_flow.scan_market_for_dark_flow(market, min_price, max_price)
                
                if results:
                    # Store for later use
                    last_scanned_dark_flow = results
                    last_scan_type = "dark_flow"
                    
                    display_dark_flow_scan_results(results)
                    
                    # Let user select stocks for detailed analysis
                    print("\n📋 SELECT STOCKS FOR DETAILED ANALYSIS")
                    print("Enter numbers (e.g., 1,2,3) or 'all' or 'skip':")
                    selection = input("Your selection: ").strip().lower()
                    
                    if selection and selection != 'skip':
                        if selection == 'all':
                            selected = results
                        else:
                            try:
                                indices = [int(x.strip()) for x in selection.split(',')]
                                selected = [results[i-1] for i in indices if 1 <= i <= len(results)]
                            except:
                                selected = []
                        
                        # Show detailed analysis for selected stocks
                        for stock in selected:
                            display_dark_flow_analysis(stock['Analysis'])
                            
                            # Ask if user wants VWAP/MACD analysis
                            analyze_choice = input(f"\nAnalyze {stock['Ticker']} with VWAP/MACD? (y/n): ").strip().lower()
                            if analyze_choice == 'y':
                                rec = analyzer.generate_recommendation(stock['Ticker'], period, interval)
                                if rec:
                                    display_recommendation(rec)
                            
                            if stock != selected[-1]:
                                input("\nPress Enter to continue...")
                
                input("\n📊 Press Enter to return to main menu...")
                continue
            
            elif df_choice == '1':
                # Original: Scan major ETFs
                tickers_to_scan = ['SPY', 'QQQ', 'IWM', 'DIA']
            else:
                # Original: Manual entry
                ticker_input = input("\nEnter ticker(s) separated by commas: ").strip()
                tickers_to_scan = [t.strip().upper() for t in ticker_input.split(',') if t.strip()]
            
            if not tickers_to_scan:
                print("❌ No tickers provided")
                input("\nPress Enter to continue...")
                continue
            
            # Create scanner and analyze tickers (original functionality)
            dark_flow = DarkFlowScanner()
            
            for ticker in tickers_to_scan:
                analysis = dark_flow.analyze_institutional_levels(ticker, period="5d")
                if analysis:
                    display_dark_flow_analysis(analysis)
                    
                    # Ask if user wants to analyze this ticker with VWAP/MACD
                    if len(tickers_to_scan) > 1:
                        analyze_choice = input(f"\nAnalyze {ticker} with VWAP/MACD? (y/n): ").strip().lower()
                        if analyze_choice == 'y':
                            rec = analyzer.generate_recommendation(ticker, period, interval)
                            if rec:
                                display_recommendation(rec)
                    else:
                        analyze_choice = input(f"\nAnalyze {ticker} with VWAP/MACD? (y/n): ").strip().lower()
                        if analyze_choice == 'y':
                            rec = analyzer.generate_recommendation(ticker, period, interval)
                            if rec:
                                display_recommendation(rec)
                
                if len(tickers_to_scan) > 1 and ticker != tickers_to_scan[-1]:
                    input("\nPress Enter to continue to next ticker...")
            
            input("\n📊 Press Enter to return to main menu...")
            continue
```

---

## Step 4: Update Session Variables

**Location:** In `main()` function, where session variables are initialized

**Action:** Add these variables after `last_scanned_crypto`:

```python
    # Store last scan results
    last_scanned_stocks = []
    last_scanned_forex = []
    last_scanned_crypto = []
    last_scanned_dark_flow = []  # NEW
    last_scan_type = None
```

---

## Step 5: Update Option 5 (Analyze from Last Scan)

**Location:** In `main()` function, Option 5 block

**Action:** Add Dark Flow handling:

```python
        # Analyze from last scan
        elif main_choice == '5':
            if not last_scan_type:
                print("\n❌ No previous scan results. Run a scan first (options 1-4)")
                input("\nPress Enter to continue...")
                continue
            
            # Show previous results based on scan type
            if last_scan_type == "stocks":
                display_scanned_stocks(last_scanned_stocks)
                tickers = choose_from_scan(last_scanned_stocks, "stocks")
            elif last_scan_type == "forex":
                display_forex_pairs(last_scanned_forex)
                tickers = choose_from_scan(last_scanned_forex, "FOREX pairs")
            elif last_scan_type == "crypto":
                display_crypto(last_scanned_crypto)
                tickers = choose_from_scan(last_scanned_crypto, "cryptocurrencies")
            elif last_scan_type == "dark_flow":  # NEW
                display_dark_flow_scan_results(last_scanned_dark_flow)
                
                print("\n📋 SELECT STOCKS FOR ANALYSIS")
                print("Enter numbers (e.g., 1,2,3) or 'all' or 'skip':")
                selection = input("Your selection: ").strip().lower()
                
                if selection == 'all':
                    tickers = [s['Ticker'] for s in last_scanned_dark_flow]
                elif selection != 'skip':
                    try:
                        indices = [int(x.strip()) for x in selection.split(',')]
                        tickers = [last_scanned_dark_flow[i-1]['Ticker'] for i in indices 
                                 if 1 <= i <= len(last_scanned_dark_flow)]
                    except:
                        tickers = []
                else:
                    tickers = []
            
            if not tickers:
                print("❌ No items selected")
                input("\nPress Enter to continue...")
                continue
```

---

## Step 6: Update Main Menu Display

**Location:** Main menu print statements

**Action:** Update menu to show Dark Flow can scan:

```python
        print("\n1. Run Momentum Scanner (stocks)")
        print("2. Scan FOREX pairs (top 10)")
        print("3. Scan Cryptocurrencies (top 20)")
        print("4. Dark Flow Scanner (institutional levels + market scan)")  # UPDATED
        print("5. Analyze from last scan results")
        print("6. Enter ticker manually")
        print("7. Change risk/reward ratio")
        print("8. Change timeframe")
        print("9. Quit")
```

---

## Testing Checklist

After making these changes, test:

- [ ] Option 4, Choice 1: Scan major ETFs (original functionality)
- [ ] Option 4, Choice 2: Market scan for Dark Flow (NEW functionality)
- [ ] Option 4, Choice 3: Manual ticker entry (original functionality)
- [ ] Market scan returns results with scores
- [ ] Can select stocks for detailed analysis
- [ ] Detailed analysis shows volume clusters, gaps, etc.
- [ ] Can run VWAP/MACD analysis on selected stocks
- [ ] Option 5 works with Dark Flow scan results
- [ ] No errors or crashes

---

## Summary of Changes

### Added:
1. `scan_market_for_dark_flow()` method to DarkFlowScanner class
2. `_calculate_dark_flow_score()` method for scoring (0-100)
3. `display_dark_flow_scan_results()` function for displaying market scan
4. Market scanning option in Dark Flow menu (Option 4, Choice 2)
5. Session variable for Dark Flow scan results
6. Dark Flow handling in "Analyze from last scan" option

### Modified:
1. DarkFlowScanner class - enhanced with scoring
2. Option 4 menu - added market scanning choice
3. Option 5 - added Dark Flow results handling
4. Main menu description for Option 4

### Result:
Dark Flow Scanner can now:
- ✅ Scan entire market for institutional patterns
- ✅ Score and rank stocks by Dark Flow strength (0-100)
- ✅ Provide actionable watchlist
- ✅ Allow detailed analysis of selected stocks
- ✅ Integrate with existing VWAP/MACD analysis

---

## File Locations

After updating, you should have:
- `trading_signal_analyzer.py` - Updated main file
- `README.md` - Already updated with Dark Flow docs
- `CHANGELOG.md` - Should add v0.93 Dark Flow enhancement notes

---

## Next Steps

1. Make the code changes above
2. Test all functionality
3. Update CHANGELOG.md with Dark Flow market scanning feature
4. Update version history if needed
5. Deploy and use!

---

**Enhancement Complete! The Dark Flow Scanner is now a true market scanner! 🌊**
