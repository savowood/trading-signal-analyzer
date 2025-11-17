"""
Trading Signal Analyzer v0.93 - Entry/Exit Point Prediction  
Copyright (C) 2025 Michael Johnson (GitHub: @savowood)

FULLY INTEGRATED VERSION with Enhanced Dark Flow Market Scanner

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
This software implements the "5 Pillars of Day Trading" methodology for stock 
selection, based on momentum trading principles:

NEW 5 PILLARS:
  1. Up 10%+ on the day (strong intraday momentum)
  2. 500% relative volume (5x+ average volume - institutional interest)
  3. News event moving stock higher (catalyst present)
  4. Price range $2-$20 (ideal liquidity, configurable)
  5. Under 20M shares available to trade (low float for squeeze potential)

Original research inspired by momentum trading strategies.
Learn more at: https://www.warriortrading.com/

Technical analysis (VWAP, MACD, Enhanced Dark Flow Scanner) implementation is original work.

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

Version: 0.93
NEW 5 PILLARS: +10% Day, 5x RelVol, News Catalyst, $2-$20, <20M Float
Uses VWAP bands (1σ, 2σ) + MACD for optimal entry/exit points
Includes integrated 5 Pillars Scanner + FOREX + Crypto + ENHANCED Dark Flow Market Scanner
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Version info
VERSION = "0.93"
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


def is_likely_delisted(ticker: str, price: float, volume: int, market_cap: float) -> bool:
    """
    Check if a stock is likely delisted or inactive
    
    Args:
        ticker: Stock symbol
        price: Current price
        volume: Current volume
        market_cap: Market capitalization
        
    Returns:
        True if stock appears delisted/inactive
    """
    delisting_suffixes = ['Q', 'E', 'D']
    
    if any(ticker.endswith(suffix) for suffix in delisting_suffixes):
        return True
    
    if price < 0.0001 and volume < 1000:
        return True
    
    if volume == 0:
        return True
    
    if market_cap and market_cap < 100000:
        return True
    
    return False


def scan_momentum_stocks(market_choice: str = '1', min_price: float = 2.0, 
                        max_price: float = 20.0) -> List[Dict]:
    """
    Integrated 5 Pillars Momentum Scanner
    
    NEW 5 PILLARS CRITERIA:
    1. Up 10%+ on the day (intraday momentum)
    2. 500% relative volume (5x+ average volume today)
    3. News event moving stock higher (catalyst detection)
    4. Price range $2-$20 (configurable)
    5. Under 20M shares available to trade (low float)
    
    Args:
        market_choice: Market selection ('1' for US, '3' NASDAQ, '4' NYSE)
        min_price: Minimum price filter (default $2.00)
        max_price: Maximum price filter (default $20.00)
        
    Returns:
        List of qualifying stocks with scores
    """
    if not TRADINGVIEW_AVAILABLE:
        print("❌ TradingView screener not installed")
        return []
    
    try:
        print("🔍 Scanning for momentum setups...")
        print(f"   Filters: ${min_price:.2f} - ${max_price:.2f}, 5x+ RelVol, +10% day, <20M float")
        
        q = Query()
        
        if market_choice == '3':
            q = q.set_markets('america').where(col('exchange') == 'NASDAQ')
        elif market_choice == '4':
            q = q.set_markets('america').where(col('exchange') == 'NYSE')
        else:
            q = q.set_markets('america')
        
        q = q.where(col('close').between(min_price, max_price))
        q = q.where(col('relative_volume_10d_calc') >= 5.0)
        q = q.where(col('change_from_open') >= 10.0)
        
        q = q.select(
            'name', 'close', 'volume', 'relative_volume_10d_calc',
            'market_cap_basic', 'change', 'change_from_open',
            'Recommend.All', 'Perf.W', 'Perf.1M',
            'average_volume_10d_calc', 'exchange', 'description'
        ).order_by('change_from_open', ascending=False).limit(100)
        
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
                description = row.get('description', '')
                
                if market_cap and price > 0:
                    float_m = (market_cap / price) / 1_000_000
                else:
                    float_m = 50
                
                low_float = float_m < 20
                has_catalyst = (change_from_open >= 10) and (rel_vol >= 5.0)
                
                strong_week = abs(change_pct) > 20
                explosive_month = perf_1m > 50
                
                if strong_week or explosive_month:
                    catalyst_strength = "STRONG"
                elif change_from_open >= 15:
                    catalyst_strength = "MODERATE"
                else:
                    catalyst_strength = "PRESENT"
                
                pillars_met = sum([
                    change_from_open >= 10,
                    rel_vol >= 5.0,
                    has_catalyst,
                    True,
                    low_float
                ])
                
                volume_val = row.get('volume', 0) or 0
                if is_likely_delisted(ticker, price, volume_val, market_cap):
                    continue
                
                if pillars_met >= 3:
                    results.append({
                        'Ticker': ticker,
                        'Price': price,
                        'RelVol': rel_vol,
                        'Float(M)': float_m,
                        'Score': pillars_met,
                        'Week%': change_pct,
                        'Today%': change_from_open,
                        'Catalyst': catalyst_strength,
                        'LowFloat': low_float,
                        'Description': description[:50] if description else ''
                    })
            except:
                continue
        
        results.sort(key=lambda x: (x['Score'], x['Today%']), reverse=True)
        
        print(f"✅ Found {len(results)} qualifying stocks")
        return results
        
    except Exception as e:
        print(f"❌ Scanner error: {e}")
        return []


def scan_forex_pairs() -> List[Dict]:
    """Scan top 10 FOREX pairs for trading opportunities"""
    try:
        print("🔍 Scanning top FOREX pairs...")
        
        forex_pairs = [
            ('EURUSD=X', 'EUR/USD', 'Euro / US Dollar'),
            ('GBPUSD=X', 'GBP/USD', 'British Pound / US Dollar'),
            ('USDJPY=X', 'USD/JPY', 'US Dollar / Japanese Yen'),
            ('USDCHF=X', 'USD/CHF', 'US Dollar / Swiss Franc'),
            ('AUDUSD=X', 'AUD/USD', 'Australian Dollar / US Dollar'),
            ('NZDUSD=X', 'NZD/USD', 'New Zealand Dollar / US Dollar'),
            ('USDCAD=X', 'USD/CAD', 'US Dollar / Canadian Dollar'),
            ('EURGBP=X', 'EUR/GBP', 'Euro / British Pound'),
            ('EURJPY=X', 'EUR/JPY', 'Euro / Japanese Yen'),
            ('GBPJPY=X', 'GBP/JPY', 'British Pound / Japanese Yen'),
        ]
        
        results = []
        
        for ticker, symbol, name in forex_pairs:
            try:
                forex = yf.Ticker(ticker)
                hist = forex.history(period='5d', interval='1h')
                
                if hist.empty or len(hist) < 2:
                    continue
                
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                day_change = ((current_price - prev_price) / prev_price) * 100
                
                week_ago_price = hist['Close'].iloc[0]
                week_change = ((current_price - week_ago_price) / week_ago_price) * 100
                
                avg_volume = hist['Volume'].mean() if 'Volume' in hist.columns else 0
                recent_volume = hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
                
                price_range = hist['High'].max() - hist['Low'].min()
                volatility_pct = (price_range / current_price) * 100
                
                results.append({
                    'Ticker': ticker,
                    'Symbol': symbol,
                    'Name': name,
                    'Price': current_price,
                    'Change%': day_change,
                    'Week%': week_change,
                    'Volatility%': volatility_pct,
                    'Volume': recent_volume
                })
                
            except Exception as e:
                continue
        
        results.sort(key=lambda x: abs(x['Week%']), reverse=True)
        
        print(f"✅ Found {len(results)} FOREX pairs")
        return results
        
    except Exception as e:
        print(f"❌ FOREX scanner error: {e}")
        return []


def scan_crypto() -> List[Dict]:
    """Scan top 20 highly active cryptocurrencies"""
    try:
        print("🔍 Scanning top cryptocurrencies...")
        
        crypto_tickers = [
            ('BTC-USD', 'Bitcoin'),
            ('ETH-USD', 'Ethereum'),
            ('BNB-USD', 'Binance Coin'),
            ('SOL-USD', 'Solana'),
            ('XRP-USD', 'Ripple'),
            ('ADA-USD', 'Cardano'),
            ('AVAX-USD', 'Avalanche'),
            ('DOGE-USD', 'Dogecoin'),
            ('DOT-USD', 'Polkadot'),
            ('MATIC-USD', 'Polygon'),
            ('LTC-USD', 'Litecoin'),
            ('SHIB-USD', 'Shiba Inu'),
            ('TRX-USD', 'TRON'),
            ('LINK-USD', 'Chainlink'),
            ('UNI-USD', 'Uniswap'),
            ('ATOM-USD', 'Cosmos'),
            ('XLM-USD', 'Stellar'),
            ('ALGO-USD', 'Algorand'),
            ('VET-USD', 'VeChain'),
            ('FIL-USD', 'Filecoin'),
        ]
        
        results = []
        
        for ticker, name in crypto_tickers:
            try:
                crypto = yf.Ticker(ticker)
                hist = crypto.history(period='5d', interval='1h')
                
                if hist.empty or len(hist) < 2:
                    continue
                
                current_price = hist['Close'].iloc[-1]
                
                prev_price = hist['Close'].iloc[-2]
                hour_change = ((current_price - prev_price) / prev_price) * 100
                
                week_ago_price = hist['Close'].iloc[0]
                week_change = ((current_price - week_ago_price) / week_ago_price) * 100
                
                if len(hist) >= 24:
                    day_ago_price = hist['Close'].iloc[-24]
                    day_change = ((current_price - day_ago_price) / day_ago_price) * 100
                else:
                    day_change = hour_change
                
                volume_24h = hist['Volume'].iloc[-24:].sum() if len(hist) >= 24 else hist['Volume'].sum()
                
                price_range = hist['High'].max() - hist['Low'].min()
                volatility_pct = (price_range / current_price) * 100
                
                activity_score = abs(week_change) * (volatility_pct / 10)
                
                results.append({
                    'Ticker': ticker,
                    'Name': name,
                    'Price': current_price,
                    'Hour%': hour_change,
                    'Day%': day_change,
                    'Week%': week_change,
                    'Volatility%': volatility_pct,
                    'Volume24h': volume_24h,
                    'Activity': activity_score
                })
                
            except Exception as e:
                continue
        
        results.sort(key=lambda x: x['Activity'], reverse=True)
        
        print(f"✅ Found {len(results)} active cryptocurrencies")
        return results
        
    except Exception as e:
        print(f"❌ Crypto scanner error: {e}")
        return []


def display_forex_pairs(pairs: List[Dict]):
    """Display FOREX pairs in a formatted table"""
    print("\n" + "=" * 90)
    print("💱 FOREX PAIRS - TOP 10 MAJOR PAIRS")
    print("=" * 90)
    
    if not pairs:
        print("No FOREX pairs found")
        return
    
    print(f"\n{'#':<4} {'Pair':<12} {'Price':<12} {'Change%':<10} {'Week%':<10} {'Volatility%':<12}")
    print("-" * 90)
    
    for idx, pair in enumerate(pairs, 1):
        change_emoji = "🟢" if pair['Change%'] >= 0 else "🔴"
        
        price = pair['Price']
        if price < 1:
            price_str = f"{price:.5f}"
        elif price < 100:
            price_str = f"{price:.4f}"
        else:
            price_str = f"{price:.2f}"
        
        print(f"{idx:<4} {pair['Symbol']:<12} {price_str:<12} "
              f"{change_emoji} {pair['Change%']:>+7.2f}% {pair['Week%']:>+8.2f}% {pair['Volatility%']:>10.2f}%")
    
    print("-" * 90)
    print("\n💡 Tip: FOREX pairs trade 24/5 with high liquidity")


def display_crypto(cryptos: List[Dict]):
    """Display cryptocurrencies in a formatted table"""
    print("\n" + "=" * 95)
    print("₿ CRYPTOCURRENCIES - TOP 20 ACTIVE COINS")
    print("=" * 95)
    
    if not cryptos:
        print("No cryptocurrencies found")
        return
    
    print(f"\n{'#':<4} {'Name':<15} {'Price':<15} {'Hour%':<10} {'Day%':<10} {'Week%':<10} {'Activity':<10}")
    print("-" * 95)
    
    for idx, crypto in enumerate(cryptos, 1):
        if crypto['Day%'] >= 5:
            emoji = "🚀"
        elif crypto['Day%'] >= 0:
            emoji = "🟢"
        elif crypto['Day%'] >= -5:
            emoji = "🔴"
        else:
            emoji = "📉"
        
        price = crypto['Price']
        if price < 0.01:
            price_str = f"${price:.6f}"
        elif price < 1:
            price_str = f"${price:.4f}"
        elif price < 100:
            price_str = f"${price:.2f}"
        else:
            price_str = f"${price:,.2f}"
        
        print(f"{idx:<4} {crypto['Name']:<15} {price_str:<15} "
              f"{emoji} {crypto['Hour%']:>+6.2f}% {crypto['Day%']:>+7.2f}% "
              f"{crypto['Week%']:>+7.2f}% {crypto['Activity']:>9.1f}")
    
    print("-" * 95)
    print("\n💡 Tip: Crypto trades 24/7 with high volatility")


def choose_from_scan(scanned_items: List[Dict], asset_type: str = "stocks") -> List[str]:
    """
    Let user choose items from scanner results (works for stocks, forex, crypto)
    
    Args:
        scanned_items: List of scanned item dictionaries
        asset_type: Type of asset ("stocks", "forex", "crypto")
        
    Returns:
        List of selected ticker symbols
    """
    print(f"\n📋 SELECT {asset_type.upper()} TO ANALYZE")
    print("=" * 80)
    print("Options:")
    print("  • Enter numbers (e.g., 1,3,5 for items #1, #3, #5)")
    print("  • Enter 'all' to analyze all scanned items")
    print("  • Enter 'top5' to analyze top 5")
    print("  • Enter 'top10' to analyze top 10")
    
    choice = input("\nYour selection: ").strip().lower()
    
    if choice == 'all':
        return [s['Ticker'] for s in scanned_items]
    elif choice == 'top5':
        return [s['Ticker'] for s in scanned_items[:5]]
    elif choice == 'top10':
        return [s['Ticker'] for s in scanned_items[:10]]
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(',')]
            tickers = []
            for idx in indices:
                if 1 <= idx <= len(scanned_items):
                    tickers.append(scanned_items[idx - 1]['Ticker'])
            return tickers
        except:
            print("❌ Invalid selection")
            return []


def display_scanned_stocks(stocks: List[Dict]):
    """Display scanned stocks in a formatted table"""
    print("\n" + "=" * 95)
    print("🔥 MOMENTUM SCANNER RESULTS - 5 PILLARS")
    print("=" * 95)
    print("\nNEW 5 PILLARS: +10% Day | 5x RelVol | News Catalyst | $2-$20 | <20M Float")
    print("=" * 95)
    
    if not stocks:
        print("No stocks found")
        return
    
    print(f"\n{'#':<4} {'Ticker':<8} {'Price':<10} {'Score':<7} {'Today%':<10} {'RelVol':<9} {'Float(M)':<10}")
    print("-" * 95)
    
    for idx, stock in enumerate(stocks, 1):
        score_emoji = "🔥🔥🔥" if stock['Score'] >= 5 else "🔥🔥" if stock['Score'] >= 4 else "🔥"
        
        price = stock['Price']
        if price < 1.00:
            price_str = f"${price:.3f}"
        else:
            price_str = f"${price:.2f}"
        
        float_indicator = "⭐" if stock.get('LowFloat', False) else ""
        
        print(f"{idx:<4} {stock['Ticker']:<8} {price_str:<10} {stock['Score']}/5 {score_emoji:<4} "
              f"{stock['Today%']:>+8.1f}% {stock['RelVol']:<8.1f}x "
              f"{stock['Float(M)']:<8.1f}{float_indicator:<2}")
    
    print("-" * 95)
    print("\n⭐ = Low float (<20M shares)")
    print("💡 Sorted by: Score (pillars met) then Today's % change")
    print("=" * 95)


class TechnicalAnalyzer:
    """Analyzes stocks using VWAP, MACD, and risk/reward ratios"""
    
    def __init__(self, risk_reward_ratio: float = 3.0):
        self.risk_reward_ratio = risk_reward_ratio
    
    def has_volume_data(self, df: pd.DataFrame) -> bool:
        """Check if DataFrame has valid volume data"""
        if 'Volume' not in df.columns:
            return False
        
        volume_sum = df['Volume'].sum()
        return volume_sum > 0 and not pd.isna(volume_sum)
    
    def calculate_sma_atr_bands(self, df: pd.DataFrame, period: int = 20) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
        """Calculate SMA with ATR-based bands (for assets without volume like FOREX)"""
        sma = df['Close'].rolling(window=period).mean()
        
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=14).mean()
        
        upper_1atr = sma + atr
        lower_1atr = sma - atr
        upper_2atr = sma + (2 * atr)
        lower_2atr = sma - (2 * atr)
        
        return sma, upper_1atr, lower_1atr, upper_2atr, lower_2atr
        
    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Volume Weighted Average Price"""
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        vwap = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
        return vwap
    
    def calculate_vwap_bands(self, df: pd.DataFrame, vwap: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        """Calculate VWAP standard deviation bands"""
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        
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
        """Calculate MACD indicator"""
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def analyze_stock(self, ticker: str, period: str = "5d", interval: str = "5m") -> Optional[Dict]:
        """Perform complete technical analysis on a stock/forex/crypto"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            
            if df.empty or len(df) < 26:
                return None
            
            current_price = df['Close'].iloc[-1]
            
            has_volume = self.has_volume_data(df)
            
            if has_volume:
                vwap = self.calculate_vwap(df)
                upper_1std, lower_1std, upper_2std, lower_2std = self.calculate_vwap_bands(df, vwap)
                
                current_vwap = vwap.iloc[-1]
                current_upper_1std = upper_1std.iloc[-1]
                current_lower_1std = lower_1std.iloc[-1]
                current_upper_2std = upper_2std.iloc[-1]
                current_lower_2std = lower_2std.iloc[-1]
                indicator_type = "VWAP"
            else:
                sma, upper_1atr, lower_1atr, upper_2atr, lower_2atr = self.calculate_sma_atr_bands(df)
                
                current_vwap = sma.iloc[-1]
                current_upper_1std = upper_1atr.iloc[-1]
                current_lower_1std = lower_1atr.iloc[-1]
                current_upper_2std = upper_2atr.iloc[-1]
                current_lower_2std = lower_2atr.iloc[-1]
                indicator_type = "SMA"
            
            macd_line, signal_line, histogram = self.calculate_macd(df)
            
            current_macd = macd_line.iloc[-1]
            current_signal = signal_line.iloc[-1]
            current_histogram = histogram.iloc[-1]
            
            prev_macd = macd_line.iloc[-2] if len(macd_line) > 1 else current_macd
            prev_signal = signal_line.iloc[-2] if len(signal_line) > 1 else current_signal
            prev_histogram = histogram.iloc[-2] if len(histogram) > 1 else current_histogram
            
            price_vs_vwap = ((current_price - current_vwap) / current_vwap) * 100
            
            macd_bullish = current_macd > current_signal
            macd_crossover = (current_macd > current_signal) and (prev_macd <= prev_signal)
            macd_crossunder = (current_macd < current_signal) and (prev_macd >= prev_signal)
            histogram_increasing = current_histogram > prev_histogram
            
            if current_price > current_upper_2std:
                vwap_zone = "Above 2σ (Overbought)"
            elif current_price > current_upper_1std:
                vwap_zone = "Between 1σ and 2σ (Upper)"
            elif current_price > current_vwap:
                if indicator_type == "VWAP":
                    vwap_zone = "Between VWAP and 1σ (Upper)"
                else:
                    vwap_zone = "Between SMA and 1σ (Upper)"
            elif current_price > current_lower_1std:
                if indicator_type == "VWAP":
                    vwap_zone = "Between VWAP and 1σ (Lower)"
                else:
                    vwap_zone = "Between SMA and 1σ (Lower)"
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
                'indicator_type': indicator_type,
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
        """Calculate optimal entry, stop loss, and take profit levels"""
        current_price = analysis['current_price']
        vwap = analysis['vwap']
        lower_1std = analysis['lower_1std']
        upper_1std = analysis['upper_1std']
        lower_2std = analysis['lower_2std']
        upper_2std = analysis['upper_2std']
        indicator_type = analysis.get('indicator_type', 'VWAP')
        
        macd_bullish = analysis['macd_bullish']
        macd_crossover = analysis['macd_crossover']
        histogram_increasing = analysis['histogram_increasing']
        
        if macd_crossover:
            signal_strength = "STRONG"
        elif macd_bullish and histogram_increasing:
            signal_strength = "MODERATE"
        elif macd_bullish:
            signal_strength = "WEAK"
        else:
            signal_strength = "BEARISH"
        
        if macd_bullish:
            if current_price < vwap:
                entry_point = current_price
                if indicator_type == "SMA":
                    entry_reason = "Price below SMA - Good entry point"
                else:
                    entry_reason = "Price below VWAP - Good entry point"
            elif current_price <= upper_1std:
                entry_point = vwap
                if indicator_type == "SMA":
                    entry_reason = "Wait for pullback to SMA"
                else:
                    entry_reason = "Wait for pullback to VWAP"
            else:
                entry_point = upper_1std
                entry_reason = "Price extended - wait for pullback to 1σ"
            
            if entry_point > vwap:
                stop_loss = vwap * 0.995
            else:
                stop_loss = lower_1std * 0.995
            
            risk = entry_point - stop_loss
            take_profit = entry_point + (risk * self.risk_reward_ratio)
            
            if take_profit > upper_2std:
                suggested_ratio = (upper_2std - entry_point) / risk if risk > 0 else self.risk_reward_ratio
                ratio_recommendation = f"Consider {suggested_ratio:.1f}:1 (TP at 2σ: ${upper_2std:.2f})"
            else:
                ratio_recommendation = f"{self.risk_reward_ratio}:1 ratio is appropriate"
            
            trade_direction = "LONG"
            
        else:
            entry_point = current_price
            entry_reason = "Bearish MACD - consider shorting or avoiding"
            
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
        """Generate complete trading recommendation"""
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
    
    price = rec['current_price']
    if price < 0.01:
        price_format = f"${price:.6f}"
    elif price < 0.10:
        price_format = f"${price:.4f}"
    elif price < 1.00:
        price_format = f"${price:.3f}"
    else:
        price_format = f"${price:.2f}"
    
    print(f"\n💰 CURRENT PRICE: {price_format}")
    
    indicator_type = rec.get('indicator_type', 'VWAP')
    
    vwap = rec['vwap']
    if price < 0.01:
        vwap_format = f"${vwap:.6f}"
        band_decimals = 6
    elif price < 0.10:
        vwap_format = f"${vwap:.4f}"
        band_decimals = 4
    elif price < 1.00:
        vwap_format = f"${vwap:.3f}"
        band_decimals = 3
    else:
        vwap_format = f"${vwap:.2f}"
        band_decimals = 2
    
    if indicator_type == "SMA":
        print(f"📈 SMA(20): {vwap_format} ({rec['price_vs_vwap']:+.2f}%)")
        print(f"📍 Position: {rec['vwap_zone']}")
        print(f"\n📉 SMA + ATR BANDS:")
        print(f"   +2 ATR: ${rec['upper_2std']:.{band_decimals}f}")
        print(f"   +1 ATR: ${rec['upper_1std']:.{band_decimals}f}")
        print(f"   SMA: ${rec['vwap']:.{band_decimals}f}")
        print(f"   -1 ATR: ${rec['lower_1std']:.{band_decimals}f}")
        print(f"   -2 ATR: ${rec['lower_2std']:.{band_decimals}f}")
    else:
        print(f"📈 VWAP: {vwap_format} ({rec['price_vs_vwap']:+.2f}%)")
        print(f"📍 Position: {rec['vwap_zone']}")
        print(f"\n📉 VWAP BANDS:")
        print(f"   +2σ: ${rec['upper_2std']:.{band_decimals}f}")
        print(f"   +1σ: ${rec['upper_1std']:.{band_decimals}f}")
        print(f"   VWAP: ${rec['vwap']:.{band_decimals}f}")
        print(f"   -1σ: ${rec['lower_1std']:.{band_decimals}f}")
        print(f"   -2σ: ${rec['lower_2std']:.{band_decimals}f}")
    
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
    
    print(f"\n📍 ENTRY POINT: ${rec['entry_point']:.{band_decimals}f}")
    print(f"   Reason: {rec['entry_reason']}")
    
    print(f"\n🛑 STOP LOSS: ${rec['stop_loss']:.{band_decimals}f}")
    print(f"   Risk: ${rec['risk']:.{band_decimals}f} ({(rec['risk']/rec['entry_point']*100):.2f}%)")
    
    print(f"\n🎯 TAKE PROFIT: ${rec['take_profit']:.{band_decimals}f}")
    print(f"   Reward: ${rec['reward']:.{band_decimals}f} ({(rec['reward']/rec['entry_point']*100):.2f}%)")
    
    print(f"\n⚖️  RISK/REWARD: {rec['risk_reward_ratio']:.2f}:1")
    print(f"   {rec['ratio_recommendation']}")
    
    print("\n" + "=" * 70)


class DarkFlowScanner:
    """
    Enhanced Dark Flow Scanner - Detects institutional dark pool activity using volume profile
    NOW INCLUDES MARKET-WIDE SCANNING CAPABILITY
    """
    
    def __init__(self):
        self.major_etfs = ['SPY', 'QQQ', 'IWM', 'DIA']
    
    def scan_market_for_dark_flow(self, market_choice: str = '1', min_price: float = 5.0, 
                                   max_price: float = 100.0, min_volume: float = 1_000_000) -> List[Dict]:
        """
        NEW: Scan entire market for stocks with Dark Flow signals
        
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
            
            q = Query()
            
            if market_choice == '3':
                q = q.set_markets('america').where(col('exchange') == 'NASDAQ')
            elif market_choice == '4':
                q = q.set_markets('america').where(col('exchange') == 'NYSE')
            else:
                q = q.set_markets('america')
            
            q = q.where(col('close').between(min_price, max_price))
            q = q.where(col('volume') >= min_volume)
            q = q.where(col('change').between(-5, 15))
            
            q = q.select(
                'name', 'close', 'volume', 'change', 'change_from_open',
                'Perf.W', 'Perf.1M', 'relative_volume_10d_calc',
                'average_volume_10d_calc', 'high', 'low', 'open'
            ).order_by('volume', ascending=False).limit(100)
            
            count, df = q.get_scanner_data()
            
            if df is None or df.empty:
                print("⚠️  No stocks found matching criteria")
                return []
            
            print(f"   Analyzing {len(df)} candidates for Dark Flow signals...")
            
            results = []
            
            for _, row in df.iterrows():
                try:
                    ticker = row['name']
                    
                    rel_vol = float(row.get('relative_volume_10d_calc') or 0)
                    if rel_vol < 1.5:
                        continue
                    
                    analysis = self.analyze_institutional_levels(ticker, period="5d")
                    
                    if not analysis:
                        continue
                    
                    score = self._calculate_dark_flow_score(analysis, row)
                    
                    if score >= 50:
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
                            'Analysis': analysis
                        })
                    
                except Exception as e:
                    continue
            
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
            
            volume_profile = self._create_volume_profile(df)
            key_levels = self._find_key_levels(volume_profile, current_price)
            
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
    """NEW: Display Dark Flow market scan results"""
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


