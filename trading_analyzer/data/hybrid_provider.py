"""
Hybrid Data Provider
Intelligently uses Polygon/Massive (if available) with yfinance fallback

Note: Polygon.io rebranded to Massive, but the API and SDK remain unchanged.
"""
import yfinance as yf
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime, timedelta

from .polygon_provider import (
    get_polygon_provider,
    ShortInterestData,
    BlockTrade,
    OptionsFlowData
)


class HybridDataProvider:
    """
    Intelligent data provider that uses best available source

    Priority:
    1. Polygon.io (if API key provided and available)
    2. yfinance (fallback)

    Features:
    - Automatic fallback on errors
    - Source tracking (know where data came from)
    - Performance monitoring
    """

    def __init__(self, polygon_api_key: Optional[str] = None):
        """
        Initialize hybrid provider

        Args:
            polygon_api_key: Polygon API key (None = yfinance only)
        """
        self.polygon = get_polygon_provider(polygon_api_key)
        self.stats = {
            'polygon_calls': 0,
            'polygon_successes': 0,
            'yfinance_fallbacks': 0
        }

    # ========== QUOTES & MARKET DATA ==========

    def get_stock_data(self, ticker: str, period: str = '3mo') -> Optional[pd.DataFrame]:
        """
        Get historical stock data with automatic fallback

        Args:
            ticker: Stock symbol
            period: '1d', '5d', '1mo', '3mo', '6mo', '1y'

        Returns:
            DataFrame with OHLCV data, labeled with source
        """
        # Try Polygon first
        if self.polygon.is_available():
            self.stats['polygon_calls'] += 1

            # Map period to Polygon parameters
            if period == '1d':
                df = self.polygon.get_historical_bars(ticker, 'minute', 390)  # Full trading day
            elif period == '5d':
                df = self.polygon.get_historical_bars(ticker, 'hour', 40)
            elif period in ['1mo', '3mo', '6mo', '1y']:
                limit_map = {'1mo': 22, '3mo': 66, '6mo': 126, '1y': 252}
                df = self.polygon.get_historical_bars(ticker, 'day', limit_map.get(period, 100))
            else:
                df = None

            if df is not None and not df.empty:
                self.stats['polygon_successes'] += 1
                df.attrs['source'] = 'polygon'
                return df

        # Fallback to yfinance
        self.stats['yfinance_fallbacks'] += 1

        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, prepost=True)

            if not df.empty:
                df.attrs['source'] = 'yfinance'
                return df

        except Exception as e:
            print(f"⚠️  Error fetching data for {ticker}: {e}")

        return None

    def get_current_quote(self, ticker: str) -> Optional[Dict]:
        """
        Get current quote (real-time or delayed)

        Returns:
            Dict with price, volume, change, etc.
        """
        # Try Polygon first
        if self.polygon.is_available():
            quote = self.polygon.get_quote(ticker)
            if quote:
                return quote

        # Fallback to yfinance
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            quote = {
                'ticker': ticker,
                'price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'open': info.get('regularMarketOpen'),
                'high': info.get('dayHigh'),
                'low': info.get('dayLow'),
                'volume': info.get('volume', 0),
                'prev_close': info.get('previousClose'),
                'change': None,  # Calculate from price and prev_close
                'change_pct': info.get('regularMarketChangePercent'),
                'timestamp': datetime.now(),
                'source': 'yfinance'
            }

            # Calculate change if not provided
            if quote['price'] and quote['prev_close']:
                quote['change'] = quote['price'] - quote['prev_close']
                if not quote['change_pct']:
                    quote['change_pct'] = (quote['change'] / quote['prev_close']) * 100

            return quote

        except Exception as e:
            print(f"⚠️  Error fetching quote for {ticker}: {e}")
            return None

    # ========== SHORT INTEREST ==========

    def get_short_interest(self, ticker: str) -> Optional[Dict]:
        """
        Get short interest data (Polygon first, yfinance fallback)

        Returns:
            Dict with short_percent, short_ratio, etc.
        """
        # Try Polygon first (if available and has this data)
        if self.polygon.is_available():
            short_data = self.polygon.get_short_interest(ticker)
            if short_data:
                return {
                    'short_percent': short_data.short_percent_float,
                    'short_ratio': short_data.days_to_cover,
                    'short_interest': short_data.short_interest,
                    'report_date': short_data.report_date,
                    'source': 'polygon'
                }

        # Fallback to yfinance (more reliable for short interest currently)
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                'short_percent': info.get('shortPercentOfFloat', 0),
                'short_ratio': info.get('shortRatio', 0),
                'short_interest': None,  # Not always available
                'report_date': None,
                'source': 'yfinance'
            }

        except Exception as e:
            return None

    # ========== OPTIONS FLOW ==========

    def get_options_flow(self, ticker: str) -> Optional[Dict]:
        """
        Get options activity data

        Returns:
            Dict with call_put_ratio, volume, OI, etc.
        """
        # Try Polygon first
        if self.polygon.is_available():
            options_data = self.polygon.get_options_flow(ticker)
            if options_data:
                return {
                    'call_volume': options_data.call_volume,
                    'put_volume': options_data.put_volume,
                    'call_oi': options_data.call_oi,
                    'put_oi': options_data.put_oi,
                    'call_put_ratio': options_data.call_put_ratio,
                    'unusual_activity': options_data.unusual_activity,
                    'gamma_exposure': options_data.gamma_exposure,
                    'source': 'polygon'
                }

        # Fallback to yfinance
        try:
            stock = yf.Ticker(ticker)
            opts = stock.options

            if not opts or len(opts) == 0:
                return None

            # Get nearest expiration
            chain = stock.option_chain(opts[0])
            calls = chain.calls
            puts = chain.puts

            # Calculate metrics
            total_call_volume = calls['volume'].sum() if 'volume' in calls else 0
            total_put_volume = puts['volume'].sum() if 'volume' in puts else 0
            total_call_oi = calls['openInterest'].sum() if 'openInterest' in calls else 0
            total_put_oi = puts['openInterest'].sum() if 'openInterest' in puts else 0

            call_put_ratio = total_call_volume / total_put_volume if total_put_volume > 0 else 0

            # Detect unusual activity
            avg_call_volume = calls['volume'].mean() if 'volume' in calls and len(calls) > 0 else 0
            unusual = total_call_volume > (avg_call_volume * 5) if avg_call_volume > 0 else False

            return {
                'call_volume': int(total_call_volume),
                'put_volume': int(total_put_volume),
                'call_oi': int(total_call_oi),
                'put_oi': int(total_put_oi),
                'call_put_ratio': call_put_ratio,
                'unusual_activity': unusual,
                'gamma_exposure': 0,  # Not calculable from yfinance
                'source': 'yfinance'
            }

        except Exception as e:
            return None

    # ========== BLOCK TRADES (DARK FLOW) ==========

    def get_block_trades(self, ticker: str, min_size: int = 10000, hours: int = 24) -> List[BlockTrade]:
        """
        Get large block trades (Polygon only - requires tick data)

        Args:
            ticker: Stock symbol
            min_size: Minimum shares
            hours: Hours of history

        Returns:
            List of BlockTrade objects (empty if Polygon not available)
        """
        if self.polygon.is_available():
            return self.polygon.get_block_trades(ticker, min_size, hours)

        # No fallback for block trades - requires tick data
        return []

    # ========== NEWS & CATALYSTS ==========

    def get_news(self, ticker: str, days: int = 7) -> List[Dict]:
        """
        Get recent news (Polygon first, external APIs as fallback)

        Args:
            ticker: Stock symbol
            days: Days of history

        Returns:
            List of news articles
        """
        # Try Polygon first
        if self.polygon.is_available():
            news = self.polygon.get_news(ticker, days)
            if news:
                return news

        # No direct yfinance fallback for news
        # Could integrate with NewsAPI here if needed
        return []

    # ========== FUNDAMENTALS ==========

    def get_fundamentals(self, ticker: str) -> Optional[Dict]:
        """
        Get fundamental data (always from yfinance - more comprehensive)

        Returns:
            Dict with float, shares outstanding, market cap, etc.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                'float_shares': info.get('floatShares', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'market_cap': info.get('marketCap', 0),
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice', 0),
                'industry': info.get('industry', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'source': 'yfinance'
            }

        except Exception as e:
            return None

    # ========== STATISTICS ==========

    def get_stats(self) -> Dict:
        """Get usage statistics"""
        total_calls = self.stats['polygon_calls'] + self.stats['yfinance_fallbacks']

        return {
            'polygon_calls': self.stats['polygon_calls'],
            'polygon_successes': self.stats['polygon_successes'],
            'polygon_success_rate': (self.stats['polygon_successes'] / self.stats['polygon_calls'] * 100)
                if self.stats['polygon_calls'] > 0 else 0,
            'yfinance_fallbacks': self.stats['yfinance_fallbacks'],
            'total_calls': total_calls,
            'polygon_available': self.polygon.is_available()
        }

    def print_stats(self):
        """Print usage statistics"""
        stats = self.get_stats()

        print(f"\n📊 DATA PROVIDER STATISTICS")
        print(f"{'=' * 60}")
        print(f"Polygon Available:      {'✅ Yes' if stats['polygon_available'] else '❌ No (using yfinance)'}")
        print(f"Total Data Requests:    {stats['total_calls']}")

        if stats['polygon_available']:
            print(f"Polygon Calls:          {stats['polygon_calls']}")
            print(f"Polygon Success Rate:   {stats['polygon_success_rate']:.1f}%")
            print(f"YFinance Fallbacks:     {stats['yfinance_fallbacks']}")
        else:
            print(f"YFinance Calls:         {stats['yfinance_fallbacks']}")

        print(f"{'=' * 60}\n")


# Singleton instance
_hybrid_instance = None

def get_hybrid_provider(polygon_api_key: Optional[str] = None) -> HybridDataProvider:
    """Get or create hybrid provider singleton"""
    global _hybrid_instance

    if _hybrid_instance is None:
        _hybrid_instance = HybridDataProvider(polygon_api_key)

    return _hybrid_instance
