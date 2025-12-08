"""
Result Display and Formatting
Clean output formatting for scan results
"""
from typing import List
from ..core.scanner import ScanResult
from ..config import MAX_RESULTS_DISPLAY


def display_results(results: List[ScanResult], max_display: int = MAX_RESULTS_DISPLAY):
    """
    Display scan results in a formatted table

    Args:
        results: List of scan results
        max_display: Maximum number of results to display
    """
    if not results:
        print("\n❌ No stocks found matching criteria")
        return

    # Check result type first
    result_type = results[0].source
    is_dark_flow = result_type == "DARK_FLOW"
    is_forex = result_type == "FOREX"
    is_crypto = result_type == "CRYPTO"

    # Dynamic result type label
    if is_dark_flow:
        result_label = "Dark Flow signals detected"
    elif is_forex:
        result_label = "FOREX pairs found"
    elif is_crypto:
        result_label = "cryptocurrencies found"
    else:
        result_label = "stocks found"

    print(f"\n{'=' * 100}")
    print(f"SCAN RESULTS ({len(results)} {result_label})")
    print(f"{'=' * 100}")

    if is_dark_flow:
        # Dark Flow specific header
        print(f"\n{'#':<4} {'Ticker':<8} {'Price':<10} {'Bias':<10} {'DFScore':<9} "
              f"{'Signals':<8} {'Description':<40}")
        print(f"{'-' * 100}")
    elif is_forex:
        # FOREX specific header
        print(f"\n{'#':<4} {'Pair':<12} {'Price':<12} {'Change%':<12} {'Week%':<12} {'Volatility%':<14}")
        print(f"{'-' * 100}")
    elif is_crypto:
        # Crypto specific header
        print(f"\n{'#':<4} {'Name':<20} {'Price':<18} {'Day%':<12} {'Week%':<12} {'Volatility%':<14}")
        print(f"{'-' * 100}")
    else:
        # Standard stock header
        print(f"\n{'#':<4} {'Ticker':<8} {'Price':<8} {'Today%':<8} {'RelVol':<8} "
              f"{'Float(M)':<10} {'Score':<6} {'Catalyst':<15}")
        print(f"{'-' * 100}")

    # Display results (limit to max_display)
    display_count = min(len(results), max_display)

    for i, result in enumerate(results[:display_count], 1):
        if is_dark_flow:
            # Dark Flow display
            price_str = f"${result.price:.2f}"

            # Extract bias from catalyst
            if 'BULLISH' in result.catalyst:
                bias_str = "🟢 BULLISH"
            elif 'BEARISH' in result.catalyst:
                bias_str = "🔴 BEARISH"
            else:
                bias_str = "⚪ NEUTRAL"

            # Dark Flow score
            df_score = getattr(result, 'dark_flow_score', 0)
            if df_score >= 80:
                score_str = f"🔥🔥🔥 {int(df_score)}"
            elif df_score >= 60:
                score_str = f"🔥🔥 {int(df_score)}"
            else:
                score_str = f"🔥 {int(df_score)}"

            # Extract signal count from catalyst
            signals = result.catalyst.split('|')[1].strip() if '|' in result.catalyst else "0 signals"

            print(f"{i:<4} {result.ticker:<8} {price_str:<10} {bias_str:<10} {score_str:<9} "
                  f"{signals:<8} {result.description:<40}")

        elif is_forex:
            # FOREX display
            price = result.price
            if price < 1:
                price_str = f"{price:.5f}"
            elif price < 100:
                price_str = f"{price:.4f}"
            else:
                price_str = f"{price:.2f}"

            # Get day change and week change from description
            # Format: "Day: +0.8% | Week: +2.1%"
            parts = result.description.split('|')
            day_change_str = parts[0].replace('Day:', '').strip() if len(parts) > 0 else "+0.0%"
            week_change_str = parts[1].replace('Week:', '').strip() if len(parts) > 1 else "+0.0%"

            # Add emoji based on day change
            day_val = float(day_change_str.replace('%', '').replace('+', ''))
            change_emoji = "🟢" if day_val >= 0 else "🔴"
            day_change_str = f"{change_emoji} {day_change_str}"

            # Volatility from catalyst
            vol_str = result.catalyst.replace('Vol:', '').strip()

            print(f"{i:<4} {result.ticker:<12} {price_str:<12} {day_change_str:<12} "
                  f"{week_change_str:<12} {vol_str:<14}")

        elif is_crypto:
            # Crypto display
            price = result.price
            if price < 0.01:
                price_str = f"${price:.6f}"
            elif price < 1:
                price_str = f"${price:.4f}"
            elif price < 100:
                price_str = f"${price:.2f}"
            else:
                price_str = f"${price:,.2f}"

            # Get day and week change from description
            # Format: "Bitcoin | Day: +2.3% | Week: +8.5%"
            parts = result.description.split('|')
            name = parts[0].strip() if len(parts) > 0 else result.ticker
            day_str = parts[1].replace('Day:', '').strip() if len(parts) > 1 else "+0.0%"
            week_str = parts[2].replace('Week:', '').strip() if len(parts) > 2 else "+0.0%"

            # Add emoji based on day change
            day_val = float(day_str.replace('%', '').replace('+', ''))
            if day_val >= 5:
                emoji = "🚀"
            elif day_val >= 0:
                emoji = "🟢"
            elif day_val >= -5:
                emoji = "🔴"
            else:
                emoji = "📉"
            day_str = f"{emoji} {day_str}"

            # Volatility from catalyst
            vol_str = result.catalyst.replace('Vol:', '').strip()

            print(f"{i:<4} {name:<20} {price_str:<18} {day_str:<12} "
                  f"{week_str:<12} {vol_str:<14}")

        else:
            # Standard stock display
            # Color coding for score
            score_str = f"{result.score}/5"
            if result.score >= 5:
                score_str = f"⭐ {score_str}"
            elif result.score >= 4:
                score_str = f"✓ {score_str}"

            # Format values
            price_str = f"${result.price:.2f}"
            change_str = f"+{result.change_pct:.1f}%"
            relvol_str = f"{result.rel_vol:.1f}x"
            float_str = f"{result.float_m:.1f}M"

            # Low float indicator
            if result.low_float:
                float_str += " 🔥"

            print(f"{i:<4} {result.ticker:<8} {price_str:<8} {change_str:<8} {relvol_str:<8} "
                  f"{float_str:<10} {score_str:<6} {result.catalyst:<15}")

    if len(results) > max_display:
        print(f"\n... and {len(results) - max_display} more")
        print(f"(Showing top {max_display} results)")

    print(f"\n{'=' * 100}")

    # Add footer tips
    if is_forex:
        print("\n💡 Tip: FOREX pairs trade 24/5 with high liquidity")
        print("💡 Sorted by activity (week change × volatility)")
    elif is_crypto:
        print("\n💡 List dynamically fetched from CoinGecko API (top 30 by market cap)")
        print("💡 Tip: Crypto trades 24/7 with high volatility")
        print("💡 Sorted by activity (week change × volatility)")


