"""
Data Provider Abstraction Layer
Handles fetching data from TradingView and yfinance
"""
import yfinance as yf
import pandas as pd
import urllib.request
import requests
from typing import List, Dict, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from ..core.scanner import Scanner, ScanResult, ScanParameters
from ..config import (
    NASDAQ_FTP, TRADINGVIEW_QUERIES, RATE_LIMIT, MIN_SCORE,
    FOREX_PAIRS, CRYPTO_PAIRS, FOREX_CRITERIA, CRYPTO_CRITERIA
)
from .cache import get_cache_manager
from .filters import TickerFilter, prioritize_tickers, is_likely_delisted

# Check TradingView availability
try:
    from tradingview_screener import Query, col
    TRADINGVIEW_AVAILABLE = True
except ImportError:
    TRADINGVIEW_AVAILABLE = False


def fetch_nasdaq_tickers() -> List[Dict]:
    """Fetch complete US ticker list from NASDAQ FTP"""
    all_tickers = []

    # Fetch NASDAQ-listed
    print(f"      Fetching NASDAQ tickers...")
    response = urllib.request.urlopen(NASDAQ_FTP['listed'], timeout=15)
    content = response.read().decode('utf-8')

    for line in content.strip().split('\n')[1:]:
        if line and not line.startswith('File Creation Time'):
            parts = line.split('|')
            if len(parts) >= 2:
                all_tickers.append({
                    'ticker': parts[0],
                    'name': parts[1],
                    'exchange': 'NASDAQ'
                })

    print(f"      ✅ {len(all_tickers)} NASDAQ tickers")

    # Fetch NYSE/other
    print(f"      Fetching NYSE/other tickers...")
    response = urllib.request.urlopen(NASDAQ_FTP['other'], timeout=15)
    content = response.read().decode('utf-8')

    initial_count = len(all_tickers)
    for line in content.strip().split('\n')[1:]:
        if line and not line.startswith('File Creation Time'):
            parts = line.split('|')
            if len(parts) >= 2:
                all_tickers.append({
                    'ticker': parts[0],
                    'name': parts[1],
                    'exchange': parts[2] if len(parts) > 2 else 'OTHER'
                })

    print(f"      ✅ {len(all_tickers) - initial_count} NYSE/other tickers")
    print(f"      ✅ Total: {len(all_tickers)} US stocks")

    return all_tickers


