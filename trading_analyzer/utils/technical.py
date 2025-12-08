"""
Advanced Technical Analysis Utilities
Support/Resistance detection and Volume Profile
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SupportResistance:
    """Support and resistance level data"""
    resistance_levels: List[float]
    support_levels: List[float]
    nearest_resistance: Optional[float]
    nearest_support: Optional[float]
    distance_to_resistance_pct: Optional[float]
    distance_to_support_pct: Optional[float]
    in_squeeze: bool  # Between tight S/R levels
    squeeze_range_pct: Optional[float]


@dataclass
class VolumeProfile:
    """Volume profile data"""
    poc_price: float  # Point of Control (highest volume price)
    value_area_high: float  # Top of value area (70% volume)
    value_area_low: float  # Bottom of value area
    volume_distribution: np.ndarray
    price_bins: np.ndarray
    at_poc: bool  # Price near POC
    above_value_area: bool
    below_value_area: bool


class TechnicalAnalyzer:
    """Advanced technical analysis tools"""

    @staticmethod
    def find_support_resistance(hist: pd.DataFrame,
                               window: int = 5,
                               cluster_threshold: float = 0.02) -> SupportResistance:
        """
        Find support and resistance levels using pivot points

        Args:
            hist: Historical OHLCV data
            window: Lookback window for pivot detection
            cluster_threshold: Price similarity threshold for clustering (2% default)

        Returns:
            SupportResistance object with all levels
        """
        if len(hist) < window * 2:
            return SupportResistance([], [], None, None, None, None, False, None)

        highs = hist['High'].values
        lows = hist['Low'].values
        closes = hist['Close'].values
        current_price = closes[-1]

        resistance_levels = []
        support_levels = []

        # Find local maxima (resistance)
        for i in range(window, len(highs) - window):
            if highs[i] == max(highs[i-window:i+window+1]):
                resistance_levels.append(float(highs[i]))

        # Find local minima (support)
        for i in range(window, len(lows) - window):
            if lows[i] == min(lows[i-window:i+window+1]):
                support_levels.append(float(lows[i]))

        # Cluster nearby levels
        resistance_levels = TechnicalAnalyzer._cluster_levels(resistance_levels, cluster_threshold)
        support_levels = TechnicalAnalyzer._cluster_levels(support_levels, cluster_threshold)

        # Find nearest levels
        resistance_above = [r for r in resistance_levels if r > current_price]
        support_below = [s for s in support_levels if s < current_price]

        nearest_resistance = min(resistance_above) if resistance_above else None
        nearest_support = max(support_below) if support_below else None

        # Calculate distances
        dist_to_resistance = ((nearest_resistance - current_price) / current_price * 100) \
                            if nearest_resistance else None
        dist_to_support = ((current_price - nearest_support) / current_price * 100) \
                         if nearest_support else None

        # Check if in squeeze (tight S/R range)
        in_squeeze = False
        squeeze_range = None
        if nearest_resistance and nearest_support:
            squeeze_range = (nearest_resistance - nearest_support) / current_price * 100
            in_squeeze = squeeze_range < 5.0  # Within 5% range

        return SupportResistance(
            resistance_levels=sorted(resistance_levels, reverse=True),
            support_levels=sorted(support_levels, reverse=True),
            nearest_resistance=nearest_resistance,
            nearest_support=nearest_support,
            distance_to_resistance_pct=dist_to_resistance,
            distance_to_support_pct=dist_to_support,
            in_squeeze=in_squeeze,
            squeeze_range_pct=squeeze_range
        )

    @staticmethod
    def _cluster_levels(levels: List[float], threshold: float) -> List[float]:
        """
        Cluster nearby price levels together

        Args:
            levels: List of price levels
            threshold: Similarity threshold (e.g., 0.02 = 2%)

        Returns:
            List of clustered levels (averaged)
        """
        if not levels:
            return []

        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]

        for level in levels[1:]:
            # Check if level is within threshold of cluster average
            cluster_avg = sum(current_cluster) / len(current_cluster)

            if abs(level - cluster_avg) / cluster_avg <= threshold:
                current_cluster.append(level)
            else:
                # Finish current cluster, start new one
                clustered.append(sum(current_cluster) / len(current_cluster))
                current_cluster = [level]

        # Add last cluster
        if current_cluster:
            clustered.append(sum(current_cluster) / len(current_cluster))

        return clustered

    @staticmethod
    def calculate_volume_profile(hist: pd.DataFrame,
                                 num_bins: int = 20) -> VolumeProfile:
        """
        Calculate volume profile (volume distribution at price levels)

        Args:
            hist: Historical OHLCV data
            num_bins: Number of price bins for volume distribution

        Returns:
            VolumeProfile object with POC and value areas
        """
        if len(hist) < 10:
            return VolumeProfile(0, 0, 0, np.array([]), np.array([]),
                               False, False, False)

        price_min = hist['Low'].min()
        price_max = hist['High'].max()
        current_price = hist['Close'].iloc[-1]

        # Create price bins
        bins = np.linspace(price_min, price_max, num_bins + 1)
        volume_at_price = np.zeros(num_bins)

        # Distribute volume across price bins
        for idx, row in hist.iterrows():
            # Find which bins this candle touches
            low_bin = np.searchsorted(bins, row['Low'], side='left')
            high_bin = np.searchsorted(bins, row['High'], side='right')

            # Clamp to valid range
            low_bin = max(0, min(low_bin, num_bins - 1))
            high_bin = max(0, min(high_bin, num_bins))

            # Distribute volume evenly across touched bins
            bins_touched = high_bin - low_bin
            if bins_touched > 0:
                volume_per_bin = row['Volume'] / bins_touched
                for bin_idx in range(low_bin, high_bin):
                    if 0 <= bin_idx < num_bins:
                        volume_at_price[bin_idx] += volume_per_bin

        # Find Point of Control (POC) - highest volume price
        poc_idx = np.argmax(volume_at_price)
        poc_price = float((bins[poc_idx] + bins[poc_idx + 1]) / 2)

        # Find Value Area (70% of volume)
        total_volume = volume_at_price.sum()
        value_area_volume = total_volume * 0.70

        # Start from POC and expand until we have 70% volume
        value_area_indices = [poc_idx]
        accumulated_volume = volume_at_price[poc_idx]

        low_idx = poc_idx - 1
        high_idx = poc_idx + 1

        while accumulated_volume < value_area_volume:
            # Expand towards higher volume side
            low_vol = volume_at_price[low_idx] if low_idx >= 0 else 0
            high_vol = volume_at_price[high_idx] if high_idx < num_bins else 0

            if low_vol >= high_vol and low_idx >= 0:
                value_area_indices.append(low_idx)
                accumulated_volume += low_vol
                low_idx -= 1
            elif high_idx < num_bins:
                value_area_indices.append(high_idx)
                accumulated_volume += high_vol
                high_idx += 1
            else:
                break

        value_area_low = float(bins[min(value_area_indices)])
        value_area_high = float(bins[max(value_area_indices) + 1])

        # Determine price position relative to profile
        at_poc = abs(current_price - poc_price) / current_price < 0.02  # Within 2%
        above_value_area = current_price > value_area_high
        below_value_area = current_price < value_area_low

        return VolumeProfile(
            poc_price=poc_price,
            value_area_high=value_area_high,
            value_area_low=value_area_low,
            volume_distribution=volume_at_price,
            price_bins=bins,
            at_poc=at_poc,
            above_value_area=above_value_area,
            below_value_area=below_value_area
        )

    @staticmethod
    def score_technical_setup(sr: SupportResistance,
                             vp: VolumeProfile,
                             current_price: float,
                             rel_vol: float) -> Tuple[int, List[str]]:
        """
        Score technical setup based on S/R and Volume Profile

        Args:
            sr: Support/Resistance data
            vp: Volume Profile data
            current_price: Current price
            rel_vol: Relative volume

        Returns:
            (score: int, factors: List[str]) - Score 0-30 pts, key factors
        """
        score = 0
        factors = []

        # === Support/Resistance Scoring (15 pts max) ===

        # Breaking resistance with volume (best setup)
        if sr.nearest_resistance and sr.distance_to_resistance_pct:
            if sr.distance_to_resistance_pct < 2 and rel_vol > 3:
                score += 15
                factors.append("Breaking Resistance with Volume")
            elif sr.distance_to_resistance_pct < 5:
                score += 8
                factors.append("Approaching Resistance")

        # Bouncing off support
        if sr.nearest_support and sr.distance_to_support_pct:
            if sr.distance_to_support_pct < 2:
                score += 10
                factors.append("Bouncing Off Support")

        # In squeeze pattern
        if sr.in_squeeze and sr.squeeze_range_pct:
            score += 5
            factors.append(f"Squeeze Pattern ({sr.squeeze_range_pct:.1f}% range)")

        # === Volume Profile Scoring (15 pts max) ===

        # Price at POC (institutional accumulation zone)
        if vp.at_poc:
            score += 10
            factors.append("At Point of Control (POC)")

        # Breaking above value area
        if vp.above_value_area and rel_vol > 3:
            score += 15
            factors.append("Breaking Above Value Area")

        # Below value area (potential support)
        if vp.below_value_area:
            score += 5
            factors.append("Below Value Area (Support Zone)")

        return min(score, 30), factors


# Test function
if __name__ == "__main__":
    import yfinance as yf

    print("Testing technical analysis...")

    ticker = 'GME'
    stock = yf.Ticker(ticker)
    hist = stock.history(period='3mo')

    analyzer = TechnicalAnalyzer()

    # Support/Resistance
    sr = analyzer.find_support_resistance(hist)
    print(f"\n{ticker} Support/Resistance:")
    print(f"  Nearest Support: ${sr.nearest_support:.2f}")
    print(f"  Nearest Resistance: ${sr.nearest_resistance:.2f}")
    print(f"  In Squeeze: {sr.in_squeeze}")

    # Volume Profile
    vp = analyzer.calculate_volume_profile(hist)
    print(f"\n{ticker} Volume Profile:")
    print(f"  POC Price: ${vp.poc_price:.2f}")
    print(f"  Value Area: ${vp.value_area_low:.2f} - ${vp.value_area_high:.2f}")
    print(f"  At POC: {vp.at_poc}")

    # Score
    current_price = hist['Close'].iloc[-1]
    rel_vol = hist['Volume'].iloc[-1] / hist['Volume'].tail(20).mean()
    score, factors = analyzer.score_technical_setup(sr, vp, current_price, rel_vol)

    print(f"\nTechnical Score: {score}/30")
    for factor in factors:
        print(f"  • {factor}")
