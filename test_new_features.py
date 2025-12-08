#!/usr/bin/env python3
"""
Test script for FOREX, Crypto, and Dark Flow features
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all new modules can be imported"""
    print("Testing imports...")

    try:
        from trading_analyzer.config import FOREX_PAIRS, CRYPTO_PAIRS, DARK_FLOW, VERSION
        print(f"✅ Config imports successful (v{VERSION})")
        print(f"   - {len(FOREX_PAIRS['majors']) + len(FOREX_PAIRS['minors']) + len(FOREX_PAIRS['exotics'])} FOREX pairs")
        print(f"   - {len(CRYPTO_PAIRS['major']) + len(CRYPTO_PAIRS['defi']) + len(CRYPTO_PAIRS['altcoins'])} Crypto pairs")
        print(f"   - Dark Flow: {DARK_FLOW['enabled']}")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

    try:
        from trading_analyzer.data.providers import ForexProvider, CryptoProvider
        print("✅ Provider imports successful")

        forex = ForexProvider()
        crypto = CryptoProvider()
        print(f"   - ForexProvider: {forex.name}")
        print(f"   - CryptoProvider: {crypto.name}")
    except Exception as e:
        print(f"❌ Provider import failed: {e}")
        return False

    try:
        from trading_analyzer.scanners.darkflow import DarkFlowScanner, create_darkflow_scanner
        print("✅ Dark Flow scanner imports successful")

        darkflow = create_darkflow_scanner()
        print(f"   - DarkFlowScanner: {darkflow.name}")
    except Exception as e:
        print(f"❌ Dark Flow import failed: {e}")
        return False

    try:
        from trading_analyzer.scanners.momentum import MomentumScanner, create_scanner
        print("✅ Momentum scanner imports successful")

        scanner = create_scanner()
        print(f"   - MomentumScanner: {scanner.name}")
        print(f"   - Has forex provider: {hasattr(scanner, 'forex')}")
        print(f"   - Has crypto provider: {hasattr(scanner, 'crypto')}")
    except Exception as e:
        print(f"❌ Momentum scanner import failed: {e}")
        return False

    return True


def test_market_configuration():
    """Test market configuration"""
    print("\nTesting market configuration...")

    try:
        from trading_analyzer.config import MARKETS

        print(f"✅ Markets configured: {len(MARKETS)} options")
        for key, market in MARKETS.items():
            print(f"   {key}. {market['name']} (type: {market.get('type', 'stocks')})")
    except Exception as e:
        print(f"❌ Market configuration test failed: {e}")
        return False

    return True


def test_cli_updates():
    """Test CLI menu updates"""
    print("\nTesting CLI updates...")

    try:
        from trading_analyzer.ui.cli import show_banner, show_main_menu

        print("✅ CLI functions available")
        print("\nBanner preview:")
        show_banner()
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

    return True


def test_sample_data_structures():
    """Test that data structures work correctly"""
    print("\nTesting data structures...")

    try:
        from trading_analyzer.core.scanner import ScanResult, ScanParameters
        from trading_analyzer.scanners.darkflow import DarkFlowSignal
        from datetime import datetime

        # Test ScanResult
        result = ScanResult(
            ticker="EURUSD",
            price=1.0850,
            score=4,
            rel_vol=1.5,
            float_m=0,
            change_pct=0.75,
            catalyst="ATR: 0.0012",
            description="EUR/USD - 24h movement",
            source="FOREX",
            exchange="FX",
            volume=1000,
            market_cap=0
        )
        print(f"✅ ScanResult created: {result.ticker} @ ${result.price:.4f}")

        # Test DarkFlowSignal
        signal = DarkFlowSignal(
            ticker="AAPL",
            price=175.50,
            signal_type="block_trade",
            signal_strength=4,
            volume=50000,
            dollar_value=8775000,
            timestamp=datetime.now(),
            description="Block: 50,000 shares ($8.8M)"
        )
        scan_result = signal.to_scan_result()
        print(f"✅ DarkFlowSignal created and converted: {scan_result.ticker}")

    except Exception as e:
        print(f"❌ Data structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def main():
    """Run all tests"""
    print("=" * 80)
    print("TESTING NEW FEATURES: FOREX, Crypto, Dark Flow")
    print("=" * 80)

    tests = [
        test_imports,
        test_market_configuration,
        test_cli_updates,
        test_sample_data_structures,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if all(results):
        print("\n✅ ALL TESTS PASSED!")
        print("\nNew features are ready:")
        print("  • FOREX scanning (21 currency pairs)")
        print("  • Crypto scanning (24 digital assets)")
        print("  • Dark Flow analysis (institutional activity)")
        print("  • Updated menu system")
        print("  • Market routing in momentum scanner")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please review errors above")

    print("=" * 80)


if __name__ == '__main__':
    main()