def display_summary(results: List[ScanResult]):
    """Display summary statistics"""
    if not results:
        return

    # Check result type
    result_type = results[0].source
    is_forex = result_type == "FOREX"
    is_crypto = result_type == "CRYPTO"
    is_dark_flow = result_type == "DARK_FLOW"

    # Skip summary for FOREX and Crypto (they have their own footer tips)
    if is_forex or is_crypto:
        return

    # Skip summary for Dark Flow (it has its own detailed summary in main.py)
    if is_dark_flow:
        return

    # Stock summary only
    avg_change = sum(r.change_pct for r in results) / len(results)
    avg_relvol = sum(r.rel_vol for r in results) / len(results)
    low_float_count = sum(1 for r in results if r.low_float)
    perfect_score_count = sum(1 for r in results if r.score == 5)

    print(f"\n📊 SUMMARY STATISTICS")
    print(f"{'=' * 50}")
    print(f"Total stocks found:     {len(results)}")
    print(f"Perfect score (5/5):    {perfect_score_count}")
    print(f"Low float stocks:       {low_float_count} ({low_float_count/len(results)*100:.1f}%)")
    print(f"Average change:         +{avg_change:.1f}%")
    print(f"Average rel volume:     {avg_relvol:.1f}x")
    print(f"{'=' * 50}\n")


