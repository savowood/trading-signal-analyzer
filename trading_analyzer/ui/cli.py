"""
Command Line Interface
Clean menu system for user interaction
"""
from typing import Optional, Tuple

from ..core.scanner import ScanParameters, ScanMode
from ..config import PRICE_RANGES, SCAN_MODES, MARKETS, VERSION


def show_banner():
    """Display application banner"""
    print("\n" + "=" * 80)
    print(f"Trading Signal Analyzer v{VERSION} - Multi-Asset Momentum Scanner")
    print("=" * 80)
    print("MARKETS: US Stocks | FOREX | Crypto | Dark Flow Analysis")
    print("FEATURES: 5 Pillars Momentum + Institutional Activity Detection")
    print("=" * 80 + "\n")


def prompt_market_choice() -> str:
    """Prompt user for market selection"""
    print("\nSelect market:")
    print("1. US Stocks (NASDAQ + NYSE) - RECOMMENDED")
    print("2. FOREX (Currency Pairs)")
    print("3. Crypto (Digital Assets)")
    print("4. NASDAQ only")
    print("5. NYSE only")
    print("q. Quit")

    choice = input("\nEnter choice (1-5 or 'q'): ").strip().lower()

    if choice == 'q':
        return None
    else:
        return choice if choice in ['1', '2', '3', '4', '5'] else '1'


def prompt_stock_market_choice() -> str:
    """Prompt user for stock market selection (for scanners that only work with stocks)"""
    print("\nSelect market:")
    print("1. US Stocks (NASDAQ + NYSE) - RECOMMENDED")
    print("2. NASDAQ only")
    print("3. NYSE only")
    print("q. Quit")

    choice = input("\nEnter choice (1-3 or 'q'): ").strip().lower()

    if choice == 'q':
        return None
    elif choice == '2':
        return '4'  # Map to NASDAQ in MARKETS config
    elif choice == '3':
        return '5'  # Map to NYSE in MARKETS config
    else:
        return '1'  # Default to all US stocks


def prompt_price_range() -> Optional[Tuple[float, float]]:
    """Prompt user for price range"""
    print("\nPrice range:")
    print("1. Default ($2.00 - $20.00) - RECOMMENDED")
    print("2. Penny stocks ($0.10 - $2.00)")
    print("3. Sub-penny ($0.0001 - $0.10)")
    print("4. Mid-cap ($20 - $100)")
    print("5. Custom range")
    print("q. Quit")

    choice = input("\nEnter choice (1-5, Enter for default, or 'q'): ").strip().lower()

    if choice == 'q':
        return None
    elif choice == '2':
        return PRICE_RANGES['penny']
    elif choice == '3':
        return PRICE_RANGES['subpenny']
    elif choice == '4':
        return PRICE_RANGES['midcap']
    elif choice == '5':
        try:
            min_input = input("Enter minimum price (e.g., 2.00): ").strip()
            max_input = input("Enter maximum price (e.g., 20.00): ").strip()
            min_price = float(min_input) if min_input else 2.0
            max_price = float(max_input) if max_input else 20.0
            return (min_price, max_price)
        except:
            print("⚠️  Invalid input, using default $2-$20")
            return PRICE_RANGES['default']
    else:
        return PRICE_RANGES['default']


def prompt_scan_mode() -> Optional[ScanMode]:
    """Prompt user for scan mode"""
    print("\nScan mode:")
    print("1. Quick Scan (ULTRA-FAST: ~10-20 seconds) - TradingView Only")
    for feature in SCAN_MODES['quick']['features']:
        print(f"   • {feature}")

    print("\n2. Smart Scan (FAST: ~30-60 seconds) - RECOMMENDED")
    for feature in SCAN_MODES['smart']['features']:
        print(f"   • {feature}")

    print("\n3. Deep Scan (COMPREHENSIVE: ~3-5 minutes)")
    for feature in SCAN_MODES['deep']['features']:
        print(f"   • {feature}")

    print("\nq. Quit")

    choice = input("\nEnter choice (1-3, Enter for Smart Scan, or 'q'): ").strip().lower()

    if choice == 'q':
        return None
    elif choice == '1':
        return ScanMode.QUICK
    elif choice == '3':
        return ScanMode.DEEP
    else:
        return ScanMode.SMART


