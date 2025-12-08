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
    display_technical_analysis
)
from .core.analysis import analyze_ticker
from .core.scanner import ScanParameters, ScanMode, ScanResult
from .scanners.momentum import create_scanner
from .scanners.darkflow import create_darkflow_scanner
from .scanners.pressurecooker_enhanced import create_enhanced_pressure_cooker_scanner
from .data.cache import get_cache_manager
from .data.database import get_database_manager
from .config import (
    VERSION, load_user_settings, apply_user_settings, save_user_settings,
    create_default_settings_file, get_settings_info
)
from .utils import (
    ResultExporter,
    ASCIIChartGenerator
)


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
            # View database statistics
            view_database_statistics()

        elif choice == '5':
            # Manage watchlist
            manage_watchlist()

        elif choice == '6':
            # View cache status
            view_cache_status(cache)

        elif choice == '7':
            # Clear cache
            clear_cache(cache)

        elif choice == '8':
            # View settings
            view_settings()

        elif choice == '9':
            # Edit settings
            edit_settings()

        elif choice == '0':
            # Create default settings file
            create_settings_file()

        elif choice == 'q':
            print("\nGoodbye!")
            break

        else:
            print("❌ Invalid choice. Please try again.")

        input("\nPress Enter to continue...")


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

        # Display results
        display_results(results)
        display_summary(results)

        if not results:
            return

        # Export options removed for cleaner workflow
        # User can manually export if needed via menu option

        # Clear separator before ticker selection
        print("\n" + "=" * 80)
        print("📊 TICKER SELECTION FOR DETAILED ANALYSIS")
        print("=" * 80)

        # Prompt for ticker selection for technical analysis
        selected = prompt_ticker_selection(results)
        if selected:
            print(f"\n✅ Selected: {', '.join(selected)}")

            # Offer chart display
            offer_chart_display(selected)

            # Technical analysis
            analyze_selected_tickers(selected)

    except KeyboardInterrupt:
        print("\n\nScan cancelled by user.")
    except Exception as e:
        print(f"\n❌ Scan error: {e}")
        import traceback
        traceback.print_exc()


def analyze_selected_tickers(tickers):
    """Analyze selected tickers with technical indicators"""
    print(f"\n{'=' * 100}")
    print(f"TECHNICAL ANALYSIS")
    print(f"{'=' * 100}")
    print(f"Analyzing {len(tickers)} ticker(s)...")

    for i, ticker in enumerate(tickers, 1):
        print(f"\n[{i}/{len(tickers)}] Analyzing {ticker}...")

        try:
            analysis = analyze_ticker(ticker)

            if analysis:
                display_technical_analysis(analysis)
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

            # Offer export options
            offer_export_options(results, scanner_type='darkflow')

            # Clear separator
            print("\n" + "=" * 80)

            # Show detailed Dark Flow analysis for top results
            show_detailed = input("Show detailed Dark Flow analysis for top stocks? (yes/no): ").strip().lower()

            if show_detailed == 'yes':
                top_results = results[:5]  # Top 5
                for i, result in enumerate(top_results, 1):
                    if hasattr(result, 'dark_flow_analysis'):
                        display_dark_flow_analysis(result.dark_flow_analysis)
                        if i < len(top_results):
                            input("\nPress Enter to continue to next stock...")

            # Prompt for technical analysis
            print("\n" + "=" * 80)
            print("📊 TICKER SELECTION FOR DETAILED ANALYSIS")
            print("=" * 80)
            selected = prompt_ticker_selection(results)
            if selected:
                print(f"\n✅ Selected: {', '.join(selected)}")

                # Offer chart display
                offer_chart_display(selected)

                # Technical analysis
                analyze_selected_tickers(selected)
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


def display_dark_flow_analysis(analysis: Dict):
    """Display detailed Dark Flow analysis for a ticker"""
    print("\n" + "=" * 80)
    print(f"🌊 DARK FLOW ANALYSIS: {analysis['ticker']}")
    print("=" * 80)

    print(f"\n💰 CURRENT PRICE: ${analysis['current_price']:.2f}")
    print(f"📊 TODAY'S OPEN: ${analysis['today_open']:.2f}")
    print(f"📈 TODAY'S RANGE: ${analysis['today_low']:.2f} - ${analysis['today_high']:.2f}")
    print(f"\n{analysis['bias_emoji']} BIAS: {analysis['bias']}")

    if analysis['key_levels']:
        print(f"\n🎯 KEY INSTITUTIONAL LEVELS (Volume Clusters):")
        for i, level in enumerate(analysis['key_levels'][:5], 1):
            distance = ((level - analysis['current_price']) / analysis['current_price']) * 100
            if abs(distance) < 1:
                marker = "⭐ ACTIVE"
            elif distance > 0:
                marker = "⬆️  RESISTANCE"
            else:
                marker = "⬇️  SUPPORT"
            print(f"   {i}. ${level:.2f} ({distance:+.2f}%) {marker}")

    if analysis['signals']:
        print(f"\n🌊 DARK FLOW SIGNALS:")
        for signal in analysis['signals']:
            print(f"   • {signal['type']} at ${signal['level']:.2f}")

    if analysis['unusual_volume']:
        print(f"\n📊 UNUSUAL VOLUME ACTIVITY:")
        for uv in analysis['unusual_volume'][-3:]:
            print(f"   • {uv['time'].strftime('%Y-%m-%d %H:%M')}: ${uv['price']:.2f} - {uv['ratio']:.1f}x avg")

    if analysis['gaps']:
        print(f"\n⚡ PRICE GAPS:")
        for gap in analysis['gaps'][-3:]:
            print(f"   • {gap['direction']}: ${gap['gap_from']:.2f} → ${gap['gap_to']:.2f} ({gap['gap_pct']:.2f}%)")

    if analysis['is_major_etf']:
        print(f"\n⭐ MAJOR ETF - Prime candidate for institutional activity")

    print("\n" + "=" * 80)
    print("💡 Volume clusters indicate where institutions are actively trading")
    print("=" * 80)


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

            # Offer export options
            offer_export_options(results, scanner_type='pressure_cooker')

            # Clear separator before ticker selection
            print("\n" + "=" * 80)
            print("📊 TICKER SELECTION FOR DETAILED ANALYSIS")
            print("=" * 80)

            # Prompt for detailed analysis
            selected = prompt_ticker_selection(results)
            if selected:
                print(f"\n✅ Selected: {', '.join(selected)}")

                # Offer chart display
                offer_chart_display(selected)

                # Show detailed analysis for each
                for ticker in selected:
                    # Find the result
                    result = next((r for r in results if r.ticker == ticker), None)
                    if result:
                        display_pressure_cooker_details(result)
                        input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\nScan cancelled by user.")
        except Exception as e:
            print(f"\n❌ Scan error: {e}")
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

        for ticker in tickers:
            print(f"\n{'=' * 100}")
            print(f"📈 CHART: {ticker}")
            print(f"{'=' * 100}")

            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="3mo")

                if not hist.empty:
                    chart_gen.plot_price_chart(hist, ticker)
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
