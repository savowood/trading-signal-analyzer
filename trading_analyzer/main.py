"""
Main Entry Point
Modular Trading Signal Analyzer
"""
import sys
from typing import Dict, List
from datetime import datetime

from .ui.cli import (
    show_banner, show_main_menu, build_scan_parameters, build_pressure_cooker_parameters,
    edit_settings_interactive
)
from .ui.display import (
    show_disclaimer, show_pressure_cooker_disclaimer,
    display_results, display_summary, display_pressure_cooker_results,
    display_pressure_cooker_details, prompt_ticker_selection,
    display_technical_analysis, display_fibonacci_analysis
)
from .core.analysis import analyze_ticker
from .core.scanner import ScanParameters, ScanMode, ScanResult
from .predictive.fibonacci import analyze_fibonacci
from .scanners.momentum import create_scanner
from .scanners.darkflow import create_darkflow_scanner
from .scanners.pressurecooker_enhanced import create_enhanced_pressure_cooker_scanner
from .data.cache import get_cache_manager
from .data.database import get_database_manager
from .config import (
    VERSION, load_user_settings, apply_user_settings, save_user_settings,
    create_default_settings_file, get_settings_info, get_technical_analysis_params
)
from .utils import (
    ResultExporter,
    ASCIIChartGenerator,
    normalize_ticker
)

# Global storage for previous scan results
PREVIOUS_SCANS = {
    'momentum': None,
    'darkflow': None,
    'pressurecooker': None
}


def main():
    """Main application loop"""
    # Show banner
    show_banner()

    # Load user settings
    print("Loading settings...")
    user_settings = load_user_settings()
    if user_settings:
        apply_user_settings(user_settings)
        print(f"✅ Loaded custom settings from ~/.trading_analyzer\n")
    else:
        print(f"ℹ️  Using default settings (create ~/.trading_analyzer to customize)\n")
        # Create settings structure if none exists
        user_settings = {}

    # Show disclaimer
    accepted, user_settings = show_disclaimer(user_settings)
    if not accepted:
        print("Exiting...")
        sys.exit(0)

    # Save settings if disclaimer was newly acknowledged
    if user_settings.get('disclaimer_acknowledged'):
        # Only save if not already in file or if newly acknowledged
        existing_settings = load_user_settings()
        if not existing_settings or not existing_settings.get('disclaimer_acknowledged'):
            # Ensure settings file exists with at least disclaimer flag
            if not existing_settings:
                create_default_settings_file()
                existing_settings = load_user_settings()
            existing_settings['disclaimer_acknowledged'] = True
            save_user_settings(existing_settings)

    # Create scanner
    scanner = create_scanner()
    cache = get_cache_manager()

    # Main loop
    while True:
        choice = show_main_menu()

        if choice == '1':
            # Run momentum scan
            run_scan(scanner)

        elif choice == '2':
            # Run Dark Flow scan
            run_darkflow_scan()

        elif choice == '3':
            # Run Pressure Cooker scan
            run_pressure_cooker_scan()

        elif choice == '4':
            # View previous scan results
            view_previous_scan_results()

        elif choice == '5':
            # Analyze single ticker
            analyze_single_ticker()

        elif choice == '6':
            # View database statistics
            view_database_statistics()

        elif choice == '7':
            # Manage watchlist
            manage_watchlist()

        elif choice == '8':
            # View cache status
            view_cache_status(cache)

        elif choice == '9':
            # Clear cache
            clear_cache(cache)

        elif choice == 's':
            # View settings
            view_settings()

        elif choice == '0':
            # Edit settings
            edit_settings()

        elif choice == 'q':
            print("\nGoodbye!")
            break

        else:
            print("❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")


def handle_scan_results(results, scan_type='momentum', skip_initial_display=False):
    """
    Handle scan results workflow: display, export, ticker selection, analysis

    Args:
        results: Scan results list
        scan_type: Type of scan ('momentum', 'darkflow', 'pressurecooker')
        skip_initial_display: If True, skip displaying results (already displayed)
    """
    # Display results (unless already displayed)
    if not skip_initial_display:
        display_results(results)
        display_summary(results)

    if not results:
        return

    # Store results for later access
    PREVIOUS_SCANS[scan_type] = {
        'results': results,
        'timestamp': datetime.now(),
        'type': scan_type
    }

    # Workflow loop - allow user to return to scan results
    first_iteration = True
    while True:
        # On subsequent iterations, redisplay the results list
        if not first_iteration:
            print("\n" + "=" * 80)
            print("📊 SCAN RESULTS")
            print("=" * 80)
            display_results(results)
            display_summary(results)

        # Export option (only on first iteration)
        if first_iteration:
            print("\n" + "=" * 80)
            print("📤 EXPORT OPTIONS")
            print("=" * 80)
            print("1. Export to CSV")
            print("2. Export to JSON")
            print("3. Export to Excel (XLSX)")
            print("4. Export to PDF")
            print("5. Export to ALL formats")
            print("6. Skip export / Continue to ticker selection")

            export_choice = input("\nEnter choice (1-6): ").strip()

            if export_choice in ['1', '2', '3', '4', '5']:
                try:
                    exporter = ResultExporter()

                    # Convert ScanResult objects to dictionaries for export
                    results_dicts = []
                    for r in results:
                        if hasattr(r, '__dict__'):
                            results_dicts.append(r.__dict__)
                        else:
                            results_dicts.append(r)

                    # Export based on choice
                    if export_choice == '1':
                        exporter.export_to_csv(results_dicts, scanner_type=scan_type)
                    elif export_choice == '2':
                        exporter.export_to_json(results_dicts, scanner_type=scan_type)
                    elif export_choice == '3':
                        exporter.export_to_excel(results_dicts, scanner_type=scan_type)
                    elif export_choice == '4':
                        exporter.export_to_pdf(results_dicts, scanner_type=scan_type)
                    elif export_choice == '5':
                        exporter.export_all_formats(results_dicts, scanner_type=scan_type)

                except Exception as e:
                    print(f"❌ Export error: {e}")
                    import traceback
                    traceback.print_exc()

                input("\nPress Enter to continue...")

        # Clear separator before ticker selection
        print("\n" + "=" * 80)
        print("📊 TICKER SELECTION FOR DETAILED ANALYSIS")
        print("=" * 80)

        # Prompt for ticker selection for technical analysis
        selected = prompt_ticker_selection(results)
        first_iteration = False  # Mark that we've been through once
        if not selected:
            # User chose to skip or back - exit workflow
            break

        print(f"\n✅ Selected: {', '.join(selected)}")

        # Show Dark Flow detailed analysis for selected tickers (if applicable)
        if scan_type == 'darkflow':
            from .ui.display import display_dark_flow_analysis
            print("\n" + "=" * 80)
            print("🌊 DETAILED DARK FLOW ANALYSIS")
            print("=" * 80)

            for i, ticker in enumerate(selected, 1):
                # Find the result for this ticker
                result = next((r for r in results if r.ticker == ticker), None)
                if result and hasattr(result, 'dark_flow_analysis'):
                    display_dark_flow_analysis(result.dark_flow_analysis)
                    if i < len(selected):
                        input("\nPress Enter to continue to next stock...")

        # Show Pressure Cooker detailed analysis for selected tickers (if applicable)
        if scan_type == 'pressurecooker':
            print("\n" + "=" * 80)
            print("🎯 DETAILED PRESSURE COOKER ANALYSIS")
            print("=" * 80)

            for i, ticker in enumerate(selected, 1):
                # Find the result for this ticker
                result = next((r for r in results if r.ticker == ticker), None)
                if result:
                    display_pressure_cooker_details(result)
                    if i < len(selected):
                        input("\nPress Enter to continue to next stock...")

        # Offer chart display
        offer_chart_display(selected)

        # Technical analysis
        analyze_selected_tickers(selected)

        # After analysis, ask if user wants to select more tickers
        print("\n" + "=" * 80)
        print("OPTIONS")
        print("=" * 80)
        print("1. Select more tickers from scan results")
        print("2. Return to main menu")

        next_choice = input("\nEnter choice (1-2): ").strip()

        if next_choice != '1':
            break


