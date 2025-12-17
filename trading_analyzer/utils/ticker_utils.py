"""
Ticker Normalization Utilities
Handles crypto ticker formatting and validation
"""


# Common crypto symbols that need -USD suffix
CRYPTO_SYMBOLS = {
    'BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOGE', 'MATIC', 'DOT', 'AVAX',
    'UNI', 'LINK', 'AAVE', 'CRV', 'SUSHI', 'LTC', 'BCH', 'XLM', 'ALGO', 'VET',
    'ATOM', 'FIL', 'TRX', 'ETC', 'ZEC', 'DASH', 'XMR', 'EOS', 'NEO', 'IOTA',
    'XTZ', 'WAVES', 'ZRX', 'BAT', 'KNC', 'COMP', 'YFI', 'SNX', 'MKR', 'REN',
    'LRC', 'ENJ', 'MANA', 'SAND', 'AXS', 'GALA', 'CHZ', 'APE', 'SHIB', 'PEPE'
}


def normalize_ticker(ticker: str) -> str:
    """
    Normalize ticker symbol for proper yfinance lookup

    Handles:
    - Crypto tickers (adds -USD if needed)
    - Case normalization
    - Whitespace cleanup

    Args:
        ticker: Raw ticker input

    Returns:
        Normalized ticker symbol

    Examples:
        >>> normalize_ticker('btc')
        'BTC-USD'
        >>> normalize_ticker('BTC')
        'BTC-USD'
        >>> normalize_ticker('BTC-USD')
        'BTC-USD'
        >>> normalize_ticker('AAPL')
        'AAPL'
        >>> normalize_ticker('zec')
        'ZEC-USD'
    """
    if not ticker:
        return ticker

    # Clean up
    ticker = ticker.strip().upper()

    # If already has -USD, return as-is
    if ticker.endswith('-USD'):
        return ticker

    # If it's a known crypto symbol, add -USD
    base_symbol = ticker.split('-')[0]  # Handle cases like BTC-USDT
    if base_symbol in CRYPTO_SYMBOLS:
        return f"{base_symbol}-USD"

    # Otherwise return as-is (stocks, ETFs, etc.)
    return ticker


def is_crypto_ticker(ticker: str) -> bool:
    """
    Check if ticker is a cryptocurrency

    Args:
        ticker: Ticker symbol

    Returns:
        True if crypto, False otherwise
    """
    if not ticker:
        return False

    ticker = ticker.upper()

    # Check if ends with -USD
    if ticker.endswith('-USD'):
        return True

    # Check if known crypto symbol
    return ticker in CRYPTO_SYMBOLS


def normalize_ticker_list(tickers: list) -> list:
    """
    Normalize a list of tickers

    Args:
        tickers: List of raw ticker strings

    Returns:
        List of normalized tickers
    """
    return [normalize_ticker(t) for t in tickers if t]


def validate_ticker_format(ticker: str) -> tuple[bool, str]:
    """
    Validate ticker format

    Args:
        ticker: Ticker symbol

    Returns:
        (is_valid: bool, message: str)
    """
    if not ticker:
        return False, "Empty ticker"

    ticker = ticker.strip()

    if len(ticker) > 10:
        return False, "Ticker too long (max 10 characters)"

    if not ticker.replace('-', '').isalnum():
        return False, "Ticker contains invalid characters"

    return True, "Valid"


# For backward compatibility, export main function
__all__ = [
    'normalize_ticker',
    'is_crypto_ticker',
    'normalize_ticker_list',
    'validate_ticker_format',
    'CRYPTO_SYMBOLS'
]