class TradingViewProvider(Scanner):
    """TradingView multi-query data provider"""

    def __init__(self):
        super().__init__("TradingView")

    def scan(self, params: ScanParameters) -> List[ScanResult]:
        """Run multi-query TradingView scan"""
        if not TRADINGVIEW_AVAILABLE:
            print("⚠️  TradingView not available")
            return []

        all_results = []
        seen_tickers = set()

        adjusted_min = params.min_price * 0.90

        # Query 1: Standard momentum
        print(f"   🔍 Query 1: Standard momentum (+10% day, 5x volume)")
        results = self._run_query(
            params.market_choice,
            adjusted_min, params.max_price,
            TRADINGVIEW_QUERIES['standard']
        )
        all_results.extend(results)
        seen_tickers.update(r.ticker for r in results)
        print(f"      ✅ Found {len(results)} stocks")

        # Query 2: Micro-cap focus
        print(f"   🔍 Query 2: Micro-cap focus (+5% day, 3x volume)")
        results = self._run_query(
            params.market_choice,
            adjusted_min, params.max_price,
            TRADINGVIEW_QUERIES['microcap']
        )
        # Deduplicate
        new_results = [r for r in results if r.ticker not in seen_tickers]
        all_results.extend(new_results)
        seen_tickers.update(r.ticker for r in new_results)
        print(f"      ✅ Found {len(new_results)} new stocks")

        # Query 3: Ultra-low float
        print(f"   🔍 Query 3: Ultra-low float (+3% day, 2x volume)")
        results = self._run_query(
            params.market_choice,
            adjusted_min, params.max_price,
            TRADINGVIEW_QUERIES['low_float']
        )
        new_results = [r for r in results if r.ticker not in seen_tickers]
        all_results.extend(new_results)
        print(f"      ✅ Found {len(new_results)} new stocks")

        print(f"   ✅ Combined: {len(all_results)} unique stocks from TradingView")

        return all_results

    def _run_query(self, market: str, min_price: float, max_price: float,
                   query_config: Dict) -> List[ScanResult]:
        """Run single TradingView query"""
        try:
            q = Query()

            # Market filter
            if market == '3':
                q = q.set_markets('america').where(col('exchange') == 'NASDAQ')
            elif market == '4':
                q = q.set_markets('america').where(col('exchange') == 'NYSE')
            else:
                q = q.set_markets('america')

            # Price filter
            q = q.where(col('close').between(min_price, max_price))

            # Apply query-specific filters
            filters = query_config['filters']
            if 'change_from_open' in filters:
                q = q.where(col('change_from_open') >= filters['change_from_open'])
            if 'rel_vol' in filters:
                q = q.where(col('relative_volume_10d_calc') >= filters['rel_vol'])
            if 'market_cap_max' in filters:
                q = q.where(col('market_cap_basic') < filters['market_cap_max'])

            # Select fields
            q = q.select(
                'name', 'close', 'volume', 'relative_volume_10d_calc',
                'market_cap_basic', 'change', 'change_from_open',
                'Perf.W', 'Perf.1M', 'exchange', 'description'
            ).order_by('change_from_open', ascending=False).limit(query_config['limit'])

            count, df = q.get_scanner_data()

            if df is None or df.empty:
                return []

            return self._parse_results(df, min_price, max_price)

        except Exception as e:
            print(f"      ⚠️  Query error: {e}")
            return []

    def _parse_results(self, df: pd.DataFrame, min_price: float, max_price: float) -> List[ScanResult]:
        """Parse TradingView DataFrame into ScanResults"""
        results = []

        for _, row in df.iterrows():
            try:
                ticker = row['name']
                price = float(row['close'])

                # Price filter
                if price > max_price or price < min_price * 0.90:
                    continue

                market_cap = row.get('market_cap_basic', 0) or 0
                volume = row.get('volume', 0) or 0

                if is_likely_delisted(ticker, price, volume, market_cap):
                    continue

                # Calculate float
                if market_cap and price > 0:
                    float_m = (market_cap / price) / 1_000_000
                else:
                    float_m = 50

                # Create result
                result = ScanResult(
                    ticker=ticker,
                    price=price,
                    score=0,  # Will be calculated later
                    rel_vol=float(row.get('relative_volume_10d_calc') or 0),
                    float_m=float_m,
                    change_pct=float(row.get('change_from_open') or 0),
                    week_change=float(row.get('Perf.W') or 0),
                    catalyst="PRESENT",
                    description=str(row.get('description', ''))[:50],
                    source="TradingView",
                    exchange=str(row.get('exchange', '')),
                    volume=int(volume),
                    market_cap=float(market_cap)
                )

                results.append(result)

            except Exception:
                continue

        return results