def run_scan(scanner):
    """Run momentum scan workflow"""
    # Get scan parameters from user
    params = build_scan_parameters()

    if params is None:
        print("\nScan cancelled.")
        return

    try:
        # Run scan
        results = scanner.scan(params)

        # Handle scan results with export and ticker selection
        handle_scan_results(results, scan_type='momentum')

    except KeyboardInterrupt:
        print("\n\nScan cancelled by user.")
    except Exception as e:
        print(f"\n❌ Scan error: {e}")
        import traceback
        traceback.print_exc()


def analyze_selected_tickers(tickers):
    """Analyze selected tickers with technical indicators"""
    import yfinance as yf
    from .config import DEFAULT_TRADING_STYLE

    # Get correct technical analysis parameters based on trading style
    ta_params = get_technical_analysis_params(DEFAULT_TRADING_STYLE)

    print(f"\n{'=' * 100}")
    print(f"TECHNICAL ANALYSIS")
    print(f"{'=' * 100}")
    print(f"Analyzing {len(tickers)} ticker(s)...")
    print(f"Using {ta_params['interval']} timeframe for indicators (based on trading style)")

    for i, ticker in enumerate(tickers, 1):
        print(f"\n[{i}/{len(tickers)}] Analyzing {ticker}...")

        try:
            # Technical analysis with correct timeframe
            analysis = analyze_ticker(ticker, period=ta_params['period'], interval=ta_params['interval'])

            if analysis:
                display_technical_analysis(analysis)

                # Fibonacci projections (predictive)
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="3mo", prepost=True)

                    if not hist.empty and len(hist) >= 20:
                        # Get real-time price (includes pre/post market)
                        info = stock.info
                        real_time_price = info.get('currentPrice') or info.get('regularMarketPrice')

                        fib_analysis = analyze_fibonacci(ticker, hist, real_time_price)
                        display_fibonacci_analysis(fib_analysis)
                    else:
                        print("\n⚠️  Insufficient data for Fibonacci projections")

                except Exception as fib_error:
                    print(f"\n⚠️  Could not calculate Fibonacci projections: {fib_error}")

                # News sentiment (predictive)
                try:
                    from .predictive.news_sentiment import analyze_news_sentiment
                    from .ui.display import display_news_sentiment

                    # Get API key from settings
                    user_settings = load_user_settings()
                    api_key = None
                    if user_settings and 'api_keys' in user_settings:
                        api_key = user_settings['api_keys'].get('finnhub')

                    if api_key:
                        news = analyze_news_sentiment(ticker, api_key, days_back=1)
                        if news:
                            display_news_sentiment(news)
                        else:
                            print("\n📰 News Sentiment: No recent news available")
                    else:
                        print("\n📰 News Sentiment: Disabled (set FinnHub API key to enable)")

                except Exception as news_error:
                    print(f"\n⚠️  Could not fetch news sentiment: {news_error}")

                # Insider trading (predictive - stocks only, not crypto)
                # Dual-source: Polygon.io (primary) + SEC EDGAR (fallback)
                try:
                    from .predictive.insider_trading import analyze_insider_trading, is_crypto
                    from .ui.display import display_insider_trading

                    # Check if this is a stock (not crypto)
                    if not is_crypto(ticker):
                        # Try to get Polygon API key, fall back to SEC EDGAR if not available
                        user_settings = load_user_settings()
                        polygon_key = None
                        if user_settings and 'api_keys' in user_settings:
                            polygon_key = user_settings['api_keys'].get('polygon')

                        insider = analyze_insider_trading(ticker, api_key=polygon_key, days_back=90)
                        if insider:
                            display_insider_trading(insider)
                        else:
                            print("\n👔 Insider Trading: No recent insider activity")
                    else:
                        # Crypto doesn't have insider trading
                        # But may have FinViz multi-timeframe performance
                        try:
                            from .data.finviz_crypto import FinVizCryptoProvider

                            # Load FinViz API key
                            user_settings = load_user_settings()
                            if user_settings and 'api_keys' in user_settings:
                                finviz_key = user_settings['api_keys'].get('finviz')

                                if finviz_key and finviz_key.strip():
                                    print("\n💎 FINVIZ MULTI-TIMEFRAME PERFORMANCE")
                                    print("=" * 100)

                                    provider = FinVizCryptoProvider(finviz_key.strip())
                                    # Normalize ticker (BTC-USD -> BTC)
                                    ticker_short = ticker.replace('-USD', '').replace('USD', '').upper()
                                    perf = provider.get_performance_for_ticker(ticker_short)

                                    if perf:
                                        # Display performance data
                                        print(f"   5 Min:          {perf.get('perf_5min', 'N/A'):>+7}%")
                                        print(f"   1 Hour:         {perf.get('perf_hour', 'N/A'):>+7}%")
                                        print(f"   1 Day:          {perf.get('perf_day', 'N/A'):>+7}%")
                                        print(f"   1 Week:         {perf.get('perf_week', 'N/A'):>+7}%")
                                        print(f"   1 Month:        {perf.get('perf_month', 'N/A'):>+7}%")
                                        print(f"   Quarter:        {perf.get('perf_quarter', 'N/A'):>+7}%")
                                        print(f"   Half Year:      {perf.get('perf_half', 'N/A'):>+7}%")
                                        print(f"   YTD:            {perf.get('perf_ytd', 'N/A'):>+7}%")
                                        print(f"   1 Year:         {perf.get('perf_year', 'N/A'):>+7}%")

                                        # Multi-timeframe trend analysis
                                        print(f"\n📈 MULTI-TIMEFRAME TREND ANALYSIS")

                                        # Calculate averages (excluding YTD as it's variable)
                                        short_term = [perf.get('perf_5min', 0), perf.get('perf_hour', 0), perf.get('perf_day', 0)]
                                        short_avg = sum(short_term) / len([x for x in short_term if x]) if any(short_term) else 0

                                        mid_term = [perf.get('perf_week', 0), perf.get('perf_month', 0)]
                                        mid_avg = sum(mid_term) / len([x for x in mid_term if x]) if any(mid_term) else 0

                                        long_term = [perf.get('perf_quarter', 0), perf.get('perf_half', 0), perf.get('perf_year', 0)]
                                        long_avg = sum(long_term) / len([x for x in long_term if x]) if any(long_term) else 0

                                        print(f"   Short-term (5min-day): {short_avg:+.1f}% avg")
                                        print(f"   Mid-term (week-month): {mid_avg:+.1f}% avg")
                                        print(f"   Long-term (qtr-year):  {long_avg:+.1f}% avg")

                                        # Momentum assessment
                                        if short_avg > 0 and mid_avg > 0:
                                            print(f"\n   ✅ Positive momentum across timeframes")
                                        elif short_avg > 0 > mid_avg:
                                            print(f"\n   ⚠️  Short-term bounce in longer downtrend")
                                        elif short_avg < 0 < mid_avg:
                                            print(f"\n   ⚠️  Short-term pullback in longer uptrend")
                                        else:
                                            print(f"\n   ❌ Negative momentum across timeframes")
                                    else:
                                        print(f"\n💎 FinViz Multi-timeframe: {ticker_short} not in top 20 cryptos")
                        except Exception as fv_error:
                            pass  # FinViz not available or error

                except Exception as insider_error:
                    print(f"\n⚠️  Could not fetch insider trading data: {insider_error}")

            else:
                print(f"❌ Failed to analyze {ticker}")

            # Pause between tickers
            if i < len(tickers):
                input("\nPress Enter to continue to next ticker...")

        except KeyboardInterrupt:
            print("\n\nAnalysis cancelled by user.")
            break
        except Exception as e:
            print(f"❌ Error analyzing {ticker}: {e}")
            continue