def display_detailed_result(result: ScanResult):
    """Display detailed information for a single stock"""
    print(f"\n{'=' * 80}")
    print(f"DETAILED VIEW: {result.ticker}")
    print(f"{'=' * 80}")

    print(f"\nPrice & Performance:")
    print(f"  Current Price:        ${result.price:.2f}")
    print(f"  Today's Change:       +{result.change_pct:.1f}%")
    if result.week_change:
        print(f"  Week Change:          {result.week_change:+.1f}%")

    print(f"\nVolume & Float:")
    print(f"  Relative Volume:      {result.rel_vol:.1f}x")
    print(f"  Float:                {result.float_m:.1f}M shares")
    if result.low_float:
        print(f"  Low Float:            ✅ YES (< 20M)")

    print(f"\nScoring:")
    print(f"  5 Pillars Score:      {result.score}/5")
    print(f"  Catalyst:             {result.catalyst}")

    print(f"\nAdditional Info:")
    print(f"  Exchange:             {result.exchange}")
    print(f"  Source:               {result.source}")
    if result.description:
        print(f"  Description:          {result.description}")

    print(f"\n{'=' * 80}")


def format_pillar_status(result: ScanResult, params) -> str:
    """Format which pillars are met"""
    pillars = []

    if result.change_pct >= params.min_change:
        pillars.append("✓ Change")
    else:
        pillars.append("✗ Change")

    if result.rel_vol >= params.min_rel_vol:
        pillars.append("✓ Volume")
    else:
        pillars.append("✗ Volume")

    if result.float_m < params.max_float:
        pillars.append("✓ Float")
    else:
        pillars.append("✗ Float")

    if params.min_price <= result.price <= params.max_price:
        pillars.append("✓ Price")
    else:
        pillars.append("✗ Price")

    if result.change_pct >= params.min_change and result.rel_vol >= params.min_rel_vol:
        pillars.append("✓ Catalyst")
    else:
        pillars.append("✗ Catalyst")

    return " | ".join(pillars)


def prompt_ticker_selection(results: List[ScanResult]) -> List[str]:
    """Prompt user to select tickers for analysis"""
    if not results:
        return []

    print(f"\nSelect stocks to analyze:")
    print(f"  • Enter numbers separated by commas (e.g., 1,3,5 for items #1, #3, #5)")
    print(f"  • Enter ticker symbols separated by commas (e.g., AAPL,TSLA)")
    print(f"  • Enter 'all' to analyze all results")
    print(f"  • Enter 'top N' to analyze top N results (e.g., 'top 5')")
    print(f"  • Press Enter to skip")

    choice = input("\nYour selection: ").strip()

    if not choice:
        return []

    # Handle 'all'
    if choice.upper() == 'ALL':
        return [r.ticker for r in results]

    # Handle 'top N'
    if choice.upper().startswith('TOP '):
        try:
            n = int(choice.split()[1])
            return [r.ticker for r in results[:n]]
        except:
            print("❌ Invalid 'top N' format")
            return []

    # Try parsing as numeric indices first
    try:
        # Check if all parts are numbers
        parts = [p.strip() for p in choice.split(',')]
        if all(p.isdigit() for p in parts):
            indices = [int(p) for p in parts]
            tickers = []
            for idx in indices:
                if 1 <= idx <= len(results):
                    tickers.append(results[idx - 1].ticker)
                else:
                    print(f"⚠️  Index {idx} out of range (1-{len(results)})")
            return tickers
    except:
        pass

    # Fall back to parsing as ticker symbols
    tickers = [t.strip().upper() for t in choice.split(',')]

    # Validate tickers exist in results
    valid_tickers = {r.ticker for r in results}
    invalid = [t for t in tickers if t not in valid_tickers]

    if invalid:
        print(f"⚠️  Unknown tickers: {', '.join(invalid)}")

    return [t for t in tickers if t in valid_tickers]