def build_scan_parameters() -> Optional[ScanParameters]:
    """Build scan parameters from user input"""
    # Market selection
    market = prompt_market_choice()
    if market is None:
        return None

    # Get market info to determine type
    market_info = MARKETS.get(market, MARKETS['1'])
    market_type = market_info.get('type', 'stocks')

    # Price range (only for stocks)
    if market_type == 'stocks':
        price_range = prompt_price_range()
        if price_range is None:
            return None
        min_price, max_price = price_range
    else:
        # FOREX and Crypto don't need price ranges
        min_price, max_price = 0.0, 999999.0

    # Scan mode (only for stocks - FOREX/Crypto scan all pairs)
    if market_type == 'stocks':
        mode = prompt_scan_mode()
        if mode is None:
            return None
    else:
        # FOREX and Crypto always use smart mode (scan all available)
        mode = ScanMode.SMART

    # Build parameters
    params = ScanParameters(
        market_choice=market,
        min_price=min_price,
        max_price=max_price,
        mode=mode
    )

    # Confirm
    if market_type == 'stocks':
        if mode == ScanMode.QUICK:
            scan_type = "QUICK SCAN"
        elif mode == ScanMode.DEEP:
            scan_type = "DEEP SCAN"
        else:
            scan_type = "SMART SCAN"
        print(f"\n✅ {scan_type}: ${min_price:.4f} - ${max_price:.2f}")
    elif market_type == 'forex':
        print(f"\n✅ FOREX SCAN: Analyzing 21 currency pairs for volatility")
    elif market_type == 'crypto':
        print(f"\n✅ CRYPTO SCAN: Analyzing 24 digital assets for momentum")

    return params


def build_pressure_cooker_parameters() -> Optional[ScanParameters]:
    """Build scan parameters for Pressure Cooker (stocks only)"""
    # Stock market selection only
    market = prompt_stock_market_choice()
    if market is None:
        return None

    # Price range
    price_range = prompt_price_range()
    if price_range is None:
        return None
    min_price, max_price = price_range

    # Scan mode
    mode = prompt_scan_mode()
    if mode is None:
        return None

    # Build parameters
    params = ScanParameters(
        market_choice=market,
        min_price=min_price,
        max_price=max_price,
        mode=mode
    )

    # Confirm
    if mode == ScanMode.QUICK:
        scan_type = "QUICK SCAN"
    elif mode == ScanMode.DEEP:
        scan_type = "DEEP SCAN"
    else:
        scan_type = "SMART SCAN"

    print(f"\n✅ PRESSURE COOKER {scan_type}: ${min_price:.4f} - ${max_price:.2f}")
    print(f"   Scanning for short squeeze setups in US stocks only")

    return params


def show_main_menu() -> str:
    """Show main menu and get user choice"""
    print("\n" + "=" * 80)
    print("MAIN MENU")
    print("=" * 80)
    print("1. 🔥 Run Momentum Scan (5 Pillars)")
    print("2. 🌊 Run Dark Flow Scan (Institutional Activity)")
    print("3. 🎯 Run Pressure Cooker (Short Squeeze Setups) ⚠️  HIGH RISK")
    print("4. 📋 View Previous Scan Results")
    print("5. 📈 Analyze Single Ticker")
    print("6. 📊 View Database Statistics")
    print("7. 👁️  Manage Watchlist")
    print("8. View Cache Status")
    print("9. Clear Cache")
    print("s. View Settings")
    print("0. Edit Settings")
    print("=" * 80)

    choice = input("\nEnter choice, or 'q' to quit: ").strip().lower()
    return choice


def confirm_action(message: str) -> bool:
    """Confirm user action"""
    response = input(f"{message} (yes/no): ").strip().lower()
    return response == 'yes'