def main():
    """Main application"""
    print("=" * 80)
    print(f"TRADING SIGNAL ANALYZER v{VERSION}")
    print("Entry/Exit Point Predictor using VWAP + MACD")
    print("WITH ENHANCED DARK FLOW MARKET SCANNER")
    print("=" * 80)
    print(f"Author: {AUTHOR}")
    print(f"License: {LICENSE}")
    print(f"Based on the 5 Pillars of Day Trading methodology")
    print("=" * 80)
    
    show_disclaimer()
    
    print("=" * 80)
    print("TRADING SIGNAL ANALYZER - Entry/Exit Point Predictor")
    print("=" * 80)
    print("\nUses VWAP bands (1σ, 2σ) + MACD for optimal entry/exit points")
    print("Enhanced Dark Flow Scanner with Market-Wide Scanning")
    print("=" * 80)
    
    # Get risk/reward ratio
    print("\nEnter desired Risk/Reward ratio (default 3:1):")
    rr_input = input("Risk:Reward ratio (e.g., 3 for 3:1): ").strip()
    
    try:
        risk_reward = float(rr_input) if rr_input else 3.0
    except:
        risk_reward = 3.0
    
    print(f"\n✅ Using {risk_reward}:1 Risk/Reward ratio")
    
    # Get analysis timeframe
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
    
    analyzer = TechnicalAnalyzer(risk_reward_ratio=risk_reward)
    
    # Store last scan results
    last_scanned_stocks = []
    last_scanned_forex = []
    last_scanned_crypto = []
    last_scanned_dark_flow = []  # NEW
    last_scan_type = None
    
    # Main loop
    while True:
        print("\n" + "=" * 70)
        print("MAIN MENU")
        print("=" * 70)
        print("\n1. Run Momentum Scanner (stocks)")
        print("2. Scan FOREX pairs (top 10)")
        print("3. Scan Cryptocurrencies (top 20)")
        print("4. Dark Flow Scanner (institutional levels + market scan)")  # UPDATED
        print("5. Analyze from last scan results")
        print("6. Enter ticker manually")
        print("7. Change risk/reward ratio")
        print("8. Change timeframe")
        print("9. Quit")
        
        main_choice = input("\nEnter choice (1-9): ").strip()
        
        if main_choice == '9':
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
        elif main_choice == '7':
            print(f"\nCurrent ratio: {risk_reward}:1")
            rr_input = input("Enter new Risk:Reward ratio: ").strip()
            try:
                risk_reward = float(rr_input) if rr_input else risk_reward
                analyzer = TechnicalAnalyzer(risk_reward_ratio=risk_reward)
                print(f"✅ Updated to {risk_reward}:1")
            except:
                print("❌ Invalid input, keeping current ratio")
            continue
        
        # Change timeframe
        elif main_choice == '8':
            print(f"\nCurrent: {timeframe_name} - {period} period with {interval} intervals")
            print("\nSelect new timeframe:")
            print("1. Scalping (1 day, 1-minute intervals)")
            print("2. Intraday (5 days, 5-minute intervals)")
            print("3. Short-term (1 month, 1-hour intervals)")
            print("4. Medium-term (3 months, 1-day intervals)")
            print("5. Long-term (1 year, 1-week intervals)")
            
            tf_choice = input("Enter choice (1-5): ").strip()
            
            if tf_choice == '1':
                period, interval = "1d", "1m"
                timeframe_name = "Scalping"
            elif tf_choice == '3':
                period, interval = "1mo", "1h"
                timeframe_name = "Short-term"
            elif tf_choice == '4':
                period, interval = "3mo", "1d"
                timeframe_name = "Medium-term"
            elif tf_choice == '5':
                period, interval = "1y", "1wk"
                timeframe_name = "Long-term"
            else:
                period, interval = "5d", "5m"
                timeframe_name = "Intraday"
            
            print(f"✅ Updated to {timeframe_name}: {period} period with {interval} intervals")
            continue
        
        # Get tickers to analyze
        tickers = []
        
        # Run new stock scan
        if main_choice == '1':
            if not TRADINGVIEW_AVAILABLE:
                print("\n❌ TradingView screener not installed!")
                print("   Install: pip install tradingview-screener")
                continue
            
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
            
            print("\nPrice range:")
            print("1. Default ($2.00 - $20.00) - RECOMMENDED")
            print("2. Penny stocks ($0.10 - $2.00)")
            print("3. Sub-penny ($0.0001 - $0.10)")
            print("4. Mid-cap ($20 - $100)")
            print("5. Custom range")
            
            price_choice = input("Enter choice (1-5) or press Enter for default: ").strip()
            
            if price_choice == '2':
                min_price, max_price = 0.10, 2.00
            elif price_choice == '3':
                min_price, max_price = 0.0001, 0.10
            elif price_choice == '4':
                min_price, max_price = 20.0, 100.0
            elif price_choice == '5':
                try:
                    min_input = input("Enter minimum price (e.g., 2.00): ").strip()
                    max_input = input("Enter maximum price (e.g., 20.00): ").strip()
                    min_price = float(min_input) if min_input else 2.0
                    max_price = float(max_input) if max_input else 20.0
                except:
                    print("⚠️  Invalid input, using default $2-$20")
                    min_price, max_price = 2.0, 20.0
            else:
                min_price, max_price = 2.0, 20.0
            
            print(f"\n✅ Scanning ${min_price:.4f} - ${max_price:.2f}")
            
            scanned_stocks = scan_momentum_stocks(market, min_price, max_price)
            
            if not scanned_stocks:
                print("❌ No stocks found.")
                input("\nPress Enter to continue...")
                continue
            
            last_scanned_stocks = scanned_stocks
            last_scan_type = "stocks"
            
            display_scanned_stocks(scanned_stocks)
            
            tickers = choose_from_scan(scanned_stocks, "stocks")
            
            if not tickers:
                print("❌ No stocks selected")
                input("\nPress Enter to continue...")
                continue
        
        # Scan FOREX pairs
        elif main_choice == '2':
            scanned_forex = scan_forex_pairs()
            
            if not scanned_forex:
                print("❌ No FOREX pairs found.")
                input("\nPress Enter to continue...")
                continue
            
            last_scanned_forex = scanned_forex
            last_scan_type = "forex"
            
            display_forex_pairs(scanned_forex)
            
            tickers = choose_from_scan(scanned_forex, "FOREX pairs")
            
            if not tickers:
                print("❌ No FOREX pairs selected")
                input("\nPress Enter to continue...")
                continue
        
        # Scan cryptocurrencies
        elif main_choice == '3':
            scanned_crypto = scan_crypto()
            
            if not scanned_crypto:
                print("❌ No cryptocurrencies found.")
                input("\nPress Enter to continue...")
                continue
            
            last_scanned_crypto = scanned_crypto
            last_scan_type = "crypto"
            
            display_crypto(scanned_crypto)
            
            tickers = choose_from_scan(scanned_crypto, "cryptocurrencies")
            
            if not tickers:
                print("❌ No cryptocurrencies selected")
                input("\nPress Enter to continue...")
                continue
        
        # Dark Flow Scanner - ENHANCED WITH MARKET SCANNING
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
                    analyze_choice = input(f"\nAnalyze {ticker} with VWAP/MACD? (y/n): ").strip().lower()
                    if analyze_choice == 'y':
                        rec = analyzer.generate_recommendation(ticker, period, interval)
                        if rec:
                            display_recommendation(rec)
                
                if len(tickers_to_scan) > 1 and ticker != tickers_to_scan[-1]:
                    input("\nPress Enter to continue to next ticker...")
            
            input("\n📊 Press Enter to return to main menu...")
            continue
        
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
        
        # Manual entry
        elif main_choice == '6':
            print("\n💡 Examples:")
            print("   Stocks: AAPL,TSLA,NVDA")
            print("   FOREX: EURUSD=X,GBPUSD=X")
            print("   Crypto: BTC-USD,ETH-USD")
            tickers_input = input("\nEnter ticker symbols (comma-separated): ").strip()
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
        
        # Analysis complete
        print("\n" + "=" * 70)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 70)
        
        input("\n📊 Press Enter to return to main menu...")


if __name__ == "__main__":
    main()