def run_darkflow_scan():
    """Run Dark Flow institutional activity scan"""
    print("\n" + "=" * 100)
    print("🌊 DARK FLOW SCANNER - Institutional Accumulation Detection")
    print("=" * 100)
    print("\nDark Flow detects:")
    print("  • Volume clusters (institutional accumulation levels)")
    print("  • Unusual volume spikes (smart money entry)")
    print("  • Price consolidation near institutional levels")
    print("  • Gap patterns being filled by institutions")
    print("=" * 100)

    # Options menu
    print("\nOptions:")
    print("1. Scan entire market for Dark Flow signals")
    print("2. Analyze specific tickers")
    print("3. Scan major ETFs (SPY, QQQ, IWM, DIA)")

    choice = input("\nEnter choice (1-3): ").strip()

    darkflow = create_darkflow_scanner()
    from .core.scanner import ScanParameters, ScanMode

    try:
        if choice == '1':
            # Market-wide scan
            print("\nSelect market:")
            print("1. US Stocks (NASDAQ + NYSE) - RECOMMENDED")
            print("2. NASDAQ only")
            print("3. NYSE only")
            market = input("Enter choice (1-3): ").strip()

            if market == '2':
                market_choice = '4'
            elif market == '3':
                market_choice = '5'
            else:
                market_choice = '1'

            # Price range
            print("\nPrice range (default $5-$100):")
            min_input = input("Min price (or Enter for $5): ").strip()
            max_input = input("Max price (or Enter for $100): ").strip()

            min_price = float(min_input) if min_input else 5.0
            max_price = float(max_input) if max_input else 100.0

            # Build parameters
            params = ScanParameters(
                market_choice=market_choice,
                min_price=min_price,
                max_price=max_price,
                mode=ScanMode.SMART
            )

            print(f"\n{'=' * 100}")
            print("SCANNING MARKET FOR DARK FLOW SIGNALS...")
            print(f"{'=' * 100}")

            # Scan market (no ticker list = market scan)
            results = darkflow.scan(params, ticker_list=None)

        elif choice == '3':
            # Major ETFs
            ticker_list = ['SPY', 'QQQ', 'IWM', 'DIA']
            print(f"\n✅ Analyzing major ETFs for Dark Flow signals...")

            params = ScanParameters()
            results = darkflow.scan(params, ticker_list=ticker_list)

        else:
            # Specific tickers
            ticker_input = input("\nEnter tickers (comma-separated): ").strip().upper()
            if not ticker_input:
                print("❌ No tickers provided")
                return

            ticker_list = [t.strip() for t in ticker_input.split(',')]
            print(f"\n✅ Analyzing {len(ticker_list)} tickers for Dark Flow...")

            params = ScanParameters()
            results = darkflow.scan(params, ticker_list=ticker_list)

        # Display results
        if results:
            display_results(results)

            # Enhanced summary with Dark Flow scores
            print(f"\n🌊 DARK FLOW SUMMARY")
            print(f"{'=' * 50}")
            print(f"Total stocks with signals:  {len(results)}")

            # Count by bias
            bullish = sum(1 for r in results if 'BULLISH' in r.catalyst)
            bearish = len(results) - bullish
            print(f"Bullish bias:               {bullish} (🟢)")
            print(f"Bearish bias:               {bearish} (🔴)")

            # Score distribution
            strong = sum(1 for r in results if hasattr(r, 'dark_flow_score') and r.dark_flow_score >= 80)
            moderate = sum(1 for r in results if hasattr(r, 'dark_flow_score') and 60 <= r.dark_flow_score < 80)
            weak = len(results) - strong - moderate

            print(f"\nSignal strength:")
            print(f"  🔥🔥🔥 Strong (80+):      {strong}")
            print(f"  🔥🔥 Moderate (60-79):    {moderate}")
            print(f"  🔥 Weak (50-59):          {weak}")
            print(f"{'=' * 50}\n")

            print("💡 Volume clusters show where institutions are accumulating/distributing")
            print("🌊 Look for tight consolidation + volume clusters = potential breakout\n")

            # Handle scan results with export and ticker selection
            # Skip initial display since we already showed Dark Flow-specific display
            handle_scan_results(results, scan_type='darkflow', skip_initial_display=True)
        else:
            print("\n✅ No significant Dark Flow signals detected")
            print("   This could mean:")
            print("   • No unusual institutional activity in current market conditions")
            print("   • Try different price range or market segment")
            print("   • Check during market hours for best results")

    except KeyboardInterrupt:
        print("\n\nDark Flow scan cancelled by user.")
    except Exception as e:
        print(f"\n❌ Dark Flow scan error: {e}")
        import traceback
        traceback.print_exc()


