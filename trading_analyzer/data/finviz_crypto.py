"""
FinViz Crypto Data Provider
Optional enhancement for crypto scanning (requires FinViz Elite API key)
"""
import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, Optional
import time


class FinVizCryptoProvider:
    """
    FinViz Elite crypto data provider

    Provides multi-timeframe performance data for top 20 cryptocurrencies:
    - 5Min, Hour, Day, Week, Month, Quarter, Half, YTD, Year performance

    Note: Requires FinViz Elite subscription and API key
    """

    BASE_URL = "https://elite.finviz.com/crypto_performance.ashx"

    def __init__(self, api_key: str):
        """
        Initialize FinViz crypto provider

        Args:
            api_key: FinViz Elite API key
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        self.last_fetch_time = 0
        self.cache_duration = 180  # 3 minutes cache
        self.cached_data = None

    def get_crypto_performance(self) -> Dict[str, Dict]:
        """
        Fetch crypto performance data from FinViz

        Returns:
            Dict mapping crypto ticker to performance data
            Example: {
                'BTC': {
                    'price': 86195.90,
                    'perf_5min': 0.20,
                    'perf_hour': -0.10,
                    'perf_day': -0.58,
                    'perf_week': -4.42,
                    'perf_month': -4.17,
                    'perf_quarter': -26.70,
                    'perf_half': -18.04,
                    'perf_ytd': -7.71,
                    'perf_year': -16.99
                }
            }
        """
        # Check cache
        current_time = time.time()
        if self.cached_data and (current_time - self.last_fetch_time) < self.cache_duration:
            return self.cached_data

        try:
            # Fetch page
            url = f"{self.BASE_URL}?auth={self.api_key}"
            response = self.session.get(url, timeout=15, allow_redirects=True)

            if response.status_code != 200:
                print(f"   ⚠️  FinViz returned status {response.status_code}")
                return {}

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract performance JavaScript object
            performance_js = {}
            scripts = soup.find_all('script')

            for script in scripts:
                script_text = script.string if script.string else ""
                perf_match = re.search(r'var\s+performance\s*=\s*(\{[^}]+\})', script_text)

                if perf_match:
                    try:
                        performance_json = perf_match.group(1)
                        performance_js = json.loads(performance_json)
                        break
                    except Exception:
                        pass

            # Find crypto data table
            crypto_data = {}
            tables = soup.find_all('table')

            for table in tables:
                # Look for table with crypto tickers
                links = table.find_all('a', string=re.compile('USD$', re.I))

                if len(links) < 3:
                    continue

                # Found the crypto table
                headers = []
                header_row = table.find('tr')
                if header_row:
                    header_cells = header_row.find_all(['th', 'td'])
                    headers = [cell.get_text().strip() for cell in header_cells]

                # Parse data rows
                rows = table.find_all('tr')[1:]

                for row in rows:
                    cells = row.find_all('td')
                    if not cells:
                        continue

                    # Extract ticker
                    ticker_link = row.find('a')
                    if not ticker_link:
                        continue

                    ticker_full = ticker_link.get_text().strip()
                    # Convert BTCUSD -> BTC, ETHUSD -> ETH
                    ticker = ticker_full.replace('USD', '').replace('usdt', '').upper()

                    # Build data dict
                    data = {'ticker_full': ticker_full}

                    for i, cell in enumerate(cells):
                        text = cell.get_text().strip()

                        if i < len(headers):
                            header = headers[i].lower()

                            # Parse based on header
                            if header == 'price':
                                try:
                                    data['price'] = float(text)
                                except:
                                    pass

                            elif 'perf' in header:
                                # Performance field
                                try:
                                    perf_value = float(text.replace('%', ''))

                                    # Map header to field name
                                    if '5min' in header:
                                        data['perf_5min'] = perf_value
                                    elif 'hour' in header:
                                        data['perf_hour'] = perf_value
                                    elif 'day' in header:
                                        data['perf_day'] = perf_value
                                    elif 'week' in header:
                                        data['perf_week'] = perf_value
                                    elif 'month' in header:
                                        data['perf_month'] = perf_value
                                    elif 'quart' in header:
                                        data['perf_quarter'] = perf_value
                                    elif 'half' in header:
                                        data['perf_half'] = perf_value
                                    elif 'ytd' in header:
                                        data['perf_ytd'] = perf_value
                                    elif 'year' in header:
                                        data['perf_year'] = perf_value
                                except:
                                    pass

                    crypto_data[ticker] = data

                break  # Found and processed the main table

            # Cache the result
            self.cached_data = crypto_data
            self.last_fetch_time = current_time

            return crypto_data

        except Exception as e:
            print(f"   ⚠️  FinViz crypto fetch error: {e}")
            return {}

    def get_performance_for_ticker(self, ticker: str) -> Optional[Dict]:
        """
        Get performance data for a specific crypto ticker

        Args:
            ticker: Crypto ticker (e.g., 'BTC', 'ETH', 'BTC-USD')

        Returns:
            Performance dict or None if not found
        """
        # Normalize ticker
        ticker = ticker.upper().replace('-USD', '').replace('USD', '')

        # Get all data
        data = self.get_crypto_performance()

        return data.get(ticker)


def test_finviz_crypto():
    """Test function"""
    from trading_analyzer.config import load_user_settings

    print("=" * 100)
    print("TESTING FINVIZ CRYPTO PROVIDER")
    print("=" * 100)

    # Load API key
    settings = load_user_settings()
    api_key = None

    if settings and 'api_keys' in settings:
        api_key = settings['api_keys'].get('finviz')

    if not api_key:
        print("\n❌ No FinViz API key configured")
        print("   Add your key to ~/.trading_analyzer under api_keys.finviz")
        return

    print(f"\n✅ FinViz API key found")

    # Test provider
    provider = FinVizCryptoProvider(api_key)

    print(f"\n🔍 Fetching crypto data...")
    data = provider.get_crypto_performance()

    print(f"\n✅ Retrieved {len(data)} cryptocurrencies")

    # Show sample data
    print(f"\nSample data:")
    for ticker in list(data.keys())[:5]:
        perf = data[ticker]
        print(f"\n{ticker}:")
        print(f"  Price: ${perf.get('price', 'N/A')}")
        print(f"  Day: {perf.get('perf_day', 'N/A')}%")
        print(f"  Week: {perf.get('perf_week', 'N/A')}%")
        print(f"  Month: {perf.get('perf_month', 'N/A')}%")
        print(f"  YTD: {perf.get('perf_ytd', 'N/A')}%")

    print("\n" + "=" * 100)


if __name__ == "__main__":
    test_finviz_crypto()
