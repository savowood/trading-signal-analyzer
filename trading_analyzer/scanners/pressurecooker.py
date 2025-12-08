"""
Pressure Cooker Scanner
Short Squeeze Setup Detection System

Identifies stocks with explosive potential based on:
- High short interest (trapped shorts)
- Low float (easy to move price)
- Volume surge (ignition/catalyst)
- Price range ($5-$20 sweet spot)
- Recent momentum

Author: Michael Johnson
License: GPL v3
"""
import yfinance as yf
import pandas as pd
from typing import List, Optional, Dict
from dataclasses import dataclass, field
import warnings
warnings.filterwarnings('ignore')

from ..core.scanner import Scanner, ScanResult, ScanParameters


@dataclass
class PressureCookerResult(ScanResult):
    """Extended result with Pressure Cooker specific fields"""
    short_percent: float = 0
    days_to_cover: float = 0
    has_reverse_split: bool = False
    consecutive_volume_days: int = 0
    breaking_20d_high: bool = False
    setup_quality: str = ""
    grade: str = ""
    avg_volume_20d: int = 0


class PressureCookerScanner(Scanner):
    """
    Detects short squeeze setups - high short interest + low float + volume surge

    Scoring System (0-100):
    - Float: 25 points (lower = better)
    - Short Interest: 25 points (higher = better)
    - Relative Volume: 25 points (higher = better)
    - Price Range: 10 points ($5-$20 sweet spot)
    - Momentum: 10 points (breaking highs)
    - Bonuses: 15 points (days to cover, catalyst, consecutive volume)

    Risk Level: EXTREME - Only for experienced traders
    """

    def __init__(self):
        super().__init__("Pressure Cooker")
        self.min_float = 100_000      # Minimum float (avoid too illiquid)
        self.max_float = 5_000_000    # Maximum float for squeeze potential
        self.min_price = 5.0
        self.max_price = 20.0
        self.min_rel_vol = 3.0        # 3x average volume minimum
        self.min_short_interest = 15  # 15% minimum short interest (reduced from 20 due to data availability)
        self.min_volume = 500_000     # Minimum daily volume for liquidity

    def scan(self, params: ScanParameters) -> List[ScanResult]:
        """
        Scan for Pressure Cooker setups

        Note: This performs individual ticker analysis.
        Use scan_market() for full market screening.

        Args:
            params: Scan parameters (market choice, price range, etc.)

        Returns:
            List of qualifying short squeeze setups
        """
        # For now, return empty - use scan_market() for actual scanning
        # This is because Pressure Cooker requires deep analysis of each ticker
        print("💡 Pressure Cooker requires market-wide scanning.")
        print("   Use the 'Scan Market' option from the menu.")
        return []

    def analyze_ticker(self, ticker: str, period: str = "6mo") -> Optional[PressureCookerResult]:
        """
        Analyze a single ticker for Pressure Cooker setup

        Args:
            ticker: Stock symbol
            period: Historical data period

        Returns:
            PressureCookerResult or None if analysis fails
        """
        try:
            stock = yf.Ticker(ticker)

            # Get historical data
            hist = stock.history(period=period)
            if hist.empty or len(hist) < 20:
                return None

            # Get stock info
            info = stock.info

            # Extract key metrics
            current_price = hist['Close'].iloc[-1]

            # Price filter first (quick rejection)
            if not (self.min_price <= current_price <= self.max_price):
                return None

            # Volume analysis
            current_volume = hist['Volume'].iloc[-1]
            avg_volume_20d = hist['Volume'].tail(20).mean()
            rel_vol = current_volume / avg_volume_20d if avg_volume_20d > 0 else 0

            # Volume filter (quick rejection)
            if current_volume < self.min_volume or rel_vol < self.min_rel_vol:
                return None

            # Get float (shares outstanding - insider holdings)
            shares_outstanding = info.get('sharesOutstanding', 0)
            float_shares = info.get('floatShares', shares_outstanding)
            float_m = float_shares / 1_000_000 if float_shares > 0 else 999

            # Float filter (quick rejection)
            if float_shares < self.min_float or float_shares > self.max_float:
                return None

            # Short interest (often unavailable, but critical)
            short_ratio = info.get('shortRatio', 0)  # Days to cover
            short_percent = info.get('shortPercentOfFloat', 0)

            # Price analysis
            high_20d = hist['High'].tail(20).max()
            breaking_high = current_price >= high_20d * 0.98  # Within 2% of 20-day high

            # Volume pattern (consecutive high volume days)
            consecutive_high_vol = self._check_consecutive_volume(hist)

            # Reverse split detection
            has_reverse_split = self._detect_reverse_split(hist)

            # News check (basic - if volume spike, assume catalyst)
            has_catalyst = rel_vol > 3.0  # Proxy for news/catalyst

            # Calculate score
            score = self._calculate_score(
                float_shares=float_shares,
                short_percent=short_percent,
                short_ratio=short_ratio,
                rel_vol=rel_vol,
                current_price=current_price,
                breaking_high=breaking_high,
                consecutive_vol=consecutive_high_vol,
                has_reverse_split=has_reverse_split,
                has_catalyst=has_catalyst
            )

            # Get grade and quality
            grade = self._get_grade(score)
            setup_quality = self._get_setup_quality(score)

            # Calculate change percentage (current vs previous close)
            change_pct = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100

            # Build result
            result = PressureCookerResult(
                ticker=ticker,
                price=current_price,
                score=score,
                rel_vol=rel_vol,
                float_m=float_m,
                change_pct=change_pct,
                catalyst=f"{setup_quality} | {consecutive_high_vol} vol days",
                description=info.get('industry', 'N/A')[:50],
                source="PRESSURE_COOKER",
                exchange=info.get('exchange', 'US'),
                volume=int(current_volume),
                market_cap=info.get('marketCap', 0),
                # Pressure Cooker specific fields
                short_percent=short_percent,
                days_to_cover=short_ratio,
                has_reverse_split=has_reverse_split,
                consecutive_volume_days=consecutive_high_vol,
                breaking_20d_high=breaking_high,
                setup_quality=setup_quality,
                grade=grade,
                avg_volume_20d=int(avg_volume_20d)
            )

            return result

        except Exception as e:
            return None

    def _check_consecutive_volume(self, hist: pd.DataFrame, days: int = 3) -> int:
        """Check for consecutive high-volume days"""
        if len(hist) < days:
            return 0

        recent_volume = hist['Volume'].tail(days)
        avg_volume = hist['Volume'].tail(20).mean()

        consecutive_count = 0
        for vol in reversed(list(recent_volume)):
            if vol > avg_volume * 2:  # 2x average
                consecutive_count += 1
            else:
                break

        return consecutive_count

    def _detect_reverse_split(self, hist: pd.DataFrame) -> bool:
        """
        Detect potential reverse split by looking for sudden price jumps
        with corresponding volume drops
        """
        if len(hist) < 40:
            return False

        # Look for >5x price increase in single day with volume drop
        price_changes = hist['Close'].pct_change()
        volume_changes = hist['Volume'].pct_change()

        # Reverse split signature: big price jump + volume drop
        for i in range(len(hist) - 30, len(hist)):
            if price_changes.iloc[i] > 4.0 and volume_changes.iloc[i] < -0.5:
                return True

        return False

    def _calculate_score(self, float_shares: float, short_percent: float,
                        short_ratio: float, rel_vol: float, current_price: float,
                        breaking_high: bool, consecutive_vol: int,
                        has_reverse_split: bool, has_catalyst: bool) -> int:
        """
        Calculate Pressure Cooker score (0-100)

        Scoring breakdown:
        - Float: 25 points max (lower is better)
        - Short interest: 25 points max (higher is better)
        - Relative volume: 25 points max (higher is better)
        - Price range: 10 points max ($5-$20 sweet spot)
        - Momentum: 10 points max (breaking highs)
        - Bonuses: 15 points max (days to cover, catalyst, consecutive vol)
        """
        score = 0

        # Float scoring (25 points max)
        if float_shares < 1_000_000:
            score += 25
        elif float_shares < 2_000_000:
            score += 20
        elif float_shares < 5_000_000:
            score += 15
        elif float_shares < 10_000_000:
            score += 10
        else:
            score += 5

        # Short interest scoring (25 points max)
        if short_percent > 40:
            score += 25
        elif short_percent > 30:
            score += 20
        elif short_percent > 20:
            score += 15
        elif short_percent > 10:
            score += 10
        else:
            score += 5

        # Relative volume scoring (25 points max)
        if rel_vol > 10:
            score += 25
        elif rel_vol > 7:
            score += 20
        elif rel_vol > 5:
            score += 15
        elif rel_vol > 3:
            score += 10
        else:
            score += 5

        # Price range scoring (10 points max)
        if self.min_price <= current_price <= self.max_price:
            score += 10
        elif current_price < self.min_price:
            score += 5  # Too cheap, higher risk
        else:
            score += 3  # Too expensive, less volatile

        # Breaking 20-day high (10 points max)
        if breaking_high:
            score += 10

        # Bonus points (15 points possible)
        if short_ratio > 5:  # Days to cover > 5
            score += 10
        elif short_ratio > 3:
            score += 5

        if has_catalyst:
            score += 5

        if consecutive_vol >= 2:
            score += 5

        return min(score, 100)  # Cap at 100

    def _get_grade(self, score: int) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _get_setup_quality(self, score: int) -> str:
        """Describe setup quality"""
        if score >= 90:
            return "EXCELLENT"
        elif score >= 80:
            return "STRONG"
        elif score >= 70:
            return "GOOD"
        elif score >= 60:
            return "MARGINAL"
        else:
            return "WEAK"

    def scan_market(self, params: ScanParameters, max_candidates: int = 100) -> List[PressureCookerResult]:
        """
        Scan market for Pressure Cooker setups

        This is the main entry point for market-wide screening.
        Uses TradingView or micro-cap list to find candidates, then analyzes each.

        Args:
            params: Scan parameters
            max_candidates: Maximum candidates to analyze

        Returns:
            List of qualifying setups sorted by score
        """
        print(f"\n🔥 PRESSURE COOKER: Scanning for short squeeze setups...")
        print(f"   Criteria: ${self.min_price}-${self.max_price}, <{self.max_float/1e6:.0f}M float, {self.min_rel_vol}x+ volume")

        # Get candidates from existing data providers
        candidates = self._get_candidates(params, max_candidates)

        if not candidates:
            print("❌ No candidates found")
            return []

        print(f"\n📊 Analyzing {len(candidates)} candidates...")

        results = []
        for idx, ticker in enumerate(candidates, 1):
            print(f"   [{idx}/{len(candidates)}] {ticker}...", end='\r')

            analysis = self.analyze_ticker(ticker, period="3mo")

            if analysis and analysis.score >= 60:  # Minimum threshold
                results.append(analysis)

        print(f"\n✅ Found {len(results)} Pressure Cooker setups")

        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)

        return results

    def _get_candidates(self, params: ScanParameters, max_candidates: int) -> List[str]:
        """
        Get list of candidate tickers to screen

        Uses existing data providers (TradingView or micro-cap list)
        """
        from ..data.providers import TradingViewProvider, MicroCapProvider

        candidates = set()

        # Try TradingView first
        try:
            tv = TradingViewProvider()
            tv_results = tv.scan(params)
            candidates.update([r.ticker for r in tv_results[:max_candidates // 2]])
            print(f"   Found {len(candidates)} candidates from TradingView")
        except Exception as e:
            print(f"   ⚠️  TradingView unavailable: {e}")

        # Add micro-caps (uses priority mode automatically for smart scan)
        try:
            microcap = MicroCapProvider()
            mc_results = microcap.scan(params, exclude_tickers=candidates)
            candidates.update([r.ticker for r in mc_results[:max_candidates // 2]])
            print(f"   Found {len(candidates)} total candidates")
        except Exception as e:
            print(f"   ⚠️  MicroCap scan unavailable: {e}")

        return list(candidates)[:max_candidates]


def create_pressure_cooker_scanner() -> PressureCookerScanner:
    """Factory function to create Pressure Cooker scanner"""
    return PressureCookerScanner()