class FinVizProvider(Scanner):
    """FinViz Elite HTTP API data provider"""

    def __init__(self, api_token: str):
        super().__init__("FinViz Elite")
        self.api_token = api_token
        self.base_url = "https://elite.finviz.com/export.ashx"

    def scan(self, params: ScanParameters) -> List[ScanResult]:
        """Run FinViz Elite API scan using HTTP export endpoint"""
        if not self.api_token:
            print("   ⚠️  FinViz API token not configured")
            return []

        try:
            import csv
            import io

            # Build filter string
            filters = self._build_filter_string(params)

            print(f"   🔍 FinViz Elite: Scanning via export API...")

            # Make request to export endpoint
            url = f"{self.base_url}?v=111&f={filters}&auth={self.api_token}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code != 200:
                print(f"   ⚠️  FinViz API error: HTTP {response.status_code}")
                return []

            # Parse CSV response
            csv_data = io.StringIO(response.text)
            reader = csv.DictReader(csv_data)

            results = []
            seen_tickers = set()

            for row in reader:
                try:
                    ticker = row.get('Ticker', '').strip()
                    if not ticker or ticker in seen_tickers:
                        continue
                    seen_tickers.add(ticker)

                    # Parse CSV fields
                    price = self._parse_float_field(row.get('Price', '0'))
                    change_str = row.get('Change', '0%').replace('%', '').replace('+', '')
                    change_pct = float(change_str) if change_str else 0

                    volume = self._parse_volume_field(row.get('Volume', '0'))
                    market_cap = self._parse_market_cap_field(row.get('Market Cap', '0'))

                    # Price filter
                    if not (params.min_price <= price <= params.max_price):
                        continue

                    # Calculate relative volume (approximate from volume if not provided)
                    rel_vol = 1.0  # FinViz export doesn't include rel vol directly

                    # Calculate float from market cap and price
                    if market_cap and price > 0:
                        float_m = (market_cap / price) / 1_000_000
                    else:
                        float_m = 50  # Default

                    result = ScanResult(
                        ticker=ticker,
                        price=price,
                        score=0,  # Calculated later
                        rel_vol=rel_vol,
                        float_m=float_m,
                        change_pct=change_pct,
                        catalyst=row.get('Industry', 'N/A')[:50],
                        description=row.get('Sector', 'N/A')[:50],
                        source="FinViz Elite",
                        exchange="US",
                        volume=volume,
                        market_cap=market_cap
                    )

                    # Mark low float
                    result.low_float = float_m > 0 and float_m < 20

                    results.append(result)

                except Exception as e:
                    continue

            print(f"   ✅ FinViz Elite: Found {len(results)} stocks")
            return results

        except Exception as e:
            print(f"   ⚠️  FinViz API error: {e}")
            return []

    def _build_filter_string(self, params: ScanParameters) -> str:
        """Build FinViz filter string for URL"""
        filters = []

        # Change (positive)
        filters.append("ta_change_u")

        # Volume (1M+)
        filters.append("sh_avgvol_o1000")

        # Optionable (quality filter)
        filters.append("sh_opt_option")

        # Join with commas
        return ','.join(filters)

    def _parse_float_field(self, value: str) -> float:
        """Parse float field from CSV"""
        try:
            return float(str(value).replace(',', '').replace('$', ''))
        except:
            return 0.0

    def _parse_volume_field(self, vol_str: str) -> int:
        """Parse volume field (handles K, M, B suffixes)"""
        try:
            vol_str = str(vol_str).replace(',', '').upper()
            if 'K' in vol_str:
                return int(float(vol_str.replace('K', '')) * 1_000)
            elif 'M' in vol_str:
                return int(float(vol_str.replace('M', '')) * 1_000_000)
            elif 'B' in vol_str:
                return int(float(vol_str.replace('B', '')) * 1_000_000_000)
            else:
                return int(float(vol_str))
        except:
            return 0

    def _parse_market_cap_field(self, cap_str: str) -> float:
        """Parse market cap field"""
        try:
            cap_str = str(cap_str).replace(',', '').upper()
            if 'K' in cap_str:
                return float(cap_str.replace('K', '')) * 1_000
            elif 'M' in cap_str:
                return float(cap_str.replace('M', '')) * 1_000_000
            elif 'B' in cap_str:
                return float(cap_str.replace('B', '')) * 1_000_000_000
            elif 'T' in cap_str:
                return float(cap_str.replace('T', '')) * 1_000_000_000_000
            else:
                return float(cap_str)
        except:
            return 0.0


