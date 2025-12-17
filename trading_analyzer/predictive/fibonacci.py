"""
Fibonacci Projection and Retracement Analysis
Predictive price targets based on Fibonacci ratios
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FibonacciLevels:
    """Fibonacci analysis results"""
    ticker: str
    current_price: float

    # Swing points used for calculation
    swing_high: float
    swing_high_date: str
    swing_low: float
    swing_low_date: str
    trend_direction: str  # "Uptrend" or "Downtrend"

    # Retracement levels (for pullbacks in trend)
    retracements: Dict[str, float]  # {level_name: price}
    current_retracement: Optional[str]  # Which level we're at

    # Extension/Projection levels (price targets)
    extensions: Dict[str, float]  # {level_name: price}
    next_target: Optional[str]  # Next likely target

    # Analysis
    nearest_support: float
    nearest_resistance: float
    prediction: str  # Summary prediction
    confidence: str  # High/Medium/Low

    # Time estimation (PREDICTIVE)
    momentum_per_day: Optional[float] = None  # Average $/day movement
    estimated_days_to_target: Optional[int] = None  # Days to next target
    target_date_range: Optional[str] = None  # Estimated date range


class FibonacciAnalyzer:
    """Calculate Fibonacci retracements and projections"""

    # Standard Fibonacci ratios
    RETRACEMENT_LEVELS = {
        '23.6%': 0.236,
        '38.2%': 0.382,
        '50.0%': 0.500,
        '61.8%': 0.618,
        '78.6%': 0.786
    }

    EXTENSION_LEVELS = {
        '100%': 1.000,
        '127.2%': 1.272,
        '161.8%': 1.618,
        '200%': 2.000,
        '261.8%': 2.618
    }

    def __init__(self, ticker: str, data: pd.DataFrame, current_price: Optional[float] = None):
        """
        Initialize Fibonacci analyzer

        Args:
            ticker: Stock symbol
            data: OHLCV DataFrame with historical price data
            current_price: Optional real-time price (includes pre/post market)
        """
        self.ticker = ticker
        self.data = data
        self.real_time_price = current_price

    def analyze(self) -> Optional[FibonacciLevels]:
        """
        Perform complete Fibonacci analysis

        Returns:
            FibonacciLevels object or None if insufficient data
        """
        if self.data is None or len(self.data) < 20:
            return None

        try:
            # Find significant swing points
            swing_high, swing_high_date, swing_low, swing_low_date = self._find_swing_points()

            if swing_high is None or swing_low is None:
                return None

            # Use real-time price if provided, otherwise last close
            current_price = self.real_time_price if self.real_time_price else float(self.data['Close'].iloc[-1])
            trend_direction = self._determine_trend(swing_high, swing_low, swing_high_date, swing_low_date)

            # Calculate Fibonacci levels
            retracements = self._calculate_retracements(swing_high, swing_low, trend_direction)
            extensions = self._calculate_extensions(swing_high, swing_low, trend_direction)

            # Determine current position
            current_retracement = self._find_current_level(current_price, retracements)
            next_target = self._find_next_target(current_price, extensions, trend_direction)

            # Find nearest support/resistance
            nearest_support = self._find_nearest_support(current_price, retracements, extensions)
            nearest_resistance = self._find_nearest_resistance(current_price, retracements, extensions)

            # Generate prediction
            prediction, confidence = self._generate_prediction(
                current_price, trend_direction, next_target,
                nearest_support, nearest_resistance, retracements, extensions
            )

            # Calculate time to target
            momentum, days_to_target, date_range = self._calculate_time_to_target(
                current_price, next_target, extensions, trend_direction
            )

            return FibonacciLevels(
                ticker=self.ticker,
                current_price=current_price,
                swing_high=swing_high,
                swing_high_date=swing_high_date,
                swing_low=swing_low,
                swing_low_date=swing_low_date,
                trend_direction=trend_direction,
                retracements=retracements,
                current_retracement=current_retracement,
                extensions=extensions,
                next_target=next_target,
                nearest_support=nearest_support,
                nearest_resistance=nearest_resistance,
                prediction=prediction,
                confidence=confidence,
                momentum_per_day=momentum,
                estimated_days_to_target=days_to_target,
                target_date_range=date_range
            )

        except Exception as e:
            print(f"❌ Fibonacci analysis failed for {self.ticker}: {e}")
            return None

    def _find_swing_points(self) -> Tuple[Optional[float], Optional[str], Optional[float], Optional[str]]:
        """
        Find significant swing high and swing low

        Returns:
            (swing_high, swing_high_date, swing_low, swing_low_date)
        """
        # Use the entire dataset to find swing points
        high_idx = self.data['High'].idxmax()
        low_idx = self.data['Low'].idxmin()

        swing_high = float(self.data.loc[high_idx, 'High'])
        swing_high_date = high_idx.strftime('%Y-%m-%d') if hasattr(high_idx, 'strftime') else str(high_idx)

        swing_low = float(self.data.loc[low_idx, 'Low'])
        swing_low_date = low_idx.strftime('%Y-%m-%d') if hasattr(low_idx, 'strftime') else str(low_idx)

        return swing_high, swing_high_date, swing_low, swing_low_date

    def _determine_trend(self, swing_high: float, swing_low: float,
                        swing_high_date: str, swing_low_date: str) -> str:
        """
        Determine if we're in an uptrend or downtrend

        Based on which swing point is more recent
        """
        # Compare dates to see which came first
        try:
            high_ts = pd.Timestamp(swing_high_date)
            low_ts = pd.Timestamp(swing_low_date)

            if low_ts > high_ts:
                # Low is more recent = uptrend from the low
                return "Uptrend"
            else:
                # High is more recent = downtrend from the high
                return "Downtrend"
        except:
            # Default to comparing prices
            current_price = float(self.data['Close'].iloc[-1])
            mid_point = (swing_high + swing_low) / 2

            return "Uptrend" if current_price > mid_point else "Downtrend"

    def _calculate_retracements(self, swing_high: float, swing_low: float,
                               trend_direction: str) -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels

        Retracements show potential support/resistance during pullbacks
        """
        retracements = {}
        price_range = swing_high - swing_low

        for level_name, ratio in self.RETRACEMENT_LEVELS.items():
            if trend_direction == "Uptrend":
                # In uptrend, retracements are below current price
                retracements[level_name] = swing_high - (price_range * ratio)
            else:
                # In downtrend, retracements are above current price
                retracements[level_name] = swing_low + (price_range * ratio)

        return retracements

    def _calculate_extensions(self, swing_high: float, swing_low: float,
                             trend_direction: str) -> Dict[str, float]:
        """
        Calculate Fibonacci extension levels (price targets)

        Extensions project where price might go beyond the current range
        """
        extensions = {}
        price_range = swing_high - swing_low

        for level_name, ratio in self.EXTENSION_LEVELS.items():
            if trend_direction == "Uptrend":
                # In uptrend, extensions are above swing high
                extensions[level_name] = swing_low + (price_range * ratio)
            else:
                # In downtrend, extensions are below swing low
                extensions[level_name] = swing_high - (price_range * ratio)

        return extensions

    def _find_current_level(self, current_price: float,
                           retracements: Dict[str, float]) -> Optional[str]:
        """Find which retracement level we're currently near"""
        tolerance = 0.02  # 2% tolerance

        for level_name, price in retracements.items():
            if abs(current_price - price) / price < tolerance:
                return level_name

        return None

    def _find_next_target(self, current_price: float, extensions: Dict[str, float],
                         trend_direction: str) -> Optional[str]:
        """Find the next Fibonacci extension target"""
        if trend_direction == "Uptrend":
            # Find next level above current price
            next_levels = [(name, price) for name, price in extensions.items()
                          if price > current_price]
            if next_levels:
                next_levels.sort(key=lambda x: x[1])  # Sort by price
                return next_levels[0][0]
        else:
            # Find next level below current price
            next_levels = [(name, price) for name, price in extensions.items()
                          if price < current_price]
            if next_levels:
                next_levels.sort(key=lambda x: x[1], reverse=True)  # Sort by price descending
                return next_levels[0][0]

        return None

    def _find_nearest_support(self, current_price: float,
                             retracements: Dict[str, float],
                             extensions: Dict[str, float]) -> float:
        """Find nearest support level below current price"""
        all_levels = list(retracements.values()) + list(extensions.values())
        support_levels = [level for level in all_levels if level < current_price]

        if support_levels:
            return max(support_levels)
        else:
            return min(all_levels)

    def _find_nearest_resistance(self, current_price: float,
                                 retracements: Dict[str, float],
                                 extensions: Dict[str, float]) -> float:
        """Find nearest resistance level above current price"""
        all_levels = list(retracements.values()) + list(extensions.values())
        resistance_levels = [level for level in all_levels if level > current_price]

        if resistance_levels:
            return min(resistance_levels)
        else:
            return max(all_levels)

    def _calculate_time_to_target(self, current_price: float, next_target: Optional[str],
                                  extensions: Dict[str, float], trend_direction: str) -> Tuple[Optional[float], Optional[int], Optional[str]]:
        """
        Calculate estimated time to reach next Fibonacci target (PREDICTIVE)

        Returns:
            (momentum_per_day, estimated_days, date_range_string)
        """
        from datetime import datetime, timedelta

        if not next_target or len(self.data) < 10:
            return None, None, None

        try:
            # Calculate recent momentum (last 20 days or available data)
            lookback = min(20, len(self.data))
            recent_data = self.data.tail(lookback)

            # Daily price change
            price_changes = recent_data['Close'].diff().dropna()

            if len(price_changes) == 0:
                return None, None, None

            # Average momentum per day
            momentum_per_day = float(price_changes.mean())

            # Get target price
            target_price = extensions.get(next_target)
            if not target_price:
                return momentum_per_day, None, None

            # Calculate distance to target
            distance = abs(target_price - current_price)

            # Estimate days (with safety check for division by zero)
            if abs(momentum_per_day) < 0.01:
                return momentum_per_day, None, "Momentum too low to estimate"

            raw_days = int(distance / abs(momentum_per_day))

            # Add volatility buffer (50% more time in volatile markets)
            volatility = float(recent_data['Close'].std() / recent_data['Close'].mean())
            if volatility > 0.05:  # High volatility
                buffered_days = int(raw_days * 1.5)
            else:
                buffered_days = int(raw_days * 1.2)

            # Create date range estimate
            min_days = max(1, int(buffered_days * 0.7))
            max_days = int(buffered_days * 1.3)

            min_date = (datetime.now() + timedelta(days=min_days)).strftime('%Y-%m-%d')
            max_date = (datetime.now() + timedelta(days=max_days)).strftime('%Y-%m-%d')

            date_range = f"{min_date} to {max_date}"

            return momentum_per_day, buffered_days, date_range

        except Exception:
            return None, None, None

    def _generate_prediction(self, current_price: float, trend_direction: str,
                           next_target: Optional[str], nearest_support: float,
                           nearest_resistance: float, retracements: Dict[str, float],
                           extensions: Dict[str, float]) -> Tuple[str, str]:
        """
        Generate price prediction with confidence level

        Returns:
            (prediction_text, confidence_level)
        """
        # Calculate distance to support/resistance
        support_distance = abs(current_price - nearest_support) / current_price
        resistance_distance = abs(current_price - nearest_resistance) / current_price

        # Determine confidence based on proximity to key levels
        if support_distance < 0.02 or resistance_distance < 0.02:
            confidence = "High"
        elif support_distance < 0.05 or resistance_distance < 0.05:
            confidence = "Medium"
        else:
            confidence = "Low"

        # Generate prediction
        if trend_direction == "Uptrend":
            if next_target:
                target_price = extensions.get(next_target, nearest_resistance)
                prediction = f"Targeting ${target_price:.2f} ({next_target} extension)"
            else:
                prediction = f"Resistance at ${nearest_resistance:.2f}"
        else:
            if next_target:
                target_price = extensions.get(next_target, nearest_support)
                prediction = f"Targeting ${target_price:.2f} ({next_target} extension)"
            else:
                prediction = f"Support at ${nearest_support:.2f}"

        return prediction, confidence


def analyze_fibonacci(ticker: str, data: pd.DataFrame, current_price: Optional[float] = None) -> Optional[FibonacciLevels]:
    """
    Convenience function to analyze Fibonacci levels

    Args:
        ticker: Stock symbol
        data: OHLCV DataFrame
        current_price: Optional real-time price (includes pre/post market)

    Returns:
        FibonacciLevels object or None
    """
    analyzer = FibonacciAnalyzer(ticker, data, current_price)
    return analyzer.analyze()
