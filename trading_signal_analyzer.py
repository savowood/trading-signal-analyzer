"""
Trading Signal Analyzer v0.97 - Entry/Exit Point Prediction
Copyright (C) 2025 Michael Johnson (GitHub: @savowood)

FULLY INTEGRATED VERSION with Enhanced Dark Flow Market Scanner

NEW in v0.97:
- Added extended trading hours support (pre-market and after-hours)
- Pre-market activity analysis (4:00 AM - 9:30 AM ET)
- After-hours activity analysis (4:00 PM - 8:00 PM ET)
- Extended hours price changes, volume, and range displays
- Full integration with all stock data fetching and analysis

NEW in v0.96:
- Added automatic update checker on application launch
- Checks GitHub releases for new versions
- Non-blocking update notification with download link

NEW in v0.95:
- Added RSI indicator (14-period)
- Added SuperTrend indicator with ATR bands
- Added volume confirmation analysis
- Added EMA 9/20 crossover signals
- Added multi-timeframe trend confirmation
- Added comprehensive signal strength scoring (0-100 with grades A-D)
- Added position sizing calculator based on risk per trade
- Added crypto-specific parameter adjustments
- Added CSV export for batch analysis

FIXES in v0.94:
- VWAP bands now use 2σ and 3σ (instead of 1σ and 2σ)
- Stock scanner price filter now properly enforced (min 90% of lower bound)
- Cryptocurrency scanner now dynamic (fetches from CoinGecko API)
- Removed delisted/inactive crypto tickers

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

Technical analysis (VWAP 2σ/3σ, MACD, Enhanced Dark Flow Scanner) implementation is original work.

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

Version: 0.97
NEW 5 PILLARS: +10% Day, 5x RelVol, News Catalyst, $2-$20, <20M Float
Uses VWAP bands (2σ, 3σ) + MACD + RSI + SuperTrend + Signal Scoring for optimal entry/exit
Includes integrated 5 Pillars Scanner + FOREX + Dynamic Crypto + ENHANCED Dark Flow Market Scanner
Extended Hours Support: Pre-market (4AM-9:30AM ET) + After-hours (4PM-8PM ET)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
import requests
import csv
warnings.filterwarnings('ignore')

# Version info
VERSION = "0.97"
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
    
    FIXED: Properly enforces price range (allows down to 90% of min_price to catch stocks moving up)
    
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
        
        # FIXED: Allow 10% below min_price for stocks moving up, but enforce strict upper bound
        adjusted_min = min_price * 0.90  # Allow stocks slightly below min if they're moving up
        
        q = Query()
        
        if market_choice == '3':
            q = q.set_markets('america').where(col('exchange') == 'NASDAQ')
        elif market_choice == '4':
            q = q.set_markets('america').where(col('exchange') == 'NYSE')
        else:
            q = q.set_markets('america')
        
        q = q.where(col('close').between(adjusted_min, max_price))
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
                
                # FIXED: Strict post-filter - only include if within actual target range
                # Exception: allow if stock is between 90-100% of min_price AND moving up strongly
                if price > max_price:
                    continue
                if price < min_price:
                    # Only allow if it's close to min_price (within 10%) and strongly bullish
                    if price < adjusted_min or float(row.get('change_from_open') or 0) < 15:
                        continue
                
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


def get_top_cryptos_from_coingecko(limit: int = 30) -> List[Tuple[str, str]]:
    """
    FIXED: Dynamically fetch top cryptocurrencies from CoinGecko API
    
    Args:
        limit: Number of top coins to fetch (default 30)
        
    Returns:
        List of (yfinance_ticker, coin_name) tuples
    """
    try:
        print("🔍 Fetching top cryptocurrencies from CoinGecko...")
        
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': limit,
            'page': 1,
            'sparkline': False
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Map CoinGecko symbols to Yahoo Finance tickers
        crypto_list = []
        for coin in data:
            symbol = coin['symbol'].upper()
            name = coin['name']
            
            # Map to Yahoo Finance ticker format
            yf_ticker = f"{symbol}-USD"
            
            crypto_list.append((yf_ticker, name))
        
        print(f"✅ Fetched {len(crypto_list)} cryptocurrencies from CoinGecko")
        return crypto_list
        
    except Exception as e:
        print(f"⚠️  Could not fetch from CoinGecko: {e}")
        print("⚠️  Falling back to hardcoded list...")
        
        # Fallback to a curated list if API fails
        return [
            ('BTC-USD', 'Bitcoin'),
            ('ETH-USD', 'Ethereum'),
            ('BNB-USD', 'Binance Coin'),
            ('SOL-USD', 'Solana'),
            ('XRP-USD', 'Ripple'),
            ('ADA-USD', 'Cardano'),
            ('AVAX-USD', 'Avalanche'),
            ('DOGE-USD', 'Dogecoin'),
            ('DOT-USD', 'Polkadot'),
            ('LTC-USD', 'Litecoin'),
            ('SHIB-USD', 'Shiba Inu'),
            ('TRX-USD', 'TRON'),
            ('LINK-USD', 'Chainlink'),
            ('ATOM-USD', 'Cosmos'),
            ('XLM-USD', 'Stellar'),
            ('ALGO-USD', 'Algorand'),
            ('VET-USD', 'VeChain'),
            ('FIL-USD', 'Filecoin'),
            ('HBAR-USD', 'Hedera'),
            ('APT-USD', 'Aptos'),
        ]


def scan_crypto() -> List[Dict]:
    """
    FIXED: Dynamically scan active cryptocurrencies from CoinGecko
    Filters out delisted/inactive coins
    """
    try:
        print("🔍 Scanning top cryptocurrencies...")
        
        # FIXED: Get dynamic list from CoinGecko
        crypto_tickers = get_top_cryptos_from_coingecko(limit=30)
        
        results = []
        
        for ticker, name in crypto_tickers:
            try:
                crypto = yf.Ticker(ticker)
                hist = crypto.history(period='5d', interval='1h')
                
                # FIXED: Skip if no data or clearly delisted
                if hist.empty or len(hist) < 2:
                    print(f"⚠️  Skipping {ticker} ({name}) - no price data")
                    continue
                
                current_price = hist['Close'].iloc[-1]
                
                # FIXED: Skip if price is 0 or NaN
                if pd.isna(current_price) or current_price <= 0:
                    print(f"⚠️  Skipping {ticker} ({name}) - invalid price")
                    continue
                
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
                
                # FIXED: Skip if no volume (likely delisted)
                if volume_24h == 0:
                    print(f"⚠️  Skipping {ticker} ({name}) - no volume")
                    continue
                
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
                print(f"⚠️  Error fetching {ticker} ({name}): {e}")
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
    print("₿ CRYPTOCURRENCIES - TOP ACTIVE COINS (DYNAMIC)")
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
    print("\n💡 List dynamically fetched from CoinGecko API (top 30 by market cap)")
    print("💡 Tip: Crypto trades 24/7 with high volatility")


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
    """Analyzes stocks using VWAP (2σ/3σ), MACD, and risk/reward ratios"""
    
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
        
        upper_2atr = sma + (2 * atr)
        lower_2atr = sma - (2 * atr)
        upper_3atr = sma + (3 * atr)
        lower_3atr = sma - (3 * atr)
        
        return sma, upper_2atr, lower_2atr, upper_3atr, lower_3atr
        
    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Volume Weighted Average Price"""
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        vwap = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
        return vwap
    
    def calculate_vwap_bands(self, df: pd.DataFrame, vwap: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        """
        FIXED: Calculate VWAP standard deviation bands (2σ and 3σ)
        Previously used 1σ and 2σ, now correctly uses 2σ and 3σ
        """
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        
        squared_diff = (typical_price - vwap) ** 2
        weighted_squared_diff = squared_diff * df['Volume']
        variance = weighted_squared_diff.cumsum() / df['Volume'].cumsum()
        std_dev = np.sqrt(variance)
        
        # FIXED: Now using 2σ and 3σ instead of 1σ and 2σ
        upper_2std = vwap + (2 * std_dev)
        lower_2std = vwap - (2 * std_dev)
        upper_3std = vwap + (3 * std_dev)
        lower_3std = vwap - (3 * std_dev)
        
        return upper_2std, lower_2std, upper_3std, lower_3std
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD indicator"""
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI)"""
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def calculate_supertrend(self, df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate SuperTrend indicator using ATR bands"""
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        hl2 = (df['High'] + df['Low']) / 2
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)

        supertrend = pd.Series(index=df.index, dtype=float)
        direction = pd.Series(index=df.index, dtype=int)

        for i in range(period, len(df)):
            if i == period:
                supertrend.iloc[i] = upper_band.iloc[i] if df['Close'].iloc[i] <= hl2.iloc[i] else lower_band.iloc[i]
                direction.iloc[i] = -1 if df['Close'].iloc[i] <= hl2.iloc[i] else 1
            else:
                if df['Close'].iloc[i] > supertrend.iloc[i-1]:
                    supertrend.iloc[i] = lower_band.iloc[i]
                    direction.iloc[i] = 1
                elif df['Close'].iloc[i] < supertrend.iloc[i-1]:
                    supertrend.iloc[i] = upper_band.iloc[i]
                    direction.iloc[i] = -1
                else:
                    supertrend.iloc[i] = supertrend.iloc[i-1]
                    direction.iloc[i] = direction.iloc[i-1]

                if direction.iloc[i] == 1 and supertrend.iloc[i] < supertrend.iloc[i-1]:
                    supertrend.iloc[i] = supertrend.iloc[i-1]
                elif direction.iloc[i] == -1 and supertrend.iloc[i] > supertrend.iloc[i-1]:
                    supertrend.iloc[i] = supertrend.iloc[i-1]

        return supertrend, upper_band, lower_band

    def calculate_ema_cross(self, df: pd.DataFrame, fast: int = 9, slow: int = 20) -> Dict:
        """Calculate EMA crossover signals"""
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()

        current_fast = ema_fast.iloc[-1]
        current_slow = ema_slow.iloc[-1]
        prev_fast = ema_fast.iloc[-2] if len(ema_fast) > 1 else current_fast
        prev_slow = ema_slow.iloc[-2] if len(ema_slow) > 1 else current_slow

        bullish_cross = (current_fast > current_slow) and (prev_fast <= prev_slow)
        bearish_cross = (current_fast < current_slow) and (prev_fast >= prev_slow)

        return {
            'ema_fast': current_fast,
            'ema_slow': current_slow,
            'bullish': current_fast > current_slow,
            'bullish_cross': bullish_cross,
            'bearish_cross': bearish_cross
        }

    def check_volume_confirmation(self, df: pd.DataFrame, lookback: int = 20) -> Dict:
        """Check if current volume confirms the move"""
        if not self.has_volume_data(df):
            return {'confirmed': None, 'rel_volume': 0, 'description': 'No volume data'}

        current_volume = df['Volume'].iloc[-1]
        avg_volume = df['Volume'].iloc[-lookback:].mean()
        rel_volume = current_volume / avg_volume if avg_volume > 0 else 0

        confirmed = rel_volume >= 1.5

        if rel_volume >= 3.0:
            description = "Very High Volume"
        elif rel_volume >= 2.0:
            description = "High Volume"
        elif rel_volume >= 1.5:
            description = "Above Average Volume"
        elif rel_volume >= 0.75:
            description = "Normal Volume"
        else:
            description = "Low Volume"

        return {
            'confirmed': confirmed,
            'rel_volume': rel_volume,
            'description': description
        }

    def analyze_extended_hours(self, df: pd.DataFrame) -> Dict:
        """Analyze pre-market and after-hours trading activity"""
        try:
            if df.empty:
                return None

            # Get market hours (9:30 AM - 4:00 PM ET)
            # Pre-market: 4:00 AM - 9:30 AM ET
            # After-hours: 4:00 PM - 8:00 PM ET

            extended_hours_data = {
                'has_premarket': False,
                'has_afterhours': False,
                'premarket_change': 0.0,
                'afterhours_change': 0.0,
                'premarket_volume': 0,
                'afterhours_volume': 0,
                'last_regular_close': None,
                'premarket_high': None,
                'premarket_low': None,
                'afterhours_high': None,
                'afterhours_low': None
            }

            # Get the most recent day's data
            if len(df) < 2:
                return extended_hours_data

            # Get timezone-aware timestamps
            latest_time = df.index[-1]

            # Find regular market hours (9:30 AM - 4:00 PM ET)
            # Pre-market is 4:00 AM - 9:30 AM ET
            # After-hours is 4:00 PM - 8:00 PM ET

            # Get last 24 hours of data
            cutoff_time = latest_time - timedelta(hours=24)
            recent_df = df[df.index > cutoff_time].copy()

            if recent_df.empty:
                return extended_hours_data

            # Convert to ET timezone for analysis
            try:
                if recent_df.index.tz is None:
                    recent_df.index = recent_df.index.tz_localize('America/New_York')
                else:
                    recent_df.index = recent_df.index.tz_convert('America/New_York')
            except:
                # If timezone conversion fails, use simple hour check
                pass

            # Separate by time of day
            premarket_data = []
            afterhours_data = []
            regular_hours_data = []

            for idx, row in recent_df.iterrows():
                hour = idx.hour
                minute = idx.minute

                # Pre-market: 4:00 AM - 9:29 AM
                if (hour >= 4 and hour < 9) or (hour == 9 and minute < 30):
                    premarket_data.append(row)
                # After-hours: 4:00 PM - 8:00 PM
                elif hour >= 16 and hour < 20:
                    afterhours_data.append(row)
                # Regular hours: 9:30 AM - 3:59 PM
                elif (hour == 9 and minute >= 30) or (hour >= 10 and hour < 16):
                    regular_hours_data.append(row)

            # Get last regular market close
            if regular_hours_data:
                extended_hours_data['last_regular_close'] = regular_hours_data[-1]['Close']

            # Analyze pre-market
            if premarket_data:
                premarket_df = pd.DataFrame(premarket_data)
                extended_hours_data['has_premarket'] = True
                extended_hours_data['premarket_volume'] = int(premarket_df['Volume'].sum())
                extended_hours_data['premarket_high'] = float(premarket_df['High'].max())
                extended_hours_data['premarket_low'] = float(premarket_df['Low'].min())

                if extended_hours_data['last_regular_close']:
                    premarket_current = premarket_df['Close'].iloc[-1]
                    extended_hours_data['premarket_change'] = (
                        (premarket_current - extended_hours_data['last_regular_close']) /
                        extended_hours_data['last_regular_close'] * 100
                    )

            # Analyze after-hours
            if afterhours_data:
                afterhours_df = pd.DataFrame(afterhours_data)
                extended_hours_data['has_afterhours'] = True
                extended_hours_data['afterhours_volume'] = int(afterhours_df['Volume'].sum())
                extended_hours_data['afterhours_high'] = float(afterhours_df['High'].max())
                extended_hours_data['afterhours_low'] = float(afterhours_df['Low'].min())

                if extended_hours_data['last_regular_close']:
                    afterhours_current = afterhours_df['Close'].iloc[-1]
                    extended_hours_data['afterhours_change'] = (
                        (afterhours_current - extended_hours_data['last_regular_close']) /
                        extended_hours_data['last_regular_close'] * 100
                    )

            return extended_hours_data

        except Exception as e:
            # Return default data if analysis fails
            return {
                'has_premarket': False,
                'has_afterhours': False,
                'premarket_change': 0.0,
                'afterhours_change': 0.0,
                'premarket_volume': 0,
                'afterhours_volume': 0
            }

    def check_multi_timeframe(self, ticker: str, asset_type: str = 'stock') -> Dict:
        """Check trend across multiple timeframes for confirmation"""
        try:
            stock = yf.Ticker(ticker)

            if asset_type == 'crypto':
                tf_1h = stock.history(period='7d', interval='1h')
                tf_4h = stock.history(period='30d', interval='1h')
                tf_1d = stock.history(period='90d', interval='1d')
            elif asset_type == 'stock':
                # Include extended hours for stock analysis
                tf_1h = stock.history(period='5d', interval='1h', prepost=True)
                tf_4h = stock.history(period='1mo', interval='1d', prepost=True)
                tf_1d = stock.history(period='3mo', interval='1d', prepost=True)
            else:
                tf_1h = stock.history(period='5d', interval='1h')
                tf_4h = stock.history(period='1mo', interval='1d')
                tf_1d = stock.history(period='3mo', interval='1d')

            def get_trend(df_tf, period=20):
                if df_tf.empty or len(df_tf) < period:
                    return 'unknown'
                ema = df_tf['Close'].ewm(span=period, adjust=False).mean()
                current_price = df_tf['Close'].iloc[-1]
                return 'bullish' if current_price > ema.iloc[-1] else 'bearish'

            trend_1h = get_trend(tf_1h, 20)
            trend_4h = get_trend(tf_4h, 20)
            trend_1d = get_trend(tf_1d, 50)

            bullish_count = [trend_1h, trend_4h, trend_1d].count('bullish')

            if bullish_count == 3:
                alignment = 'strong_bullish'
            elif bullish_count == 2:
                alignment = 'bullish'
            elif bullish_count == 1:
                alignment = 'bearish'
            else:
                alignment = 'strong_bearish'

            return {
                'trend_1h': trend_1h,
                'trend_4h': trend_4h,
                'trend_1d': trend_1d,
                'alignment': alignment,
                'bullish_timeframes': bullish_count
            }
        except:
            return {
                'trend_1h': 'unknown',
                'trend_4h': 'unknown',
                'trend_1d': 'unknown',
                'alignment': 'unknown',
                'bullish_timeframes': 0
            }

    def calculate_signal_score(self, analysis: Dict) -> Dict:
        """Calculate comprehensive signal strength score (0-100) with letter grade"""
        score = 0
        factors = []

        # VWAP/SMA Position (0-20 points)
        price_vs_vwap = analysis.get('price_vs_vwap', 0)
        if analysis.get('macd_bullish', False):
            if -2 < price_vs_vwap < 2:
                score += 20
                factors.append("Perfect VWAP alignment")
            elif -5 < price_vs_vwap < 5:
                score += 15
                factors.append("Good VWAP position")
            elif price_vs_vwap < -5:
                score += 10
                factors.append("Below VWAP (potential entry)")
            else:
                score += 5
                factors.append("Above VWAP (extended)")

        # MACD Signal (0-20 points)
        if analysis.get('macd_crossover', False):
            score += 20
            factors.append("MACD bullish crossover")
        elif analysis.get('macd_bullish', False) and analysis.get('histogram_increasing', False):
            score += 15
            factors.append("MACD bullish & strengthening")
        elif analysis.get('macd_bullish', False):
            score += 10
            factors.append("MACD bullish")

        # RSI (0-15 points)
        rsi = analysis.get('rsi', 50)
        if 40 < rsi < 60:
            score += 15
            factors.append("RSI neutral (ideal for entry)")
        elif 30 < rsi < 70:
            score += 10
            factors.append("RSI in normal range")
        elif rsi < 30:
            score += 12
            factors.append("RSI oversold (potential bounce)")
        else:
            score += 5
            factors.append("RSI overbought (caution)")

        # SuperTrend (0-15 points)
        if analysis.get('supertrend_bullish', False):
            score += 15
            factors.append("SuperTrend bullish")

        # EMA Crossover (0-10 points)
        ema_data = analysis.get('ema_cross', {})
        if ema_data.get('bullish_cross', False):
            score += 10
            factors.append("EMA 9/20 bullish cross")
        elif ema_data.get('bullish', False):
            score += 7
            factors.append("EMA 9/20 bullish")

        # Volume Confirmation (0-10 points)
        volume_data = analysis.get('volume_check', {})
        if volume_data.get('confirmed', False):
            score += 10
            factors.append(f"Volume confirmed ({volume_data.get('description', '')})")
        elif volume_data.get('rel_volume', 0) >= 1.0:
            score += 5
            factors.append("Average volume")

        # Multi-Timeframe Alignment (0-10 points)
        mtf = analysis.get('multi_timeframe', {})
        alignment = mtf.get('alignment', 'unknown')
        if alignment == 'strong_bullish':
            score += 10
            factors.append("All timeframes bullish")
        elif alignment == 'bullish':
            score += 7
            factors.append("2/3 timeframes bullish")
        elif alignment == 'bearish':
            score += 3
            factors.append("Only 1 timeframe bullish")

        # Assign letter grade
        if score >= 85:
            grade = 'A'
            quality = 'Excellent'
        elif score >= 70:
            grade = 'B'
            quality = 'Good'
        elif score >= 55:
            grade = 'C'
            quality = 'Fair'
        elif score >= 40:
            grade = 'D'
            quality = 'Poor'
        else:
            grade = 'F'
            quality = 'Very Poor'

        return {
            'score': score,
            'grade': grade,
            'quality': quality,
            'factors': factors
        }

    def calculate_position_size(self, account_balance: float, risk_per_trade: float,
                               entry_price: float, stop_loss: float) -> Dict:
        """Calculate position size based on risk management"""
        risk_amount = account_balance * (risk_per_trade / 100)
        risk_per_share = abs(entry_price - stop_loss)

        if risk_per_share == 0:
            return {
                'shares': 0,
                'position_value': 0,
                'risk_amount': risk_amount,
                'error': 'Stop loss equals entry price'
            }

        shares = risk_amount / risk_per_share
        position_value = shares * entry_price
        percent_of_account = (position_value / account_balance) * 100

        return {
            'shares': int(shares),
            'position_value': position_value,
            'risk_amount': risk_amount,
            'risk_per_share': risk_per_share,
            'percent_of_account': percent_of_account
        }

    def analyze_stock(self, ticker: str, period: str = "5d", interval: str = "5m",
                     asset_type: str = 'stock') -> Optional[Dict]:
        """Perform complete technical analysis on a stock/forex/crypto"""
        try:
            stock = yf.Ticker(ticker)
            # Include extended hours (pre-market and after-hours) for stocks
            if asset_type == 'stock':
                df = stock.history(period=period, interval=interval, prepost=True)
            else:
                df = stock.history(period=period, interval=interval)
            
            if df.empty or len(df) < 26:
                return None
            
            current_price = df['Close'].iloc[-1]
            
            has_volume = self.has_volume_data(df)
            
            if has_volume:
                vwap = self.calculate_vwap(df)
                upper_2std, lower_2std, upper_3std, lower_3std = self.calculate_vwap_bands(df, vwap)
                
                current_vwap = vwap.iloc[-1]
                current_upper_2std = upper_2std.iloc[-1]
                current_lower_2std = lower_2std.iloc[-1]
                current_upper_3std = upper_3std.iloc[-1]
                current_lower_3std = lower_3std.iloc[-1]
                indicator_type = "VWAP"
            else:
                sma, upper_2atr, lower_2atr, upper_3atr, lower_3atr = self.calculate_sma_atr_bands(df)
                
                current_vwap = sma.iloc[-1]
                current_upper_2std = upper_2atr.iloc[-1]
                current_lower_2std = lower_2atr.iloc[-1]
                current_upper_3std = upper_3atr.iloc[-1]
                current_lower_3std = lower_3atr.iloc[-1]
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
            
            # FIXED: Updated zone descriptions to reflect 2σ and 3σ
            if current_price > current_upper_3std:
                vwap_zone = "Above 3σ (Extremely Overbought)"
            elif current_price > current_upper_2std:
                vwap_zone = "Between 2σ and 3σ (Overbought)"
            elif current_price > current_vwap:
                if indicator_type == "VWAP":
                    vwap_zone = "Between VWAP and 2σ (Upper)"
                else:
                    vwap_zone = "Between SMA and 2σ (Upper)"
            elif current_price > current_lower_2std:
                if indicator_type == "VWAP":
                    vwap_zone = "Between VWAP and 2σ (Lower)"
                else:
                    vwap_zone = "Between SMA and 2σ (Lower)"
            elif current_price > current_lower_3std:
                vwap_zone = "Between 2σ and 3σ (Oversold)"
            else:
                vwap_zone = "Below 3σ (Extremely Oversold)"

            # Calculate new indicators (v0.95)
            rsi = self.calculate_rsi(df)
            current_rsi = rsi.iloc[-1] if len(rsi) > 0 and not pd.isna(rsi.iloc[-1]) else 50

            supertrend, st_upper, st_lower = self.calculate_supertrend(df)
            current_supertrend = supertrend.iloc[-1] if len(supertrend) > 0 and not pd.isna(supertrend.iloc[-1]) else current_price
            supertrend_bullish = current_price > current_supertrend

            ema_cross = self.calculate_ema_cross(df)
            volume_check = self.check_volume_confirmation(df)
            multi_timeframe = self.check_multi_timeframe(ticker, asset_type)

            # Analyze extended hours for stocks
            extended_hours = None
            if asset_type == 'stock':
                extended_hours = self.analyze_extended_hours(df)

            # Create analysis dict
            analysis_dict = {
                'ticker': ticker,
                'current_price': current_price,
                'vwap': current_vwap,
                'upper_2std': current_upper_2std,
                'lower_2std': current_lower_2std,
                'upper_3std': current_upper_3std,
                'lower_3std': current_lower_3std,
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
                'rsi': current_rsi,
                'supertrend': current_supertrend,
                'supertrend_bullish': supertrend_bullish,
                'ema_cross': ema_cross,
                'volume_check': volume_check,
                'multi_timeframe': multi_timeframe,
                'extended_hours': extended_hours,
                'asset_type': asset_type,
                'dataframe': df
            }

            # Calculate signal score
            signal_score = self.calculate_signal_score(analysis_dict)
            analysis_dict['signal_score'] = signal_score

            return analysis_dict
            
        except Exception as e:
            print(f"⚠️  Error analyzing {ticker}: {e}")
            return None
    
    def calculate_entry_exit(self, analysis: Dict) -> Dict:
        """Calculate optimal entry, stop loss, and take profit levels (using 2σ and 3σ)"""
        current_price = analysis['current_price']
        vwap = analysis['vwap']
        lower_2std = analysis['lower_2std']
        upper_2std = analysis['upper_2std']
        lower_3std = analysis['lower_3std']
        upper_3std = analysis['upper_3std']
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
            elif current_price <= upper_2std:
                entry_point = vwap
                if indicator_type == "SMA":
                    entry_reason = "Wait for pullback to SMA"
                else:
                    entry_reason = "Wait for pullback to VWAP"
            else:
                entry_point = upper_2std
                entry_reason = "Price extended - wait for pullback to 2σ"
            
            if entry_point > vwap:
                stop_loss = vwap * 0.995
            else:
                stop_loss = lower_2std * 0.995
            
            risk = entry_point - stop_loss
            take_profit = entry_point + (risk * self.risk_reward_ratio)
            
            # FIXED: Reference 3σ in recommendations
            if take_profit > upper_3std:
                suggested_ratio = (upper_3std - entry_point) / risk if risk > 0 else self.risk_reward_ratio
                ratio_recommendation = f"Consider {suggested_ratio:.1f}:1 (TP at 3σ: ${upper_3std:.2f})"
            else:
                ratio_recommendation = f"{self.risk_reward_ratio}:1 ratio is appropriate"
            
            trade_direction = "LONG"
            
        else:
            entry_point = current_price
            entry_reason = "Bearish MACD - consider shorting or avoiding"
            
            if current_price > vwap:
                stop_loss = upper_2std * 1.005
            else:
                stop_loss = vwap * 1.005
            
            risk = stop_loss - entry_point
            take_profit = entry_point - (risk * self.risk_reward_ratio)
            
            # FIXED: Reference 3σ in recommendations
            if take_profit < lower_3std:
                suggested_ratio = (entry_point - lower_3std) / risk if risk > 0 else self.risk_reward_ratio
                ratio_recommendation = f"Consider {suggested_ratio:.1f}:1 (TP at 3σ: ${lower_3std:.2f})"
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
    
    def generate_recommendation(self, ticker: str, period: str = "5d", interval: str = "5m",
                               asset_type: str = 'stock') -> Optional[Dict]:
        """Generate complete trading recommendation"""
        analysis = self.analyze_stock(ticker, period, interval, asset_type)

        if not analysis:
            return None

        entry_exit = self.calculate_entry_exit(analysis)

        return {
            **analysis,
            **entry_exit
        }


def display_recommendation(rec: Dict):
    """Display formatted trading recommendation (with 2σ and 3σ bands)"""
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

    # Display extended hours information for stocks
    if rec.get('extended_hours') and rec.get('asset_type') == 'stock':
        ext_hours = rec['extended_hours']

        if ext_hours.get('has_premarket') or ext_hours.get('has_afterhours'):
            print(f"\n🌅 EXTENDED HOURS ACTIVITY:")

            if ext_hours.get('has_premarket'):
                pm_change = ext_hours['premarket_change']
                pm_emoji = "🟢" if pm_change > 0 else "🔴" if pm_change < 0 else "⚪"
                pm_volume = ext_hours.get('premarket_volume', 0)

                print(f"   Pre-Market: {pm_emoji} {pm_change:+.2f}%", end="")
                if pm_volume > 0:
                    print(f" | Vol: {pm_volume:,}", end="")

                pm_high = ext_hours.get('premarket_high')
                pm_low = ext_hours.get('premarket_low')
                if pm_high and pm_low:
                    if price < 0.01:
                        print(f" | Range: ${pm_low:.6f} - ${pm_high:.6f}")
                    elif price < 0.10:
                        print(f" | Range: ${pm_low:.4f} - ${pm_high:.4f}")
                    elif price < 1.00:
                        print(f" | Range: ${pm_low:.3f} - ${pm_high:.3f}")
                    else:
                        print(f" | Range: ${pm_low:.2f} - ${pm_high:.2f}")
                else:
                    print()

            if ext_hours.get('has_afterhours'):
                ah_change = ext_hours['afterhours_change']
                ah_emoji = "🟢" if ah_change > 0 else "🔴" if ah_change < 0 else "⚪"
                ah_volume = ext_hours.get('afterhours_volume', 0)

                print(f"   After-Hours: {ah_emoji} {ah_change:+.2f}%", end="")
                if ah_volume > 0:
                    print(f" | Vol: {ah_volume:,}", end="")

                ah_high = ext_hours.get('afterhours_high')
                ah_low = ext_hours.get('afterhours_low')
                if ah_high and ah_low:
                    if price < 0.01:
                        print(f" | Range: ${ah_low:.6f} - ${ah_high:.6f}")
                    elif price < 0.10:
                        print(f" | Range: ${ah_low:.4f} - ${ah_high:.4f}")
                    elif price < 1.00:
                        print(f" | Range: ${ah_low:.3f} - ${ah_high:.3f}")
                    else:
                        print(f" | Range: ${ah_low:.2f} - ${ah_high:.2f}")
                else:
                    print()

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
    
    # FIXED: Display 2σ and 3σ bands
    if indicator_type == "SMA":
        print(f"📈 SMA(20): {vwap_format} ({rec['price_vs_vwap']:+.2f}%)")
        print(f"📍 Position: {rec['vwap_zone']}")
        print(f"\n📉 SMA + ATR BANDS (2σ and 3σ):")
        print(f"   +3 ATR: ${rec['upper_3std']:.{band_decimals}f}")
        print(f"   +2 ATR: ${rec['upper_2std']:.{band_decimals}f}")
        print(f"   SMA: ${rec['vwap']:.{band_decimals}f}")
        print(f"   -2 ATR: ${rec['lower_2std']:.{band_decimals}f}")
        print(f"   -3 ATR: ${rec['lower_3std']:.{band_decimals}f}")
    else:
        print(f"📈 VWAP: {vwap_format} ({rec['price_vs_vwap']:+.2f}%)")
        print(f"📍 Position: {rec['vwap_zone']}")
        print(f"\n📉 VWAP BANDS (2σ and 3σ):")
        print(f"   +3σ: ${rec['upper_3std']:.{band_decimals}f}")
        print(f"   +2σ: ${rec['upper_2std']:.{band_decimals}f}")
        print(f"   VWAP: ${rec['vwap']:.{band_decimals}f}")
        print(f"   -2σ: ${rec['lower_2std']:.{band_decimals}f}")
        print(f"   -3σ: ${rec['lower_3std']:.{band_decimals}f}")
    
    print(f"\n📊 MACD:")
    print(f"   MACD Line: {rec['macd']:.4f}")
    print(f"   Signal Line: {rec['signal']:.4f}")
    print(f"   Histogram: {rec['histogram']:.4f}")

    if rec['macd_crossover']:
        print(f"   🔥 BULLISH CROSSOVER!")
    elif rec['macd_crossunder']:
        print(f"   ❄️  BEARISH CROSSUNDER!")

    # Display new indicators (v0.95)
    if 'rsi' in rec:
        rsi = rec['rsi']
        rsi_status = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
        print(f"\n📊 RSI(14): {rsi:.2f} ({rsi_status})")

    if 'supertrend_bullish' in rec:
        st_emoji = "🟢" if rec['supertrend_bullish'] else "🔴"
        st_status = "Bullish" if rec['supertrend_bullish'] else "Bearish"
        print(f"\n📊 SuperTrend: {st_emoji} {st_status}")
        print(f"   Level: ${rec['supertrend']:.{band_decimals}f}")

    if 'ema_cross' in rec:
        ema = rec['ema_cross']
        if ema.get('bullish_cross'):
            print(f"\n📊 EMA 9/20: 🔥 BULLISH CROSSOVER!")
        elif ema.get('bearish_cross'):
            print(f"\n📊 EMA 9/20: ❄️  BEARISH CROSSUNDER!")
        elif ema.get('bullish'):
            print(f"\n📊 EMA 9/20: 🟢 Bullish")
        else:
            print(f"\n📊 EMA 9/20: 🔴 Bearish")

    if 'volume_check' in rec and rec['volume_check'].get('confirmed') is not None:
        vol = rec['volume_check']
        vol_emoji = "✅" if vol['confirmed'] else "⚠️"
        print(f"\n📊 Volume: {vol_emoji} {vol['description']} ({vol['rel_volume']:.2f}x avg)")

    if 'multi_timeframe' in rec:
        mtf = rec['multi_timeframe']
        alignment = mtf.get('alignment', 'unknown')
        if alignment == 'strong_bullish':
            print(f"\n📊 Multi-Timeframe: 🟢🟢🟢 All timeframes bullish")
        elif alignment == 'bullish':
            print(f"\n📊 Multi-Timeframe: 🟢🟢 2/3 timeframes bullish")
        elif alignment == 'bearish':
            print(f"\n📊 Multi-Timeframe: 🟢 1/3 timeframes bullish")
        elif alignment == 'strong_bearish':
            print(f"\n📊 Multi-Timeframe: 🔴🔴🔴 All timeframes bearish")

    if 'signal_score' in rec:
        score_data = rec['signal_score']
        grade = score_data['grade']
        score = score_data['score']
        quality = score_data['quality']
        print(f"\n🎯 SIGNAL SCORE: {score}/100 (Grade: {grade} - {quality})")
        if score_data.get('factors'):
            print(f"   Key Factors:")
            for factor in score_data['factors'][:5]:
                print(f"   • {factor}")

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


def detect_asset_type(ticker: str) -> str:
    """Detect asset type from ticker format"""
    ticker_upper = ticker.upper()

    # FOREX pairs end with =X
    if ticker_upper.endswith('=X'):
        return 'forex'

    # Crypto pairs typically contain -USD, -USDT, etc
    if '-USD' in ticker_upper or '-USDT' in ticker_upper or '-BTC' in ticker_upper:
        return 'crypto'

    # Default to stock
    return 'stock'


def export_to_csv(recommendations: List[Dict], filename: str = None):
    """Export analysis results to CSV file"""
    if not recommendations:
        print("⚠️  No data to export")
        return

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trading_signals_{timestamp}.csv"

    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'Ticker', 'Price', 'Direction', 'Signal_Score', 'Grade',
                'RSI', 'MACD_Signal', 'SuperTrend', 'Volume_Confirmed',
                'MTF_Alignment', 'Entry', 'Stop_Loss', 'Take_Profit',
                'Risk_Reward', 'Position_Size_Shares'
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for rec in recommendations:
                signal_score = rec.get('signal_score', {})
                volume_check = rec.get('volume_check', {})
                mtf = rec.get('multi_timeframe', {})

                row = {
                    'Ticker': rec.get('ticker', 'N/A'),
                    'Price': f"{rec.get('current_price', 0):.2f}",
                    'Direction': rec.get('trade_direction', 'N/A'),
                    'Signal_Score': signal_score.get('score', 0),
                    'Grade': signal_score.get('grade', 'N/A'),
                    'RSI': f"{rec.get('rsi', 0):.2f}",
                    'MACD_Signal': 'Bullish' if rec.get('macd_bullish') else 'Bearish',
                    'SuperTrend': 'Bullish' if rec.get('supertrend_bullish') else 'Bearish',
                    'Volume_Confirmed': 'Yes' if volume_check.get('confirmed') else 'No',
                    'MTF_Alignment': mtf.get('alignment', 'unknown'),
                    'Entry': f"{rec.get('entry_point', 0):.2f}",
                    'Stop_Loss': f"{rec.get('stop_loss', 0):.2f}",
                    'Take_Profit': f"{rec.get('take_profit', 0):.2f}",
                    'Risk_Reward': f"{rec.get('risk_reward_ratio', 0):.2f}",
                    'Position_Size_Shares': 'N/A'
                }
                writer.writerow(row)

        print(f"✅ Data exported to {filename}")
        return filename

    except Exception as e:
        print(f"❌ Error exporting to CSV: {e}")
        return None


def calculate_batch_position_sizes(recommendations: List[Dict], account_balance: float,
                                   risk_per_trade: float = 1.0) -> List[Dict]:
    """Calculate position sizes for a batch of recommendations"""
    analyzer = TechnicalAnalyzer()

    for rec in recommendations:
        entry = rec.get('entry_point', 0)
        stop = rec.get('stop_loss', 0)

        if entry > 0 and stop > 0:
            position = analyzer.calculate_position_size(
                account_balance, risk_per_trade, entry, stop
            )
            rec['position_size'] = position

    return recommendations


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
            # Include extended hours for comprehensive volume analysis
            df = stock.history(period=period, interval="1h", prepost=True)
            
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


def check_for_updates():
    """Check for updates from GitHub releases"""
    try:
        # Query GitHub API for latest release
        url = "https://api.github.com/repos/savowood/trading-signal-analyzer/releases/latest"
        response = requests.get(url, timeout=2)

        if response.status_code == 200:
            latest_version = response.json().get('tag_name', '').lstrip('v')

            # Compare versions (simple string comparison works for semantic versioning)
            if latest_version and latest_version != VERSION:
                # Parse versions for proper comparison
                try:
                    current_parts = [int(x) for x in VERSION.split('.')]
                    latest_parts = [int(x) for x in latest_version.split('.')]

                    # Pad to same length
                    max_len = max(len(current_parts), len(latest_parts))
                    current_parts.extend([0] * (max_len - len(current_parts)))
                    latest_parts.extend([0] * (max_len - len(latest_parts)))

                    if latest_parts > current_parts:
                        print("\n" + "🔔" * 40)
                        print(f"📢 UPDATE AVAILABLE!")
                        print(f"   Current version: v{VERSION}")
                        print(f"   Latest version:  v{latest_version}")
                        print(f"   Download: https://github.com/savowood/trading-signal-analyzer/releases/latest")
                        print("🔔" * 40 + "\n")
                except (ValueError, AttributeError):
                    # If version parsing fails, just do string comparison
                    if latest_version > VERSION:
                        print(f"\n📢 Update available: v{latest_version} (current: v{VERSION})")
                        print(f"   Download: https://github.com/savowood/trading-signal-analyzer/releases/latest\n")
    except:
        # Silently fail - don't block app if update check fails
        pass


def main():
    """Main application"""
    print("=" * 80)
    print(f"TRADING SIGNAL ANALYZER v{VERSION}")
    print("Comprehensive Technical Analysis with Signal Scoring")
    print("=" * 80)
    print(f"Author: {AUTHOR} | License: {LICENSE}")
    print(f"Based on the 5 Pillars of Day Trading methodology")

    # Check for updates
    check_for_updates()
    print("\nNEW in v0.97:")
    print("  🌅 Extended Trading Hours Support")
    print("  🌅 Pre-Market Analysis (4:00 AM - 9:30 AM ET)")
    print("  🌅 After-Hours Analysis (4:00 PM - 8:00 PM ET)")
    print("  🌅 Extended Hours Price Changes, Volume & Ranges")
    print("\nFROM v0.96:")
    print("  🔔 Automatic Update Checker on Launch")
    print("\nFROM v0.95:")
    print("  ✨ RSI Indicator (14-period)")
    print("  ✨ SuperTrend Indicator (ATR-based)")
    print("  ✨ EMA 9/20 Crossover Signals")
    print("  ✨ Volume Confirmation Analysis")
    print("  ✨ Multi-Timeframe Trend Alignment")
    print("  ✨ Signal Strength Scoring (0-100 with A-F grades)")
    print("  ✨ Position Sizing Calculator")
    print("  ✨ CSV Export for Batch Analysis")
    print("=" * 80)
    
    show_disclaimer()

    print("=" * 80)
    print("📊 TECHNICAL ANALYSIS INDICATORS")
    print("=" * 80)
    print("VWAP (2σ/3σ) • MACD • RSI • SuperTrend • EMA 9/20")
    print("Volume Confirmation • Multi-Timeframe Analysis • Signal Scoring")
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
    last_scanned_dark_flow = []
    last_scan_type = None
    
    # Main loop
    while True:
        print("\n" + "=" * 70)
        print(f"TRADING SIGNAL ANALYZER v{VERSION}")
        print("=" * 70)
        print(f"Settings: {timeframe_name} ({period}/{interval}) | R:R {risk_reward}:1")
        print(f"Analysis: VWAP • MACD • RSI • SuperTrend • EMA • Volume • MTF • Scoring")
        print("=" * 70)

        print("\n📊 SCANNERS (Find Opportunities)")
        print("  1. Momentum Scanner - High volume stocks breaking out")
        print("  2. FOREX Scanner - Top 10 currency pairs")
        print("  3. Crypto Scanner - Top 30+ cryptocurrencies")
        print("  4. Dark Flow Scanner - Institutional activity detection")

        print("\n🔍 ANALYSIS (Deep Dive)")
        print("  5. Analyze from last scan")
        print("  6. Enter ticker manually")
        print("  7. Batch analysis with CSV export")

        print("\n⚙️  TOOLS & SETTINGS")
        print("  8. Position size calculator")
        print(f"  9. Change risk/reward ratio (current: {risk_reward}:1)")
        print(f"  10. Change timeframe (current: {timeframe_name})")
        print("  11. Quit")

        main_choice = input("\nEnter choice (1-11): ").strip()

        # Quit
        if main_choice == '11':
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
        elif main_choice == '9':
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
        elif main_choice == '10':
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

        # Batch CSV Export
        elif main_choice == '7':
            if not last_scan_type:
                print("\n❌ No previous scan results. Run a scan first (options 1-4)")
                input("\nPress Enter to continue...")
                continue

            print("\n" + "=" * 70)
            print("📊 BATCH ANALYSIS WITH CSV EXPORT")
            print("=" * 70)

            # Get tickers from last scan
            if last_scan_type == "stocks":
                display_scanned_stocks(last_scanned_stocks)
                tickers_to_export = choose_from_scan(last_scanned_stocks, "stocks")
            elif last_scan_type == "forex":
                display_forex_pairs(last_scanned_forex)
                tickers_to_export = choose_from_scan(last_scanned_forex, "FOREX pairs")
            elif last_scan_type == "crypto":
                display_crypto(last_scanned_crypto)
                tickers_to_export = choose_from_scan(last_scanned_crypto, "cryptocurrencies")
            elif last_scan_type == "dark_flow":
                display_dark_flow_scan_results(last_scanned_dark_flow)
                print("\nEnter numbers (e.g., 1,2,3) or 'all':")
                selection = input("Your selection: ").strip().lower()
                if selection == 'all':
                    tickers_to_export = [s['Ticker'] for s in last_scanned_dark_flow]
                else:
                    try:
                        indices = [int(x.strip()) for x in selection.split(',')]
                        tickers_to_export = [last_scanned_dark_flow[i-1]['Ticker'] for i in indices
                                           if 1 <= i <= len(last_scanned_dark_flow)]
                    except:
                        tickers_to_export = []
            else:
                tickers_to_export = []

            if not tickers_to_export:
                print("❌ No tickers selected")
                input("\nPress Enter to continue...")
                continue

            # Analyze all and store results
            print(f"\n🔍 Analyzing {len(tickers_to_export)} ticker(s) for CSV export...")
            recommendations = []

            for idx, ticker in enumerate(tickers_to_export, 1):
                print(f"⏳ Analyzing {ticker} ({idx}/{len(tickers_to_export)})...")
                asset_type = detect_asset_type(ticker)
                rec = analyzer.generate_recommendation(ticker, period, interval, asset_type)
                if rec:
                    recommendations.append(rec)

            if recommendations:
                # Export to CSV
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"trading_signals_{timestamp}.csv"
                export_to_csv(recommendations, filename)

                print(f"\n✅ Analyzed {len(recommendations)} ticker(s)")
                print(f"📁 Results exported to: {filename}")
            else:
                print("\n⚠️  No successful analyses to export")

            input("\n📊 Press Enter to return to main menu...")
            continue

        # Position Size Calculator
        elif main_choice == '8':
            print("\n" + "=" * 70)
            print("💰 POSITION SIZE CALCULATOR")
            print("=" * 70)
            print("\nCalculate optimal position size based on account risk management")

            try:
                account_balance = float(input("\nEnter account balance ($): ").strip())
                risk_percent = float(input("Risk per trade (%, e.g., 1 for 1%): ").strip())
                entry_price = float(input("Entry price ($): ").strip())
                stop_loss = float(input("Stop loss price ($): ").strip())

                position = analyzer.calculate_position_size(account_balance, risk_percent, entry_price, stop_loss)

                if 'error' in position:
                    print(f"\n❌ {position['error']}")
                else:
                    print("\n" + "=" * 70)
                    print("📊 POSITION SIZE RECOMMENDATION")
                    print("=" * 70)
                    print(f"\n💰 Account Balance: ${account_balance:,.2f}")
                    print(f"⚠️  Risk Per Trade: {risk_percent}% (${position['risk_amount']:,.2f})")
                    print(f"\n📍 Entry Price: ${entry_price:.2f}")
                    print(f"🛑 Stop Loss: ${stop_loss:.2f}")
                    print(f"📏 Risk Per Share: ${position['risk_per_share']:.2f}")
                    print(f"\n✅ SHARES TO BUY: {position['shares']:,}")
                    print(f"💵 Position Value: ${position['position_value']:,.2f}")
                    print(f"📊 Percent of Account: {position['percent_of_account']:.1f}%")

                    if position['percent_of_account'] > 20:
                        print("\n⚠️  WARNING: Position exceeds 20% of account!")
                        print("   Consider reducing position size for better risk management")

            except ValueError:
                print("\n❌ Invalid input. Please enter numeric values.")
            except Exception as e:
                print(f"\n❌ Error: {e}")

            input("\n📊 Press Enter to return to main menu...")
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
                            
                            # Ask if user wants full technical analysis
                            analyze_choice = input(f"\nRun full technical analysis on {stock['Ticker']}? (y/n): ").strip().lower()
                            if analyze_choice == 'y':
                                asset_type = detect_asset_type(stock['Ticker'])
                                rec = analyzer.generate_recommendation(stock['Ticker'], period, interval, asset_type)
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
                    
                    # Ask if user wants full technical analysis
                    analyze_choice = input(f"\nRun full technical analysis on {ticker}? (y/n): ").strip().lower()
                    if analyze_choice == 'y':
                        asset_type = detect_asset_type(ticker)
                        rec = analyzer.generate_recommendation(ticker, period, interval, asset_type)
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
            elif last_scan_type == "dark_flow":
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

            asset_type = detect_asset_type(ticker)
            rec = analyzer.generate_recommendation(ticker, period, interval, asset_type)

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
