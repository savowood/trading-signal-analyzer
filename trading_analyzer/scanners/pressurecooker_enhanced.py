"""
Pressure Cooker Scanner - ENHANCED VERSION
Advanced Short Squeeze Setup Detection System

Phase 1 Features (No External APIs):
- Technical indicators (RSI, MACD, Bollinger Bands)
- Time-series analysis (setup progression)
- Enhanced multi-factor scoring
- Improved display output

Phase 2 Features (Free APIs):
- NewsAPI catalyst detection
- Options flow analysis
- Reddit sentiment (WSB/stocks)

Author: Michael Johnson
License: GPL v3
"""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from ..core.scanner import Scanner, ScanResult, ScanParameters
from ..config import API_KEYS
from ..utils import (
    parallel_analyze,
    SmartPreFilter,
    create_pressure_cooker_prefilter,
    TechnicalAnalyzer,
    DataValidator
)


@dataclass
class EnhancedPressureCookerResult(ScanResult):
    """Extended result with comprehensive squeeze analysis"""
    # Basic squeeze metrics
    short_percent: float = 0
    days_to_cover: float = 0
    has_reverse_split: bool = False
    consecutive_volume_days: int = 0
    breaking_20d_high: bool = False
    avg_volume_20d: int = 0

    # Technical indicators
    rsi: float = 50
    rsi_oversold: bool = False
    macd_bullish: bool = False
    near_bb_support: bool = False

    # Options flow
    call_put_ratio: float = 0
    unusual_options_activity: bool = False
    gamma_squeeze_potential: bool = False

    # Catalyst detection
    has_news_catalyst: bool = False
    catalyst_type: str = ""
    news_count: int = 0
    news_headline: str = ""

    # Social sentiment
    wsb_mentions: int = 0
    social_sentiment: str = ""
    trending_social: bool = False

    # Setup progression
    setup_stage: str = ""  # 'forming', 'ready', 'breaking'
    volume_trend: str = ""  # 'accelerating', 'steady', 'declining'

    # Enhanced scoring
    technical_score: int = 0
    catalyst_score: int = 0
    risk_score: int = 0
    setup_quality: str = ""
    grade: str = ""
    key_factors: List[str] = field(default_factory=list)


