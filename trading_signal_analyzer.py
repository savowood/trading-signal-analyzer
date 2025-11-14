"""
Trading Signal Analyzer v0.9 - Entry/Exit Point Prediction
Copyright (C) 2025 Michael Johnson (GitHub: @savowood)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

================================================================================
ATTRIBUTION & METHODOLOGY
================================================================================
This software implements Ross Cameron's "5 Pillars of Day Trading" methodology
for stock selection. The 5 Pillars are:
  1. Strong Relative Volume (2x+ average)
  2. Float under 100 million shares
  3. Price range $1-$20 (ideal for momentum)
  4. Recent news catalyst or earnings
  5. Chart pattern (breakout, consolidation)

Learn more about Ross Cameron's trading strategies at:
https://www.warriortrading.com/

Technical analysis (VWAP, MACD) implementation is original work.

================================================================================
FINANCIAL DISCLAIMER
================================================================================
This software is provided for EDUCATIONAL and INFORMATIONAL purposes only.

⚠️  IMPORTANT: Trading stocks, options, and other securities involves risk
and can result in substantial financial losses. Past performance is not
indicative of future results.

The information and analysis provided by this software should NOT be considered
as financial advice, investment advice, or trading advice. This software is
a tool to assist in technical analysis only.

Before making any trading decisions, you should:
  • Consult with a licensed financial advisor
  • Understand the risks involved in trading
  • Only trade with money you can afford to lose
  • Conduct your own due diligence and research

The author and contributors assume NO LIABILITY for any trading losses or
damages incurred through the use of this software. You alone are responsible
for your trading decisions and their consequences.

USE AT YOUR OWN RISK.
================================================================================

Version: 0.9
Uses VWAP bands (1σ, 2σ) + MACD for optimal entry/exit points
Includes integrated Ross Cameron 5 Pillars Scanner
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Version info
VERSION = "0.9"
AUTHOR = "Michael Johnson"
LICENSE = "GPL v3"

# Import TradingView screener
try:
    from tradingview_screener import Query, col
    TRADINGVIEW_AVAILABLE = True
except ImportError:
    TRADINGVIEW_AVAILABLE = False
    print("⚠️  TradingView screener not available. Install: pip install tradingview-screener")


def show_disclaimer():
    """Display legal and financial disclaimer"""
    print("\n" + "=" * 80)
    print("⚠️  LEGAL & FINANCIAL DISCLAIMER")
    print("=" * 80)
    print("""
This software is provided for EDUCATIONAL and INFORMATIONAL purposes only.

Trading stocks, options, and other securities involves SUBSTANTIAL RISK and can
result in SIGNIFICANT FINANCIAL LOSSES. Past performance is NOT indicative of
future results.

The information provided by this software is NOT financial advice, investment
advice, or trading advice. This is a technical analysis tool only.

Before trading, you should:
  ✓ Consult with a licensed financial advisor
  ✓ Understand the risks involved
  ✓ Only trade with money you can afford to lose
  ✓ Conduct your own research and due diligence

By using this software, you acknowledge that:
  • You are solely responsible for your trading decisions
  • The author assumes NO LIABILITY for any losses incurred
  • You understand the risks involved in trading
  • This is educational software, not professional advice

