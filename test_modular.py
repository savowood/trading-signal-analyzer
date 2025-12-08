#!/usr/bin/env python3
"""
Test script for modular trading analyzer
Verifies all imports and basic functionality
"""

print("Testing modular trading analyzer...")
print("=" * 80)

# Test imports
print("\n[1] Testing imports...")
try:
    from trading_analyzer import config
    print("  ✅ config")

    from trading_analyzer.core import scanner
    print("  ✅ core.scanner")

    from trading_analyzer.data import cache, filters, providers
    print("  ✅ data.cache")
    print("  ✅ data.filters")
    print("  ✅ data.providers")

    from trading_analyzer.scanners import momentum
    print("  ✅ scanners.momentum")

    from trading_analyzer.ui import cli, display
    print("  ✅ ui.cli")
    print("  ✅ ui.display")

    from trading_analyzer import main
    print("  ✅ main")

    print("\n✅ All imports successful!")

except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test basic functionality
print("\n[2] Testing basic functionality...")
try:
    # Test ScanParameters
    params = scanner.ScanParameters(
        market_choice='1',
        min_price=2.0,
        max_price=20.0,
        mode=scanner.ScanMode.SMART
    )
    print(f"  ✅ ScanParameters created: {params.to_cache_key()}")

    # Test ScanResult
    result = scanner.ScanResult(
        ticker="TEST",
        price=10.0,
        score=4,
        rel_vol=7.5,
        float_m=15.0,
        change_pct=12.5
    )
    print(f"  ✅ ScanResult created: {result.ticker} @ ${result.price}")

    # Test CacheManager
    cache_mgr = cache.get_cache_manager()
    print(f"  ✅ CacheManager created")

    # Test TickerFilter
    test_tickers = [
        {'ticker': 'AAPL', 'name': 'Apple Inc', 'exchange': 'NASDAQ'},
        {'ticker': 'TEST.W', 'name': 'Test Warrant', 'exchange': 'NASDAQ'},
        {'ticker': 'BOND', 'name': 'Bond ETF', 'exchange': 'NYSE'}
    ]
    ticker_filter = filters.TickerFilter()
    filtered = ticker_filter.filter(test_tickers)
    print(f"  ✅ TickerFilter: {len(test_tickers)} → {len(filtered)} tickers")

    # Test MomentumScanner creation
    momentum_scanner = momentum.create_scanner()
    print(f"  ✅ MomentumScanner created: {momentum_scanner.name}")

    print("\n✅ All functionality tests passed!")

except Exception as e:
    print(f"\n❌ Functionality test failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Count lines of code
print("\n[3] Code statistics...")
import os
from pathlib import Path

def count_lines(directory):
    """Count lines of Python code"""
    total = 0
    files = 0

    for root, dirs, filenames in os.walk(directory):
        # Skip __pycache__
        if '__pycache__' in root:
            continue

        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                with open(filepath, 'r') as f:
                    lines = len(f.readlines())
                    total += lines
                    files += 1
                    print(f"  {filepath.replace(str(directory), '.')}: {lines} lines")

    return total, files

base_dir = Path(__file__).parent / 'trading_analyzer'
total_lines, total_files = count_lines(base_dir)

print(f"\n📊 Total: {total_lines} lines across {total_files} files")
print(f"  Average: {total_lines // total_files} lines per file")

# Compare with old version
old_file = Path(__file__).parent / 'trading_signal_analyzer.py'
if old_file.exists():
    with open(old_file, 'r') as f:
        old_lines = len(f.readlines())

    reduction = ((old_lines - total_lines) / old_lines) * 100
    print(f"\n📈 Comparison:")
    print(f"  Old version: {old_lines} lines (monolithic)")
    print(f"  New version: {total_lines} lines (modular)")
    print(f"  Reduction: {reduction:.1f}%")

print("\n" + "=" * 80)
print("✅ All tests passed! Modular architecture is ready.")
print("=" * 80)
print("\nTo run the new modular scanner:")
print("  python -m trading_analyzer.main")
print("\nOr:")
print("  cd trading_analyzer && python main.py")