class EnhancedPressureCookerScanner(Scanner):
    """
    Advanced Pressure Cooker Scanner with multi-factor analysis

    Scoring System (0-100):
    1. Squeeze Fundamentals (40 pts): float, short%, volume
    2. Technical Setup (25 pts): RSI, MACD, Bollinger Bands
    3. Catalyst Strength (20 pts): news, options, social
    4. Risk Factors (15 pts): liquidity, dilution, sentiment
    """

    def __init__(self):
        super().__init__("Enhanced Pressure Cooker")
        self.min_float = 100_000
        self.max_float = 5_000_000
        self.min_price = 5.0
        self.max_price = 20.0
        self.min_rel_vol = 3.0
        self.min_short_interest = 15
        self.min_volume = 500_000

        # Initialize utility modules
        self.prefilter = create_pressure_cooker_prefilter()
        self.validator = DataValidator()
        self.technical_analyzer = TechnicalAnalyzer()

    # ========== PHASE 1: TECHNICAL INDICATORS ==========

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50

    def _calculate_macd(self, prices: pd.Series) -> Tuple[float, float, bool]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()

        macd_val = macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0
        signal_val = signal.iloc[-1] if not pd.isna(signal.iloc[-1]) else 0
        bullish = macd_val > signal_val

        return macd_val, signal_val, bullish

    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()

        upper = sma + (std * 2)
        lower = sma - (std * 2)

        current_price = prices.iloc[-1]
        upper_val = upper.iloc[-1] if not pd.isna(upper.iloc[-1]) else current_price * 1.1
        lower_val = lower.iloc[-1] if not pd.isna(lower.iloc[-1]) else current_price * 0.9

        return upper_val, lower_val, current_price

    def _analyze_technicals(self, hist: pd.DataFrame, rel_vol: float = 1.0) -> Dict:
        """Comprehensive technical analysis with S/R and Volume Profile"""
        if len(hist) < 30:
            return {
                'rsi': 50,
                'rsi_oversold': False,
                'macd_bullish': False,
                'near_bb_support': False,
                'technical_score': 0,
                'sr_data': None,
                'vp_data': None
            }

        # RSI
        rsi = self._calculate_rsi(hist['Close'])
        rsi_oversold = rsi < 30

        # MACD
        macd, signal, macd_bullish = self._calculate_macd(hist['Close'])

        # Bollinger Bands
        bb_upper, bb_lower, current_price = self._calculate_bollinger_bands(hist['Close'])
        near_bb_support = current_price < (bb_lower * 1.05)  # Within 5% of lower band

        # Support/Resistance levels
        sr_levels = self.technical_analyzer.find_support_resistance(hist)

        # Volume Profile
        volume_profile = self.technical_analyzer.calculate_volume_profile(hist)

        # Advanced technical scoring using the unified method
        sr_vp_score, sr_vp_factors = self.technical_analyzer.score_technical_setup(
            sr_levels, volume_profile, current_price, rel_vol
        )

        # Calculate technical score
        tech_score = 0
        if rsi_oversold:
            tech_score += 8
        if macd_bullish:
            tech_score += 7
        if near_bb_support:
            tech_score += 10

        # Add S/R and VP scores (max 25 points total for technical)
        tech_score = min(25, tech_score + sr_vp_score)

        return {
            'rsi': rsi,
            'rsi_oversold': rsi_oversold,
            'macd_bullish': macd_bullish,
            'near_bb_support': near_bb_support,
            'technical_score': tech_score,
            'sr_data': sr_levels,
            'vp_data': volume_profile
        }

    def _analyze_setup_progression(self, hist: pd.DataFrame) -> Dict:
        """Analyze how the squeeze setup is evolving"""
        if len(hist) < 30:
            return {
                'setup_stage': 'unknown',
                'volume_trend': 'unknown',
                'consolidating': False,
                'approaching_breakout': False
            }

        # Volume trend (using linear regression)
        volumes = hist['Volume'].values[-20:]
        x = np.arange(len(volumes))
        if len(x) > 0 and len(volumes) > 0:
            volume_slope = np.polyfit(x, volumes, 1)[0]
            volume_trend = 'accelerating' if volume_slope > 0 else 'declining'
        else:
            volume_trend = 'steady'

        # Price consolidation (ATR analysis)
        high_low = hist['High'] - hist['Low']
        atr = high_low.rolling(14).mean()
        recent_atr = atr.tail(5).mean()
        older_atr = atr.tail(20).mean()
        consolidating = recent_atr < older_atr * 0.7 if not pd.isna(recent_atr) and not pd.isna(older_atr) else False

        # Breakout detection
        resistance = hist['High'].tail(20).max()
        current_price = hist['Close'].iloc[-1]
        approaching_breakout = current_price > (resistance * 0.95)

        # Determine setup stage
        if consolidating and not approaching_breakout:
            stage = 'forming'
        elif consolidating and approaching_breakout:
            stage = 'ready'
        elif approaching_breakout and volume_trend == 'accelerating':
            stage = 'breaking'
        else:
            stage = 'early'

        return {
            'setup_stage': stage,
            'volume_trend': volume_trend,
            'consolidating': consolidating,
            'approaching_breakout': approaching_breakout
        }

    # ========== PHASE 2: OPTIONS FLOW ANALYSIS ==========

    def _analyze_options_flow(self, ticker: str) -> Dict:
        """Analyze options activity for gamma squeeze potential"""
        try:
            stock = yf.Ticker(ticker)
            opts = stock.options

            if not opts or len(opts) == 0:
                return {
                    'call_put_ratio': 0,
                    'unusual_activity': False,
                    'gamma_squeeze_potential': False,
                    'options_score': 0
                }

            # Get nearest expiration
            chain = stock.option_chain(opts[0])
            calls = chain.calls
            puts = chain.puts

            # Volume analysis
            total_call_volume = calls['volume'].sum() if 'volume' in calls else 0
            total_put_volume = puts['volume'].sum() if 'volume' in puts else 0
            call_put_ratio = total_call_volume / total_put_volume if total_put_volume > 0 else 0

            # Open interest analysis
            total_call_oi = calls['openInterest'].sum() if 'openInterest' in calls else 0
            total_put_oi = puts['openInterest'].sum() if 'openInterest' in puts else 0

            # Detect unusual activity
            avg_call_volume = calls['volume'].mean() if 'volume' in calls and len(calls) > 0 else 0
            unusual_activity = total_call_volume > (avg_call_volume * 5) if avg_call_volume > 0 else False
            gamma_potential = total_call_oi > (total_put_oi * 2)

            # Scoring
            options_score = 0
            if call_put_ratio > 3:
                options_score += 10
            if unusual_activity:
                options_score += 5
            if gamma_potential:
                options_score += 5

            return {
                'call_put_ratio': call_put_ratio,
                'unusual_activity': unusual_activity,
                'gamma_squeeze_potential': gamma_potential,
                'options_score': options_score
            }
        except Exception as e:
            return {
                'call_put_ratio': 0,
                'unusual_activity': False,
                'gamma_squeeze_potential': False,
                'options_score': 0
            }

    # ========== PHASE 2: NEWS/CATALYST DETECTION ==========

    def _detect_catalyst_news(self, ticker: str) -> Dict:
        """Detect catalysts using NewsAPI"""
        api_key = API_KEYS.get('newsapi', '')

        if not api_key:
            # Fallback: no news data
            return {
                'has_catalyst': False,
                'catalyst_type': 'Unknown',
                'news_count': 0,
                'headline': '',
                'catalyst_score': 0
            }

        try:
            import requests
            from datetime import datetime, timedelta

            # Search for news in last 7 days
            date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            url = f"https://newsapi.org/v2/everything?q={ticker}&from={date_from}&sortBy=publishedAt&apiKey={api_key}"

            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                return {
                    'has_catalyst': False,
                    'catalyst_type': 'Unknown',
                    'news_count': 0,
                    'headline': '',
                    'catalyst_score': 0
                }

            data = response.json()
            articles = data.get('articles', [])

            if not articles:
                return {
                    'has_catalyst': False,
                    'catalyst_type': 'No recent news',
                    'news_count': 0,
                    'headline': '',
                    'catalyst_score': 0
                }

            # Classify catalyst type
            catalyst_type = self._classify_catalyst(articles)

            # Scoring
            catalyst_score = 0
            if len(articles) > 5:
                catalyst_score += 10  # Multiple news articles = strong catalyst
            elif len(articles) > 0:
                catalyst_score += 5

            return {
                'has_catalyst': True,
                'catalyst_type': catalyst_type,
                'news_count': len(articles),
                'headline': articles[0]['title'][:100] if articles else '',
                'catalyst_score': catalyst_score
            }
        except Exception as e:
            return {
                'has_catalyst': False,
                'catalyst_type': 'Error fetching news',
                'news_count': 0,
                'headline': '',
                'catalyst_score': 0
            }

    def _classify_catalyst(self, articles: List[Dict]) -> str:
        """Classify the type of catalyst from news articles"""
        # Combine all titles and descriptions
        text = ' '.join([
            (article.get('title', '') + ' ' + article.get('description', ''))
            for article in articles[:10]
        ]).lower()

        # Keyword matching
        if any(word in text for word in ['earnings', 'eps', 'revenue', 'profit', 'beat', 'miss']):
            return 'Earnings'
        elif any(word in text for word in ['fda', 'approval', 'clinical', 'trial', 'drug']):
            return 'FDA/Biotech'
        elif any(word in text for word in ['merger', 'acquisition', 'buyout', 'takeover']):
            return 'M&A'
        elif any(word in text for word in ['contract', 'deal', 'partnership', 'agreement']):
            return 'Contract/Deal'
        elif any(word in text for word in ['short', 'seller', 'report', 'fraud', 'investigation']):
            return 'Short Report'
        else:
            return 'General News'

    # ========== PHASE 2: SOCIAL SENTIMENT ==========

    def _analyze_social_sentiment(self, ticker: str) -> Dict:
        """Analyze Reddit (WSB) sentiment"""
        # Check if Reddit API credentials are available
        if not all([API_KEYS.get('reddit_client_id'), API_KEYS.get('reddit_client_secret')]):
            # Fallback: no social data
            return {
                'wsb_mentions': 0,
                'sentiment': 'unknown',
                'trending': False,
                'social_score': 0
            }

        try:
            import praw

            reddit = praw.Reddit(
                client_id=API_KEYS.get('reddit_client_id'),
                client_secret=API_KEYS.get('reddit_client_secret'),
                user_agent='TradingAnalyzer/1.0'
            )

            # Search WallStreetBets
            wsb = reddit.subreddit('wallstreetbets')
            mentions = 0
            sentiment_score = 0

            for post in wsb.search(ticker, limit=50, time_filter='week'):
                mentions += 1
                # Simple sentiment: bullish vs bearish keywords
                text = (post.title + ' ' + post.selftext).lower()
                sentiment_score += text.count('🚀') + text.count('moon') + text.count('calls')
                sentiment_score -= text.count('🐻') + text.count('puts') + text.count('puts')

            trending = mentions > 10
            sentiment = 'bullish' if sentiment_score > 0 else 'bearish' if sentiment_score < 0 else 'neutral'

            # Scoring
            social_score = 0
            if mentions > 20:
                social_score += 10
            elif mentions > 10:
                social_score += 5

            if sentiment == 'bullish':
                social_score += 5

            return {
                'wsb_mentions': mentions,
                'sentiment': sentiment,
                'trending': trending,
                'social_score': social_score
            }
        except Exception as e:
            return {
                'wsb_mentions': 0,
                'sentiment': 'unknown',
                'trending': False,
                'social_score': 0
            }

    # ========== ENHANCED SCORING ALGORITHM ==========

    def _calculate_enhanced_score(self, metrics: Dict) -> Dict:
        """
        Multi-factor scoring system

        Categories:
        1. Squeeze Fundamentals (40 pts): float, short%, volume
        2. Technical Setup (25 pts): RSI, MACD, BB
        3. Catalyst Strength (20 pts): news, options, social
        4. Risk Adjustment (15 pts): liquidity, dilution
        """
        score = 0
        key_factors = []

        # 1. SQUEEZE FUNDAMENTALS (40 points max)
        float_score = 0
        if metrics['float_m'] < 1:
            float_score = 15
            key_factors.append('Ultra-Low Float (<1M)')
        elif metrics['float_m'] < 2:
            float_score = 12
        elif metrics['float_m'] < 5:
            float_score = 10
        score += float_score

        short_score = 0
        if metrics['short_percent'] > 40:
            short_score = 15
            key_factors.append('Extreme Short Interest (>40%)')
        elif metrics['short_percent'] > 30:
            short_score = 12
        elif metrics['short_percent'] > 20:
            short_score = 10
        elif metrics['short_percent'] > 10:
            short_score = 7
        score += short_score

        volume_score = 0
        if metrics['rel_vol'] > 10:
            volume_score = 10
            key_factors.append('Massive Volume (>10x)')
        elif metrics['rel_vol'] > 7:
            volume_score = 8
        elif metrics['rel_vol'] > 5:
            volume_score = 6
        elif metrics['rel_vol'] > 3:
            volume_score = 4
        score += volume_score

        # 2. TECHNICAL SETUP (25 points max)
        score += metrics.get('technical_score', 0)
        if metrics.get('rsi_oversold'):
            key_factors.append('RSI Oversold')
        if metrics.get('macd_bullish'):
            key_factors.append('MACD Bullish Cross')

        # 3. CATALYST STRENGTH (20 points max)
        score += metrics.get('options_score', 0)
        score += metrics.get('catalyst_score', 0)
        score += metrics.get('social_score', 0)

        if metrics.get('has_news_catalyst'):
            key_factors.append(f"Catalyst: {metrics.get('catalyst_type', 'News')}")
        if metrics.get('unusual_options_activity'):
            key_factors.append('Unusual Options Activity')
        if metrics.get('trending_social'):
            key_factors.append('Trending on Social Media')

        # 4. RISK ADJUSTMENT (-15 to +15 points)
        risk_score = 0
        if metrics.get('has_reverse_split'):
            risk_score -= 5
        if metrics.get('avg_volume_20d', 1000000) < 500000:
            risk_score -= 5
        if not metrics.get('has_news_catalyst'):
            risk_score -= 3

        # Setup progression bonus
        if metrics.get('setup_stage') == 'ready':
            risk_score += 5
            key_factors.append('Setup Ready to Break')
        elif metrics.get('setup_stage') == 'breaking':
            risk_score += 8
            key_factors.append('Breakout in Progress')

        score = max(0, min(100, score + risk_score))

        # Determine quality
        if score >= 90:
            quality = "EXCELLENT - Prime squeeze setup"
        elif score >= 80:
            quality = "STRONG - High potential"
        elif score >= 70:
            quality = "GOOD - Moderate potential"
        elif score >= 60:
            quality = "MARGINAL - Proceed with caution"
        else:
            quality = "WEAK - High risk"

        # Grade
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"

        return {
            'score': score,
            'grade': grade,
            'setup_quality': quality,
            'key_factors': key_factors,
            'technical_score': metrics.get('technical_score', 0),
            'catalyst_score': metrics.get('catalyst_score', 0) + metrics.get('options_score', 0) + metrics.get('social_score', 0),
            'risk_score': risk_score
        }

    # ========== MAIN ANALYSIS FUNCTION ==========

    def analyze_ticker(self, ticker: str, period: str = "6mo") -> Optional[EnhancedPressureCookerResult]:
        """
        Comprehensive squeeze analysis with all Phase 1 and Phase 2 features
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, prepost=True)

            if hist.empty or len(hist) < 20:
                return None

            # Convert timezone-aware index to timezone-naive to avoid datetime arithmetic issues
            if hist.index.tz is not None:
                hist.index = hist.index.tz_localize(None)

            info = stock.info

            # Validate data quality
            validation = self.validator.validate_stock_data(ticker, hist, info)
            if not validation.is_valid:
                print(f"   ⚠️  Data quality issues for {ticker} (score: {validation.quality_score}/100)")
                if validation.quality_score < 30:
                    return None  # Skip if data is really bad

            current_price = hist['Close'].iloc[-1]

            # Quick filters
            if not (self.min_price <= current_price <= self.max_price):
                return None

            # Volume analysis
            current_volume = hist['Volume'].iloc[-1]
            avg_volume_20d = hist['Volume'].tail(20).mean()
            rel_vol = current_volume / avg_volume_20d if avg_volume_20d > 0 else 0

            if current_volume < self.min_volume or rel_vol < self.min_rel_vol:
                return None

            # Float analysis
            shares_outstanding = info.get('sharesOutstanding', 0)
            float_shares = info.get('floatShares', shares_outstanding)
            float_m = float_shares / 1_000_000 if float_shares > 0 else 999

            if float_shares < self.min_float or float_shares > self.max_float:
                return None

            # Short interest
            short_ratio = info.get('shortRatio', 0)
            short_percent = info.get('shortPercentOfFloat', 0)

            # Basic metrics
            high_20d = hist['High'].tail(20).max()
            breaking_high = current_price >= high_20d * 0.98
            consecutive_vol = self._check_consecutive_volume(hist)
            has_reverse_split = self._detect_reverse_split(hist)
            change_pct = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100

            # PHASE 1: Technical Analysis
            print(f"   📊 Analyzing technicals for {ticker}...")
            technicals = self._analyze_technicals(hist, rel_vol)
            progression = self._analyze_setup_progression(hist)

            # PHASE 2: Options, News, Social
            print(f"   🔍 Checking options flow for {ticker}...")
            options_data = self._analyze_options_flow(ticker)

            print(f"   📰 Detecting catalysts for {ticker}...")
            news_data = self._detect_catalyst_news(ticker)

            print(f"   💬 Analyzing social sentiment for {ticker}...")
            social_data = self._analyze_social_sentiment(ticker)

            # Combine all metrics
            all_metrics = {
                'float_m': float_m,
                'short_percent': short_percent,
                'rel_vol': rel_vol,
                'avg_volume_20d': avg_volume_20d,
                'has_reverse_split': has_reverse_split,
                **technicals,
                **progression,
                **options_data,
                **news_data,
                **social_data
            }

            # Calculate enhanced score
            scoring = self._calculate_enhanced_score(all_metrics)

            # Note: For single ticker analysis, show results regardless of score
            # This allows users to see why a ticker doesn't qualify

            # Build result
            result = EnhancedPressureCookerResult(
                ticker=ticker,
                price=current_price,
                score=scoring['score'],
                rel_vol=rel_vol,
                float_m=float_m,
                change_pct=change_pct,
                catalyst=f"{scoring['setup_quality']} | {len(scoring['key_factors'])} factors",
                description=info.get('industry', 'N/A')[:50],
                source="ENHANCED_PRESSURE_COOKER",
                exchange=info.get('exchange', 'US'),
                volume=int(current_volume),
                market_cap=info.get('marketCap', 0),
                # Basic squeeze metrics
                short_percent=short_percent,
                days_to_cover=short_ratio,
                has_reverse_split=has_reverse_split,
                consecutive_volume_days=consecutive_vol,
                breaking_20d_high=breaking_high,
                avg_volume_20d=int(avg_volume_20d),
                # Technical indicators
                rsi=technicals['rsi'],
                rsi_oversold=technicals['rsi_oversold'],
                macd_bullish=technicals['macd_bullish'],
                near_bb_support=technicals['near_bb_support'],
                # Options flow
                call_put_ratio=options_data['call_put_ratio'],
                unusual_options_activity=options_data['unusual_activity'],
                gamma_squeeze_potential=options_data['gamma_squeeze_potential'],
                # Catalyst
                has_news_catalyst=news_data['has_catalyst'],
                catalyst_type=news_data['catalyst_type'],
                news_count=news_data['news_count'],
                news_headline=news_data['headline'],
                # Social sentiment
                wsb_mentions=social_data['wsb_mentions'],
                social_sentiment=social_data['sentiment'],
                trending_social=social_data['trending'],
                # Setup progression
                setup_stage=progression['setup_stage'],
                volume_trend=progression['volume_trend'],
                # Enhanced scoring
                technical_score=scoring['technical_score'],
                catalyst_score=scoring['catalyst_score'],
                risk_score=scoring['risk_score'],
                setup_quality=scoring['setup_quality'],
                grade=scoring['grade'],
                key_factors=scoring['key_factors']
            )

            return result

        except Exception as e:
            print(f"   ❌ Error analyzing {ticker}: {e}")
            return None

    def _check_consecutive_volume(self, hist: pd.DataFrame, days: int = 3) -> int:
        """Check for consecutive high-volume days"""
        if len(hist) < days:
            return 0

        recent_volume = hist['Volume'].tail(days)
        avg_volume = hist['Volume'].tail(20).mean()

        consecutive_count = 0
        for vol in reversed(list(recent_volume)):
            if vol > avg_volume * 2:
                consecutive_count += 1
            else:
                break

        return consecutive_count

    def _detect_reverse_split(self, hist: pd.DataFrame) -> bool:
        """Detect potential reverse split"""
        if len(hist) < 40:
            return False

        price_changes = hist['Close'].pct_change()
        volume_changes = hist['Volume'].pct_change()

        for i in range(len(hist) - 30, len(hist)):
            if price_changes.iloc[i] > 4.0 and volume_changes.iloc[i] < -0.5:
                return True

        return False

    # ========== SCANNER INTEGRATION ==========

    def scan(self, params: ScanParameters) -> List[ScanResult]:
        """Scan interface (use scan_market for actual scanning)"""
        print("💡 Enhanced Pressure Cooker requires market-wide scanning.")
        print("   Use the 'Scan Market' option from the menu.")
        return []

    def scan_market(self, params: ScanParameters, max_candidates: int = 100) -> List[EnhancedPressureCookerResult]:
        """Market-wide enhanced squeeze detection with parallel processing"""
        print(f"\n🔥 ENHANCED PRESSURE COOKER: Multi-factor squeeze analysis...")
        print(f"   Criteria: ${self.min_price}-${self.max_price}, <{self.max_float/1e6:.0f}M float, {self.min_rel_vol}x+ volume")
        print(f"   Analysis: Technicals + Options + News + Social Sentiment")

        candidates = self._get_candidates(params, max_candidates)

        if not candidates:
            print("❌ No candidates found")
            return []

        # Pre-filter candidates (fast rejection)
        print(f"\n🔍 Pre-filtering {len(candidates)} candidates...")
        filtered_candidates = []
        for ticker in candidates:
            passed, reason = self.prefilter.quick_check(ticker)
            if passed:
                filtered_candidates.append(ticker)
            else:
                print(f"   ⏭️  Skipped {ticker}: {reason}")

        if not filtered_candidates:
            print("❌ No candidates passed pre-filtering")
            return []

        print(f"✅ {len(filtered_candidates)} candidates passed pre-filtering")
        print(f"\n📊 Deep analysis using parallel processing...")
        print(f"   (Using {len(filtered_candidates)} workers for faster analysis)")

        # Parallel analysis
        results = parallel_analyze(
            filtered_candidates,
            lambda ticker: self.analyze_ticker(ticker, period="3mo"),
            max_workers=min(5, len(filtered_candidates))
        )

        # Filter by score and remove None values
        results = [r for r in results if r is not None and r.score >= 60]

        print(f"\n✅ Found {len(results)} high-quality squeeze setups")

        # Print prefilter statistics
        self.prefilter.print_statistics()

        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def _get_candidates(self, params: ScanParameters, max_candidates: int) -> List[str]:
        """Get candidate tickers"""
        from ..data.providers import TradingViewProvider, MicroCapProvider

        candidates = set()

        try:
            tv = TradingViewProvider()
            tv_results = tv.scan(params)
            candidates.update([r.ticker for r in tv_results[:max_candidates // 2]])
            print(f"   Found {len(candidates)} candidates from TradingView")
        except Exception as e:
            print(f"   ⚠️  TradingView unavailable: {e}")

        try:
            microcap = MicroCapProvider()
            mc_results = microcap.scan(params, exclude_tickers=candidates)
            candidates.update([r.ticker for r in mc_results[:max_candidates // 2]])
            print(f"   Found {len(candidates)} total candidates")
        except Exception as e:
            print(f"   ⚠️  MicroCap scan unavailable: {e}")

        return list(candidates)[:max_candidates]


def create_enhanced_pressure_cooker_scanner() -> EnhancedPressureCookerScanner:
    """Factory function"""
    return EnhancedPressureCookerScanner()