def view_cache_status(cache):
    """View cache status"""
    print("\n" + "=" * 80)
    print("CACHE STATUS")
    print("=" * 80)

    status = cache.get_status()

    for name, info in status.items():
        print(f"\n{name}:")
        if 'error' in info:
            print(f"  ❌ {info['error']}")
        else:
            print(f"  Entries: {info['entries']}")
            print(f"  TTL: {info['ttl_minutes']:.1f} minutes")
            print(f"  File: {info['file']}")

    print("\n" + "=" * 80)


def clear_cache(cache):
    """Clear cache"""
    print("\n" + "=" * 80)
    print("CLEAR CACHE")
    print("=" * 80)

    print("\n1. Clear all caches")
    print("2. Clear scan results only")
    print("3. Clear micro-cap list only")
    print("q. Cancel")

    choice = input("\nEnter choice: ").strip()

    if choice == '1':
        cache.clear()
        print("\n✅ All caches cleared")
    elif choice == '2':
        cache.clear('scan_results')
        print("\n✅ Scan results cache cleared")
    elif choice == '3':
        cache.clear('microcap_list')
        print("\n✅ Micro-cap list cache cleared")
    else:
        print("\nCancelled")


def view_settings():
    """View current settings"""
    print("\n" + "=" * 80)
    print("CURRENT SETTINGS")
    print("=" * 80)

    settings_info = get_settings_info()

    print(f"\nSettings File: {settings_info['settings_file']}")
    print(f"Exists: {'✅ Yes' if settings_info['exists'] else '❌ No (using defaults)'}")

    print(f"\n📦 Cache Settings:")
    for key, value in settings_info['cache_settings'].items():
        print(f"  {key}: {value} seconds ({value/60:.1f} minutes)")

    print(f"\n⚡ Rate Limit:")
    for key, value in settings_info['rate_limit'].items():
        print(f"  {key}: {value}")

    print(f"\n🎯 5 Pillars Thresholds:")
    for pillar, config in settings_info['pillars'].items():
        if 'threshold' in config:
            print(f"  {pillar}: {config['threshold']}")
        else:
            print(f"  {pillar}: min={config.get('min', 'N/A')}, max={config.get('max', 'N/A')}")

    print(f"\n📊 Display:")
    print(f"  Min Score: {settings_info['min_score']}")
    print(f"  Max Results: {settings_info['max_results_display']}")

    print(f"\n📈 Trading Preferences:")
    from .config import TRADING_STYLES
    style_key = settings_info.get('trading_style', 'day_trader')
    style_info = TRADING_STYLES.get(style_key, TRADING_STYLES['day_trader'])
    rr_ratio = settings_info.get('rr_ratio', 2.0)
    print(f"  Style: {style_info['name']}")
    print(f"  Duration: {style_info['typical_duration']}")
    print(f"  R:R Ratio: 1:{rr_ratio:.1f}")

    print(f"\n🔑 API Keys:")
    for key, status in settings_info.get('api_keys', {}).items():
        print(f"  {key}: {status}")

    print("\n" + "=" * 80)


def edit_settings():
    """Edit settings interactively"""
    # Load current settings
    current_settings = load_user_settings()

    # If no settings file, create default first
    if not current_settings:
        print("\n⚠️  No settings file found. Creating default settings first...")
        if not create_default_settings_file():
            print("❌ Failed to create settings file")
            return
        current_settings = load_user_settings()

    # Interactive editor
    updated_settings = edit_settings_interactive(current_settings)

    if updated_settings is not None:
        # Save changes
        if save_user_settings(updated_settings):
            print("\n✅ Settings saved successfully!")
            print("   Restart the application to apply changes.")
        else:
            print("\n❌ Failed to save settings")
    else:
        print("\n   No changes made")


