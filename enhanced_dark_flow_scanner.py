"""
Enhanced Dark Flow Scanner - Market-Wide Scanning for Institutional Accumulation

This module adds market scanning capability to find stocks with:
- Strong institutional accumulation (volume clusters near current price)
- Unusual volume activity indicating smart money entry
- Price action suggesting imminent breakouts
- Gap patterns that institutions are trading

Usage:
  Run Option 4 in main menu, then choose:
  1. Scan major ETFs (original functionality)
  2. Scan market for Dark Flow signals (NEW)
  3. Enter ticker(s) manually (original functionality)
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import yfinance as yf
from tradingview_screener import Query, col


class EnhancedDarkFlowScanner:
    """
    Enhanced Dark Flow Scanner with market scanning capability
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
        try:
            from tradingview_screener import Query, col
            
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
            
        except ImportError:
            print("❌ TradingView screener not available")
            return []
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
        
        Args:
            analysis: Dark Flow analysis dictionary
            row: Scanner row data
            
        Returns:
            Score from 0-100
        """
        score = 0.0
        
        current_price = analysis['current_price']
        
        # 1. Active volume clusters (institutions active at current level)
        active_clusters = [s for s in analysis['signals'] if s['type'] == 'VOLUME_CLUSTER']
        if active_clusters:
            score += 30
        elif analysis['key_levels']:
            # Check if any key level is within 2%
            closest_level = min(analysis['key_levels'], 
                              key=lambda x: abs(x - current_price))
            distance_pct = abs(closest_level - current_price) / current_price
            if distance_pct < 0.02:
                score += 20
        
        # 2. Unusual volume (smart money entry)
        unusual_vol_count = len(analysis['unusual_volume'])
        if unusual_vol_count >= 3:
            score += 20
        elif unusual_vol_count >= 1:
            score += 10
        
        # 3. Bullish bias with tight range (coiling for breakout)
        if analysis['bias'] == 'BULLISH':
            today_range = analysis['today_high'] - analysis['today_low']
            range_pct = today_range / current_price
            
            if range_pct < 0.03:  # Tight 3% range = consolidation
                score += 20
            elif range_pct < 0.05:  # Moderate 5% range
                score += 10
        
        # 4. Key institutional levels creating squeeze setup
        if len(analysis['key_levels']) >= 3:
            # Check if price is between levels (squeeze)
            levels_above = [l for l in analysis['key_levels'] if l > current_price]
            levels_below = [l for l in analysis['key_levels'] if l < current_price]
            
            if levels_above and levels_below:
                # Measure squeeze tightness
                nearest_resistance = min(levels_above)
                nearest_support = max(levels_below)
                squeeze_range = nearest_resistance - nearest_support
                squeeze_pct = squeeze_range / current_price
                
                if squeeze_pct < 0.05:  # Tight 5% squeeze
                    score += 15
                elif squeeze_pct < 0.10:  # Moderate 10% squeeze
                    score += 8
        
        # 5. Gap filling patterns (institutions accumulating)
        if analysis['gaps']:
            recent_gap = analysis['gaps'][-1]
            gap_direction = recent_gap['direction']
            
            # Bullish: Gap down being filled (buying dip)
            # Bearish gap being ignored is also bullish (strength)
            if gap_direction == 'DOWN' and analysis['bias'] == 'BULLISH':
                score += 15
            elif gap_direction == 'UP' and analysis['bias'] == 'BULLISH':
                score += 8  # Continuing strength
        
        return min(score, 100)  # Cap at 100
    
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


def display_dark_flow_analysis(analysis: Dict):
    """Display Dark Flow analysis for individual ticker"""
    print("\n" + "=" * 80)
    print(f"🌊 DARK FLOW ANALYSIS: {analysis['ticker']}")
    print("=" * 80)
    
    print(f"\n💰 CURRENT PRICE: ${analysis['current_price']:.2f}")
    print(f"📊 TODAY'S OPEN: ${analysis['today_open']:.2f}")
    print(f"📈 TODAY'S RANGE: ${analysis['today_low']:.2f} - ${analysis['today_high']:.2f}")
    print(f"\n{analysis['bias_emoji']} BIAS: {analysis['bias']}")
    
    if analysis['key_levels']:
        print(f"\n🎯 KEY INSTITUTIONAL LEVELS (Volume Clusters):")
        for i, level in enumerate(analysis['key_levels'][:5], 1):
            distance = ((level - analysis['current_price']) / analysis['current_price']) * 100
            if abs(distance) < 1:
                marker = "⭐ ACTIVE"
            elif distance > 0:
                marker = "⬆️  RESISTANCE"
            else:
                marker = "⬇️  SUPPORT"
            print(f"   {i}. ${level:.2f} ({distance:+.2f}%) {marker}")
    
    if analysis['signals']:
        print(f"\n🌊 DARK FLOW SIGNALS:")
        for signal in analysis['signals']:
            print(f"   • {signal['type']} at ${signal['level']:.2f}")
    
    if analysis['unusual_volume']:
        print(f"\n📊 UNUSUAL VOLUME ACTIVITY:")
        for uv in analysis['unusual_volume'][-3:]:
            print(f"   • {uv['time'].strftime('%Y-%m-%d %H:%M')}: ${uv['price']:.2f} - {uv['ratio']:.1f}x avg")
    
    if analysis['gaps']:
        print(f"\n⚡ PRICE GAPS:")
        for gap in analysis['gaps'][-3:]:
            print(f"   • {gap['direction']}: ${gap['gap_from']:.2f} → ${gap['gap_to']:.2f} ({gap['gap_pct']:.2f}%)")
    
    if analysis['is_major_etf']:
        print(f"\n⭐ MAJOR ETF - Prime candidate for signature prints")
    
    print("\n" + "=" * 80)
    print("💡 Volume clusters show institutional accumulation/distribution levels")
    print("=" * 80)


# Example integration into main menu
def enhanced_dark_flow_menu():
    """
    Enhanced Dark Flow Scanner menu with market scanning option
    
    Add this to Option 4 in the main menu
    """
    scanner = EnhancedDarkFlowScanner()
    
    print("\n" + "=" * 70)
    print("🌊 DARK FLOW SCANNER")
    print("=" * 70)
    print("\nDetect institutional accumulation patterns")
    print("\nOptions:")
    print("1. Scan major ETFs (SPY, QQQ, IWM, DIA)")
    print("2. Scan market for Dark Flow signals")
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
        
        # Scan market
        results = scanner.scan_market_for_dark_flow(market, min_price, max_price)
        
        if results:
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
                    input("\nPress Enter to continue...")
        
        return results
    
    elif df_choice == '1':
        # Original: Scan major ETFs
        tickers_to_scan = ['SPY', 'QQQ', 'IWM', 'DIA']
    else:
        # Original: Manual entry
        ticker_input = input("\nEnter ticker(s) separated by commas: ").strip()
        tickers_to_scan = [t.strip().upper() for t in ticker_input.split(',') if t.strip()]
    
    # Analyze tickers (original functionality)
    for ticker in tickers_to_scan:
        analysis = scanner.analyze_institutional_levels(ticker, period="5d")
        if analysis:
            display_dark_flow_analysis(analysis)
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    print("Enhanced Dark Flow Scanner - Demo")
    print("=" * 70)
    
    # Demo the market scanning feature
    scanner = EnhancedDarkFlowScanner()
    
    print("\n🌊 Scanning US market for Dark Flow signals...")
    results = scanner.scan_market_for_dark_flow('1', min_price=10.0, max_price=50.0)
    
    if results:
        display_dark_flow_scan_results(results)
        
        # Show detailed analysis for top result
        if results:
            print("\n📊 Detailed analysis for top candidate:")
            display_dark_flow_analysis(results[0]['Analysis'])
