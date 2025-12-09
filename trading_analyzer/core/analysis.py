"""
Technical Analysis Module
Indicators: VWAP, MACD, RSI, SuperTrend, EMA, Signal Scoring
"""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from ..config import TECHNICAL_SETTINGS


@dataclass
class TechnicalAnalysis:
    """Technical analysis results for a stock"""
    ticker: str
    current_price: float

    # VWAP
    vwap: float
    vwap_2std: Tuple[float, float]  # (lower, upper)
    vwap_3std: Tuple[float, float]  # (lower, upper)
    vwap_position: str  # Above/Below/At

    # MACD
    macd: float
    macd_signal: float
    macd_histogram: float
    macd_trend: str  # Bullish/Bearish/Neutral

    # RSI
    rsi: float
    rsi_signal: str  # Oversold/Overbought/Neutral

    # SuperTrend
    supertrend: float
    supertrend_signal: str  # Buy/Sell

    # EMAs
    ema9: float
    ema20: float
    ema_crossover: str  # Bullish/Bearish/Neutral

    # Overall
    signal_score: int  # 0-100
    signal_grade: str  # A-D
    recommendation: str  # Strong Buy/Buy/Hold/Sell/Strong Sell

    # Additional info
    volume: int
    avg_volume: int
    rel_volume: float