def create_settings_file():
    """Create default settings file"""
    print("\n" + "=" * 80)
    print("CREATE SETTINGS FILE")
    print("=" * 80)

    settings_info = get_settings_info()

    if settings_info['exists']:
        print(f"\n⚠️  Settings file already exists: {settings_info['settings_file']}")
        overwrite = input("Overwrite with defaults? (yes/no): ").strip().lower()
        if overwrite != 'yes':
            print("Cancelled")
            return

    if create_default_settings_file():
        print(f"\n✅ Settings file created successfully!")
        print(f"   Location: {settings_info['settings_file']}")
        print(f"\n💡 Edit this file to customize:")
        print(f"   • Cache durations")
        print(f"   • Rate limiting")
        print(f"   • 5 Pillars thresholds")
        print(f"   • Display options")
        print(f"\n   Restart the application to load new settings.")
    else:
        print(f"\n❌ Failed to create settings file")


def view_previous_scan_results():
    """View and work with previous scan results"""
    print("\n" + "=" * 80)
    print("📋 PREVIOUS SCAN RESULTS")
    print("=" * 80)

    # Check if any scans are available
    available_scans = []
    for scan_type, scan_data in PREVIOUS_SCANS.items():
        if scan_data:
            available_scans.append((scan_type, scan_data))

    if not available_scans:
        print("\n❌ No previous scan results available.")
        print("   Run a scan first (Momentum, Dark Flow, or Pressure Cooker).")
        input("\nPress Enter to continue...")
        return

    # Show available scans
    print("\nAvailable scans:")
    for i, (scan_type, scan_data) in enumerate(available_scans, 1):
        timestamp = scan_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        result_count = len(scan_data['results'])
        scan_name = {
            'momentum': '🔥 Momentum Scan (5 Pillars)',
            'darkflow': '🌊 Dark Flow (Institutional Activity)',
            'pressurecooker': '🎯 Pressure Cooker (Short Squeeze)'
        }.get(scan_type, scan_type)
        print(f"{i}. {scan_name}")
        print(f"   Time: {timestamp} | Results: {result_count} tickers")

    # Select scan
    choice = input(f"\nSelect scan to view (1-{len(available_scans)}) or 'q' to go back: ").strip().lower()

    if choice == 'q':
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(available_scans):
            scan_type, scan_data = available_scans[idx]
            results = scan_data['results']

            print(f"\n{'=' * 80}")
            print(f"Loading {scan_type} scan results...")
            print(f"{'=' * 80}")

            # Handle the scan results (export, ticker selection, analysis)
            handle_scan_results(results, scan_type=scan_type)
        else:
            print("❌ Invalid selection")
    except ValueError:
        print("❌ Invalid input")


def run_pressure_cooker_scan():
    """Run Pressure Cooker short squeeze scanner"""
    # Load current settings
    current_settings = load_user_settings()

    # Show Pressure Cooker specific disclaimer
    accepted, updated_settings = show_pressure_cooker_disclaimer(current_settings)

    if not accepted:
        return

    # Save updated settings if disclaimer was newly acknowledged
    if updated_settings.get('pressure_cooker_disclaimer_acknowledged'):
        if not current_settings or not current_settings.get('pressure_cooker_disclaimer_acknowledged'):
            save_user_settings(updated_settings)

    print("\n" + "=" * 100)
    print("🔥 PRESSURE COOKER - SHORT SQUEEZE SCANNER")
    print("=" * 100)
    print("\nOptions:")
    print("1. Scan market for squeeze setups")
    print("2. Analyze specific ticker")
    print("q. Back to main menu")

    choice = input("\nEnter choice: ").strip()

    if choice == 'q':
        return

    elif choice == '2':
        # Analyze specific ticker
        ticker = input("\nEnter ticker to analyze: ").strip().upper()
        if not ticker:
            print("❌ No ticker provided")
            return

        print(f"\n🔍 Analyzing {ticker} for short squeeze potential...")

        scanner = create_enhanced_pressure_cooker_scanner()
        result = scanner.analyze_ticker(ticker)

        if result:
            display_pressure_cooker_details(result)
        else:
            print(f"\n❌ Could not analyze {ticker}")
            print("   Possible reasons:")
            print("   • Ticker not found")
            print("   • Insufficient data")
            print("   • Does not meet minimum criteria")

    else:
        # Market scan
        # Get scan parameters (stocks only)
        params = build_pressure_cooker_parameters()

        if params is None:
            print("\nScan cancelled.")
            return

        try:
            # Create scanner and run scan
            print("\n⚠️  This may take several minutes - analyzing candidates for squeeze potential...")

            scanner = create_enhanced_pressure_cooker_scanner()

            # Apply custom price range from user input
            scanner.min_price = params.min_price
            scanner.max_price = params.max_price

            start_time = datetime.now()

            results = scanner.scan_market(params, max_candidates=100)

            duration = (datetime.now() - start_time).total_seconds()

            # Save to database
            db = get_database_manager()
            scan_metadata = {
                'scan_mode': params.mode.value if hasattr(params.mode, 'value') else 'smart',
                'market_choice': params.market_choice,
                'total_candidates': 100,
                'min_price': params.min_price,
                'max_price': params.max_price,
                'duration_seconds': duration,
                'criteria': {
                    'min_float': scanner.min_float,
                    'max_float': scanner.max_float,
                    'min_rel_vol': scanner.min_rel_vol,
                    'min_short_interest': scanner.min_short_interest
                }
            }
            db.save_scan_results(results, 'pressure_cooker', scan_metadata)

            # Display results
            display_pressure_cooker_results(results)

            if not results:
                return

            # Handle scan results with export and ticker selection
            # Skip initial display since we already showed Pressure Cooker-specific display
            handle_scan_results(results, scan_type='pressurecooker', skip_initial_display=True)

        except KeyboardInterrupt:
            print("\n\nScan cancelled by user.")
        except Exception as e:
            print(f"\n❌ Scan error: {e}")
            import traceback
            traceback.print_exc()


