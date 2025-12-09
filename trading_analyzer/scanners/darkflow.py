"""
Enhanced Dark Flow Scanner
Detects institutional accumulation patterns through volume profile analysis
"""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..core.scanner import Scanner, ScanResult, ScanParameters
from ..config import DARK_FLOW, RATE_LIMIT
from ..data.cache import get_cache_manager
from ..utils import (
    parallel_analyze,
    DataValidator,
    TechnicalAnalyzer
)


class DarkFlowScanner(Scanner):
    """
    Enhanced Dark Flow Scanner with market scanning capability

    Detects:
    - Volume clusters (institutional accumulation levels)
    - Unusual volume activity (smart money entry)
    - Price consolidation near institutional levels
    - Gap patterns being filled by institutions
    """

    def __init__(self):
        super().__init__("Dark Flow")
        self.cache = get_cache_manager()
        self.major_etfs = ['SPY', 'QQQ', 'IWM', 'DIA']

        # Initialize utility modules
        self.validator = DataValidator()
        self.technical_analyzer = TechnicalAnalyzer()

    def scan(self, params: ScanParameters, ticker_list: List[str] = None) -> List[ScanResult]:
        """
        Scan for Dark Flow signals

        If ticker_list provided: Analyze specific tickers
        Otherwise: Scan entire market using TradingView
        """
        if ticker_list:
            return self._scan_specific_tickers(ticker_list)
        else:
            return self._scan_market(params)

    def _scan_market(self, params: ScanParameters) -> List[ScanResult]:
        """Scan entire market for Dark Flow signals"""
        try:
            from tradingview_screener import Query, col

            print(f"   🌊 Scanning market for Dark Flow signals...")
            print(f"      Filters: ${params.min_price:.2f}-${params.max_price:.2f}, 1M+ avg volume")

            # Build query
            q = Query()

            if params.market_choice == '4':
                q = q.set_markets('america').where(col('exchange') == 'NASDAQ')
            elif params.market_choice == '5':
                q = q.set_markets('america').where(col('exchange') == 'NYSE')
            else:
                q = q.set_markets('america')

            # Apply filters
            q = q.where(col('close').between(params.min_price, params.max_price))
            q = q.where(col('volume') >= 1_000_000)
            q = q.where(col('change').between(-5, 15))  # Not too extended

            # Select fields
            q = q.select(
                'name', 'close', 'volume', 'change', 'change_from_open',
                'Perf.W', 'Perf.1M', 'relative_volume_10d_calc',
                'average_volume_10d_calc', 'high', 'low', 'open'
            ).order_by('volume', ascending=False).limit(100)

            # Execute
            count, df = q.get_scanner_data()

            if df is None or df.empty:
                print("      ⚠️  No stocks found matching criteria")
                return []

            print(f"      Analyzing {len(df)} candidates for Dark Flow signals...")

            results = []

            for _, row in df.iterrows():
                try:
                    ticker = row['name']

                    # Quick pre-filter
                    rel_vol = float(row.get('relative_volume_10d_calc') or 0)
                    if rel_vol < 1.5:  # Need at least 1.5x volume
                        continue

                    # Analyze for Dark Flow signals
                    analysis = self.analyze_institutional_levels(ticker, period="5d")

                    if not analysis:
                        continue

                    # Score the Dark Flow signals
                    score = self._calculate_dark_flow_score(analysis, row)

                    if score >= 50:  # Minimum score threshold
                        # Convert to ScanResult
                        result = ScanResult(
                            ticker=ticker,
                            price=analysis['current_price'],
                            score=min(5, int(score / 20)),  # Convert 0-100 to 0-5
                            rel_vol=rel_vol,
                            float_m=0,
                            change_pct=float(row.get('change') or 0),
                            catalyst=f"{analysis['bias']} | {len(analysis['signals'])} signals",
                            description=f"Score: {int(score)}/100 | {len(analysis['key_levels'])} levels",
                            source="DARK_FLOW",
                            exchange="Multiple",
                            volume=int(row.get('volume', 0)),
                            market_cap=0
                        )
                        # Store full analysis in description for later use
                        result.dark_flow_analysis = analysis
                        result.dark_flow_score = score
                        results.append(result)

                except Exception:
                    continue

            # Sort by Dark Flow score
            results.sort(key=lambda x: x.dark_flow_score, reverse=True)

            print(f"      ✅ Found {len(results)} stocks with Dark Flow signals")
            return results

        except ImportError:
            print("      ❌ TradingView screener not available")
            print("      💡 Install with: pip install tradingview-screener")
            return []
        except Exception as e:
            print(f"      ❌ Dark Flow scan error: {e}")
            return []

    def _scan_specific_tickers(self, ticker_list: List[str]) -> List[ScanResult]:
        """Analyze specific tickers for Dark Flow"""
        print(f"      Analyzing {len(ticker_list)} tickers for Dark Flow...")

        results = []

        for ticker in ticker_list:
            try:
                analysis = self.analyze_institutional_levels(ticker, period="5d")

                if not analysis:
                    continue

                # Calculate score
                score = self._calculate_dark_flow_score(analysis, None)

                if score >= 50:
                    result = ScanResult(
                        ticker=ticker,
                        price=analysis['current_price'],
                        score=min(5, int(score / 20)),
                        rel_vol=0,
                        float_m=0,
                        change_pct=0,
                        catalyst=f"{analysis['bias']} | {len(analysis['signals'])} signals",
                        description=f"Score: {int(score)}/100 | {len(analysis['key_levels'])} levels",
                        source="DARK_FLOW",
                        exchange="Multiple",
                        volume=0,
                        market_cap=0
                    )
                    result.dark_flow_analysis = analysis
                    result.dark_flow_score = score
                    results.append(result)

            except Exception:
                continue

        results.sort(key=lambda x: x.dark_flow_score, reverse=True)
        print(f"      ✅ Found {len(results)} Dark Flow signals")

        return results

    def analyze_institutional_levels(self, ticker: str, period: str = "5d") -> Optional[Dict]:
        """Analyze volume profile to detect institutional activity levels"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval="1h", prepost=True)

            if df.empty or len(df) < 10:
                return None

            current_price = df['Close'].iloc[-1]
            today_open = df['Open'].iloc[-5] if len(df) >= 5 else df['Open'].iloc[0]
            today_high = df['High'].tail(24).max() if len(df) >= 24 else df['High'].max()
            today_low = df['Low'].tail(24).min() if len(df) >= 24 else df['Low'].min()

            # Create volume profile
            volume_profile = self._create_volume_profile(df)
            key_levels = self._find_key_levels(volume_profile, current_price)

            # Detect signals
            signals = []
            for level in key_levels[:3]:
                if abs(current_price - level) / current_price < 0.005:
                    signals.append({
                        'type': 'VOLUME_CLUSTER',
                        'level': level,
                        'distance': ((level - current_price) / current_price) * 100
                    })

            unusual_volume = self._detect_unusual_volume(df)
            gaps = self._detect_gaps(df)

            bias = "BULLISH" if current_price > today_open else "BEARISH"
            bias_emoji = "🟢" if bias == "BULLISH" else "🔴"

            return {
                'ticker': ticker,
                'current_price': current_price,
                'today_open': today_open,
                'today_high': today_high,
                'today_low': today_low,
                'bias': bias,
                'bias_emoji': bias_emoji,
                'key_levels': key_levels[:5],
                'signals': signals,
                'unusual_volume': unusual_volume,
                'gaps': gaps,
                'is_major_etf': ticker in self.major_etfs
            }
        except Exception:
            return None

    def _calculate_dark_flow_score(self, analysis: Dict, row: pd.Series = None) -> float:
        """
        Calculate Dark Flow signal strength score (0-100)

        Scoring:
        - Active volume clusters (near current price): +30 points
        - Unusual volume events: +20 points
        - Bullish bias with consolidation: +20 points
        - Key levels (squeeze setup): +15 points
        - Gap filling patterns: +15 points
        """
        score = 0.0

        current_price = analysis['current_price']

        # 1. Active volume clusters (institutions active at current level)
        active_clusters = [s for s in analysis['signals'] if s['type'] == 'VOLUME_CLUSTER']
        if active_clusters:
            score += 30
        elif analysis['key_levels']:
            # Check if any key level is within 2%
            closest_level = min(analysis['key_levels'],
                              key=lambda x: abs(x - current_price))
            distance_pct = abs(closest_level - current_price) / current_price
            if distance_pct < 0.02:
                score += 20

        # 2. Unusual volume (smart money entry)
        unusual_vol_count = len(analysis['unusual_volume'])
        if unusual_vol_count >= 3:
            score += 20
        elif unusual_vol_count >= 1:
            score += 10

        # 3. Bullish bias with tight range (coiling for breakout)
        if analysis['bias'] == 'BULLISH':
            today_range = analysis['today_high'] - analysis['today_low']
            range_pct = today_range / current_price

            if range_pct < 0.03:  # Tight 3% range = consolidation
                score += 20
            elif range_pct < 0.05:  # Moderate 5% range
                score += 10

        # 4. Key institutional levels creating squeeze setup
        if len(analysis['key_levels']) >= 3:
            levels_above = [l for l in analysis['key_levels'] if l > current_price]
            levels_below = [l for l in analysis['key_levels'] if l < current_price]

            if levels_above and levels_below:
                nearest_resistance = min(levels_above)
                nearest_support = max(levels_below)
                squeeze_range = nearest_resistance - nearest_support
                squeeze_pct = squeeze_range / current_price

                if squeeze_pct < 0.05:  # Tight 5% squeeze
                    score += 15
                elif squeeze_pct < 0.10:  # Moderate 10% squeeze
                    score += 8

        # 5. Gap filling patterns (institutions accumulating)
        if analysis['gaps']:
            recent_gap = analysis['gaps'][-1]
            gap_direction = recent_gap['direction']

            if gap_direction == 'DOWN' and analysis['bias'] == 'BULLISH':
                score += 15
            elif gap_direction == 'UP' and analysis['bias'] == 'BULLISH':
                score += 8

        return min(score, 100)

    def _create_volume_profile(self, df: pd.DataFrame, bins: int = 20) -> pd.DataFrame:
        """Create volume profile"""
        price_range = df['Close'].max() - df['Close'].min()
        if price_range == 0:
            return pd.DataFrame()

        bin_size = price_range / bins
        df['price_bin'] = ((df['Close'] - df['Close'].min()) / bin_size).astype(int)

        volume_profile = df.groupby('price_bin').agg({
            'Volume': 'sum',
            'Close': 'mean'
        }).reset_index()

        volume_profile.columns = ['bin', 'volume', 'price']
        volume_profile = volume_profile.sort_values('volume', ascending=False)

        return volume_profile

    def _find_key_levels(self, volume_profile: pd.DataFrame, current_price: float) -> List[float]:
        """Find key price levels where institutions accumulated"""
        if volume_profile.empty:
            return []
        top_levels = volume_profile.head(10)['price'].tolist()
        top_levels.sort(key=lambda x: abs(x - current_price))
        return top_levels

    def _detect_unusual_volume(self, df: pd.DataFrame) -> List[Dict]:
        """Detect unusual volume spikes (smart money entry)"""
        avg_volume = df['Volume'].mean()
        std_volume = df['Volume'].std()

        unusual = []
        for idx, row in df.iterrows():
            if row['Volume'] > avg_volume + (2 * std_volume):
                unusual.append({
                    'time': idx,
                    'price': row['Close'],
                    'volume': row['Volume'],
                    'ratio': row['Volume'] / avg_volume
                })

        return unusual[-5:] if len(unusual) > 5 else unusual

    def _detect_gaps(self, df: pd.DataFrame) -> List[Dict]:
        """Detect price gaps (institutional activity)"""
        gaps = []
        for i in range(1, len(df)):
            prev_close = df['Close'].iloc[i-1]
            curr_open = df['Open'].iloc[i]
            gap_pct = abs(curr_open - prev_close) / prev_close

            if gap_pct > 0.01:
                gaps.append({
                    'time': df.index[i],
                    'gap_from': prev_close,
                    'gap_to': curr_open,
                    'gap_pct': gap_pct * 100,
                    'direction': 'UP' if curr_open > prev_close else 'DOWN'
                })

        return gaps


def create_darkflow_scanner() -> DarkFlowScanner:
    """Factory function to create DarkFlowScanner"""
    return DarkFlowScanner()