USE AT YOUR OWN RISK.
""")
    print("=" * 80)
    
    response = input("\nDo you understand and accept these terms? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ You must accept the terms to use this software.")
        print("Exiting...")
        exit(0)
    
    print("\n✅ Terms accepted. Proceeding...\n")


def scan_ross_cameron_stocks(market_choice: str = '1') -> List[Dict]:
    """
    Integrated Ross Cameron 5 Pillars Scanner
    
    Args:
        market_choice: Market selection ('1' for US, '3' NASDAQ, '4' NYSE)
        
    Returns:
        List of qualifying stocks with scores
    """
    if not TRADINGVIEW_AVAILABLE:
        print("❌ TradingView screener not installed")
        return []
    
    try:
        print("🔍 Scanning for Ross Cameron 5 Pillars setups...")
        
        # Build query
        q = Query()
        
        if market_choice == '3':
            q = q.set_markets('america').where(col('exchange') == 'NASDAQ')
        elif market_choice == '4':
            q = q.set_markets('america').where(col('exchange') == 'NYSE')
        else:
            q = q.set_markets('america')
        
        # Apply 5 pillars filters
        q = q.where(col('close').between(1, 20))  # Price range
        q = q.where(col('relative_volume_10d_calc') >= 2.0)  # Relative volume
        q = q.where(col('market_cap_basic') < 10_000_000_000)  # Market cap
        q = q.where(col('change_from_open').between(-50, 50))
        
        # Select fields
        q = q.select(
            'name', 'close', 'volume', 'relative_volume_10d_calc',
            'market_cap_basic', 'change', 'change_from_open',
            'Recommend.All', 'Perf.W', 'Perf.1M',
            'average_volume_10d_calc', 'exchange'
        ).order_by('relative_volume_10d_calc', ascending=False).limit(50)
        
        # Execute
        count, df = q.get_scanner_data()
        
        if df is None or df.empty:
            print("⚠️  No stocks found matching criteria")
            return []
        
        results = []
        for _, row in df.iterrows():
            try:
                ticker = row['name']
                price = float(row['close'])
                rel_vol = float(row.get('relative_volume_10d_calc') or 0)
                market_cap = row.get('market_cap_basic', 0) or 0
                change_pct = float(row.get('Perf.W') or 0)
                change_from_open = float(row.get('change_from_open') or 0)
                perf_1m = float(row.get('Perf.1M') or 0)
                
                # Estimate float
                if market_cap and price > 0:
                    float_m = (market_cap / price) / 1_000_000
                else:
                    float_m = 50
                
                # Pattern detection (simplified)
                near_breakout = perf_1m > 15
                consolidation = abs(change_from_open) < 1
                pattern_score = near_breakout or consolidation
                
                # Catalyst
                has_catalyst = abs(change_pct) > 10 or abs(change_from_open) > 2
                
                # Score pillars
                pillars_met = sum([
                    rel_vol >= 2.0,
                    float_m < 100,
                    True,  # Price already filtered
                    has_catalyst,
                    pattern_score
                ])
                
                if pillars_met >= 2:
                    results.append({
                        'Ticker': ticker,
                        'Price': price,
                        'RelVol': rel_vol,
                        'Float(M)': float_m,
                        'Score': pillars_met,
                        'Week%': change_pct,
                        'Today%': change_from_open,
                        'Catalyst': has_catalyst,
                        'Pattern': pattern_score
                    })
            except:
                continue
        
        # Sort by score and relative volume
        results.sort(key=lambda x: (x['Score'], x['RelVol']), reverse=True)
        
        print(f"✅ Found {len(results)} qualifying stocks")
        return results
        
    except Exception as e:
        print(f"❌ Scanner error: {e}")
        return []


def display_scanned_stocks(stocks: List[Dict]):
    """Display scanned stocks in a formatted table"""
    print("\n" + "=" * 80)
    print("🔥 ROSS CAMERON SCANNER RESULTS")
    print("=" * 80)
    
    if not stocks:
        print("No stocks found")
        return
    
    print(f"\n{'#':<4} {'Ticker':<8} {'Price':<10} {'Score':<7} {'RelVol':<8} {'Week%':<9} {'Today%':<9}")
    print("-" * 80)
    
    for idx, stock in enumerate(stocks, 1):
        score_emoji = "🔥🔥🔥" if stock['Score'] >= 4 else "🔥🔥" if stock['Score'] >= 3 else "🔥"
        print(f"{idx:<4} {stock['Ticker']:<8} ${stock['Price']:<9.2f} {stock['Score']}/5 {score_emoji:<4} "
              f"{stock['RelVol']:<7.1f}x {stock['Week%']:>+7.1f}% {stock['Today%']:>+7.1f}%")
    
    print("-" * 80)


def choose_stocks_from_scan(scanned_stocks: List[Dict]) -> List[str]:
    """
    Let user choose stocks from scanner results
    
    Args:
        scanned_stocks: List of scanned stock dictionaries
        
    Returns:
        List of selected ticker symbols
    """
    print("\n📋 SELECT STOCKS TO ANALYZE")
    print("=" * 80)
    print("Options:")
    print("  • Enter numbers (e.g., 1,3,5 for stocks #1, #3, #5)")
    print("  • Enter 'all' to analyze all scanned stocks")
    print("  • Enter 'top5' to analyze top 5")
    print("  • Enter 'top10' to analyze top 10")
    
    choice = input("\nYour selection: ").strip().lower()
    
    if choice == 'all':
        return [s['Ticker'] for s in scanned_stocks]
    elif choice == 'top5':
        return [s['Ticker'] for s in scanned_stocks[:5]]
    elif choice == 'top10':
        return [s['Ticker'] for s in scanned_stocks[:10]]
    else:
        # Parse numbers
        try:
            indices = [int(x.strip()) for x in choice.split(',')]
            tickers = []
            for idx in indices:
                if 1 <= idx <= len(scanned_stocks):
                    tickers.append(scanned_stocks[idx - 1]['Ticker'])
            return tickers
        except:
            print("❌ Invalid selection")
            return []


class TechnicalAnalyzer:
    """Analyzes stocks using VWAP, MACD, and risk/reward ratios"""
    
    def __init__(self, risk_reward_ratio: float = 3.0):
        self.risk_reward_ratio = risk_reward_ratio
        
    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate Volume Weighted Average Price
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Series with VWAP values
        """
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        vwap = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
        return vwap
    
    def calculate_vwap_bands(self, df: pd.DataFrame, vwap: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        """
        Calculate VWAP standard deviation bands
        
        Args:
            df: DataFrame with OHLCV data
            vwap: VWAP series
            
        Returns:
            Tuple of (upper_1std, lower_1std, upper_2std, lower_2std)
        """
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        
        # Calculate rolling standard deviation of price from VWAP
        squared_diff = (typical_price - vwap) ** 2
        weighted_squared_diff = squared_diff * df['Volume']
        variance = weighted_squared_diff.cumsum() / df['Volume'].cumsum()
        std_dev = np.sqrt(variance)
        
        upper_1std = vwap + std_dev
        lower_1std = vwap - std_dev
        upper_2std = vwap + (2 * std_dev)
        lower_2std = vwap - (2 * std_dev)
        
        return upper_1std, lower_1std, upper_2std, lower_2std
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD indicator
        
        Args:
            df: DataFrame with price data
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line period (default 9)
            
        Returns:
            Tuple of (macd_line, signal_line, histogram)
        """
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def analyze_stock(self, ticker: str, period: str = "5d", interval: str = "5m") -> Optional[Dict]:
        """
        Perform complete technical analysis on a stock
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, etc.)
            interval: Data interval (1m, 5m, 15m, 1h, 1d)
            
        Returns:
            Dictionary with analysis results or None if failed
        """
        try:
            # Download data
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            
            if df.empty or len(df) < 26:  # Need at least 26 periods for MACD
                return None
            
            # Calculate indicators
            current_price = df['Close'].iloc[-1]
            vwap = self.calculate_vwap(df)
            upper_1std, lower_1std, upper_2std, lower_2std = self.calculate_vwap_bands(df, vwap)
            macd_line, signal_line, histogram = self.calculate_macd(df)
            
            # Current values
            current_vwap = vwap.iloc[-1]
            current_upper_1std = upper_1std.iloc[-1]
            current_lower_1std = lower_1std.iloc[-1]
            current_upper_2std = upper_2std.iloc[-1]
            current_lower_2std = lower_2std.iloc[-1]
            current_macd = macd_line.iloc[-1]
            current_signal = signal_line.iloc[-1]
            current_histogram = histogram.iloc[-1]
            
            # Previous values for trend
            prev_macd = macd_line.iloc[-2] if len(macd_line) > 1 else current_macd
            prev_signal = signal_line.iloc[-2] if len(signal_line) > 1 else current_signal
            prev_histogram = histogram.iloc[-2] if len(histogram) > 1 else current_histogram
            
            # Determine position relative to VWAP
            price_vs_vwap = ((current_price - current_vwap) / current_vwap) * 100
            
            # MACD signals
            macd_bullish = current_macd > current_signal
            macd_crossover = (current_macd > current_signal) and (prev_macd <= prev_signal)
            macd_crossunder = (current_macd < current_signal) and (prev_macd >= prev_signal)
            histogram_increasing = current_histogram > prev_histogram
            
            # Determine position in VWAP bands
            if current_price > current_upper_2std:
                vwap_zone = "Above 2σ (Overbought)"
            elif current_price > current_upper_1std:
                vwap_zone = "Between 1σ and 2σ (Upper)"
            elif current_price > current_vwap:
                vwap_zone = "Between VWAP and 1σ (Upper)"
            elif current_price > current_lower_1std:
                vwap_zone = "Between VWAP and 1σ (Lower)"
            elif current_price > current_lower_2std:
                vwap_zone = "Between 1σ and 2σ (Lower)"
            else:
                vwap_zone = "Below 2σ (Oversold)"
            
            return {
                'ticker': ticker,
                'current_price': current_price,
                'vwap': current_vwap,
                'upper_1std': current_upper_1std,
                'lower_1std': current_lower_1std,
                'upper_2std': current_upper_2std,
                'lower_2std': current_lower_2std,
                'price_vs_vwap': price_vs_vwap,
                'vwap_zone': vwap_zone,
                'macd': current_macd,
                'signal': current_signal,
                'histogram': current_histogram,
                'macd_bullish': macd_bullish,
                'macd_crossover': macd_crossover,
                'macd_crossunder': macd_crossunder,
                'histogram_increasing': histogram_increasing,
                'dataframe': df
            }
            
        except Exception as e:
            print(f"⚠️  Error analyzing {ticker}: {e}")
            return None
    
    def calculate_entry_exit(self, analysis: Dict) -> Dict:
        """
        Calculate optimal entry, stop loss, and take profit levels
        
        Args:
            analysis: Technical analysis dictionary
            
        Returns:
            Dictionary with entry/exit recommendations
        """
        current_price = analysis['current_price']
        vwap = analysis['vwap']
        lower_1std = analysis['lower_1std']
        upper_1std = analysis['upper_1std']
        lower_2std = analysis['lower_2std']
        upper_2std = analysis['upper_2std']
        
        macd_bullish = analysis['macd_bullish']
        macd_crossover = analysis['macd_crossover']
        histogram_increasing = analysis['histogram_increasing']
        
        # Determine trade direction and signal strength
        if macd_crossover:
            signal_strength = "STRONG"
        elif macd_bullish and histogram_increasing:
            signal_strength = "MODERATE"
        elif macd_bullish:
            signal_strength = "WEAK"
        else:
            signal_strength = "BEARISH"
        
        # Long trade logic
        if macd_bullish:
            # Entry point suggestions
            if current_price < vwap:
                entry_point = current_price  # Already at good entry
                entry_reason = "Price below VWAP - Good entry point"
            elif current_price <= upper_1std:
                entry_point = vwap  # Wait for pullback
                entry_reason = "Wait for pullback to VWAP"
            else:
                entry_point = upper_1std  # Wait for deeper pullback
                entry_reason = "Price extended - wait for pullback to 1σ"
            
            # Stop loss: Below VWAP or 1σ lower band
            if entry_point > vwap:
                stop_loss = vwap * 0.995  # Just below VWAP with buffer
            else:
                stop_loss = lower_1std * 0.995  # Just below 1σ lower band
            
            # Risk calculation
            risk = entry_point - stop_loss
            
            # Take profit based on risk/reward ratio
            take_profit = entry_point + (risk * self.risk_reward_ratio)
            
            # Check if take profit is realistic (not beyond 2σ upper)
            if take_profit > upper_2std:
                suggested_ratio = (upper_2std - entry_point) / risk if risk > 0 else self.risk_reward_ratio
                ratio_recommendation = f"Consider {suggested_ratio:.1f}:1 (TP at 2σ: ${upper_2std:.2f})"
            else:
                ratio_recommendation = f"{self.risk_reward_ratio}:1 ratio is appropriate"
            
            trade_direction = "LONG"
            
        else:  # Bearish - short trade or no trade
            entry_point = current_price
            entry_reason = "Bearish MACD - consider shorting or avoiding"
            
            # For short trades
            if current_price > vwap:
                stop_loss = upper_1std * 1.005
            else:
                stop_loss = vwap * 1.005
            
            risk = stop_loss - entry_point
            take_profit = entry_point - (risk * self.risk_reward_ratio)
            
            if take_profit < lower_2std:
                suggested_ratio = (entry_point - lower_2std) / risk if risk > 0 else self.risk_reward_ratio
                ratio_recommendation = f"Consider {suggested_ratio:.1f}:1 (TP at 2σ: ${lower_2std:.2f})"
            else:
                ratio_recommendation = f"{self.risk_reward_ratio}:1 ratio is appropriate"
            
            trade_direction = "SHORT"
        
        return {
            'trade_direction': trade_direction,
            'signal_strength': signal_strength,
            'entry_point': entry_point,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk': risk,
            'reward': abs(take_profit - entry_point),
            'risk_reward_ratio': abs(take_profit - entry_point) / risk if risk > 0 else 0,
            'entry_reason': entry_reason,
            'ratio_recommendation': ratio_recommendation
        }
    
    def generate_recommendation(self, ticker: str, period: str = "5d", interval: str = "5m") -> Optional[Dict]:
        """
        Generate complete trading recommendation
        
        Args:
            ticker: Stock ticker symbol
            period: Time period for analysis
            interval: Data interval
            
        Returns:
            Complete recommendation dictionary
        """
        analysis = self.analyze_stock(ticker, period, interval)
        
        if not analysis:
            return None
        
        entry_exit = self.calculate_entry_exit(analysis)
        
        return {
            **analysis,
            **entry_exit
        }


def display_recommendation(rec: Dict):
    """Display formatted trading recommendation"""
    print("\n" + "=" * 70)
    print(f"📊 TRADING ANALYSIS: {rec['ticker']}")
    print("=" * 70)
    
    print(f"\n💰 CURRENT PRICE: ${rec['current_price']:.2f}")
    print(f"📈 VWAP: ${rec['vwap']:.2f} ({rec['price_vs_vwap']:+.2f}%)")
    print(f"📍 Position: {rec['vwap_zone']}")
    
    print(f"\n📉 VWAP BANDS:")
    print(f"   +2σ: ${rec['upper_2std']:.2f}")
    print(f"   +1σ: ${rec['upper_1std']:.2f}")
    print(f"   VWAP: ${rec['vwap']:.2f}")
    print(f"   -1σ: ${rec['lower_1std']:.2f}")
    print(f"   -2σ: ${rec['lower_2std']:.2f}")
    
    print(f"\n📊 MACD:")
    print(f"   MACD Line: {rec['macd']:.4f}")
    print(f"   Signal Line: {rec['signal']:.4f}")
    print(f"   Histogram: {rec['histogram']:.4f}")
    
    if rec['macd_crossover']:
        print(f"   🔥 BULLISH CROSSOVER!")
    elif rec['macd_crossunder']:
        print(f"   ❄️  BEARISH CROSSUNDER!")
    
    print(f"\n{'='*70}")
    print(f"🎯 TRADING RECOMMENDATION")
    print("=" * 70)
    
    direction_emoji = "🟢" if rec['trade_direction'] == "LONG" else "🔴"
    print(f"\n{direction_emoji} DIRECTION: {rec['trade_direction']} ({rec['signal_strength']} signal)")
    
    print(f"\n📍 ENTRY POINT: ${rec['entry_point']:.2f}")
    print(f"   Reason: {rec['entry_reason']}")
    
    print(f"\n🛑 STOP LOSS: ${rec['stop_loss']:.2f}")
    print(f"   Risk: ${rec['risk']:.2f} ({(rec['risk']/rec['entry_point']*100):.2f}%)")
    
    print(f"\n🎯 TAKE PROFIT: ${rec['take_profit']:.2f}")
    print(f"   Reward: ${rec['reward']:.2f} ({(rec['reward']/rec['entry_point']*100):.2f}%)")
    
    print(f"\n⚖️  RISK/REWARD: {rec['risk_reward_ratio']:.2f}:1")
    print(f"   {rec['ratio_recommendation']}")
    
    print("\n" + "=" * 70)


def main():
    """Main application"""
    # Show version and disclaimer
    print("=" * 80)
    print(f"TRADING SIGNAL ANALYZER v{VERSION}")
    print("Entry/Exit Point Predictor using VWAP + MACD")
    print("=" * 80)
    print(f"Author: {AUTHOR}")
    print(f"License: {LICENSE}")
    print(f"Based on Ross Cameron's 5 Pillars of Day Trading")
    print("=" * 80)
    
    # Show disclaimer and require acceptance
    show_disclaimer()
    
    print("=" * 80)
    print("TRADING SIGNAL ANALYZER - Entry/Exit Point Predictor")
    print("=" * 80)
    print("\nUses VWAP bands (1σ, 2σ) + MACD for optimal entry/exit points")
    print("=" * 80)
    
    # Get risk/reward ratio (persistent across session)
    print("\nEnter desired Risk/Reward ratio (default 3:1):")
    rr_input = input("Risk:Reward ratio (e.g., 3 for 3:1): ").strip()
    
    try:
        risk_reward = float(rr_input) if rr_input else 3.0
    except:
        risk_reward = 3.0
    
    print(f"\n✅ Using {risk_reward}:1 Risk/Reward ratio")
    
    # Get analysis timeframe (persistent across session)
    print("\nSelect analysis timeframe:")
    print("1. Scalping (1 day, 1-minute intervals)")
    print("2. Intraday (5 days, 5-minute intervals)")
    print("3. Short-term (1 month, 1-hour intervals)")
    print("4. Medium-term (3 months, 1-day intervals)")
    print("5. Long-term (1 year, 1-week intervals)")
    
    timeframe_choice = input("Enter choice (1-5) or press Enter for intraday: ").strip()
    
    if timeframe_choice == '1':
        period, interval = "1d", "1m"
        timeframe_name = "Scalping"
    elif timeframe_choice == '3':
        period, interval = "1mo", "1h"
        timeframe_name = "Short-term"
    elif timeframe_choice == '4':
        period, interval = "3mo", "1d"
        timeframe_name = "Medium-term"
    elif timeframe_choice == '5':
        period, interval = "1y", "1wk"
        timeframe_name = "Long-term"
    else:
        period, interval = "5d", "5m"
        timeframe_name = "Intraday"
    
    print(f"\n✅ Using {timeframe_name}: {period} period with {interval} intervals")
    
    # Initialize analyzer
    analyzer = TechnicalAnalyzer(risk_reward_ratio=risk_reward)
    
    # Store last scan results
    last_scanned_stocks = []
    
    # Main loop
    while True:
        print("\n" + "=" * 70)
        print("MAIN MENU")
        print("=" * 70)
        print("\n1. Run Ross Cameron Scanner (find new momentum setups)")
        print("2. Analyze from last scan results")
        print("3. Enter ticker manually")
        print("4. Change risk/reward ratio")
        print("5. Change timeframe")
        print("6. Quit")
        
        main_choice = input("\nEnter choice (1-6): ").strip()
        
        # Quit
        if main_choice == '6':
            print("\n" + "=" * 80)
            print(f"TRADING SIGNAL ANALYZER v{VERSION}")
            print("=" * 80)
            print("\n⚠️  FINAL REMINDER - RISK DISCLAIMER")
            print("=" * 80)
            print("""