def analyze_single_ticker():
    """Analyze a single ticker with comprehensive technical analysis"""
    from .config import DEFAULT_TRADING_STYLE, DEFAULT_RR_RATIO, TRADING_STYLES
    import yfinance as yf
    import pandas as pd

    print("\n" + "=" * 100)
    print("📈 SINGLE TICKER ANALYSIS")
    print("=" * 100)

    # Get ticker input
    ticker_input = input("\nEnter ticker symbol (e.g., AAPL, BTC, DOGE): ").strip()
    ticker = normalize_ticker(ticker_input)  # Auto-add -USD for crypto

    if not ticker:
        print("❌ No ticker entered")
        return

    try:
        print(f"\n🔍 Analyzing {ticker}...")
        stock = yf.Ticker(ticker)

        # Get trading style settings
        style_config = TRADING_STYLES[DEFAULT_TRADING_STYLE]
        rr_ratio = DEFAULT_RR_RATIO

        # Fetch data with pre-market and after-hours for chart display
        info = stock.info
        hist = stock.history(period=style_config['chart_period'], interval=style_config['chart_interval'], prepost=True)

        if hist.empty:
            print(f"❌ No data available for {ticker}")
            return

        # Current price and basic info
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        change = current_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close > 0 else 0

        # Check if current price is from extended hours
        import datetime
        last_timestamp = hist.index[-1]
        is_extended_hours = False
        extended_label = ""

        if hasattr(last_timestamp, 'hour'):
            hour = last_timestamp.hour
            # Market hours are 9:30 AM - 4:00 PM EST (14:30 - 21:00 UTC typically)
            if hour < 14 or hour >= 21:
                is_extended_hours = True
                if hour < 14:
                    extended_label = " [PRE-MARKET]"
                else:
                    extended_label = " [AFTER-HOURS]"

        # Volume analysis - use stock.info for actual day's volume (not last candle)
        # This fixes issue with 0 volume showing for intraday charts after hours
        current_volume = info.get('volume') or info.get('regularMarketVolume', 0)
        avg_volume = info.get('averageVolume') or info.get('averageVolume10days', 0)

        # Fallback to historical data if info doesn't have volume
        if current_volume == 0:
            current_volume = hist['Volume'].iloc[-1]
        if avg_volume == 0:
            avg_volume = hist['Volume'].tail(20).mean()

        rel_vol = current_volume / avg_volume if avg_volume > 0 else 0.0

        # Price analysis
        day_high = hist['High'].iloc[-1]
        day_low = hist['Low'].iloc[-1]
        week_high = hist['High'].tail(5).max()
        week_low = hist['Low'].tail(5).min()

        # Support/Resistance
        recent_data = hist.tail(20)
        support = float(recent_data['Low'].min())
        resistance = float(recent_data['High'].max())

        # Calculate R:R levels
        risk = current_price - support
        reward = risk * rr_ratio
        target = current_price + reward

        # Display analysis
        print("\n" + "=" * 100)
        print(f"📊 {ticker} - {info.get('longName', ticker)}")
        print("=" * 100)

        # Price Section
        print(f"\n💰 PRICE INFORMATION")
        print(f"   Current:        ${current_price:.2f}{extended_label}")
        if is_extended_hours:
            # Try to get regular hours close
            regular_close = info.get('regularMarketPreviousClose', info.get('previousClose'))
            if regular_close:
                ext_change = current_price - regular_close
                ext_change_pct = (ext_change / regular_close * 100) if regular_close > 0 else 0
                print(f"   Regular Close:  ${regular_close:.2f}")
                print(f"   Extended Move:  ${ext_change:+.2f} ({ext_change_pct:+.2f}%)")
        print(f"   Change:         ${change:+.2f} ({change_pct:+.2f}%)")
        print(f"   Day Range:      ${day_low:.2f} - ${day_high:.2f}")
        print(f"   Week Range:     ${week_low:.2f} - ${week_high:.2f}")

        # Volume Section
        print(f"\n📊 VOLUME ANALYSIS")
        print(f"   Current Volume: {current_volume:,.0f}")
        print(f"   Avg Volume:     {avg_volume:,.0f}")
        print(f"   Relative Vol:   {rel_vol:.2f}x")

        # Technical Levels
        print(f"\n📈 TECHNICAL LEVELS")
        print(f"   Support:        ${support:.2f}")
        print(f"   Resistance:     ${resistance:.2f}")
        print(f"   Range:          ${resistance - support:.2f}")

        # R:R Analysis
        print(f"\n🎯 RISK/REWARD ANALYSIS (1:{rr_ratio:.1f})")
        print(f"   Entry:          ${current_price:.2f}")
        print(f"   Stop Loss:      ${support:.2f}")
        print(f"   Target:         ${target:.2f}")
        print(f"   Risk:           ${risk:.2f}")
        print(f"   Reward:         ${reward:.2f}")

        # Additional Info
        if info.get('marketCap'):
            market_cap = info['marketCap'] / 1_000_000_000
            print(f"\n💼 COMPANY INFO")
            print(f"   Market Cap:     ${market_cap:.2f}B")
            if info.get('floatShares'):
                float_shares = info['floatShares'] / 1_000_000
                print(f"   Float:          {float_shares:.2f}M shares")
            if info.get('sector'):
                print(f"   Sector:         {info['sector']}")
            if info.get('industry'):
                print(f"   Industry:       {info['industry']}")

        # Technical Indicators
        print(f"\n📉 TECHNICAL INDICATORS")

        # Calculate MACD
        try:
            exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
            exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            macd_current = macd.iloc[-1]
            signal_current = signal.iloc[-1]
            macd_cross = "BULLISH ✅" if macd_current > signal_current else "BEARISH ⚠️"
            print(f"   MACD:           {macd_current:.2f} / {signal_current:.2f} - {macd_cross}")
        except:
            pass

        # Calculate RSI
        try:
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_current = rsi.iloc[-1]
            rsi_signal = "OVERSOLD 🟢" if rsi_current < 30 else "OVERBOUGHT 🔴" if rsi_current > 70 else "NEUTRAL"
            print(f"   RSI(14):        {rsi_current:.2f} - {rsi_signal}")
        except:
            pass

        # Calculate VWAP
        try:
            typical_price = (hist['High'] + hist['Low'] + hist['Close']) / 3
            vwap = (typical_price * hist['Volume']).cumsum() / hist['Volume'].cumsum()
            vwap_current = vwap.iloc[-1]
            vwap_signal = "ABOVE VWAP ✅" if current_price > vwap_current else "BELOW VWAP ⚠️"
            print(f"   VWAP:           ${vwap_current:.2f} - {vwap_signal}")
        except:
            pass

        # Moving Averages - calculated from SAME timeframe as chart
        # For day traders: SMAs from 5-min candles, for swing traders: from daily, etc.
        try:
            sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else None
            sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else None
            sma_200 = hist['Close'].rolling(window=200).mean().iloc[-1] if len(hist) >= 200 else None

            # Show timeframe context
            timeframe_label = f"{style_config['chart_interval']}" if style_config['chart_interval'] != '1d' else 'daily'

            if sma_20:
                print(f"   SMA(20):        ${sma_20:.2f} ({timeframe_label}) - {'ABOVE ✅' if current_price > sma_20 else 'BELOW ⚠️'}")
            if sma_50:
                print(f"   SMA(50):        ${sma_50:.2f} ({timeframe_label}) - {'ABOVE ✅' if current_price > sma_50 else 'BELOW ⚠️'}")
            if sma_200:
                print(f"   SMA(200):       ${sma_200:.2f} ({timeframe_label}) - {'ABOVE ✅' if current_price > sma_200 else 'BELOW ⚠️'}")
            elif len(hist) < 200:
                print(f"   SMA(200):       Not enough data ({len(hist)} {timeframe_label} candles)")

            # Golden Cross / Death Cross detection
            if sma_20 and sma_200:
                if sma_20 > sma_200:
                    print(f"   Trend:          GOLDEN CROSS 🌟 (SMA 20 > SMA 200) - Bullish")
                else:
                    print(f"   Trend:          DEATH CROSS ⚰️  (SMA 20 < SMA 200) - Bearish")
        except Exception as e:
            print(f"   ⚠️  Could not calculate SMAs: {str(e)}")
            pass

        print("\n" + "=" * 100)

        # Offer chart display
        print("\nOptions:")
        print("1. View ASCII chart")
        print("2. Back to main menu")

        choice = input("\nEnter choice: ").strip()

        if choice == '1':
            chart_gen = ASCIIChartGenerator()
            sr_levels = {
                'nearest_support': support,
                'nearest_resistance': resistance
            }

            chart_gen.plot_price_chart(
                hist,
                ticker,
                sr_levels=sr_levels,
                rr_ratio=rr_ratio
            )
            input("\nPress Enter to continue...")

    except Exception as e:
        print(f"\n❌ Error analyzing {ticker}: {e}")
        import traceback
        traceback.print_exc()