def edit_settings_interactive(current_settings: dict) -> dict:
    """
    Interactive settings editor

    Args:
        current_settings: Current settings dictionary

    Returns:
        Updated settings dictionary
    """
    print("\n" + "=" * 80)
    print("INTERACTIVE SETTINGS EDITOR")
    print("=" * 80)

    while True:
        print("\nWhat would you like to edit?")
        print("=" * 80)
        print("1. Trading Style & Risk Management")
        print("2. Cache Settings (scan results, microcap list, stock data)")
        print("3. Rate Limiting (workers, delays)")
        print("4. 5 Pillars Thresholds (change %, relative volume, float)")
        print("5. Display Settings (min score, max results)")
        print("6. API Keys (FinViz, Polygon, etc.)")
        print("7. Save and Exit")
        print("q. Cancel (don't save)")
        print("=" * 80)

        choice = input("\nEnter choice: ").strip().lower()

        if choice == '1':
            current_settings = edit_trading_style_settings(current_settings)
        elif choice == '2':
            current_settings = edit_cache_settings(current_settings)
        elif choice == '3':
            current_settings = edit_rate_limit_settings(current_settings)
        elif choice == '4':
            current_settings = edit_pillars_settings(current_settings)
        elif choice == '5':
            current_settings = edit_display_settings(current_settings)
        elif choice == '6':
            current_settings = edit_api_keys(current_settings)
        elif choice == '7':
            print("\n✅ Settings will be saved")
            return current_settings
        elif choice == 'q':
            print("\n❌ Changes cancelled")
            return None
        else:
            print("❌ Invalid choice")


def edit_trading_style_settings(settings: dict) -> dict:
    """Edit trading style and risk management settings"""
    from ..config import TRADING_STYLES, RR_RATIOS

    print("\n" + "=" * 80)
    print("TRADING STYLE & RISK MANAGEMENT")
    print("=" * 80)

    # Trading Style Selection
    print("\n1. Select Your Trading Style:")
    print("=" * 80)

    current_style = settings.get('trading_style', 'day_trader')
    styles_list = list(TRADING_STYLES.keys())

    for i, (key, style) in enumerate(TRADING_STYLES.items(), 1):
        marker = "→" if key == current_style else " "
        print(f"{marker} {i}. {style['name']:<20} | {style['typical_duration']:<20} | Hold: {style['hold_time']}")
        print(f"   {style['description']}")
        print()

    print(f"Current: {TRADING_STYLES[current_style]['name']}")
    change = input("\nChange trading style? (y/n): ").strip().lower()

    if change == 'y':
        try:
            choice = int(input(f"Select style (1-{len(styles_list)}): ").strip())
            if 1 <= choice <= len(styles_list):
                new_style = styles_list[choice - 1]
                settings['trading_style'] = new_style
                print(f"✅ Trading style set to: {TRADING_STYLES[new_style]['name']}")
            else:
                print("❌ Invalid choice, keeping current style")
        except:
            print("❌ Invalid input, keeping current style")

    # R:R Ratio Selection
    print("\n2. Risk/Reward Ratio:")
    print("=" * 80)

    current_rr = settings.get('rr_ratio', 2.0)
    print(f"\nCurrent R:R Ratio: 1:{current_rr:.1f}")
    print("   (Risk $1 to make ${:.0f})".format(current_rr))

    print("\nPresets:")
    for i, (key, rr) in enumerate(RR_RATIOS.items(), 1):
        marker = "→" if rr['ratio'] == current_rr else " "
        print(f"{marker} {i}. {rr['name']:<25} - {rr['description']}")

    print(f"\n{len(RR_RATIOS) + 1}. Custom ratio")

    change = input("\nChange R:R ratio? (y/n): ").strip().lower()

    if change == 'y':
        try:
            choice = int(input(f"Select option (1-{len(RR_RATIOS) + 1}): ").strip())

            if 1 <= choice <= len(RR_RATIOS):
                # Preset selected
                rr_list = list(RR_RATIOS.values())
                new_rr = rr_list[choice - 1]['ratio']
                settings['rr_ratio'] = new_rr
                print(f"✅ R:R ratio set to 1:{new_rr:.1f}")

            elif choice == len(RR_RATIOS) + 1:
                # Custom ratio
                custom = float(input("Enter custom R:R ratio (e.g., 2.5 for 1:2.5): ").strip())
                if 0.5 <= custom <= 10.0:
                    settings['rr_ratio'] = custom
                    print(f"✅ Custom R:R ratio set to 1:{custom:.1f}")
                else:
                    print("❌ Ratio must be between 0.5 and 10.0")

            else:
                print("❌ Invalid choice, keeping current ratio")

        except:
            print("❌ Invalid input, keeping current ratio")

    # Summary
    final_style = settings.get('trading_style', 'day_trader')
    final_rr = settings.get('rr_ratio', 2.0)
    style_info = TRADING_STYLES[final_style]

    print("\n" + "=" * 80)
    print("TRADING PREFERENCES SUMMARY")
    print("=" * 80)
    print(f"Style:        {style_info['name']}")
    print(f"Duration:     {style_info['typical_duration']}")
    print(f"Hold Time:    {style_info['hold_time']}")
    print(f"R:R Ratio:    1:{final_rr:.1f}")
    print(f"Charts:       {style_info['chart_period']} period, {style_info['chart_interval']} interval")
    print(f"Indicators:   {', '.join(style_info['indicators'])}")
    print("=" * 80)

    return settings


