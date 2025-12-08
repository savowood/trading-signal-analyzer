"""
Smart Pre-filtering Utilities
Quick rejection criteria to skip expensive analysis
"""
import yfinance as yf
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class FilterCriteria:
    """Pre-filter criteria (quick checks)"""
    min_price: float = 1.0
    max_price: float = 100.0
    min_volume: int = 100_000
    max_float: Optional[float] = None  # In shares
    min_market_cap: Optional[float] = None
    max_market_cap: Optional[float] = None


class SmartPreFilter:
    """
    Fast pre-filtering to skip expensive analysis

    Uses only basic metrics that don't require historical data:
    - Current price
    - Current volume
    - Float shares
    - Market cap

    Avoids expensive yfinance.history() calls for obvious rejections
    """

    def __init__(self, criteria: Optional[FilterCriteria] = None):
        self.criteria = criteria or FilterCriteria()
        self.stats = {
            'total': 0,
            'passed': 0,
            'rejected': 0,
            'errors': 0,
            'rejection_reasons': {}
        }

    def quick_check(self, ticker: str) -> tuple[bool, Optional[str]]:
        """
        Quick check if ticker passes basic criteria

        Args:
            ticker: Stock symbol

        Returns:
            (passes: bool, rejection_reason: Optional[str])
        """
        self.stats['total'] += 1

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Get basic metrics (no historical data needed)
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            volume = info.get('volume') or info.get('regularMarketVolume', 0)
            float_shares = info.get('floatShares', 0)
            market_cap = info.get('marketCap', 0)

            # Quick rejection checks
            if current_price < self.criteria.min_price:
                self._record_rejection('price_too_low')
                return False, f"Price ${current_price:.2f} < ${self.criteria.min_price}"

            if current_price > self.criteria.max_price:
                self._record_rejection('price_too_high')
                return False, f"Price ${current_price:.2f} > ${self.criteria.max_price}"

            if volume < self.criteria.min_volume:
                self._record_rejection('volume_too_low')
                return False, f"Volume {volume:,} < {self.criteria.min_volume:,}"

            if self.criteria.max_float and float_shares > self.criteria.max_float:
                self._record_rejection('float_too_high')
                return False, f"Float {float_shares/1e6:.1f}M > {self.criteria.max_float/1e6:.1f}M"

            if self.criteria.min_market_cap and market_cap < self.criteria.min_market_cap:
                self._record_rejection('market_cap_too_low')
                return False, f"Market cap ${market_cap/1e6:.0f}M too low"

            if self.criteria.max_market_cap and market_cap > self.criteria.max_market_cap:
                self._record_rejection('market_cap_too_high')
                return False, f"Market cap ${market_cap/1e6:.0f}M too high"

            # Passed all checks
            self.stats['passed'] += 1
            return True, None

        except Exception as e:
            self.stats['errors'] += 1
            return False, f"Error: {str(e)[:50]}"

    def filter_tickers(self, tickers: List[str], verbose: bool = False) -> List[str]:
        """
        Filter list of tickers, keeping only those that pass

        Args:
            tickers: List of ticker symbols
            verbose: Print rejection reasons

        Returns:
            List of tickers that passed pre-filter
        """
        passed_tickers = []

        print(f"\n🔍 Pre-filtering {len(tickers)} candidates...")

        for i, ticker in enumerate(tickers, 1):
            passes, reason = self.quick_check(ticker)

            if passes:
                passed_tickers.append(ticker)
            elif verbose and reason:
                print(f"   ❌ {ticker}: {reason}")

            # Progress indicator
            if i % 25 == 0:
                print(f"   [{i}/{len(tickers)}] Filtered...", end='\r')

        print(f"\n   ✅ {len(passed_tickers)}/{len(tickers)} tickers passed pre-filter")

        return passed_tickers

    def _record_rejection(self, reason: str):
        """Record rejection reason for statistics"""
        self.stats['rejected'] += 1
        self.stats['rejection_reasons'][reason] = \
            self.stats['rejection_reasons'].get(reason, 0) + 1

    def get_statistics(self) -> Dict:
        """Get pre-filter statistics"""
        return {
            'total_checked': self.stats['total'],
            'passed': self.stats['passed'],
            'rejected': self.stats['rejected'],
            'errors': self.stats['errors'],
            'pass_rate': (self.stats['passed'] / self.stats['total'] * 100)
                        if self.stats['total'] > 0 else 0,
            'rejection_breakdown': self.stats['rejection_reasons']
        }

    def print_statistics(self):
        """Print pre-filter statistics"""
        stats = self.get_statistics()

        print(f"\n📊 PRE-FILTER STATISTICS")
        print(f"{'=' * 60}")
        print(f"Total Tickers Checked:  {stats['total_checked']}")
        print(f"Passed Pre-Filter:      {stats['passed']} ({stats['pass_rate']:.1f}%)")
        print(f"Rejected:               {stats['rejected']}")
        print(f"Errors:                 {stats['errors']}")

        if stats['rejection_breakdown']:
            print(f"\nRejection Breakdown:")
            for reason, count in sorted(stats['rejection_breakdown'].items(),
                                       key=lambda x: x[1], reverse=True):
                pct = (count / stats['rejected'] * 100) if stats['rejected'] > 0 else 0
                print(f"  • {reason.replace('_', ' ').title()}: {count} ({pct:.1f}%)")

        print(f"{'=' * 60}")


def create_pressure_cooker_prefilter() -> SmartPreFilter:
    """Create pre-filter optimized for Pressure Cooker scanner"""
    criteria = FilterCriteria(
        min_price=2.0,
        max_price=50.0,
        min_volume=500_000,
        max_float=20_000_000,  # 20M float max
    )
    return SmartPreFilter(criteria)


def create_momentum_prefilter() -> SmartPreFilter:
    """Create pre-filter optimized for Momentum scanner"""
    criteria = FilterCriteria(
        min_price=2.0,
        max_price=100.0,
        min_volume=1_000_000,
    )
    return SmartPreFilter(criteria)


def create_darkflow_prefilter() -> SmartPreFilter:
    """Create pre-filter optimized for Dark Flow scanner"""
    criteria = FilterCriteria(
        min_price=5.0,
        max_price=500.0,
        min_volume=500_000,
        min_market_cap=100_000_000,  # $100M minimum
    )
    return SmartPreFilter(criteria)


# Test function
if __name__ == "__main__":
    print("Testing smart pre-filter...")

    test_tickers = ['AAPL', 'TSLA', 'GME', 'AMC', 'PENNY', 'NVDA']

    # Test with Pressure Cooker criteria
    prefilter = create_pressure_cooker_prefilter()
    passed = prefilter.filter_tickers(test_tickers, verbose=True)

    print(f"\nPassed tickers: {passed}")
    prefilter.print_statistics()
