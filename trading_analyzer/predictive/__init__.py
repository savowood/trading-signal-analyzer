"""
Predictive Trading Analysis Module
Forward-looking indicators for price forecasting
"""

from .fibonacci import (
    FibonacciLevels,
    FibonacciAnalyzer,
    analyze_fibonacci
)
from .news_sentiment import (
    NewsArticle,
    NewsSentiment,
    FinnHubNewsClient,
    analyze_news_sentiment
)
from .insider_trading import (
    InsiderTransaction,
    InsiderAnalysis,
    PolygonInsiderClient,
    SECEdgarClient,
    analyze_insider_trading,
    is_crypto
)

__all__ = [
    # Fibonacci
    'FibonacciLevels',
    'FibonacciAnalyzer',
    'analyze_fibonacci',

    # News Sentiment
    'NewsArticle',
    'NewsSentiment',
    'FinnHubNewsClient',
    'analyze_news_sentiment',

    # Insider Trading
    'InsiderTransaction',
    'InsiderAnalysis',
    'PolygonInsiderClient',
    'SECEdgarClient',
    'analyze_insider_trading',
    'is_crypto',
]