def edit_cache_settings(settings: dict) -> dict:
    """Edit cache settings"""
    print("\n" + "=" * 80)
    print("CACHE SETTINGS")
    print("=" * 80)

    cache = settings.get('cache_settings', {})

    print("\n1. Scan Results Cache")
    print(f"   Current: {cache.get('scan_results', 900)} seconds ({cache.get('scan_results', 900)/60:.0f} minutes)")
    change = input("   Change? (y/n): ").strip().lower()
    if change == 'y':
        try:
            minutes = int(input("   New value (minutes): ").strip())
            cache['scan_results'] = minutes * 60
            print(f"   ✅ Updated to {minutes} minutes")
        except:
            print("   ❌ Invalid input, keeping current value")

    print("\n2. Microcap List Cache")
    print(f"   Current: {cache.get('microcap_list', 14400)} seconds ({cache.get('microcap_list', 14400)/3600:.1f} hours)")
    change = input("   Change? (y/n): ").strip().lower()
    if change == 'y':
        try:
            hours = float(input("   New value (hours): ").strip())
            cache['microcap_list'] = int(hours * 3600)
            print(f"   ✅ Updated to {hours} hours")
        except:
            print("   ❌ Invalid input, keeping current value")

    print("\n3. Stock Data Cache")
    print(f"   Current: {cache.get('stock_data', 300)} seconds ({cache.get('stock_data', 300)/60:.0f} minutes)")
    change = input("   Change? (y/n): ").strip().lower()
    if change == 'y':
        try:
            minutes = int(input("   New value (minutes): ").strip())
            cache['stock_data'] = minutes * 60
            print(f"   ✅ Updated to {minutes} minutes")
        except:
            print("   ❌ Invalid input, keeping current value")

    settings['cache_settings'] = cache
    return settings


def edit_rate_limit_settings(settings: dict) -> dict:
    """Edit rate limit settings"""
    print("\n" + "=" * 80)
    print("RATE LIMITING SETTINGS")
    print("=" * 80)

    rate = settings.get('rate_limit', {})

    print("\n1. Concurrent Workers")
    print(f"   Current: {rate.get('workers', 3)}")
    print("   (Higher = faster but more likely to hit rate limits)")
    change = input("   Change? (y/n): ").strip().lower()
    if change == 'y':
        try:
            workers = int(input("   New value (1-10): ").strip())
            if 1 <= workers <= 10:
                rate['workers'] = workers
                print(f"   ✅ Updated to {workers} workers")
            else:
                print("   ❌ Value must be between 1-10")
        except:
            print("   ❌ Invalid input, keeping current value")

    print("\n2. Delay Every N Requests")
    print(f"   Current: {rate.get('delay_every', 10)}")
    change = input("   Change? (y/n): ").strip().lower()
    if change == 'y':
        try:
            delay_every = int(input("   New value (5-50): ").strip())
            if 5 <= delay_every <= 50:
                rate['delay_every'] = delay_every
                print(f"   ✅ Updated to every {delay_every} requests")
            else:
                print("   ❌ Value must be between 5-50")
        except:
            print("   ❌ Invalid input, keeping current value")

    print("\n3. Delay Duration (milliseconds)")
    print(f"   Current: {rate.get('delay_ms', 100)} ms")
    change = input("   Change? (y/n): ").strip().lower()
    if change == 'y':
        try:
            delay_ms = int(input("   New value (50-500): ").strip())
            if 50 <= delay_ms <= 500:
                rate['delay_ms'] = delay_ms
                print(f"   ✅ Updated to {delay_ms} ms")
            else:
                print("   ❌ Value must be between 50-500")
        except:
            print("   ❌ Invalid input, keeping current value")

    settings['rate_limit'] = rate
    return settings