class MicroCapProvider(Scanner):
    """Direct micro-cap scanner using yfinance"""

    def __init__(self):
        super().__init__("MicroCap")
        self.cache = get_cache_manager()
        self.candidate_list: Optional[List[str]] = None

    def scan(self, params: ScanParameters, exclude_tickers: Set[str] = None) -> List[ScanResult]:
        """Scan micro-cap candidates"""
        exclude_tickers = exclude_tickers or set()

        # Get candidate list
        if self.candidate_list is None:
            self.candidate_list = self._get_candidates()

        # Filter exclusions
        tickers_to_scan = [t for t in self.candidate_list if t not in exclude_tickers]

        # Priority filtering for smart mode
        if params.mode.value == 'smart' and len(tickers_to_scan) > 500:
            tickers_to_scan = prioritize_tickers(tickers_to_scan, 500)
            print(f"   💎 Priority micro-cap scan ({len(tickers_to_scan)} high-priority tickers)")
        else:
            print(f"   💎 Micro-cap scan ({len(tickers_to_scan)} tickers)")

        if not tickers_to_scan:
            print(f"      ✅ All candidates already found by TradingView!")
            return []

        print(f"      (Scanning with rate limiting...)")

        # Scan with rate limiting
        return self._scan_tickers(tickers_to_scan, params)

    def _get_candidates(self) -> List[str]:
        """Get micro-cap candidate list (with caching)"""
        # Check cache
        cached = self.cache.get('microcap_list', 'candidates')
        if cached:
            age = self.cache.get_age('microcap_list', 'candidates')
            print(f"   📋 Using cached micro-cap universe ({len(cached)} tickers, {age:.1f}h old)")
            return cached

        # Build fresh list
        print(f"   🌐 Building comprehensive micro-cap candidate list...")
        print(f"      This will take ~5 seconds (cached for 4 hours)")

        all_tickers = fetch_nasdaq_tickers()

        # Smart filter
        ticker_filter = TickerFilter()
        candidates = ticker_filter.filter(all_tickers)
        ticker_filter.print_stats()

        # Cache
        self.cache.set('microcap_list', 'candidates', candidates)

        print(f"   ✅ Micro-cap candidate universe: {len(candidates)} tickers")

        return candidates

    def _scan_tickers(self, tickers: List[str], params: ScanParameters) -> List[ScanResult]:
        """Scan tickers with rate limiting"""
        results = []

        def check_ticker(ticker: str) -> Optional[ScanResult]:
            """Check single ticker"""
            try:
                stock = yf.Ticker(ticker)
                info = stock.info

                # Get price
                price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                if not price or not (params.min_price <= price <= params.max_price):
                    return None

                # Get change
                prev_close = info.get('previousClose', 0)
                if not prev_close:
                    return None
                change_pct = ((price - prev_close) / prev_close) * 100

                if change_pct < params.min_change:
                    return None

                # Volume
                volume = info.get('volume', 0)
                avg_volume = info.get('averageVolume', 1)
                if avg_volume == 0:
                    return None
                rel_vol = volume / avg_volume

                if rel_vol < params.min_rel_vol:
                    return None

                # Float
                float_shares = info.get('floatShares', info.get('sharesOutstanding', 0))
                float_m = float_shares / 1_000_000 if float_shares else 50

                # Create result
                result = ScanResult(
                    ticker=ticker,
                    price=price,
                    score=0,
                    rel_vol=rel_vol,
                    float_m=float_m,
                    change_pct=change_pct,
                    source="DIRECT",
                    exchange=info.get('exchange', 'N/A'),
                    volume=volume,
                    market_cap=info.get('marketCap', 0)
                )

                return result

            except Exception:
                return None

        # Concurrent scanning with rate limiting
        with ThreadPoolExecutor(max_workers=RATE_LIMIT['workers']) as executor:
            futures = {executor.submit(check_ticker, ticker): ticker for ticker in tickers}

            completed = 0
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)

                completed += 1

                # Progress
                if completed % RATE_LIMIT['batch_size'] == 0:
                    print(f"      ... checked {completed}/{len(tickers)} ({len(results)} found)")

                # Rate limit
                if completed % RATE_LIMIT['delay_every'] == 0:
                    time.sleep(RATE_LIMIT['delay_ms'] / 1000)

        return results


class ForexProvider(Scanner):
    """FOREX currency pairs scanner"""

    def __init__(self):
        super().__init__("FOREX")
        self.cache = get_cache_manager()

    def scan(self, params: ScanParameters) -> List[ScanResult]:
        """Scan FOREX pairs for volatility and momentum"""
        print(f"   💱 Scanning FOREX pairs...")

        # Get all pairs - use only majors for speed (top 10)
        all_pairs = FOREX_PAIRS['majors'][:10]  # Top 10 most liquid pairs

        print(f"      Analyzing {len(all_pairs)} currency pairs")

        results = []

        # Scan each pair
        for pair in all_pairs:
            result = self._check_forex_pair(pair)
            if result:
                results.append(result)

        # Sort by activity score (week change * volatility)
        results.sort(key=lambda x: getattr(x, 'activity_score', 0), reverse=True)

        print(f"      ✅ Found {len(results)} FOREX pairs")
        return results

    def _check_forex_pair(self, pair: str) -> Optional[ScanResult]:
        """Check single FOREX pair"""
        try:
            ticker = yf.Ticker(pair)

            # Get 5-day data
            hist = ticker.history(period='5d', interval='1h')
            if hist.empty or len(hist) < 2:
                return None

            current_price = hist['Close'].iloc[-1]
            prev_hour = hist['Close'].iloc[-2]

            # 24h change
            if len(hist) >= 24:
                day_ago = hist['Close'].iloc[-24]
                day_change = ((current_price - day_ago) / day_ago) * 100
            else:
                day_change = ((current_price - prev_hour) / prev_hour) * 100

            # Week change
            week_ago = hist['Close'].iloc[0]
            week_change = ((current_price - week_ago) / week_ago) * 100

            # Calculate volatility
            price_range = hist['High'].max() - hist['Low'].min()
            volatility_pct = (price_range / current_price) * 100

            # Volume
            volume = int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0
            avg_volume = int(hist['Volume'].mean()) if 'Volume' in hist.columns else 0
            rel_vol = volume / avg_volume if avg_volume > 0 else 1.0

            # Get pair name (clean up symbol)
            pair_name = pair.replace('=X', '')

            # Activity score (week change * volatility)
            activity = abs(week_change) * (volatility_pct / 10)

            result = ScanResult(
                ticker=pair_name,
                price=current_price,
                score=0,
                rel_vol=rel_vol,
                float_m=0,  # N/A for forex
                change_pct=week_change,  # Use week change for sorting
                catalyst=f"Vol: {volatility_pct:.2f}%",
                description=f"Day: {day_change:+.2f}% | Week: {week_change:+.2f}%",
                source="FOREX",
                exchange="FX",
                volume=volume,
                market_cap=0
            )

            # Store activity for sorting
            result.activity_score = activity

            return result

        except Exception:
            return None


