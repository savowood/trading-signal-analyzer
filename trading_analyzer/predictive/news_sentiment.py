"""
News Sentiment Analysis using FinnHub API
Real-time news aggregation and sentiment scoring
"""
import requests
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class NewsArticle:
    """Individual news article with sentiment"""
    headline: str
    summary: str
    source: str
    datetime: int  # Unix timestamp
    url: str
    sentiment: float  # -1.0 to 1.0 (negative to positive)

    def time_ago(self) -> str:
        """Return human-readable time ago string"""
        article_time = datetime.fromtimestamp(self.datetime)
        now = datetime.now()
        delta = now - article_time

        hours = delta.total_seconds() / 3600
        if hours < 1:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m ago"
        elif hours < 24:
            return f"{int(hours)}h ago"
        else:
            days = int(hours / 24)
            return f"{days}d ago"


@dataclass
class NewsSentiment:
    """Aggregated news sentiment analysis"""
    ticker: str
    overall_sentiment: str  # "Bullish", "Bearish", "Neutral", "Mixed"
    sentiment_score: float  # -1.0 to 1.0
    confidence: str  # "High", "Medium", "Low"

    positive_count: int
    negative_count: int
    neutral_count: int
    total_articles: int

    recent_articles: List[NewsArticle]  # Last 5 most relevant

    interpretation: str
    time_range: str  # "Last 24 Hours", "Last 7 Days", etc.