def edit_pillars_settings(settings: dict) -> dict:
    """Edit 5 Pillars thresholds"""
    print("\n" + "=" * 80)
    print("5 PILLARS THRESHOLDS")
    print("=" * 80)

    pillars = settings.get('pillars', {})

    print("\n1. Change Percentage Threshold")
    change_config = pillars.get('change', {})
    print(f"   Current: {change_config.get('threshold', 10.0)}%")
    change = input("   Change? (y/n): ").strip().lower()
    if change == 'y':
        try:
            threshold = float(input("   New value (5-50%): ").strip())
            if 5 <= threshold <= 50:
                if 'change' not in pillars:
                    pillars['change'] = {}
                pillars['change']['threshold'] = threshold
                print(f"   ✅ Updated to {threshold}%")
            else:
                print("   ❌ Value must be between 5-50")
        except:
            print("   ❌ Invalid input, keeping current value")

    print("\n2. Relative Volume Threshold")
    relvol_config = pillars.get('rel_vol', {})
    print(f"   Current: {relvol_config.get('threshold', 5.0)}x")
    change = input("   Change? (y/n): ").strip().lower()
    if change == 'y':
        try:
            threshold = float(input("   New value (2-20x): ").strip())
            if 2 <= threshold <= 20:
                if 'rel_vol' not in pillars:
                    pillars['rel_vol'] = {}
                pillars['rel_vol']['threshold'] = threshold
                print(f"   ✅ Updated to {threshold}x")
            else:
                print("   ❌ Value must be between 2-20")
        except:
            print("   ❌ Invalid input, keeping current value")

    print("\n3. Float Threshold (millions)")
    float_config = pillars.get('float', {})
    print(f"   Current: {float_config.get('threshold', 20.0)}M shares")
    change = input("   Change? (y/n): ").strip().lower()
    if change == 'y':
        try:
            threshold = float(input("   New value (5-100M): ").strip())
            if 5 <= threshold <= 100:
                if 'float' not in pillars:
                    pillars['float'] = {}
                pillars['float']['threshold'] = threshold
                print(f"   ✅ Updated to {threshold}M shares")
            else:
                print("   ❌ Value must be between 5-100")
        except:
            print("   ❌ Invalid input, keeping current value")

    settings['pillars'] = pillars
    return settings


def edit_display_settings(settings: dict) -> dict:
    """Edit display settings"""
    print("\n" + "=" * 80)
    print("DISPLAY SETTINGS")
    print("=" * 80)

    print("\n1. Minimum Score to Display")
    print(f"   Current: {settings.get('min_score', 50)}")
    change = input("   Change? (y/n): ").strip().lower()
    if change == 'y':
        try:
            min_score = int(input("   New value (0-100): ").strip())
            if 0 <= min_score <= 100:
                settings['min_score'] = min_score
                print(f"   ✅ Updated to {min_score}")
            else:
                print("   ❌ Value must be between 0-100")
        except:
            print("   ❌ Invalid input, keeping current value")

    print("\n2. Maximum Results to Display")
    print(f"   Current: {settings.get('max_results_display', 50)}")
    change = input("   Change? (y/n): ").strip().lower()
    if change == 'y':
        try:
            max_display = int(input("   New value (10-200): ").strip())
            if 10 <= max_display <= 200:
                settings['max_results_display'] = max_display
                print(f"   ✅ Updated to {max_display}")
            else:
                print("   ❌ Value must be between 10-200")
        except:
            print("   ❌ Invalid input, keeping current value")

    return settings


