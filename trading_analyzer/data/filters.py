"""
Smart Filtering Logic
Heuristic-based filtering to reduce candidate lists without API calls
"""
from typing import List, Dict
from ..config import ETF_KEYWORDS, PRIORITY_EXCHANGES


def is_likely_etf(name: str) -> bool:
    """Check if ticker name suggests it's an ETF"""
    name_upper = name.upper()
    return any(keyword in name_upper for keyword in ETF_KEYWORDS)


def is_test_symbol(ticker: str) -> bool:
    """Check if ticker is a test symbol"""
    return ticker.endswith('.TEST')


def is_warrant(ticker: str) -> bool:
    """
    Check if ticker is a warrant
    More specific pattern: ends in W without a letter before it
    """
    if ticker.endswith('.W'):
        return True

    # Check for warrant pattern like "ABCDW" but not "BELOW"
    if len(ticker) > 4 and ticker[-1] == 'W' and not ticker[-2].isalpha():
        return True

    return False


def is_priority_exchange(exchange: str) -> bool:
    """Check if exchange is high-priority for micro-caps"""
    return exchange in PRIORITY_EXCHANGES


def is_likely_delisted(ticker: str, price: float, volume: int, market_cap: float) -> bool:
    """
    Check if stock appears to be delisted or inactive

    Args:
        ticker: Stock symbol
        price: Current price
        volume: Current volume
        market_cap: Market capitalization

    Returns:
        True if stock appears delisted/inactive
    """
    # Delisting suffixes
    delisting_suffixes = ['Q', 'E', 'D']
    if any(ticker.endswith(suffix) for suffix in delisting_suffixes):
        return True

    # Extremely low price and volume
    if price < 0.0001 and volume < 1000:
        return True

    # No volume
    if volume == 0:
        return True

    # Tiny market cap
    if market_cap and market_cap < 100000:
        return True

    return False


def filter_microcap_candidates(all_tickers: List[Dict]) -> List[str]:
    """
    Smart filter to identify likely micro-cap candidates WITHOUT API calls

    Uses heuristics:
    - Exchange filtering (prioritize NASDAQ, NCM, AMEX, BATS)
    - Name filtering (exclude ETFs)
    - Pattern filtering (exclude test symbols, warrants)
    - Length filtering (exclude special symbols)

    Args:
        all_tickers: List of dicts with ticker, exchange, name

    Returns:
        List of ticker symbols (candidate micro-caps)
    """
    candidates = []

    for ticker_dict in all_tickers:
        ticker = ticker_dict['ticker']
        name = ticker_dict['name']
        exchange = ticker_dict['exchange']

        # Skip test symbols and warrants
        if is_test_symbol(ticker) or is_warrant(ticker):
            continue

        # Skip long tickers (usually special symbols)
        if len(ticker) > 5:
            continue

        # Skip ETFs
        if is_likely_etf(name):
            continue

        # Include if on priority exchange
        if is_priority_exchange(exchange):
            candidates.append(ticker)

    return candidates


def prioritize_tickers(tickers: List[str], limit: int = 500) -> List[str]:
    """
    Prioritize tickers for scanning

    Priority criteria:
    1. NCM exchange patterns (4-letter tickers)
    2. Small exchange tickers
    3. Alphabetical for consistency

    Args:
        tickers: List of ticker symbols
        limit: Maximum number to return

    Returns:
        Prioritized list of tickers (up to limit)
    """
    if len(tickers) <= limit:
        return tickers

    priority_tickers = []
    regular_tickers = []

    for ticker in tickers:
        # Prioritize 4-letter tickers (likely NCM)
        if len(ticker) == 4:
            priority_tickers.append(ticker)
        else:
            regular_tickers.append(ticker)

    # Take top priority + some regular = limit total
    priority_count = min(int(limit * 0.8), len(priority_tickers))  # 80% from priority
    regular_count = limit - priority_count

    return priority_tickers[:priority_count] + regular_tickers[:regular_count]


class TickerFilter:
    """Reusable ticker filtering with statistics"""

    def __init__(self):
        self.stats = {
            'total': 0,
            'filtered_etf': 0,
            'filtered_test': 0,
            'filtered_warrant': 0,
            'filtered_exchange': 0,
            'filtered_length': 0,
            'passed': 0
        }

    def filter(self, all_tickers: List[Dict]) -> List[str]:
        """Filter tickers and track statistics"""
        self.stats['total'] = len(all_tickers)
        candidates = []

        for ticker_dict in all_tickers:
            ticker = ticker_dict['ticker']
            name = ticker_dict['name']
            exchange = ticker_dict['exchange']

            # Test symbol check
            if is_test_symbol(ticker):
                self.stats['filtered_test'] += 1
                continue

            # Warrant check
            if is_warrant(ticker):
                self.stats['filtered_warrant'] += 1
                continue

            # Length check
            if len(ticker) > 5:
                self.stats['filtered_length'] += 1
                continue

            # ETF check
            if is_likely_etf(name):
                self.stats['filtered_etf'] += 1
                continue

            # Exchange check
            if not is_priority_exchange(exchange):
                self.stats['filtered_exchange'] += 1
                continue

            # Passed all filters
            candidates.append(ticker)
            self.stats['passed'] += 1

        return candidates

    def get_stats(self) -> Dict:
        """Get filtering statistics"""
        return self.stats.copy()

    def print_stats(self):
        """Print filtering statistics"""
        print(f"   Filtering Results:")
        print(f"      Total tickers: {self.stats['total']}")
        print(f"      Filtered (ETF): {self.stats['filtered_etf']}")
        print(f"      Filtered (Test): {self.stats['filtered_test']}")
        print(f"      Filtered (Warrant): {self.stats['filtered_warrant']}")
        print(f"      Filtered (Exchange): {self.stats['filtered_exchange']}")
        print(f"      Filtered (Length): {self.stats['filtered_length']}")
        print(f"      ✅ Passed: {self.stats['passed']}")
        reduction_pct = (1 - self.stats['passed'] / self.stats['total']) * 100
        print(f"      Reduction: {reduction_pct:.1f}%")