Trading involves SUBSTANTIAL RISK of loss. The analysis provided by this
software is for educational purposes only and should not be considered as
financial or investment advice.

Key Reminders:
  • Always use stop losses on every trade
  • Never risk more than 1-2% of your account on a single trade
  • Past performance does not guarantee future results
  • Consult a licensed financial advisor before trading
  • You are solely responsible for your trading decisions

The author and contributors assume NO LIABILITY for any losses incurred
through use of this software.
""")
            print("=" * 80)
            print("\n📊 Session Statistics:")
            print(f"   • Version: {VERSION}")
            print(f"   • License: {LICENSE} (Open Source)")
            print(f"   • GitHub: https://github.com/savowood/trading-signal-analyzer")
            print("\n💡 Contributions Welcome!")
            print("   Found a bug? Have an improvement? Submit a pull request!")
            print("   All modifications must be shared back per GPL v3 license.")
            print("\n" + "=" * 80)
            print("👋 Thanks for using Trading Signal Analyzer!")
            print("   Trade safe. Trade smart. Manage your risk.")
            print("=" * 80)
            break
        
        # Change risk/reward ratio
        elif main_choice == '4':
            print("\nCurrent ratio: {risk_reward}:1")
            rr_input = input("Enter new Risk:Reward ratio: ").strip()
            try:
                risk_reward = float(rr_input) if rr_input else risk_reward
                analyzer = TechnicalAnalyzer(risk_reward_ratio=risk_reward)
                print(f"✅ Updated to {risk_reward}:1")
            except:
                print("❌ Invalid input, keeping current ratio")
            continue
        
        # Change timeframe
        elif main_choice == '5':
            print(f"\nCurrent: {period} period with {interval} intervals")
            print("\nSelect new timeframe:")
            print("1. Intraday (5 days, 5-minute intervals)")
            print("2. Short-term (1 month, 1-hour intervals)")
            print("3. Medium-term (3 months, 1-day intervals)")
            
            tf_choice = input("Enter choice (1-3): ").strip()
            
            if tf_choice == '2':
                period, interval = "1mo", "1h"
            elif tf_choice == '3':
                period, interval = "3mo", "1d"
            else:
                period, interval = "5d", "5m"
            
            print(f"✅ Updated to {period} period with {interval} intervals")
            continue
        
        # Get tickers to analyze
        tickers = []
        
        # Run new scan
        if main_choice == '1':
            if not TRADINGVIEW_AVAILABLE:
                print("\n❌ TradingView screener not installed!")
                print("   Install: pip install tradingview-screener")
                continue
            
            # Market selection
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
            
            # Run scanner
            scanned_stocks = scan_ross_cameron_stocks(market)
            
            if not scanned_stocks:
                print("❌ No stocks found.")
                input("\nPress Enter to continue...")
                continue
            
            # Store for later use
            last_scanned_stocks = scanned_stocks
            
            # Display results
            display_scanned_stocks(scanned_stocks)
            
            # Let user choose
            tickers = choose_stocks_from_scan(scanned_stocks)
            
            if not tickers:
                print("❌ No stocks selected")
                input("\nPress Enter to continue...")
                continue
        
        # Analyze from last scan
        elif main_choice == '2':
            if not last_scanned_stocks:
                print("\n❌ No previous scan results. Run a scan first (option 1)")
                input("\nPress Enter to continue...")
                continue
            
            # Show previous results
            display_scanned_stocks(last_scanned_stocks)
            
            # Let user choose
            tickers = choose_stocks_from_scan(last_scanned_stocks)
            
            if not tickers:
                print("❌ No stocks selected")
                input("\nPress Enter to continue...")
                continue
        
        # Manual entry
        elif main_choice == '3':
            tickers_input = input("\nEnter ticker symbols (comma-separated, e.g., AAPL,TSLA,NVDA): ").strip()
            tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
            
            if not tickers:
                print("❌ No tickers provided")
                input("\nPress Enter to continue...")
                continue
        
        else:
            print("❌ Invalid choice")
            continue
        
        # Analyze selected tickers
        print(f"\n🔍 Analyzing {len(tickers)} stock(s)...")
        
        for idx, ticker in enumerate(tickers, 1):
            print(f"\n{'='*70}")
            print(f"⏳ Analyzing {ticker} ({idx}/{len(tickers)})...")
            print(f"{'='*70}")
            
            rec = analyzer.generate_recommendation(ticker, period, interval)
            
            if rec:
                display_recommendation(rec)
            else:
                print(f"❌ Could not analyze {ticker}")
            
            # Pause between stocks if multiple
            if len(tickers) > 1 and idx < len(tickers):
                input("\n📊 Press Enter to continue to next stock...")
        
        # Analysis complete - ask what to do next
        print("\n" + "=" * 70)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 70)
        
        input("\n📊 Press Enter to return to main menu...")


if __name__ == "__main__":
    main()