def display_technical_analysis(analysis):
    """Display technical analysis results"""
    from ..core.analysis import TechnicalAnalysis

    if not isinstance(analysis, TechnicalAnalysis):
        print("❌ Invalid analysis data")
        return

    print(f"\n{'=' * 100}")
    print(f"TECHNICAL ANALYSIS: {analysis.ticker}")
    print(f"{'=' * 100}")

    # Overall Signal
    print(f"\n📊 OVERALL SIGNAL")
    print(f"{'=' * 100}")
    print(f"  Score:            {analysis.signal_score}/100 (Grade: {analysis.signal_grade})")
    print(f"  Recommendation:   {analysis.recommendation}")
    print(f"  Current Price:    ${analysis.current_price:.2f}")

    # VWAP
    print(f"\n📈 VWAP ANALYSIS")
    print(f"{'=' * 100}")
    print(f"  VWAP:             ${analysis.vwap:.2f}")
    print(f"  Position:         {analysis.vwap_position}")
    print(f"  2σ Bands:         ${analysis.vwap_2std[0]:.2f} - ${analysis.vwap_2std[1]:.2f}")
    print(f"  3σ Bands:         ${analysis.vwap_3std[0]:.2f} - ${analysis.vwap_3std[1]:.2f}")

    # MACD
    print(f"\n📉 MACD")
    print(f"{'=' * 100}")
    print(f"  MACD Line:        {analysis.macd:.4f}")
    print(f"  Signal Line:      {analysis.macd_signal:.4f}")
    print(f"  Histogram:        {analysis.macd_histogram:.4f}")
    print(f"  Trend:            {analysis.macd_trend}")

    # RSI
    print(f"\n⚡ RSI (14-period)")
    print(f"{'=' * 100}")
    print(f"  RSI:              {analysis.rsi:.2f}")
    print(f"  Signal:           {analysis.rsi_signal}")
    if analysis.rsi < 30:
        print(f"  Status:           🟢 Potentially Oversold")
    elif analysis.rsi > 70:
        print(f"  Status:           🔴 Potentially Overbought")
    else:
        print(f"  Status:           🟡 Neutral Zone")

    # SuperTrend
    print(f"\n🎯 SUPERTREND")
    print(f"{'=' * 100}")
    print(f"  SuperTrend:       ${analysis.supertrend:.2f}")
    print(f"  Signal:           {analysis.supertrend_signal}")

    # EMAs
    print(f"\n📊 MOVING AVERAGES")
    print(f"{'=' * 100}")
    print(f"  EMA 9:            ${analysis.ema9:.2f}")
    print(f"  EMA 20:           ${analysis.ema20:.2f}")
    print(f"  Crossover:        {analysis.ema_crossover}")

    # Volume
    print(f"\n📦 VOLUME")
    print(f"{'=' * 100}")
    print(f"  Current:          {analysis.volume:,}")
    print(f"  Average:          {analysis.avg_volume:,}")
    print(f"  Relative:         {analysis.rel_volume:.2f}x")

    print(f"\n{'=' * 100}")


