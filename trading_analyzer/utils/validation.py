"""
Data Validation Utilities
Verify data quality before analysis
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ValidationIssue:
    """Data quality issue"""
    severity: str  # 'CRITICAL', 'WARNING', 'INFO'
    message: str
    field: Optional[str] = None


@dataclass
class ValidationResult:
    """Data validation result"""
    is_valid: bool
    quality_score: int  # 0-100
    issues: List[ValidationIssue]
    ticker: str


class DataValidator:
    """Validate stock data quality"""

    def __init__(self):
        self.validation_stats = {
            'total_validated': 0,
            'passed': 0,
            'warnings': 0,
            'critical': 0
        }

    def validate_stock_data(self,
                           ticker: str,
                           hist: pd.DataFrame,
                           info: dict) -> ValidationResult:
        """
        Comprehensive data validation

        Args:
            ticker: Stock symbol
            hist: Historical OHLCV data
            info: Stock info dictionary

        Returns:
            ValidationResult with quality score and issues
        """
        self.validation_stats['total_validated'] += 1
        issues = []

        # === HISTORICAL DATA VALIDATION ===

        # Check for empty data
        if hist.empty:
            issues.append(ValidationIssue(
                'CRITICAL',
                'No historical data available',
                'hist'
            ))
            return self._create_result(ticker, issues)

        # Check for sufficient data
        if len(hist) < 20:
            issues.append(ValidationIssue(
                'WARNING',
                f'Insufficient data ({len(hist)} days, expected 20+)',
                'hist'
            ))

        # Check for data gaps
        trading_days_expected = self._count_expected_trading_days(hist)
        actual_days = len(hist)

        if actual_days < trading_days_expected * 0.7:
            gap_pct = (1 - actual_days / trading_days_expected) * 100
            issues.append(ValidationIssue(
                'WARNING',
                f'Data gaps detected ({gap_pct:.0f}% missing)',
                'hist'
            ))

        # Check for price anomalies
        price_issues = self._check_price_anomalies(hist)
        issues.extend(price_issues)

        # Check volume consistency
        vol_issues = self._check_volume_anomalies(hist)
        issues.extend(vol_issues)

        # Check data freshness
        last_date = hist.index[-1]
        days_old = (datetime.now() - last_date).days

        if days_old > 5:
            issues.append(ValidationIssue(
                'WARNING',
                f'Data is {days_old} days old (stale)',
                'hist'
            ))

        # === INFO DATA VALIDATION ===

        # Check for missing critical fields
        critical_fields = ['floatShares', 'sharesOutstanding']
        for field in critical_fields:
            if not info.get(field):
                issues.append(ValidationIssue(
                    'INFO',
                    f'Missing {field} data',
                    field
                ))

        # Check for missing optional but useful fields
        useful_fields = ['shortPercentOfFloat', 'shortRatio']
        for field in useful_fields:
            if not info.get(field):
                issues.append(ValidationIssue(
                    'INFO',
                    f'Missing {field} data (squeeze detection limited)',
                    field
                ))

        # Validate field values
        if info.get('currentPrice', 0) <= 0:
            issues.append(ValidationIssue(
                'WARNING',
                'Invalid current price',
                'currentPrice'
            ))

        if info.get('floatShares', 0) > info.get('sharesOutstanding', 0):
            issues.append(ValidationIssue(
                'WARNING',
                'Float shares > shares outstanding (data error)',
                'floatShares'
            ))

        return self._create_result(ticker, issues)

    def _check_price_anomalies(self, hist: pd.DataFrame) -> List[ValidationIssue]:
        """Check for price data anomalies"""
        issues = []

        if hist.empty:
            return issues

        # Check for extreme single-day moves (possible split/error)
        price_changes = hist['Close'].pct_change()
        extreme_moves = abs(price_changes) > 0.50  # >50% single day

        if extreme_moves.any():
            num_extreme = extreme_moves.sum()
            issues.append(ValidationIssue(
                'WARNING',
                f'{num_extreme} extreme price movements detected (possible split/data error)',
                'Close'
            ))

        # Check for zero/negative prices
        if (hist['Close'] <= 0).any():
            issues.append(ValidationIssue(
                'CRITICAL',
                'Zero or negative prices detected',
                'Close'
            ))

        # Check for OHLC consistency (High >= Low, etc.)
        ohlc_valid = (
            (hist['High'] >= hist['Low']) &
            (hist['High'] >= hist['Close']) &
            (hist['High'] >= hist['Open']) &
            (hist['Low'] <= hist['Close']) &
            (hist['Low'] <= hist['Open'])
        )

        if not ohlc_valid.all():
            num_invalid = (~ohlc_valid).sum()
            issues.append(ValidationIssue(
                'WARNING',
                f'{num_invalid} days with invalid OHLC relationships',
                'OHLC'
            ))

        return issues

    def _check_volume_anomalies(self, hist: pd.DataFrame) -> List[ValidationIssue]:
        """Check for volume data anomalies"""
        issues = []

        if hist.empty or 'Volume' not in hist.columns:
            return issues

        # Check for zero volume days
        zero_volume_days = (hist['Volume'] == 0).sum()

        if zero_volume_days > 3:
            issues.append(ValidationIssue(
                'WARNING',
                f'{zero_volume_days} zero-volume days detected',
                'Volume'
            ))

        # Check for negative volume
        if (hist['Volume'] < 0).any():
            issues.append(ValidationIssue(
                'CRITICAL',
                'Negative volume detected',
                'Volume'
            ))

        # Check for extreme volume spikes (possible data error)
        if len(hist) > 5:
            avg_volume = hist['Volume'].mean()
            max_volume = hist['Volume'].max()

            if max_volume > avg_volume * 100:  # 100x spike
                issues.append(ValidationIssue(
                    'INFO',
                    'Extreme volume spike detected (verify manually)',
                    'Volume'
                ))

        return issues

    def _count_expected_trading_days(self, hist: pd.DataFrame) -> int:
        """Estimate expected number of trading days"""
        if hist.empty:
            return 0

        # Calculate date range
        date_range = (hist.index[-1] - hist.index[0]).days

        # Rough estimate: ~252 trading days per year
        # Adjust for weekends (~5/7 days)
        expected_days = int(date_range * (5/7))

        return max(expected_days, len(hist))

    def _create_result(self, ticker: str, issues: List[ValidationIssue]) -> ValidationResult:
        """Create validation result with quality score"""

        # Count by severity
        critical_count = len([i for i in issues if i.severity == 'CRITICAL'])
        warning_count = len([i for i in issues if i.severity == 'WARNING'])
        info_count = len([i for i in issues if i.severity == 'INFO'])

        # Update stats
        if critical_count > 0:
            self.validation_stats['critical'] += 1
        elif warning_count > 0:
            self.validation_stats['warnings'] += 1
        else:
            self.validation_stats['passed'] += 1

        # Calculate quality score (0-100)
        quality_score = 100
        quality_score -= critical_count * 50  # -50 per critical
        quality_score -= warning_count * 10   # -10 per warning
        quality_score -= info_count * 2       # -2 per info

        quality_score = max(0, min(100, quality_score))

        # Valid if no critical issues and score >= 50
        is_valid = (critical_count == 0) and (quality_score >= 50)

        return ValidationResult(
            is_valid=is_valid,
            quality_score=quality_score,
            issues=issues,
            ticker=ticker
        )

    def print_validation_result(self, result: ValidationResult, verbose: bool = False):
        """Print validation result"""

        if not result.issues:
            print(f"✅ {result.ticker}: Data quality excellent ({result.quality_score}/100)")
            return

        # Print summary
        critical = len([i for i in result.issues if i.severity == 'CRITICAL'])
        warnings = len([i for i in result.issues if i.severity == 'WARNING'])
        info = len([i for i in result.issues if i.severity == 'INFO'])

        status_icon = "❌" if critical > 0 else "⚠️" if warnings > 0 else "ℹ️"

        print(f"{status_icon} {result.ticker}: Data Quality Score: {result.quality_score}/100")

        if verbose or critical > 0:
            # Print issues
            for issue in result.issues:
                icon = "🔴" if issue.severity == 'CRITICAL' else "⚠️" if issue.severity == 'WARNING' else "ℹ️"
                print(f"   {icon} {issue.severity}: {issue.message}")

    def get_statistics(self) -> Dict:
        """Get validation statistics"""
        total = self.validation_stats['total_validated']

        return {
            'total_validated': total,
            'passed': self.validation_stats['passed'],
            'warnings': self.validation_stats['warnings'],
            'critical_failures': self.validation_stats['critical'],
            'pass_rate': (self.validation_stats['passed'] / total * 100) if total > 0 else 0
        }

    def print_statistics(self):
        """Print validation statistics"""
        stats = self.get_statistics()

        print(f"\n📊 DATA VALIDATION STATISTICS")
        print(f"{'=' * 60}")
        print(f"Total Validated:        {stats['total_validated']}")
        print(f"Passed:                 {stats['passed']} ({stats['pass_rate']:.1f}%)")
        print(f"Warnings:               {stats['warnings']}")
        print(f"Critical Failures:      {stats['critical_failures']}")
        print(f"{'=' * 60}")


# Test function
if __name__ == "__main__":
    import yfinance as yf

    print("Testing data validation...")

    validator = DataValidator()

    # Test with good ticker
    test_tickers = ['AAPL', 'GME', 'INVALID123']

    for ticker in test_tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='3mo', prepost=True)
            info = stock.info

            result = validator.validate_stock_data(ticker, hist, info)
            validator.print_validation_result(result, verbose=True)

        except Exception as e:
            print(f"❌ {ticker}: Error - {e}")

    # Print summary
    validator.print_statistics()