class CryptoProvider(Scanner):
    """Cryptocurrency scanner"""

    def __init__(self):
        super().__init__("CRYPTO")
        self.cache = get_cache_manager()

    def scan(self, params: ScanParameters) -> List[ScanResult]:
        """Scan crypto pairs for momentum"""
        print(f"   ₿ Scanning Cryptocurrency markets...")

        # Get top cryptos from CoinGecko
        crypto_list = self._get_top_cryptos_from_coingecko(limit=30)

        print(f"      Analyzing {len(crypto_list)} cryptocurrencies")

        results = []

        # Scan each crypto
        for ticker, name in crypto_list:
            result = self._check_crypto(ticker, name)
            if result:
                results.append(result)

        # Sort by activity score
        results.sort(key=lambda x: getattr(x, 'activity_score', 0), reverse=True)

        print(f"      ✅ Found {len(results)} active cryptocurrencies")
        return results

    def _get_top_cryptos_from_coingecko(self, limit: int = 30) -> List[Tuple[str, str]]:
        """
        Dynamically fetch top cryptocurrencies from CoinGecko API

        Returns:
            List of (yfinance_ticker, coin_name) tuples
        """
        try:
            print("      Fetching top cryptos from CoinGecko...")

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

            print(f"      ✅ Fetched {len(crypto_list)} from CoinGecko")
            return crypto_list

        except Exception as e:
            print(f"      ⚠️  CoinGecko API error, using fallback list")

            # Fallback to hardcoded list
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
                ('MATIC-USD', 'Polygon'),
                ('UNI-USD', 'Uniswap'),
            ]

    def _check_crypto(self, crypto: str, name: str) -> Optional[ScanResult]:
        """Check single cryptocurrency"""
        try:
            ticker = yf.Ticker(crypto)

            # Get 5-day data
            hist = ticker.history(period='5d', interval='1h')
            if hist.empty or len(hist) < 2:
                return None

            current_price = hist['Close'].iloc[-1]

            # Skip if invalid price
            if pd.isna(current_price) or current_price <= 0:
                return None

            prev_hour = hist['Close'].iloc[-2]
            hour_change = ((current_price - prev_hour) / prev_hour) * 100

            # 24h change
            if len(hist) >= 24:
                day_ago = hist['Close'].iloc[-24]
                day_change = ((current_price - day_ago) / day_ago) * 100
            else:
                day_change = hour_change

            # Week change
            week_ago = hist['Close'].iloc[0]
            week_change = ((current_price - week_ago) / week_ago) * 100

            # Volume
            volume_24h = hist['Volume'].iloc[-24:].sum() if len(hist) >= 24 else hist['Volume'].sum()

            # Skip if no volume (likely delisted)
            if volume_24h == 0:
                return None

            # Volatility
            price_range = hist['High'].max() - hist['Low'].min()
            volatility_pct = (price_range / current_price) * 100

            # Activity score (week change * volatility)
            activity = abs(week_change) * (volatility_pct / 10)

            result = ScanResult(
                ticker=crypto.replace('-USD', ''),
                price=current_price,
                score=0,
                rel_vol=0,
                float_m=0,  # N/A for crypto
                change_pct=week_change,  # Use week change
                catalyst=f"Vol: {volatility_pct:.1f}%",
                description=f"{name} | Day: {day_change:+.1f}% | Week: {week_change:+.1f}%",
                source="CRYPTO",
                exchange="Crypto",
                volume=int(volume_24h),
                market_cap=0
            )

            # Store activity for sorting
            result.activity_score = activity

            return result

        except Exception:
            return None