def view_database_statistics():
    """View database statistics and historical performance"""
    print("\n" + "=" * 80)
    print("📊 DATABASE STATISTICS")
    print("=" * 80)

    db = get_database_manager()
    info = db.get_database_info()

    print(f"\n📁 Database File:")
    print(f"   Location: {info['path']}")
    print(f"   Size: {info['size_mb']:.2f} MB")

    print(f"\n📊 Table Row Counts:")
    for table, count in info['tables'].items():
        print(f"   {table}: {count:,} rows")

    # Get scan statistics
    print("\n" + "=" * 80)
    print("Options:")
    print("1. View 7-day statistics")
    print("2. View 30-day statistics")
    print("3. View 90-day statistics")
    print("4. View top performing tickers")
    print("5. Clean up old data (>90 days)")
    print("q. Back")

    choice = input("\nEnter choice: ").strip()

    if choice == 'q':
        return

    days_map = {'1': 7, '2': 30, '3': 90}
    days = days_map.get(choice, 30)

    if choice in ['1', '2', '3']:
        stats = db.get_scan_statistics(days=days)

        print(f"\n📈 STATISTICS (Last {days} days)")
        print("=" * 80)
        print(f"Total scans run: {stats['total_scans']}")
        print(f"Total results found: {stats['total_results']}")
        print(f"Average results per scan: {stats['avg_results_per_scan']:.1f}")

        print(f"\nScans by type:")
        for scan_type, count in stats['scans_by_type'].items():
            print(f"  {scan_type}: {count}")

        print(f"\nResults by type:")
        for scan_type, count in stats['results_by_type'].items():
            print(f"  {scan_type}: {count}")

        print(f"\nTop scoring tickers:")
        for item in stats['top_tickers']:
            print(f"  {item['ticker']}: max score {item['max_score']}, appeared {item['appearances']} times")

    elif choice == '4':
        # Top performers
        results = db.get_recent_results(days=30, min_score=80)
        print(f"\n🏆 TOP PERFORMERS (Last 30 days, score ≥80)")
        print("=" * 80)
        for result in results[:20]:
            print(f"{result['ticker']}: {result['score']} ({result['scan_type']}) on {result['scan_date']}")

    elif choice == '5':
        # Cleanup
        confirm = input("\n⚠️  Delete all data older than 90 days? (yes/no): ").strip().lower()
        if confirm == 'yes':
            deleted = db.cleanup_old_data(days=90)
            print(f"\n✅ Cleanup complete:")
            print(f"   Scan results deleted: {deleted['results_deleted']}")
            print(f"   Scan history deleted: {deleted['history_deleted']}")
            print(f"   Performance records deleted: {deleted['performance_deleted']}")
        else:
            print("\nCancelled")


