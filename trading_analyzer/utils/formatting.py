"""
Display Formatting Utilities
Smart formatting for prices, percentages, and numbers
"""


def format_crypto_price(price: float) -> str:
    """
    Format crypto price with appropriate decimal precision

    For expensive cryptos like BTC ($80,000), show 2 decimals
    For penny cryptos like DOGE ($0.12553), show 5 decimals

    Args:
        price: Price in USD

    Returns:
        Formatted price string with $ prefix
    """
    if price >= 1000:
        # Expensive coins (BTC, ETH) - 2 decimals
        return f"${price:,.2f}"
    elif price >= 1:
        # Mid-range coins ($1-$1000) - 4 decimals
        return f"${price:.4f}"
    elif price >= 0.01:
        # Penny coins ($0.01-$1) - 5 decimals
        return f"${price:.5f}"
    else:
        # Sub-penny coins - 6 decimals or scientific notation
        if price >= 0.000001:
            return f"${price:.6f}"
        else:
            return f"${price:.2e}"


def format_stock_price(price: float) -> str:
    """
    Format stock price with standard 2 decimal precision

    Args:
        price: Price in USD

    Returns:
        Formatted price string with $ prefix
    """
    return f"${price:,.2f}"


def format_price(price: float, is_crypto: bool = False) -> str:
    """
    Auto-format price based on asset type

    Args:
        price: Price in USD
        is_crypto: True for crypto, False for stocks

    Returns:
        Formatted price string with $ prefix
    """
    if is_crypto:
        return format_crypto_price(price)
    else:
        return format_stock_price(price)


def format_percentage(value: float, decimals: int = 2, show_sign: bool = True) -> str:
    """
    Format percentage value

    Args:
        value: Percentage value (e.g., 5.23 for 5.23%)
        decimals: Number of decimal places
        show_sign: Include + for positive values

    Returns:
        Formatted percentage string
    """
    if show_sign:
        return f"{value:+.{decimals}f}%"
    else:
        return f"{value:.{decimals}f}%"


def format_volume(volume: int) -> str:
    """
    Format volume with thousand separators

    Args:
        volume: Volume as integer

    Returns:
        Formatted volume string
    """
    return f"{volume:,}"


def format_market_cap(market_cap: float) -> str:
    """
    Format market cap in millions or billions

    Args:
        market_cap: Market cap in dollars

    Returns:
        Formatted market cap string (e.g., "$1.5B", "$350M")
    """
    if market_cap >= 1_000_000_000:
        return f"${market_cap / 1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:
        return f"${market_cap / 1_000_000:.2f}M"
    elif market_cap >= 1_000:
        return f"${market_cap / 1_000:.2f}K"
    else:
        return f"${market_cap:.2f}"