def show_disclaimer(settings: dict = None):
    """
    Display trading disclaimer

    Args:
        settings: Current user settings dictionary

    Returns:
        Tuple of (accepted: bool, updated_settings: dict)
    """
    # Check if already acknowledged
    if settings and settings.get('disclaimer_acknowledged', False):
        print("\n" + "=" * 80)
        print("⚠️  FINANCIAL DISCLAIMER")
        print("=" * 80)
        print("✅ You have already acknowledged the terms and conditions.")
        print("   (Trading involves substantial risk - use at your own risk)")
        print("=" * 80 + "\n")
        return True, settings

    # Show full disclaimer
    print("\n" + "=" * 80)
    print("⚠️  FINANCIAL DISCLAIMER")
    print("=" * 80)
    print("""
This software is provided for EDUCATIONAL and INFORMATIONAL purposes only.

Trading involves SUBSTANTIAL RISK and can result in SIGNIFICANT FINANCIAL LOSSES.
Past performance is NOT indicative of future results.

The information provided is NOT financial advice, investment advice, or trading
advice. This is a technical analysis tool only.

Before trading, you should:
  ✓ Consult with a licensed financial advisor
  ✓ Understand the risks involved
  ✓ Only trade with money you can afford to lose
  ✓ Conduct your own research and due diligence

USE AT YOUR OWN RISK.
""")
    print("=" * 80)

    response = input("\nDo you understand and accept these terms? (yes/no): ").strip().lower()

    if response != 'yes':
        print("\n❌ You must accept the terms to use this software.")
        return False, settings

    print("\n✅ Terms accepted. Proceeding...\n")

    # Update settings to mark disclaimer as acknowledged
    if settings is None:
        settings = {}
    settings['disclaimer_acknowledged'] = True

    return True, settings


def show_pressure_cooker_disclaimer(settings: dict = None):
    """
    Display Pressure Cooker specific disclaimer for high-risk trading

    Args:
        settings: Current user settings dictionary

    Returns:
        Tuple of (accepted: bool, updated_settings: dict)
    """
    # Check if already acknowledged
    if settings and settings.get('pressure_cooker_disclaimer_acknowledged', False):
        return True, settings

    # Show specific warning
    print("\n" + "=" * 80)
    print("⚠️  🔥 PRESSURE COOKER - EXTREME RISK WARNING 🔥")
    print("=" * 80)
    print("""
PRESSURE COOKER identifies SHORT SQUEEZE setups - these are EXTREMELY VOLATILE.

CHARACTERISTICS OF SHORT SQUEEZE SETUPS:
  🔴 Can move 50-500%+ in DAYS (or even hours)
  🔴 Can REVERSE just as quickly - massive losses possible
  🔴 Often involve heavily diluted penny stocks
  🔴 Reverse splits indicate struggling business fundamentals
  🔴 Liquidity can VANISH INSTANTLY
  🔴 Subject to manipulation and pump-and-dump schemes

THIS IS NOT INVESTING - THIS IS HIGH-RISK SPECULATION

MANDATORY TRADING RULES IF YOU PROCEED:
  ✓ NEVER risk more than 1-2% of your account per trade
  ✓ Use TIGHT stop losses (3-5% maximum)
  ✓ Take partial profits at 20%, 50%, 100% gains
  ✓ NEVER hold through major resistance
  ✓ EXIT IMMEDIATELY if volume dies
  ✓ NEVER EVER average down on these setups
  ✓ Position size should be SMALL

RECOMMENDED FOR EXPERIENCED TRADERS ONLY.
NOT SUITABLE FOR BEGINNERS OR CONSERVATIVE INVESTORS.

This is in ADDITION to the general trading disclaimer you already accepted.
""")
    print("=" * 80)

    response = input("\nI understand the extreme risks and accept responsibility (yes/no): ").strip().lower()

    if response != 'yes':
        print("\n✅ Wise decision. Pressure Cooker is not for everyone.")
        return False, settings

    print("\n⚠️  Proceed with extreme caution. Small positions only!\n")

    # Update settings
    if settings is None:
        settings = {}
    settings['pressure_cooker_disclaimer_acknowledged'] = True

    return True, settings


