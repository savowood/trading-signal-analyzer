"""
Insider Trading Analysis Module
Track and analyze insider buying/selling activity using SEC EDGAR Form 4 filings
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
import time
import xml.etree.ElementTree as ET
from urllib.parse import quote


@dataclass
class InsiderTransaction:
    """Individual insider trading transaction"""
    filing_date: str
    transaction_date: str
    insider_name: str
    insider_title: str
    transaction_type: str  # "P-Purchase", "S-Sale", "M-Award", etc.
    shares: int
    price: float
    value: float
    shares_owned_after: int

    def is_buy(self) -> bool:
        """Check if transaction is a buy/purchase"""
        # SEC Form 4 transaction codes
        buy_codes = ['P', 'A', 'M']  # Purchase, Award, Exercise
        # Also handle verbose format from other APIs
        buy_types = ['P-Purchase', 'A-Award', 'M-Exempt', 'Purchase']
        return (self.transaction_type in buy_codes or
                self.transaction_type in buy_types or
                'Purchase' in self.transaction_type)

    def is_sell(self) -> bool:
        """Check if transaction is a sale"""
        # SEC Form 4 transaction codes
        sell_codes = ['S', 'D']  # Sale, Disposition
        # Also handle verbose format from other APIs
        sell_types = ['S-Sale', 'D-Disposition', 'Sale']
        return (self.transaction_type in sell_codes or
                self.transaction_type in sell_types or
                'Sale' in self.transaction_type)

    def days_ago(self) -> int:
        """Calculate days since transaction"""
        try:
            trans_date = datetime.strptime(self.transaction_date, "%Y-%m-%d")
            return (datetime.now() - trans_date).days
        except:
            return 999


@dataclass
class InsiderAnalysis:
    """Aggregated insider trading analysis"""
    ticker: str
    signal: str  # "Strong Buy", "Buy", "Neutral", "Sell", "Strong Sell"
    confidence: str  # "High", "Medium", "Low"

    # Transaction counts
    total_transactions: int
    buy_transactions: int
    sell_transactions: int

    # Dollar values
    total_buy_value: float
    total_sell_value: float
    net_activity: float  # Positive = more buying, Negative = more selling

    # Recent activity
    recent_transactions: List[InsiderTransaction]

    # Analysis
    interpretation: str
    time_range: str

    # Key insiders
    key_buyers: List[str]  # Names of significant buyers
    key_sellers: List[str]  # Names of significant sellers


class PolygonInsiderClient:
    """Polygon.io client for insider trading data (faster, cleaner alternative to SEC)"""

    BASE_URL = "https://api.polygon.io"

    def __init__(self, api_key: str):
        """Initialize Polygon client with API key"""
        self.api_key = api_key
        self.session = requests.Session()
        self.last_call_time = 0
        self.min_call_interval = 12.0  # Free tier: 5 calls/minute = 12 seconds between calls

    def _rate_limit(self):
        """Enforce Polygon rate limiting (5 calls per minute on free tier)"""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_call_interval:
            time.sleep(self.min_call_interval - elapsed)
        self.last_call_time = time.time()

    def get_insider_trades(self, ticker: str, days_back: int = 90) -> List[Dict]:
        """
        Get insider trading transactions from Polygon

        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to look back

        Returns:
            List of insider trading transactions
        """
        self._rate_limit()

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Try the correct Polygon endpoint format
        url = f"{self.BASE_URL}/v2/reference/insider-trades/{ticker}"
        params = {
            'filing_date.gte': start_date.strftime('%Y-%m-%d'),
            'filing_date.lte': end_date.strftime('%Y-%m-%d'),
            'limit': 100,
            'apiKey': self.api_key
        }

        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            results = data.get('results', [])

            # If no results, return empty list (not an error)
            if not results:
                return []

            # Convert Polygon format to our standard format
            transactions = []
            for item in results:
                # Polygon provides clean, structured data
                transactions.append({
                    'transactionDate': item.get('transaction_date', ''),
                    'filingDate': item.get('filing_date', ''),
                    'transactionCode': item.get('transaction_code', ''),
                    'acquistionOrDisposition': item.get('acquisition_or_disposition', ''),
                    'securitiesTransacted': float(item.get('securities_transacted', 0)),
                    'price': float(item.get('transaction_price_per_share', 0)),
                    'securitiesOwned': float(item.get('securities_owned', 0)),
                    'reportingName': item.get('owner_name', 'Unknown'),
                    'typeOfOwner': item.get('owner_relationship', 'Unknown')
                })

            return transactions

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise PermissionError("Polygon.io: API key invalid or insider trades not included in your plan")
            elif e.response.status_code == 404:
                # No data for this ticker - not an error, just return empty
                return []
            elif e.response.status_code == 429:
                raise PermissionError("Polygon.io rate limit exceeded")
            else:
                raise Exception(f"Polygon HTTP {e.response.status_code}: {e}")
        except Exception as e:
            raise Exception(f"Polygon error: {e}")


class SECEdgarClient:
    """SEC EDGAR client for Form 4 insider trading filings"""

    BASE_URL = "https://www.sec.gov"

    def __init__(self, user_agent: str = None):
        """
        Initialize SEC EDGAR client

        Args:
            user_agent: User agent string (SEC requires identification with contact)
        """
        # SEC requires proper User-Agent with contact info
        if user_agent is None:
            user_agent = "Trading Signal Analyzer/1.0 (Educational Research; mailto:analysis@tradinganalyzer.com)"

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept-Encoding': 'gzip, deflate'
        })
        self.last_call_time = 0
        self.min_call_interval = 0.1  # SEC rate limit: 10 requests/second

    def _rate_limit(self):
        """Enforce SEC rate limiting (10 requests per second max)"""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_call_interval:
            time.sleep(self.min_call_interval - elapsed)
        self.last_call_time = time.time()

    def get_company_cik(self, ticker: str) -> Optional[str]:
        """
        Get CIK (Central Index Key) for a ticker symbol

        Args:
            ticker: Stock ticker symbol

        Returns:
            CIK number as string, or None if not found
        """
        self._rate_limit()

        # Try SEC company tickers JSON
        url = f"{self.BASE_URL}/files/company_tickers.json"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Search for ticker
            ticker_upper = ticker.upper()
            for entry in data.values():
                if entry.get('ticker', '').upper() == ticker_upper:
                    cik = str(entry['cik_str']).zfill(10)  # Pad to 10 digits
                    return cik

            return None

        except Exception as e:
            print(f"SEC CIK lookup error: {e}")
            return None

    def get_form4_filings(self, ticker: str, days_back: int = 90, max_retries: int = 3) -> List[Dict]:
        """
        Get Form 4 filings for a ticker

        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to look back
            max_retries: Number of retries for 503 errors

        Returns:
            List of Form 4 filing data
        """
        # Get CIK
        cik = self.get_company_cik(ticker)
        if not cik:
            return []

        # Get recent filings with retry logic for 503 errors
        url = f"{self.BASE_URL}/cgi-bin/browse-edgar"
        params = {
            'action': 'getcompany',
            'CIK': cik,
            'type': '4',  # Form 4 (insider transactions)
            'dateb': '',  # End date (blank = today)
            'owner': 'include',
            'count': '100',  # Max filings to retrieve
            'output': 'atom'  # XML/Atom format
        }

        for attempt in range(max_retries):
            try:
                self._rate_limit()
                response = self.session.get(url, params=params, timeout=15)
                response.raise_for_status()

                # Parse XML
                filings = self._parse_atom_feed(response.text, days_back)
                return filings

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 503 and attempt < max_retries - 1:
                    # SEC servers overloaded, wait and retry
                    wait_time = (attempt + 1) * 2  # 2, 4, 6 seconds
                    print(f"   SEC servers busy, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"SEC Form 4 error: {e}")
                    return []
            except Exception as e:
                print(f"SEC Form 4 error: {e}")
                return []

        return []

    def _parse_atom_feed(self, xml_content: str, days_back: int) -> List[Dict]:
        """Parse SEC EDGAR Atom feed to extract Form 4 filing URLs"""
        try:
            root = ET.fromstring(xml_content)

            # Namespace handling
            ns = {'atom': 'http://www.w3.org/2005/Atom'}

            filings = []
            cutoff_date = datetime.now() - timedelta(days=days_back)

            # Find all entry elements
            for entry in root.findall('atom:entry', ns):
                # Get filing date
                updated = entry.find('atom:updated', ns)
                if updated is not None:
                    filing_date = datetime.fromisoformat(updated.text.replace('Z', '+00:00'))

                    # Skip if too old
                    if filing_date.replace(tzinfo=None) < cutoff_date:
                        continue

                # Get filing URL
                link = entry.find('atom:link[@rel="alternate"]', ns)
                if link is not None:
                    filing_url = link.get('href')

                    filings.append({
                        'filing_date': filing_date.replace(tzinfo=None),
                        'filing_url': filing_url
                    })

            return filings

        except Exception as e:
            print(f"XML parse error: {e}")
            return []

    def parse_form4(self, filing_url: str) -> List[Dict]:
        """
        Parse a Form 4 filing to extract insider transactions

        Args:
            filing_url: URL to Form 4 filing index

        Returns:
            List of transactions from the filing
        """
        self._rate_limit()

        try:
            # Get filing page to find XML link
            response = self.session.get(filing_url, timeout=10)
            response.raise_for_status()

            # Find XML document link (ends with .xml, not xsl transform)
            import re
            xml_links = re.findall(r'href="([^"]*\.xml)"', response.text, re.IGNORECASE)

            # Filter out xsl stylesheets, get the actual form4 XML
            xml_url = None
            for link in xml_links:
                if 'xsl' not in link.lower() and link.startswith('/'):
                    xml_url = f"{self.BASE_URL}{link}"
                    break

            if not xml_url:
                return []

            # Fetch and parse XML
            self._rate_limit()
            response = self.session.get(xml_url, timeout=10)
            response.raise_for_status()

            return self._parse_form4_xml(response.text)

        except Exception as e:
            return []

    def _parse_form4_xml(self, xml_content: str) -> List[Dict]:
        """Parse Form 4 XML to extract transaction details"""
        try:
            root = ET.fromstring(xml_content)

            transactions = []

            # Get reporting owner info
            owner_name = "Unknown"
            owner_title = "Unknown"

            reporting_owner = root.find('.//reportingOwner')
            if reporting_owner is not None:
                name_elem = reporting_owner.find('.//rptOwnerName')
                if name_elem is not None:
                    owner_name = name_elem.text or "Unknown"

                title_elem = reporting_owner.find('.//officerTitle')
                if title_elem is not None:
                    owner_title = title_elem.text or "Unknown"

            # Parse non-derivative transactions
            for trans in root.findall('.//nonDerivativeTransaction'):
                try:
                    # Transaction date
                    trans_date_elem = trans.find('.//transactionDate/value')
                    trans_date = trans_date_elem.text if trans_date_elem is not None else ""

                    # Transaction code (P=Purchase, S=Sale, A=Award, etc.)
                    code_elem = trans.find('.//transactionCode')
                    trans_code = code_elem.text if code_elem is not None else ""

                    # Shares
                    shares_elem = trans.find('.//transactionShares/value')
                    shares = float(shares_elem.text) if shares_elem is not None else 0

                    # Price
                    price_elem = trans.find('.//transactionPricePerShare/value')
                    price = float(price_elem.text) if price_elem is not None else 0

                    # Shares owned after
                    owned_elem = trans.find('.//sharesOwnedFollowingTransaction/value')
                    owned_after = float(owned_elem.text) if owned_elem is not None else 0

                    # Acquisition/Disposition
                    acq_disp_elem = trans.find('.//transactionAcquiredDisposedCode/value')
                    acq_disp = acq_disp_elem.text if acq_disp_elem is not None else ""

                    transactions.append({
                        'transactionDate': trans_date,
                        'transactionCode': trans_code,
                        'acquistionOrDisposition': acq_disp,
                        'securitiesTransacted': shares,
                        'price': price,
                        'securitiesOwned': owned_after,
                        'reportingName': owner_name,
                        'typeOfOwner': owner_title,
                        'filingDate': trans_date  # Use transaction date as filing date
                    })

                except Exception:
                    continue

            return transactions

        except Exception as e:
            return []


def analyze_insider_trading(ticker: str, api_key: str = None, days_back: int = 90) -> Optional[InsiderAnalysis]:
    """
    Analyze insider trading activity for a ticker

    Uses dual-source approach:
    1. Primary: Polygon.io (faster, cleaner data) if API key provided
    2. Fallback: SEC EDGAR (free, always works)

    Args:
        ticker: Stock ticker symbol
        api_key: Polygon.io API key (optional, falls back to SEC if not provided)
        days_back: Number of days to look back (default 90)

    Returns:
        InsiderAnalysis object or None if no data/error
    """
    trades_data = []
    data_source = "Unknown"

    # Try Polygon.io first if API key is provided
    if api_key and api_key != "your_polygon_api_key_here":
        try:
            polygon_client = PolygonInsiderClient(api_key)
            trades_data = polygon_client.get_insider_trades(ticker, days_back=days_back)
            data_source = "Polygon.io"

            if trades_data:
                print(f"   ✅ Fetched {len(trades_data)} transactions from Polygon.io")
        except PermissionError as e:
            print(f"   ⚠️  Polygon.io error: {e}")
            print(f"   ↪️  Falling back to SEC EDGAR...")
        except Exception as e:
            print(f"   ⚠️  Polygon.io failed: {e}")
            print(f"   ↪️  Falling back to SEC EDGAR...")

    # Fallback to SEC EDGAR if Polygon didn't work or no API key
    if not trades_data:
        try:
            sec_client = SECEdgarClient()

            # Get Form 4 filings
            filings = sec_client.get_form4_filings(ticker, days_back=days_back)

            if filings:
                # Parse all filings to get transactions
                for filing in filings[:20]:  # Limit to 20 most recent filings
                    transactions = sec_client.parse_form4(filing['filing_url'])
                    trades_data.extend(transactions)

                data_source = "SEC EDGAR"
                if trades_data:
                    print(f"   ✅ Parsed {len(trades_data)} transactions from SEC EDGAR")
        except Exception as e:
            print(f"   ❌ SEC EDGAR error: {e}")
            return None

    if not trades_data:
        return None

    # Filter to date range and parse transactions
    cutoff_date = datetime.now() - timedelta(days=days_back)
    transactions = []

    for trade in trades_data:
        try:
            # Parse transaction date
            trans_date = datetime.strptime(trade.get('transactionDate', ''), "%Y-%m-%d")

            # Skip if outside date range
            if trans_date < cutoff_date:
                continue

            # Parse transaction
            transaction = InsiderTransaction(
                filing_date=trade.get('filingDate', ''),
                transaction_date=trade.get('transactionDate', ''),
                insider_name=trade.get('reportingName', 'Unknown'),
                insider_title=trade.get('typeOfOwner', 'Unknown'),
                transaction_type=trade.get('acquistionOrDisposition', ''),
                shares=abs(int(trade.get('securitiesTransacted', 0))),
                price=float(trade.get('price', 0)),
                value=abs(float(trade.get('securitiesTransacted', 0)) * float(trade.get('price', 0))),
                shares_owned_after=int(trade.get('securitiesOwned', 0))
            )

            transactions.append(transaction)

        except (ValueError, KeyError, TypeError) as e:
            # Skip malformed transactions
            continue

    if not transactions:
        return None

    # Aggregate statistics
    buy_transactions = [t for t in transactions if t.is_buy()]
    sell_transactions = [t for t in transactions if t.is_sell()]

    total_buy_value = sum(t.value for t in buy_transactions)
    total_sell_value = sum(t.value for t in sell_transactions)
    net_activity = total_buy_value - total_sell_value

    # Identify key insiders
    # Key buyers: Insiders with > $100k in purchases
    key_buyers = list(set([
        t.insider_name for t in buy_transactions
        if t.value > 100000
    ]))

    # Key sellers: Insiders with > $500k in sales
    key_sellers = list(set([
        t.insider_name for t in sell_transactions
        if t.value > 500000
    ]))

    # Determine signal
    signal, confidence, interpretation = _interpret_insider_activity(
        buy_transactions=len(buy_transactions),
        sell_transactions=len(sell_transactions),
        total_buy_value=total_buy_value,
        total_sell_value=total_sell_value,
        net_activity=net_activity,
        key_buyers=key_buyers,
        key_sellers=key_sellers,
        days_back=days_back
    )

    # Sort transactions by date (most recent first)
    transactions.sort(key=lambda t: t.transaction_date, reverse=True)

    return InsiderAnalysis(
        ticker=ticker,
        signal=signal,
        confidence=confidence,
        total_transactions=len(transactions),
        buy_transactions=len(buy_transactions),
        sell_transactions=len(sell_transactions),
        total_buy_value=total_buy_value,
        total_sell_value=total_sell_value,
        net_activity=net_activity,
        recent_transactions=transactions[:10],  # Top 10 most recent
        interpretation=interpretation,
        time_range=f"Last {days_back} days",
        key_buyers=key_buyers[:5],  # Top 5
        key_sellers=key_sellers[:5]  # Top 5
    )


def _interpret_insider_activity(
    buy_transactions: int,
    sell_transactions: int,
    total_buy_value: float,
    total_sell_value: float,
    net_activity: float,
    key_buyers: List[str],
    key_sellers: List[str],
    days_back: int
) -> tuple[str, str, str]:
    """
    Interpret insider trading activity and generate signal

    Returns:
        (signal, confidence, interpretation)
    """
    # Calculate ratios
    total_transactions = buy_transactions + sell_transactions
    if total_transactions == 0:
        return "Neutral", "Low", "No insider activity detected"

    buy_ratio = buy_transactions / total_transactions

    # Value-based analysis (more important than count)
    if total_buy_value + total_sell_value > 0:
        value_buy_ratio = total_buy_value / (total_buy_value + total_sell_value)
    else:
        value_buy_ratio = 0.5

    # Determine signal based on activity
    signal = "Neutral"
    confidence = "Low"

    # Strong bullish signals
    if net_activity > 5_000_000 and buy_ratio > 0.7:
        signal = "Strong Buy"
        confidence = "High"
    elif net_activity > 1_000_000 and buy_ratio > 0.6:
        signal = "Buy"
        confidence = "High" if len(key_buyers) > 2 else "Medium"
    elif net_activity > 0 and buy_ratio > 0.5:
        signal = "Buy"
        confidence = "Medium"

    # Bearish signals
    elif net_activity < -5_000_000 and buy_ratio < 0.3:
        signal = "Strong Sell"
        confidence = "High"
    elif net_activity < -1_000_000 and buy_ratio < 0.4:
        signal = "Sell"
        confidence = "High" if len(key_sellers) > 2 else "Medium"
    elif net_activity < 0 and buy_ratio < 0.5:
        signal = "Sell"
        confidence = "Medium"

    # Adjust confidence based on activity level
    if total_transactions < 3:
        confidence = "Low"

    # Generate interpretation
    interpretation = _generate_interpretation(
        signal=signal,
        buy_transactions=buy_transactions,
        sell_transactions=sell_transactions,
        total_buy_value=total_buy_value,
        total_sell_value=total_sell_value,
        net_activity=net_activity,
        key_buyers=key_buyers,
        key_sellers=key_sellers
    )

    return signal, confidence, interpretation


def _generate_interpretation(
    signal: str,
    buy_transactions: int,
    sell_transactions: int,
    total_buy_value: float,
    total_sell_value: float,
    net_activity: float,
    key_buyers: List[str],
    key_sellers: List[str]
) -> str:
    """Generate human-readable interpretation of insider activity"""

    # Format dollar values
    def format_value(value):
        if value >= 1_000_000:
            return f"${value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"${value/1_000:.0f}K"
        else:
            return f"${value:.0f}"

    parts = []

    # Net activity summary
    if net_activity > 1_000_000:
        parts.append(f"Strong insider buying detected with net purchases of {format_value(net_activity)}.")
    elif net_activity > 0:
        parts.append(f"Modest insider buying with net purchases of {format_value(net_activity)}.")
    elif net_activity < -1_000_000:
        parts.append(f"Heavy insider selling detected with net sales of {format_value(abs(net_activity))}.")
    elif net_activity < 0:
        parts.append(f"Insider selling activity with net sales of {format_value(abs(net_activity))}.")
    else:
        parts.append("Balanced insider activity with no clear directional bias.")

    # Transaction mix
    if buy_transactions > sell_transactions * 2:
        parts.append(f"Buyers outnumber sellers significantly ({buy_transactions} buys vs {sell_transactions} sells).")
    elif sell_transactions > buy_transactions * 2:
        parts.append(f"Sellers outnumber buyers significantly ({sell_transactions} sells vs {buy_transactions} buys).")

    # Key participants
    if key_buyers and signal in ["Buy", "Strong Buy"]:
        if len(key_buyers) == 1:
            parts.append(f"Key buyer: {key_buyers[0]}.")
        else:
            parts.append(f"Multiple key buyers including {key_buyers[0]} and others.")

    if key_sellers and signal in ["Sell", "Strong Sell"]:
        if len(key_sellers) == 1:
            parts.append(f"Key seller: {key_sellers[0]}.")
        else:
            parts.append(f"Multiple key sellers including {key_sellers[0]} and others.")

    # Trading context
    if signal in ["Buy", "Strong Buy"]:
        parts.append("Insiders typically buy when they believe stock is undervalued.")
    elif signal in ["Sell", "Strong Sell"]:
        parts.append("Heavy selling may indicate concerns, though could also be portfolio diversification.")

    return " ".join(parts)


def is_crypto(ticker: str) -> bool:
    """Check if ticker is cryptocurrency (insiders only apply to stocks)"""
    crypto_suffixes = ['-USD', '-USDT', 'USD', 'USDT', 'BTC', 'ETH']
    return any(ticker.endswith(suffix) for suffix in crypto_suffixes) or ticker in ['BTC', 'ETH']