def manage_watchlist():
    """Manage ticker watchlist"""
    db = get_database_manager()

    while True:
        print("\n" + "=" * 80)
        print("👁️  WATCHLIST MANAGEMENT")
        print("=" * 80)

        # Get watchlist
        watchlist = db.get_watchlist()

        if watchlist:
            print(f"\nCurrent watchlist ({len(watchlist)} tickers):")
            print("-" * 80)
            print(f"{'Ticker':<10} {'Status':<12} {'Score':<8} {'Appeared':<10} {'Last Seen':<12}")
            print("-" * 80)

            for item in watchlist[:20]:
                print(f"{item['ticker']:<10} {item['status']:<12} "
                      f"{item['highest_score'] if item['highest_score'] else 'N/A':<8} "
                      f"{item['times_appeared']:<10} "
                      f"{item['last_seen'] if item['last_seen'] else 'Never':<12}")
        else:
            print("\n📋 Watchlist is empty")

        print("\n" + "=" * 80)
        print("Options:")
        print("1. Add ticker to watchlist")
        print("2. Remove ticker from watchlist")
        print("3. Update ticker status")
        print("4. View ticker history")
        print("q. Back to main menu")

        choice = input("\nEnter choice: ").strip()

        if choice == 'q':
            break

        elif choice == '1':
            # Add ticker
            ticker = input("\nEnter ticker to add: ").strip().upper()
            notes = input("Notes (optional): ").strip()

            if db.add_to_watchlist(ticker, notes if notes else None):
                print(f"\n✅ Added {ticker} to watchlist")
            else:
                print(f"\n⚠️  {ticker} is already on the watchlist")

        elif choice == '2':
            # Remove ticker
            ticker = input("\nEnter ticker to remove: ").strip().upper()

            if db.remove_from_watchlist(ticker):
                print(f"\n✅ Removed {ticker} from watchlist")
            else:
                print(f"\n❌ {ticker} not found in watchlist")

        elif choice == '3':
            # Update status
            ticker = input("\nEnter ticker: ").strip().upper()
            print("\nStatus options: watching, bought, sold, passed")
            status = input("New status: ").strip().lower()
            notes = input("Update notes (optional): ").strip()

            if db.update_watchlist_status(ticker, status, notes if notes else None):
                print(f"\n✅ Updated {ticker} status to '{status}'")
            else:
                print(f"\n❌ {ticker} not found in watchlist")

        elif choice == '4':
            # View history
            ticker = input("\nEnter ticker: ").strip().upper()
            history = db.get_ticker_history(ticker, days=90)

            if history:
                print(f"\n📊 HISTORY: {ticker} (Last 90 days)")
                print("-" * 80)
                print(f"{'Date':<12} {'Type':<20} {'Score':<8} {'Price':<10} {'RelVol':<8}")
                print("-" * 80)

                for item in history[:20]:
                    print(f"{item['scan_date']:<12} {item['scan_type']:<20} "
                          f"{item['score']:<8} ${item['price']:<9.2f} {item['rel_vol']:<8.1f}x")
            else:
                print(f"\n❌ No history found for {ticker}")


def offer_export_options(results: List[ScanResult], scanner_type: str = 'scan'):
    """Offer to export results to CSV/Excel/PDF"""
    if not results:
        return

    print("\n" + "=" * 80)
    print("📤 EXPORT OPTIONS")
    print("=" * 80)
    print("\n1. Export to CSV")
    print("2. Export to Excel (with formatting)")
    print("3. Export to PDF report")
    print("4. Export to all formats")
    print("5. Skip export")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == '5':
        return

    exporter = ResultExporter()

    # Convert ScanResult objects to dicts for export
    results_dicts = []
    for r in results:
        result_dict = {
            'ticker': r.ticker,
            'price': r.price,
            'score': r.score,
            'rel_vol': r.rel_vol,
            'float_m': r.float_m,
            'change_pct': r.change_pct,
            'catalyst': r.catalyst,
            'description': r.description,
            'source': r.source,
            'volume': r.volume
        }
        # Add scanner-specific fields if available
        if hasattr(r, 'grade'):
            result_dict['grade'] = r.grade
        if hasattr(r, 'setup_stage'):
            result_dict['setup_stage'] = r.setup_stage
        if hasattr(r, 'short_percent'):
            result_dict['short_percent'] = r.short_percent
        if hasattr(r, 'key_factors'):
            result_dict['key_factors'] = ', '.join(r.key_factors) if r.key_factors else ''

        results_dicts.append(result_dict)

    try:
        if choice == '1':
            exporter.export_to_csv(results_dicts, scanner_type=scanner_type)
        elif choice == '2':
            exporter.export_to_excel(results_dicts, scanner_type=scanner_type)
        elif choice == '3':
            exporter.export_to_pdf(results_dicts, scanner_type=scanner_type)
        elif choice == '4':
            exporter.export_all_formats(results_dicts, scanner_type=scanner_type)
        else:
            print("\nSkipping export")
    except Exception as e:
        print(f"\n❌ Export error: {e}")


def offer_chart_display(tickers: List[str]):
    """Offer to display ASCII charts for selected tickers"""
    if not tickers:
        return

    from .config import DEFAULT_TRADING_STYLE, DEFAULT_RR_RATIO, TRADING_STYLES

    print("\n" + "=" * 80)
    print("📊 CHART DISPLAY OPTIONS")
    print("=" * 80)
    print("\n1. Show ASCII charts for selected tickers")
    print("2. Skip charts")

    choice = input("\nEnter choice (1-2): ").strip()

    if choice != '1':
        return

    try:
        import yfinance as yf
        chart_gen = ASCIIChartGenerator()

        # Get trading style settings
        style_config = TRADING_STYLES[DEFAULT_TRADING_STYLE]
        chart_period = style_config['chart_period']
        rr_ratio = DEFAULT_RR_RATIO

        print(f"\n📋 Using {style_config['name']} settings:")
        print(f"   Period: {chart_period} | Interval: {style_config['chart_interval']} | R:R: 1:{rr_ratio:.1f}")

        for ticker in tickers:
            print(f"\n{'=' * 100}")
            print(f"📈 CHART: {ticker}")
            print(f"{'=' * 100}")

            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=chart_period, interval=style_config['chart_interval'], prepost=True)

                if not hist.empty:
                    # Calculate basic S/R levels from price data
                    sr_levels = None
                    try:
                        # Simple S/R: use recent high/low as resistance/support
                        recent_data = hist.tail(20)  # Last 20 periods
                        if len(recent_data) > 0:
                            sr_levels = {
                                'nearest_support': float(recent_data['Low'].min()),
                                'nearest_resistance': float(recent_data['High'].max())
                            }
                    except:
                        pass  # If S/R calculation fails, chart will work without it

                    chart_gen.plot_price_chart(
                        hist,
                        ticker,
                        sr_levels=sr_levels,
                        rr_ratio=rr_ratio
                    )
                else:
                    print(f"❌ No data available for {ticker}")

            except Exception as e:
                print(f"❌ Error displaying chart for {ticker}: {e}")

            if len(tickers) > 1 and ticker != tickers[-1]:
                input("\nPress Enter to continue to next chart...")

    except Exception as e:
        print(f"\n❌ Chart display error: {e}")


if __name__ == '__main__':
    main()