def display_pressure_cooker_results(results: List[ScanResult]):
    """Display Pressure Cooker scan results with specific formatting"""
    if not results:
        print("\n✅ No Pressure Cooker setups found")
        print("   This is often GOOD NEWS - these setups are extremely risky!")
        return

    print(f"\n{'=' * 120}")
    print(f"🔥 PRESSURE COOKER RESULTS ({len(results)} short squeeze setups found)")
    print(f"{'=' * 120}")

    # Check if enhanced results (has technical_score attribute)
    is_enhanced = hasattr(results[0], 'technical_score')

    if is_enhanced:
        # Enhanced display with more columns
        print(f"\n{'#':<4} {'Ticker':<8} {'Price':<8} {'Grade':<6} {'Score':<6} "
              f"{'Short%':<8} {'RelVol':<8} {'Float':<8} {'RSI':<6} {'Stage':<12} {'Catalysts':<15}")
        print(f"{'-' * 120}")
    else:
        # Basic display
        print(f"\n{'#':<4} {'Ticker':<8} {'Price':<8} {'Grade':<6} {'Score':<6} "
              f"{'Short%':<8} {'RelVol':<8} {'Float(M)':<10} {'Setup Quality':<15}")
        print(f"{'-' * 120}")

    for i, result in enumerate(results, 1):
        # Grade emoji
        if result.score >= 90:
            grade_emoji = "🔥🔥🔥"
        elif result.score >= 80:
            grade_emoji = "🔥🔥"
        elif result.score >= 70:
            grade_emoji = "🔥"
        else:
            grade_emoji = "⚠️"

        # Get Pressure Cooker specific fields
        grade = getattr(result, 'grade', 'N/A')
        short_percent = getattr(result, 'short_percent', 0)

        if is_enhanced:
            # Enhanced display
            rsi = getattr(result, 'rsi', 50)
            rsi_str = f"{rsi:.0f}"
            if rsi < 30:
                rsi_str += "🔥"

            stage = getattr(result, 'setup_stage', 'N/A')
            stage_str = stage.upper() if stage else 'N/A'

            # Count catalysts
            catalyst_count = 0
            if getattr(result, 'has_news_catalyst', False):
                catalyst_count += 1
            if getattr(result, 'unusual_options_activity', False):
                catalyst_count += 1
            if getattr(result, 'trending_social', False):
                catalyst_count += 1

            catalyst_str = f"{catalyst_count} active"
            if catalyst_count >= 2:
                catalyst_str += " 🚀"

            float_str = f"{result.float_m:.1f}M"

            print(f"{i:<4} {result.ticker:<8} ${result.price:<7.2f} "
                  f"{grade:<6} {result.score:<6} "
                  f"{short_percent:<7.1f}% {result.rel_vol:<7.1f}x "
                  f"{float_str:<8} {rsi_str:<6} {stage_str:<12} {catalyst_str:<15} {grade_emoji}")
        else:
            # Basic display
            setup_quality = getattr(result, 'setup_quality', 'UNKNOWN')
            print(f"{i:<4} {result.ticker:<8} ${result.price:<7.2f} "
                  f"{grade:<6} {result.score:<6} "
                  f"{short_percent:<7.1f}% {result.rel_vol:<7.1f}x "
                  f"{result.float_m:<9.2f} {setup_quality:<15} {grade_emoji}")

    print(f"\n{'=' * 120}")
    print("⚠️  PRESSURE COOKER SETUPS ARE EXTREMELY VOLATILE")
    print("   • Use TIGHT stop losses (3-5% maximum)")
    print("   • SMALL position sizes (1-2% of account max)")
    print("   • Can reverse INSTANTLY - take profits quickly")
    print("   • NEVER hold through major resistance")
    print("   • EXIT if volume dies")
    print("=" * 120)


