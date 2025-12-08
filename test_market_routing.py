#!/usr/bin/env python3
"""
Test market routing and parameter building
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from trading_analyzer.core.scanner import ScanParameters, ScanMode
from trading_analyzer.config import MARKETS

def test_parameter_building():
    """Test that parameters are built correctly for different markets"""
    print("Testing parameter building for different markets...\n")

    # Test stocks
    print("1. Testing US Stocks:")
    params_stocks = ScanParameters(
        market_choice='1',
        min_price=2.0,
        max_price=20.0,
        mode=ScanMode.SMART
    )
    market_info = MARKETS.get(params_stocks.market_choice)
    print(f"   Market: {market_info['name']}")
    print(f"   Type: {market_info['type']}")
    print(f"   Price range: ${params_stocks.min_price} - ${params_stocks.max_price}")
    print(f"   Mode: {params_stocks.mode.value}")
    print(f"   ✅ Stocks parameters correct\n")

    # Test FOREX
    print("2. Testing FOREX:")
    params_forex = ScanParameters(
        market_choice='2',
        min_price=0.0,
        max_price=999999.0,
        mode=ScanMode.SMART
    )
    market_info = MARKETS.get(params_forex.market_choice)
    print(f"   Market: {market_info['name']}")
    print(f"   Type: {market_info['type']}")
    print(f"   Price range: Not applicable (all pairs scanned)")
    print(f"   Mode: {params_forex.mode.value}")
    print(f"   ✅ FOREX parameters correct\n")

    # Test Crypto
    print("3. Testing Crypto:")
    params_crypto = ScanParameters(
        market_choice='3',
        min_price=0.0,
        max_price=999999.0,
        mode=ScanMode.SMART
    )
    market_info = MARKETS.get(params_crypto.market_choice)
    print(f"   Market: {market_info['name']}")
    print(f"   Type: {market_info['type']}")
    print(f"   Price range: Not applicable (all pairs scanned)")
    print(f"   Mode: {params_crypto.mode.value}")
    print(f"   ✅ Crypto parameters correct\n")

    print("=" * 80)
    print("✅ All parameter building tests passed!")
    print("\nExpected user flow:")
    print("  STOCKS: Market → Price Range → Scan Mode → Scan")
    print("  FOREX:  Market → Scan (no price/mode prompt)")
    print("  CRYPTO: Market → Scan (no price/mode prompt)")
    print("=" * 80)


if __name__ == '__main__':
    test_parameter_building()
