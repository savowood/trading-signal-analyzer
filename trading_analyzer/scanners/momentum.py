"""
5 Pillars Momentum Scanner
Main scanner implementation combining FinViz/TradingView + MicroCap providers
"""
from typing import List, Optional

from ..core.scanner import (
    CompositeScanner, ScanResult, ScanParameters, ScanMode,
    calculate_pillars_score, calculate_quality_score
)
from ..data.providers import (
    TradingViewProvider, MicroCapProvider, ForexProvider, CryptoProvider, FinVizProvider
)
from ..data.cache import get_cache_manager
from ..config import MIN_SCORE, MARKETS, API_KEYS


class MomentumScanner(CompositeScanner):
    """
    5 Pillars Momentum Scanner

    Combines:
    - TradingView multi-query (3 filters for max coverage)
    - Direct micro-cap scan (priority or comprehensive)
    - 15-minute result caching
    - Intelligent deduplication and scoring
    """

    def __init__(self):
        super().__init__("5 Pillars Momentum")
        self.cache = get_cache_manager()

        # Initialize providers
        # FinViz Elite HTTP API (uses export endpoint with API token)
        self.finviz: Optional[FinVizProvider] = None
        if API_KEYS.get('finviz'):
            self.finviz = FinVizProvider(API_KEYS['finviz'])

        self.tradingview = TradingViewProvider()
        self.microcap = MicroCapProvider()
        self.forex = ForexProvider()
        self.crypto = CryptoProvider()

    def scan(self, params: ScanParameters) -> List[ScanResult]:
        """
        Perform optimized hybrid scan

        Args:
            params: Scan parameters

        Returns:
            List of scan results sorted by score
        """
        # Check cache first
        cached_results = self._check_cache(params)
        if cached_results:
            return cached_results

        # Determine market type
        market_info = MARKETS.get(params.market_choice, MARKETS['1'])
        market_type = market_info.get('type', 'stocks')

        # Route to appropriate provider based on market type
        if market_type == 'forex':
            return self._scan_forex(params)
        elif market_type == 'crypto':
            return self._scan_crypto(params)
        else:
            return self._scan_stocks(params)

    def _scan_stocks(self, params: ScanParameters) -> List[ScanResult]:
        """Scan stocks using FinViz/TradingView + MicroCap providers"""
        # Fresh scan
        if params.mode == ScanMode.QUICK:
            scan_mode = "QUICK SCAN"
        elif params.mode == ScanMode.DEEP:
            scan_mode = "DEEP SCAN"
        else:
            scan_mode = "SMART SCAN"

        print(f"🔍 {scan_mode}: Scanning for momentum setups...")
        print(f"   Filters: ${params.min_price:.2f} - ${params.max_price:.2f}, "
              f"{params.min_rel_vol}x+ RelVol, +{params.min_change}% day, <{params.max_float}M float")

        # Step 1: FinViz Elite (if available) or TradingView
        if self.finviz:
            print(f"   💎 Using FinViz Elite API (faster, unlimited results)")
            tv_results = self.finviz.scan(params)
        else:
            tv_results = self.tradingview.scan(params)

        # Enrich top results with accurate data from yfinance
        # Limit to top 30 by change% to avoid rate limiting
        if tv_results:
            # Sort by change% to prioritize best candidates
            tv_results_sorted = sorted(tv_results, key=lambda x: x.change_pct, reverse=True)
            top_results = tv_results_sorted[:30]

            if len(tv_results) > 30:
                print(f"   📊 Enriching top 30 of {len(tv_results)} results (sorted by change%)...")
            else:
                print(f"   📊 Enriching {len(tv_results)} results with detailed data...")

            tv_results = self._enrich_results(top_results, params)

        # Step 2: Micro-cap scan (skip for QUICK mode)
        mc_results = []
        if params.mode != ScanMode.QUICK:
            tv_tickers = {r.ticker for r in tv_results}
            print(f"   💡 Skipping {len(tv_tickers)} tickers already found by TradingView")

            mc_results = self.microcap.scan(params, exclude_tickers=tv_tickers)

            if mc_results:
                print(f"✅ Micro-cap scan: {len(mc_results)} additional stocks found")
        else:
            print(f"   ⚡ QUICK MODE: Skipping micro-cap direct scan (TradingView only)")

        # Step 3: Merge and score results
        all_results = tv_results + mc_results

        # Calculate scores
        for result in all_results:
            result.score = calculate_pillars_score(result, params)

        # Filter by minimum pillars (at least 3/5)
        all_results = [r for r in all_results if r.score >= 3]

        # Sort by score and change
        all_results.sort(key=lambda x: (x.score, x.change_pct), reverse=True)

        # Summary
        total_count = len(all_results)
        tv_count = len([r for r in all_results if r.source == "TradingView"])
        finviz_count = len([r for r in all_results if r.source == "FinViz Elite"])
        mc_count = len([r for r in all_results if r.source == "DIRECT"])

        if finviz_count > 0:
            print(f"✅ Total: {total_count} stocks ({finviz_count} from FinViz Elite + {mc_count} from direct scan)")
        else:
            print(f"✅ Total: {total_count} stocks ({tv_count} from TradingView + {mc_count} from direct scan)")

        # Cache results
        self._save_cache(params, all_results)
        print(f"   💾 Results cached for 15 minutes")

        return all_results

    def _scan_forex(self, params: ScanParameters) -> List[ScanResult]:
        """Scan FOREX pairs"""
        print(f"🔍 FOREX SCAN: Analyzing currency pairs...")

        # Scan forex
        all_results = self.forex.scan(params)

        # Sort by absolute change (forex can go both ways)
        all_results.sort(key=lambda x: abs(x.change_pct), reverse=True)

        print(f"✅ Total: {len(all_results)} active FOREX pairs")

        # Cache results
        self._save_cache(params, all_results)
        print(f"   💾 Results cached for 5 minutes")

        return all_results

    def _scan_crypto(self, params: ScanParameters) -> List[ScanResult]:
        """Scan cryptocurrency pairs"""
        print(f"🔍 CRYPTO SCAN: Analyzing digital assets...")

        # Scan crypto
        all_results = self.crypto.scan(params)

        # Sort by absolute change
        all_results.sort(key=lambda x: abs(x.change_pct), reverse=True)

        print(f"✅ Total: {len(all_results)} active cryptocurrencies")

        # Cache results
        self._save_cache(params, all_results)
        print(f"   💾 Results cached for 3 minutes")

        return all_results

    def _check_cache(self, params: ScanParameters) -> List[ScanResult]:
        """Check if we have cached results"""
        cache_key = params.to_cache_key()
        cached = self.cache.get('scan_results', cache_key)

        if cached:
            age = self.cache.get_age('scan_results', cache_key)
            print(f"   ⚡ Using cached results ({len(cached)} stocks, {age:.1f} min old)")
            print(f"      Cache expires in {15 - age:.1f} minutes")

            # Convert dicts back to ScanResult objects
            return [ScanResult(**item) for item in cached]

        return None

    def _save_cache(self, params: ScanParameters, results: List[ScanResult]):
        """Save results to cache"""
        cache_key = params.to_cache_key()

        # Convert ScanResult objects to dicts
        results_dict = [
            {
                'ticker': r.ticker,
                'price': r.price,
                'score': r.score,
                'rel_vol': r.rel_vol,
                'float_m': r.float_m,
                'change_pct': r.change_pct,
                'week_change': r.week_change,
                'catalyst': r.catalyst,
                'low_float': r.low_float,
                'description': r.description,
                'source': r.source,
                'exchange': r.exchange,
                'volume': r.volume,
                'market_cap': r.market_cap
            }
            for r in results
        ]

        self.cache.set('scan_results', cache_key, results_dict)

    def _enrich_results(self, results: List[ScanResult], params: ScanParameters) -> List[ScanResult]:
        """Enrich results with accurate data from yfinance"""
        import yfinance as yf
        import time

        enriched = []
        filtered_out = 0
        rate_limited = 0
        total = len(results)

        # Check if using FinViz Elite (already pre-filtered)
        using_finviz = len(results) > 0 and results[0].source == "FinViz Elite"

        for i, result in enumerate(results, 1):
            try:
                # Show progress (cleaner output)
                print(f"      Processing {i}/{total}: {result.ticker}...", end='\r')

                # Small delay to avoid rate limiting (50ms)
                if i > 1:
                    time.sleep(0.05)

                # Fetch real data from yfinance
                ticker = yf.Ticker(result.ticker)
                info = ticker.info
                hist = ticker.history(period='1mo')

                if hist.empty or len(hist) < 20:
                    # Skip if insufficient data - we need accurate data to show
                    filtered_out += 1
                    continue

                # Get accurate relative volume
                current_volume = hist['Volume'].iloc[-1]
                avg_volume = hist['Volume'].tail(20).mean()
                rel_vol = current_volume / avg_volume if avg_volume > 0 else result.rel_vol

                # Get accurate float
                float_shares = info.get('floatShares', info.get('sharesOutstanding', 0))
                float_m = float_shares / 1_000_000 if float_shares else result.float_m

                # For FinViz Elite results, be lenient (80% threshold) since already pre-filtered
                # For TradingView, use strict filters
                if using_finviz:
                    min_rel_vol_threshold = params.min_rel_vol * 0.8
                    max_float_threshold = params.max_float * 1.2
                else:
                    min_rel_vol_threshold = params.min_rel_vol
                    max_float_threshold = params.max_float

                # Apply filters with real data
                if rel_vol < min_rel_vol_threshold:
                    filtered_out += 1
                    continue
                if float_m > max_float_threshold:
                    filtered_out += 1
                    continue

                # Update result with accurate data
                result.rel_vol = rel_vol
                result.float_m = float_m
                result.low_float = 0 < float_m < 20

                enriched.append(result)

            except Exception as e:
                error_msg = str(e)
                if "Rate limit" in error_msg or "Too Many Requests" in error_msg:
                    rate_limited += 1
                # Skip if enrichment fails - we need accurate data
                filtered_out += 1
                continue

        # Clear progress line and show summary
        print(" " * 80, end='\r')  # Clear the line
        print(f"      ✅ Found {len(enriched)} stocks meeting all criteria")
        if filtered_out > 0:
            print(f"      ⚠️  Filtered out: {filtered_out} stocks (low RelVol/high float/insufficient data)")
        if rate_limited > 0:
            print(f"      ⚠️  Rate limited: {rate_limited} stocks (try again in a few minutes)")

        return enriched


def create_scanner() -> MomentumScanner:
    """Factory function to create momentum scanner"""
    return MomentumScanner()