def edit_api_keys(settings: dict) -> dict:
    """Edit API keys"""
    print("\n" + "=" * 80)
    print("API KEYS CONFIGURATION")
    print("=" * 80)
    print("\n⚠️  API keys are stored in plaintext in ~/.trading_analyzer")
    print("   Keep this file secure and never commit it to version control")

    api_keys = settings.get('api_keys', {})

    # Define API key information
    api_info = {
        'finviz': {
            'name': 'FinViz Elite',
            'description': 'Faster, unlimited stock screening',
            'url': 'https://elite.finviz.com/',
            'required': False
        },
        'polygon': {
            'name': 'Polygon.io',
            'description': 'Real-time market data and dark pool prints',
            'url': 'https://polygon.io/',
            'required': False
        },
        'alphavantage': {
            'name': 'Alpha Vantage',
            'description': 'Additional market data and indicators',
            'url': 'https://www.alphavantage.co/',
            'required': False
        },
        'newsapi': {
            'name': 'NewsAPI',
            'description': 'News and catalyst detection',
            'url': 'https://newsapi.org/',
            'required': False
        },
        'tradingview': {
            'name': 'TradingView',
            'description': 'Enhanced TradingView integration',
            'url': 'https://www.tradingview.com/',
            'required': False
        },
        'reddit_client_id': {
            'name': 'Reddit Client ID',
            'description': 'Social sentiment analysis (requires client_secret too)',
            'url': 'https://www.reddit.com/prefs/apps',
            'required': False
        },
        'reddit_client_secret': {
            'name': 'Reddit Client Secret',
            'description': 'Social sentiment analysis (requires client_id too)',
            'url': 'https://www.reddit.com/prefs/apps',
            'required': False
        }
    }

    while True:
        print("\n" + "=" * 80)
        print("Available API Keys:")
        print("=" * 80)

        # Show current status
        for i, (key, info) in enumerate(api_info.items(), 1):
            current_value = api_keys.get(key, '')
            if current_value and current_value.strip():
                # Mask the key
                if len(current_value) > 12:
                    masked = f"{current_value[:4]}...{current_value[-4:]}"
                else:
                    masked = f"{current_value[:2]}...{current_value[-2:]}" if len(current_value) > 4 else "***"
                status = f"✅ Configured ({masked})"
            else:
                status = "❌ Not configured"

            print(f"{i}. {info['name']}")
            print(f"   {info['description']}")
            print(f"   Status: {status}")
            print(f"   Get key: {info['url']}")
            print()

        print("=" * 80)
        print(f"{len(api_info) + 1}. Clear all API keys")
        print(f"{len(api_info) + 2}. Back to settings menu")
        print("=" * 80)

        try:
            choice = input("\nEnter number to edit/add API key: ").strip()

            if not choice:
                continue

            choice_num = int(choice)

            if choice_num == len(api_info) + 1:
                # Clear all keys
                confirm = input("\n⚠️  Clear ALL API keys? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    api_keys = {key: '' for key in api_info.keys()}
                    print("✅ All API keys cleared")
                continue

            elif choice_num == len(api_info) + 2:
                # Back to menu
                settings['api_keys'] = api_keys
                return settings

            elif 1 <= choice_num <= len(api_info):
                # Edit specific key
                key_name = list(api_info.keys())[choice_num - 1]
                info = api_info[key_name]

                print(f"\n{'=' * 80}")
                print(f"Configure: {info['name']}")
                print(f"{'=' * 80}")
                print(f"Description: {info['description']}")
                print(f"Get your API key: {info['url']}")

                current = api_keys.get(key_name, '')
                if current and current.strip():
                    print(f"\nCurrent: {current[:4]}...{current[-4:] if len(current) > 8 else '***'}")
                    print("\n1. Update API key")
                    print("2. Remove API key")
                    print("3. Keep current")

                    action = input("\nChoice: ").strip()

                    if action == '1':
                        new_key = input(f"\nEnter new {info['name']} API key: ").strip()
                        if new_key:
                            api_keys[key_name] = new_key
                            print(f"✅ {info['name']} API key updated")
                        else:
                            print("❌ Empty key, keeping current value")

                    elif action == '2':
                        api_keys[key_name] = ''
                        print(f"✅ {info['name']} API key removed")

                    elif action == '3':
                        print("Keeping current value")

                else:
                    new_key = input(f"\nEnter {info['name']} API key (or press Enter to skip): ").strip()
                    if new_key:
                        api_keys[key_name] = new_key
                        print(f"✅ {info['name']} API key added")
                    else:
                        print("Skipped")

            else:
                print("❌ Invalid choice")

        except ValueError:
            print("❌ Invalid input, please enter a number")
        except KeyboardInterrupt:
            print("\n\nReturning to settings menu...")
            settings['api_keys'] = api_keys
            return settings

    settings['api_keys'] = api_keys
    return settings
