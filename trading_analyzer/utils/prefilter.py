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

    def quick_check(self, ticker: str, retry_count: int = 2) -> tuple[bool, Optional[str]]:
        """
        Quick check if ticker passes basic criteria with retry logic

        Args:
            ticker: Stock symbol
            retry_count: Number of retries for rate limit errors

        Returns:
            (passes: bool, rejection_reason: Optional[str])
        """
        import time
        self.stats['total'] += 1

        for attempt in range(retry_count + 1):
            try:
                # Add delay to avoid rate limiting (100ms between requests)
                if attempt > 0:
                    # Exponential backoff on retries
                    wait_time = 0.5 * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    # Small delay between initial requests
                    time.sleep(0.1)

                stock = yf.Ticker(ticker)
                info = stock.info

                # Check if we got valid data (not empty or error response)
                if not info or len(info) < 3:
                    if attempt < retry_count:
                        continue  # Retry
                    self.stats['errors'] += 1
                    return False, "No data available"

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
                error_msg = str(e)

                # Check for rate limiting or auth errors
                if "Too Many Requests" in error_msg or "429" in error_msg:
                    if attempt < retry_count:
                        continue  # Retry with backoff
                    self.stats['errors'] += 1
                    return False, "Rate limited"

                elif "Unauthorized" in error_msg or "401" in error_msg or "Invalid Crumb" in error_msg:
                    if attempt < retry_count:
                        continue  # Retry
                    self.stats['errors'] += 1
                    return False, "Auth error"

                # Other errors
                self.stats['errors'] += 1
                return False, f"Error: {error_msg[:50]}"

        # If we exhausted all retries
        self.stats['errors'] += 1
        return False, "Max retries exceeded"

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
        rate_limited_count = 0
        auth_error_count = 0

        print(f"\n🔍 Pre-filtering {len(tickers)} candidates...")
        print("   (This may take a moment to avoid rate limiting...)")

        for i, ticker in enumerate(tickers, 1):
            passes, reason = self.quick_check(ticker)

            if passes:
                passed_tickers.append(ticker)
            elif reason:
                # Count specific error types
                if reason == "Rate limited":
                    rate_limited_count += 1
                    if verbose and rate_limited_count <= 3:
                        print(f"   ⏭️  Skipped {ticker}: Rate limited")
                elif reason == "Auth error":
                    auth_error_count += 1
                    if verbose and auth_error_count == 1:
                        print(f"   ⚠️  Authentication issues detected (will retry automatically)")
                elif verbose and reason not in ["Rate limited", "Auth error"]:
                    print(f"   ⏭️  Skipped {ticker}: {reason}")

            # Progress indicator every 10 tickers
            if i % 10 == 0:
                print(f"   Progress: {i}/{len(tickers)} checked ({len(passed_tickers)} passed)...", end='\r')

        # Clear progress line
        print(" " * 80, end='\r')

        # Show summary
        print(f"\n   ✅ {len(passed_tickers)}/{len(tickers)} tickers passed pre-filter")
        if rate_limited_count > 0:
            print(f"   ⚠️  {rate_limited_count} tickers skipped due to rate limiting")
        if auth_error_count > 0:
            print(f"   ⚠️  {auth_error_count} authentication errors (temporary)")

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