class FinnHubNewsClient:
    """
    FinnHub API client for news sentiment
    Free tier: 60 calls/minute
    """

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self, api_key: str):
        """
        Initialize FinnHub client

        Args:
            api_key: FinnHub API key
        """
        self.api_key = api_key
        self.last_call_time = 0
        self.min_call_interval = 1.0  # 1 second between calls (60/min)

    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_call_interval:
            time.sleep(self.min_call_interval - elapsed)
        self.last_call_time = time.time()

    def get_company_news(self, symbol: str, days_back: int = 1) -> List[Dict]:
        """
        Get company news for a symbol

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            days_back: Number of days to look back (default 1 = last 24 hours)

        Returns:
            List of news articles
        """
        self._rate_limit()

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        from_date = start_date.strftime('%Y-%m-%d')
        to_date = end_date.strftime('%Y-%m-%d')

        # Clean symbol (remove -USD for crypto)
        clean_symbol = symbol.replace('-USD', '').upper()

        try:
            url = f"{self.BASE_URL}/company-news"
            params = {
                'symbol': clean_symbol,
                'from': from_date,
                'to': to_date,
                'token': self.api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"⚠️  FinnHub API error for {symbol}: {e}")
            return []

    def get_news_sentiment_score(self, symbol: str, days_back: int = 1) -> Optional[float]:
        """
        Get overall sentiment score using FinnHub's sentiment endpoint

        Args:
            symbol: Stock symbol
            days_back: Number of days to analyze

        Returns:
            Sentiment score (-1.0 to 1.0) or None
        """
        self._rate_limit()

        # Clean symbol
        clean_symbol = symbol.replace('-USD', '').upper()

        try:
            url = f"{self.BASE_URL}/news-sentiment"
            params = {
                'symbol': clean_symbol,
                'token': self.api_key
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                # FinnHub returns sentiment data with various metrics
                if 'sentiment' in data:
                    return data['sentiment'].get('score', 0.0)
                elif 'companyNewsScore' in data:
                    return data['companyNewsScore']

            return None

        except requests.exceptions.RequestException:
            return None


def analyze_news_sentiment(ticker: str, api_key: str, days_back: int = 1) -> Optional[NewsSentiment]:
    """
    Analyze news sentiment for a ticker

    Args:
        ticker: Stock/Crypto symbol
        api_key: FinnHub API key
        days_back: Number of days to analyze (default 1 = last 24 hours)

    Returns:
        NewsSentiment object or None
    """
    if not api_key or api_key == "your_finnhub_api_key_here":
        return None

    client = FinnHubNewsClient(api_key)

    # Get company news
    news_articles = client.get_company_news(ticker, days_back=days_back)

    if not news_articles:
        return None

    # Parse articles and calculate sentiment
    articles = []
    sentiment_scores = []

    for article in news_articles[:20]:  # Limit to 20 most recent
        try:
            # Extract sentiment (if available) or estimate from headline
            sentiment = article.get('sentiment', 0.0)

            # If no sentiment provided, do basic keyword analysis
            if sentiment == 0.0:
                sentiment = _estimate_sentiment_from_text(
                    article.get('headline', '') + ' ' + article.get('summary', '')
                )

            news_obj = NewsArticle(
                headline=article.get('headline', 'No headline'),
                summary=article.get('summary', '')[:200],  # Limit summary length
                source=article.get('source', 'Unknown'),
                datetime=article.get('datetime', int(time.time())),
                url=article.get('url', ''),
                sentiment=sentiment
            )

            articles.append(news_obj)
            sentiment_scores.append(sentiment)

        except Exception as e:
            continue

    if not articles:
        return None

    # Calculate aggregate sentiment
    positive_count = sum(1 for s in sentiment_scores if s > 0.2)
    negative_count = sum(1 for s in sentiment_scores if s < -0.2)
    neutral_count = len(sentiment_scores) - positive_count - negative_count

    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

    # Determine overall sentiment
    if avg_sentiment > 0.4:
        overall = "Bullish"
        confidence = "High" if avg_sentiment > 0.6 else "Medium"
    elif avg_sentiment < -0.4:
        overall = "Bearish"
        confidence = "High" if avg_sentiment < -0.6 else "Medium"
    elif abs(avg_sentiment) < 0.1:
        overall = "Neutral"
        confidence = "Medium"
    else:
        overall = "Mixed"
        confidence = "Low"

    # Generate interpretation
    interpretation = _generate_interpretation(
        avg_sentiment, positive_count, negative_count, articles
    )

    # Time range label
    time_range = f"Last {days_back * 24} Hours" if days_back == 1 else f"Last {days_back} Days"

    return NewsSentiment(
        ticker=ticker,
        overall_sentiment=overall,
        sentiment_score=avg_sentiment,
        confidence=confidence,
        positive_count=positive_count,
        negative_count=negative_count,
        neutral_count=neutral_count,
        total_articles=len(articles),
        recent_articles=articles[:5],  # Top 5 most recent
        interpretation=interpretation,
        time_range=time_range
    )


def _estimate_sentiment_from_text(text: str) -> float:
    """
    Simple keyword-based sentiment estimation
    Returns -1.0 to 1.0
    """
    text_lower = text.lower()

    # Positive keywords
    positive_words = [
        'beat', 'beats', 'exceed', 'exceeds', 'surge', 'surges', 'rally',
        'bullish', 'upgrade', 'raised', 'raises', 'partnership', 'deal',
        'growth', 'strong', 'record', 'success', 'breakthrough', 'approval',
        'innovation', 'launch', 'expand', 'acquisition', 'profit'
    ]

    # Negative keywords
    negative_words = [
        'miss', 'misses', 'decline', 'declines', 'fall', 'falls', 'drop',
        'bearish', 'downgrade', 'cut', 'cuts', 'concern', 'concerns',
        'weak', 'loss', 'losses', 'fail', 'fails', 'recall', 'lawsuit',
        'investigation', 'fraud', 'scandal', 'bankruptcy'
    ]

    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    if positive_count == 0 and negative_count == 0:
        return 0.0

    # Calculate score
    total = positive_count + negative_count
    score = (positive_count - negative_count) / total if total > 0 else 0.0

    # Scale to -1.0 to 1.0
    return max(-1.0, min(1.0, score))


def _generate_interpretation(avg_sentiment: float, pos_count: int,
                             neg_count: int, articles: List[NewsArticle]) -> str:
    """Generate human-readable interpretation of sentiment"""

    if avg_sentiment > 0.4:
        if pos_count > neg_count * 2:
            return "Strong positive news flow with overwhelmingly bullish sentiment. "
        else:
            return "Positive news sentiment with some negative articles present. "

    elif avg_sentiment < -0.4:
        if neg_count > pos_count * 2:
            return "Heavy negative news flow with predominantly bearish sentiment. "
        else:
            return "Negative news sentiment with some positive articles present. "

    elif abs(avg_sentiment) < 0.1:
        return "Balanced news coverage with neutral overall sentiment. "

    else:
        return "Mixed news sentiment with conflicting signals. "