class TechnicalAnalyzer:
    """Technical analysis calculator"""

    def __init__(self, ticker: str, period: str = "1mo"):
        self.ticker = ticker
        self.period = period
        self.data: Optional[pd.DataFrame] = None

    def fetch_data(self) -> bool:
        """Fetch stock data"""
        try:
            stock = yf.Ticker(self.ticker)
            self.data = stock.history(period=self.period, prepost=True)

            if self.data.empty:
                return False

            return True

        except Exception as e:
            print(f"❌ Failed to fetch data for {self.ticker}: {e}")
            return False

    def analyze(self) -> Optional[TechnicalAnalysis]:
        """Perform complete technical analysis"""
        if self.data is None or self.data.empty:
            if not self.fetch_data():
                return None

        try:
            # Calculate all indicators
            vwap_data = self._calculate_vwap()
            macd_data = self._calculate_macd()
            rsi_data = self._calculate_rsi()
            supertrend_data = self._calculate_supertrend()
            ema_data = self._calculate_emas()

            # Get current values
            current_price = float(self.data['Close'].iloc[-1])
            volume = int(self.data['Volume'].iloc[-1])
            avg_volume = int(self.data['Volume'].mean())
            rel_volume = volume / avg_volume if avg_volume > 0 else 0

            # Calculate signal score
            score, grade, recommendation = self._calculate_signal_score(
                vwap_data, macd_data, rsi_data, supertrend_data, ema_data
            )

            # Build result
            analysis = TechnicalAnalysis(
                ticker=self.ticker,
                current_price=current_price,
                vwap=vwap_data['vwap'],
                vwap_2std=vwap_data['2std'],
                vwap_3std=vwap_data['3std'],
                vwap_position=vwap_data['position'],
                macd=macd_data['macd'],
                macd_signal=macd_data['signal'],
                macd_histogram=macd_data['histogram'],
                macd_trend=macd_data['trend'],
                rsi=rsi_data['rsi'],
                rsi_signal=rsi_data['signal'],
                supertrend=supertrend_data['value'],
                supertrend_signal=supertrend_data['signal'],
                ema9=ema_data['ema9'],
                ema20=ema_data['ema20'],
                ema_crossover=ema_data['crossover'],
                signal_score=score,
                signal_grade=grade,
                recommendation=recommendation,
                volume=volume,
                avg_volume=avg_volume,
                rel_volume=rel_volume
            )

            return analysis

        except Exception as e:
            print(f"❌ Analysis failed for {self.ticker}: {e}")
            return None

    def _calculate_vwap(self) -> Dict:
        """Calculate VWAP with 2σ and 3σ bands"""
        # VWAP = Cumulative (Price × Volume) / Cumulative Volume
        typical_price = (self.data['High'] + self.data['Low'] + self.data['Close']) / 3
        vwap = (typical_price * self.data['Volume']).cumsum() / self.data['Volume'].cumsum()

        # Standard deviation bands
        squared_diff = (typical_price - vwap) ** 2
        variance = (squared_diff * self.data['Volume']).cumsum() / self.data['Volume'].cumsum()
        std_dev = np.sqrt(variance)

        current_vwap = float(vwap.iloc[-1])
        current_std = float(std_dev.iloc[-1])
        current_price = float(self.data['Close'].iloc[-1])

        # 2σ and 3σ bands
        vwap_2std_lower = current_vwap - (2 * current_std)
        vwap_2std_upper = current_vwap + (2 * current_std)
        vwap_3std_lower = current_vwap - (3 * current_std)
        vwap_3std_upper = current_vwap + (3 * current_std)

        # Position
        if current_price > current_vwap:
            position = "Above VWAP"
        elif current_price < current_vwap:
            position = "Below VWAP"
        else:
            position = "At VWAP"

        return {
            'vwap': current_vwap,
            '2std': (vwap_2std_lower, vwap_2std_upper),
            '3std': (vwap_3std_lower, vwap_3std_upper),
            'position': position
        }

    def _calculate_macd(self) -> Dict:
        """Calculate MACD"""
        settings = TECHNICAL_SETTINGS['macd']

        # Calculate EMAs
        ema_fast = self.data['Close'].ewm(span=settings['fast'], adjust=False).mean()
        ema_slow = self.data['Close'].ewm(span=settings['slow'], adjust=False).mean()

        # MACD line
        macd_line = ema_fast - ema_slow

        # Signal line
        signal_line = macd_line.ewm(span=settings['signal'], adjust=False).mean()

        # Histogram
        histogram = macd_line - signal_line

        current_macd = float(macd_line.iloc[-1])
        current_signal = float(signal_line.iloc[-1])
        current_histogram = float(histogram.iloc[-1])

        # Trend
        if current_macd > current_signal and current_histogram > 0:
            trend = "Bullish"
        elif current_macd < current_signal and current_histogram < 0:
            trend = "Bearish"
        else:
            trend = "Neutral"

        return {
            'macd': current_macd,
            'signal': current_signal,
            'histogram': current_histogram,
            'trend': trend
        }

    def _calculate_rsi(self) -> Dict:
        """Calculate RSI"""
        settings = TECHNICAL_SETTINGS['rsi']
        period = settings['period']

        # Calculate price changes
        delta = self.data['Close'].diff()

        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # Calculate RS and RSI
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        current_rsi = float(rsi.iloc[-1])

        # Signal
        if current_rsi < settings['oversold']:
            signal = "Oversold"
        elif current_rsi > settings['overbought']:
            signal = "Overbought"
        else:
            signal = "Neutral"

        return {
            'rsi': current_rsi,
            'signal': signal
        }

    def _calculate_supertrend(self) -> Dict:
        """Calculate SuperTrend"""
        settings = TECHNICAL_SETTINGS['supertrend']
        period = settings['period']
        multiplier = settings['multiplier']

        # Calculate ATR
        high_low = self.data['High'] - self.data['Low']
        high_close = np.abs(self.data['High'] - self.data['Close'].shift())
        low_close = np.abs(self.data['Low'] - self.data['Close'].shift())

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(period).mean()

        # Calculate basic bands
        hl_avg = (self.data['High'] + self.data['Low']) / 2
        upper_band = hl_avg + (multiplier * atr)
        lower_band = hl_avg - (multiplier * atr)

        # SuperTrend calculation
        supertrend = pd.Series(index=self.data.index, dtype=float)
        direction = pd.Series(index=self.data.index, dtype=int)

        for i in range(period, len(self.data)):
            if i == period:
                supertrend.iloc[i] = lower_band.iloc[i]
                direction.iloc[i] = 1
            else:
                if self.data['Close'].iloc[i] > supertrend.iloc[i-1]:
                    supertrend.iloc[i] = lower_band.iloc[i]
                    direction.iloc[i] = 1
                else:
                    supertrend.iloc[i] = upper_band.iloc[i]
                    direction.iloc[i] = -1

        current_supertrend = float(supertrend.iloc[-1])
        current_direction = int(direction.iloc[-1])

        signal = "Buy" if current_direction == 1 else "Sell"

        return {
            'value': current_supertrend,
            'signal': signal
        }

    def _calculate_emas(self) -> Dict:
        """Calculate EMAs and crossover"""
        ema9 = self.data['Close'].ewm(span=9, adjust=False).mean()
        ema20 = self.data['Close'].ewm(span=20, adjust=False).mean()

        current_ema9 = float(ema9.iloc[-1])
        current_ema20 = float(ema20.iloc[-1])

        # Crossover
        if current_ema9 > current_ema20:
            crossover = "Bullish"
        elif current_ema9 < current_ema20:
            crossover = "Bearish"
        else:
            crossover = "Neutral"

        return {
            'ema9': current_ema9,
            'ema20': current_ema20,
            'crossover': crossover
        }

    def _calculate_signal_score(self, vwap, macd, rsi, supertrend, ema) -> Tuple[int, str, str]:
        """Calculate overall signal score (0-100)"""
        score = 0

        # VWAP (20 points)
        if vwap['position'] == "Above VWAP":
            score += 20
        elif vwap['position'] == "At VWAP":
            score += 10

        # MACD (25 points)
        if macd['trend'] == "Bullish":
            score += 25
        elif macd['trend'] == "Neutral":
            score += 12

        # RSI (20 points)
        if 40 <= rsi['rsi'] <= 60:
            score += 20  # Neutral zone (best for entry)
        elif 30 <= rsi['rsi'] < 40:
            score += 15  # Slightly oversold
        elif 60 < rsi['rsi'] <= 70:
            score += 15  # Slightly overbought
        elif rsi['rsi'] < 30:
            score += 10  # Very oversold

        # SuperTrend (20 points)
        if supertrend['signal'] == "Buy":
            score += 20

        # EMA Crossover (15 points)
        if ema['crossover'] == "Bullish":
            score += 15
        elif ema['crossover'] == "Neutral":
            score += 7

        # Grade
        if score >= 90:
            grade = "A"
            recommendation = "Strong Buy"
        elif score >= 75:
            grade = "B"
            recommendation = "Buy"
        elif score >= 50:
            grade = "C"
            recommendation = "Hold"
        elif score >= 25:
            grade = "D"
            recommendation = "Sell"
        else:
            grade = "F"
            recommendation = "Strong Sell"

        return score, grade, recommendation


def analyze_ticker(ticker: str) -> Optional[TechnicalAnalysis]:
    """Convenience function to analyze a ticker"""
    analyzer = TechnicalAnalyzer(ticker)
    return analyzer.analyze()