def display_pressure_cooker_details(result: ScanResult):
    """Display detailed Pressure Cooker analysis for a single ticker"""
    print("\n" + "=" * 100)
    print(f"🔥 PRESSURE COOKER ANALYSIS: {result.ticker}")
    print("=" * 100)

    # Check if enhanced result
    is_enhanced = hasattr(result, 'technical_score')

    # Get common fields
    score = result.score
    grade = getattr(result, 'grade', 'N/A')
    setup_quality = getattr(result, 'setup_quality', 'UNKNOWN')
    short_percent = getattr(result, 'short_percent', 0)
    days_to_cover = getattr(result, 'days_to_cover', 0)
    has_reverse_split = getattr(result, 'has_reverse_split', False)
    consecutive_vol_days = getattr(result, 'consecutive_volume_days', 0)
    breaking_high = getattr(result, 'breaking_20d_high', False)
    avg_volume_20d = getattr(result, 'avg_volume_20d', 0)

    # Score and grade
    if score >= 90:
        emoji = "🔥🔥🔥"
    elif score >= 80:
        emoji = "🔥🔥"
    elif score >= 70:
        emoji = "🔥"
    else:
        emoji = "⚠️"

    print(f"\nSETUP SCORE: {score}/100 {emoji} (Grade: {grade})")
    print(f"QUALITY: {setup_quality}")

    # === SQUEEZE FUNDAMENTALS ===
    print(f"\n{'=' * 100}")
    print("🔥 SQUEEZE FUNDAMENTALS:")
    print("=" * 100)

    print(f"   Float: {result.float_m:.2f}M | Short%: {short_percent:.1f}% | Days to Cover: {days_to_cover:.1f}")

    short_emoji = "🔥🔥🔥" if short_percent > 40 else "🔥🔥" if short_percent > 20 else "🔥"
    float_emoji = "🔥🔥🔥" if result.float_m < 1 else "🔥🔥" if result.float_m < 3 else "🔥"

    print(f"   • Short Interest: {short_percent:.1f}% {short_emoji}")
    print(f"   • Float: {result.float_m:.2f}M shares {float_emoji}")
    print(f"   • Days to Cover: {days_to_cover:.1f} days")

    # === TECHNICAL SETUP (Enhanced only) ===
    if is_enhanced:
        print(f"\n{'=' * 100}")
        print("📊 TECHNICAL SETUP:")
        print("=" * 100)

        rsi = getattr(result, 'rsi', 50)
        rsi_oversold = getattr(result, 'rsi_oversold', False)
        macd_bullish = getattr(result, 'macd_bullish', False)
        near_bb_support = getattr(result, 'near_bb_support', False)

        rsi_status = "✅ OVERSOLD" if rsi_oversold else "NEUTRAL"
        print(f"   RSI: {rsi:.1f} {rsi_status}")
        print(f"   MACD: {'✅ BULLISH CROSSOVER' if macd_bullish else 'NEUTRAL'}")
        print(f"   Bollinger Bands: {'✅ NEAR SUPPORT' if near_bb_support else 'NEUTRAL'}")

        # Setup progression
        setup_stage = getattr(result, 'setup_stage', 'unknown')
        volume_trend = getattr(result, 'volume_trend', 'unknown')

        stage_emoji = "🚀" if setup_stage == 'breaking' else "⚠️" if setup_stage == 'ready' else "📊"
        print(f"   Setup Stage: {setup_stage.upper()} {stage_emoji}")
        print(f"   Volume Trend: {volume_trend.upper()}")

    # === VOLUME ANALYSIS ===
    vol_emoji = "🚀" if result.rel_vol > 10 else "📈" if result.rel_vol > 5 else "📊"
    print(f"\n{'=' * 100}")
    print("📊 VOLUME ANALYSIS:")
    print("=" * 100)
    print(f"   Current: {result.volume:,.0f} | Avg (20d): {avg_volume_20d:,.0f} | RelVol: {result.rel_vol:.1f}x {vol_emoji}")
    print(f"   • Consecutive high-volume days: {consecutive_vol_days}")
    print(f"   • Breaking 20-day high: {'✅ YES' if breaking_high else '❌ NO'}")

    # === CATALYST DETECTION (Enhanced only) ===
    if is_enhanced:
        has_news = getattr(result, 'has_news_catalyst', False)
        has_options = getattr(result, 'unusual_options_activity', False)
        has_social = getattr(result, 'trending_social', False)

        if has_news or has_options or has_social:
            print(f"\n{'=' * 100}")
            print("🎯 CATALYST DETECTED:")
            print("=" * 100)

            if has_news:
                news_headline = getattr(result, 'news_headline', 'N/A')
                news_count = getattr(result, 'news_count', 0)
                catalyst_type = getattr(result, 'catalyst_type', 'General')
                print(f"   ✅ News Catalyst ({news_count} articles)")
                print(f"      Type: {catalyst_type}")
                if news_headline:
                    print(f"      Latest: {news_headline[:80]}...")

            if has_options:
                call_put_ratio = getattr(result, 'call_put_ratio', 0)
                gamma_squeeze = getattr(result, 'gamma_squeeze_potential', False)
                print(f"   ✅ Unusual options activity (C/P ratio: {call_put_ratio:.2f})")
                if gamma_squeeze:
                    print(f"      🚀 GAMMA SQUEEZE POTENTIAL")

            if has_social:
                wsb_mentions = getattr(result, 'wsb_mentions', 0)
                social_sentiment = getattr(result, 'social_sentiment', 'neutral')
                print(f"   ✅ Trending on WSB ({wsb_mentions} mentions, {social_sentiment})")

    # === KEY FACTORS (Enhanced only) ===
    if is_enhanced:
        key_factors = getattr(result, 'key_factors', [])
        if key_factors:
            print(f"\n{'=' * 100}")
            print("📈 KEY FACTORS:")
            print("=" * 100)
            for factor in key_factors:
                print(f"   • {factor}")

    # === INTERPRETATION ===
    print(f"\n{'=' * 100}")
    print("🎯 INTERPRETATION:")
    print("=" * 100)
    if score >= 90:
        print("   ✅ EXCELLENT setup - Rare high-quality squeeze opportunity")
        print("   ✅ All key factors aligned - strong confirmation")
        print("   ✅ This is what we look for in Pressure Cooker setups")
    elif score >= 80:
        print("   ✅ STRONG squeeze potential - Most key factors present")
        print("   ✅ High short interest + low float = explosive setup")
        print("   ✅ Volume confirms interest")
    elif score >= 70:
        print("   ⚠️  GOOD setup but missing some key factors")
        print("   ⚠️  Monitor closely for additional confirmation")
    elif score >= 60:
        print("   ⚠️  MARGINAL setup - several factors weak")
        print("   ⚠️  High risk, consider smaller position or wait")
    else:
        print("   ❌ WEAK setup - does not meet criteria")
        print("   ❌ Pass or wait for better confirmation")

    # === RISK WARNINGS ===
    print(f"\n{'=' * 100}")
    print("⚠️  RISK WARNINGS:")
    print("=" * 100)
    warnings = []
    if result.float_m < 1:
        warnings.append("🔴 EXTREME low float - high volatility risk")
    if has_reverse_split:
        warnings.append("🔴 Reverse split history - dilution pattern")
    if short_percent < 15:
        warnings.append("🔴 Low short interest - limited squeeze potential")
    if result.rel_vol < 5:
        warnings.append("🔴 Moderate volume - needs more confirmation")

    if is_enhanced:
        rsi = getattr(result, 'rsi', 50)
        if rsi > 70:
            warnings.append("🔴 RSI overbought - potential pullback risk")

    if warnings:
        for warning in warnings:
            print(f"   {warning}")
    else:
        print("   ⚠️  All Pressure Cooker setups are high-risk - use caution")

    print("\n" + "=" * 100)
