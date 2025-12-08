"""
Trading Analyzer Configuration
Centralized configuration for all scanner settings
"""
from pathlib import Path
import json
from typing import Dict, Any

# Version
VERSION = "1.1.0"
AUTHOR = "Michael Johnson"
LICENSE = "GPL v3"

# File paths
HOME_DIR = Path.home()
CACHE_DIR = HOME_DIR / 'Documents'
SETTINGS_FILE = HOME_DIR / '.trading_analyzer'

# API Keys (loaded from settings)
API_KEYS = {
    'finviz': None,
    'tradingview': None,
    'polygon': None,
    'alphavantage': None,
    'newsapi': None,
    'reddit_client_id': None,
    'reddit_client_secret': None
}

# Cache settings (in seconds)
CACHE_SETTINGS = {
    'scan_results': 900,        # 15 minutes
    'microcap_list': 14400,     # 4 hours
    'stock_data': 300,          # 5 minutes
    'dark_flow': 300,           # 5 minutes (real-time data)
    'forex_data': 300,          # 5 minutes
    'crypto_data': 180,         # 3 minutes (more volatile)
}

# NASDAQ FTP URLs
NASDAQ_FTP = {
    'listed': 'ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt',
    'other': 'ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt'
}

# 5 Pillars criteria
PILLARS = {
    'change': {
        'threshold': 10.0,      # 10%+ day change
        'weight': 0.20
    },
    'rel_vol': {
        'threshold': 5.0,       # 5x+ relative volume
        'weight': 0.20
    },
    'float': {
        'threshold': 20.0,      # <20M float
        'weight': 0.20
    },
    'price_range': {
        'min': 2.0,
        'max': 20.0,
        'weight': 0.20
    },
    'catalyst': {
        'weight': 0.20
    }
}

# Scan modes
SCAN_MODES = {
    'quick': {
        'name': 'Quick Scan',
        'description': 'Ultra-fast scan (~10-20 seconds)',
        'tradingview_queries': 3,
        'microcap_limit': 0,  # TradingView only
        'features': [
            'TradingView only (3 optimized queries)',
            'No micro-cap direct scan',
            '~150 top movers maximum',
            '15-minute result caching'
        ]
    },
    'smart': {
        'name': 'Smart Scan',
        'description': 'Fast scan (~30-60 seconds)',
        'tradingview_queries': 3,
        'microcap_limit': 500,
        'features': [
            'Multi-query TradingView (3 filters)',
            'Top 500 priority micro-caps',
            '15-minute result caching'
        ]
    },
    'deep': {
        'name': 'Deep Scan',
        'description': 'Comprehensive scan (~3-5 minutes)',
        'tradingview_queries': 3,
        'microcap_limit': None,  # All tickers
        'features': [
            'Multi-query TradingView (3 filters)',
            'ALL 6,301 micro-cap candidates',
            'Maximum coverage'
        ]
    }
}

# TradingView query configurations
TRADINGVIEW_QUERIES = {
    'standard': {
        'name': 'Standard Momentum',
        'filters': {
            'change_from_open': 10.0,
            'rel_vol': 5.0
        },
        'limit': 50
    },
    'microcap': {
        'name': 'Micro-Cap Focus',
        'filters': {
            'change_from_open': 5.0,
            'rel_vol': 3.0,
            'market_cap_max': 300_000_000
        },
        'limit': 50
    },
    'low_float': {
        'name': 'Ultra-Low Float',
        'filters': {
            'change_from_open': 3.0,
            'rel_vol': 2.0,
            'market_cap_max': 100_000_000
        },
        'limit': 50
    }
}

# Smart filtering keywords
ETF_KEYWORDS = [
    'ETF', 'FUND', 'TRUST', 'INDEX', 'LEVERAGED',
    'TREASURY', 'BOND', 'NOTE', 'BITCOIN', 'ETHEREUM',
    'GOLD', 'SILVER', 'COMMODITY'
]

# Priority exchanges for micro-caps
PRIORITY_EXCHANGES = ['NASDAQ', 'P', 'A', 'Z']  # P=NYSE Arca/NCM

# Rate limiting settings
RATE_LIMIT = {
    'workers': 3,               # Concurrent workers
    'delay_every': 10,          # Delay every N requests
    'delay_ms': 100,            # Delay duration in milliseconds
    'batch_size': 500           # Progress update every N tickers
}

# Price ranges (for menu)
PRICE_RANGES = {
    'default': (2.0, 20.0),
    'penny': (0.10, 2.0),
    'subpenny': (0.0001, 0.10),
    'midcap': (20.0, 100.0)
}

# Market choices
MARKETS = {
    '1': {'name': 'US Stocks (NASDAQ + NYSE)', 'filter': 'america', 'type': 'stocks'},
    '2': {'name': 'FOREX (Currency Pairs)', 'filter': 'forex', 'type': 'forex'},
    '3': {'name': 'Crypto (Digital Assets)', 'filter': 'crypto', 'type': 'crypto'},
    '4': {'name': 'NASDAQ only', 'filter': 'america', 'exchange': 'NASDAQ', 'type': 'stocks'},
    '5': {'name': 'NYSE only', 'filter': 'america', 'exchange': 'NYSE', 'type': 'stocks'}
}

# FOREX pairs (major and minor pairs)
FOREX_PAIRS = {
    'majors': [
        'EURUSD=X',  # Euro / US Dollar
        'GBPUSD=X',  # British Pound / US Dollar
        'USDJPY=X',  # US Dollar / Japanese Yen
        'USDCHF=X',  # US Dollar / Swiss Franc
        'AUDUSD=X',  # Australian Dollar / US Dollar
        'USDCAD=X',  # US Dollar / Canadian Dollar
        'NZDUSD=X',  # New Zealand Dollar / US Dollar
    ],
    'minors': [
        'EURGBP=X',  # Euro / British Pound
        'EURJPY=X',  # Euro / Japanese Yen
        'GBPJPY=X',  # British Pound / Japanese Yen
        'EURCHF=X',  # Euro / Swiss Franc
        'EURAUD=X',  # Euro / Australian Dollar
        'EURCAD=X',  # Euro / Canadian Dollar
        'GBPCHF=X',  # British Pound / Swiss Franc
        'GBPAUD=X',  # British Pound / Australian Dollar
        'AUDJPY=X',  # Australian Dollar / Japanese Yen
        'CADJPY=X',  # Canadian Dollar / Japanese Yen
    ],
    'exotics': [
        'USDMXN=X',  # US Dollar / Mexican Peso
        'USDZAR=X',  # US Dollar / South African Rand
        'USDTRY=X',  # US Dollar / Turkish Lira
        'USDBRL=X',  # US Dollar / Brazilian Real
    ]
}

# Crypto pairs (major cryptocurrencies)
CRYPTO_PAIRS = {
    'major': [
        'BTC-USD',   # Bitcoin
        'ETH-USD',   # Ethereum
        'BNB-USD',   # Binance Coin
        'XRP-USD',   # Ripple
        'ADA-USD',   # Cardano
        'SOL-USD',   # Solana
        'DOGE-USD',  # Dogecoin
        'MATIC-USD', # Polygon
        'DOT-USD',   # Polkadot
        'AVAX-USD',  # Avalanche
    ],
    'defi': [
        'UNI-USD',   # Uniswap
        'LINK-USD',  # Chainlink
        'AAVE-USD',  # Aave
        'CRV-USD',   # Curve
        'SUSHI-USD', # SushiSwap
    ],
    'altcoins': [
        'LTC-USD',   # Litecoin
        'BCH-USD',   # Bitcoin Cash
        'XLM-USD',   # Stellar
        'ALGO-USD',  # Algorand
        'VET-USD',   # VeChain
        'ATOM-USD',  # Cosmos
        'FIL-USD',   # Filecoin
        'TRX-USD',   # Tron
        'ETC-USD',   # Ethereum Classic
    ]
}

# FOREX screening criteria (different from stocks)
FOREX_CRITERIA = {
    'min_change': 0.5,      # 0.5% move is significant for forex
    'min_atr': 0.003,       # Minimum Average True Range
    'timeframes': ['1h', '4h', '1d'],
}

# Crypto screening criteria
CRYPTO_CRITERIA = {
    'min_change': 5.0,      # 5% move
    'min_volume_usd': 1_000_000,  # $1M minimum 24h volume
    'min_rel_vol': 2.0,     # 2x relative volume
    'max_market_cap': None, # No market cap limit
}

# Dark Flow settings
DARK_FLOW = {
    'enabled': True,
    'min_block_size': 10000,           # Minimum shares for block trade
    'min_dollar_value': 100000,        # Minimum $100k for dark pool print
    'unusual_volume_threshold': 3.0,   # 3x average volume
    'options_flow': {
        'min_premium': 50000,          # Minimum $50k premium
        'unusual_oi_threshold': 2.0,   # 2x normal open interest
        'sweep_detect': True,          # Detect multi-leg sweeps
    },
    'institutional_indicators': [
        'Large block trades',
        'After-hours accumulation',
        'Unusual options activity',
        'Dark pool prints',
        'Algorithmic patterns'
    ]
}

# Technical analysis settings
TECHNICAL_SETTINGS = {
    'vwap_bands': [2, 3],       # 2σ and 3σ
    'macd': {
        'fast': 12,
        'slow': 26,
        'signal': 9
    },
    'rsi': {
        'period': 14,
        'oversold': 30,
        'overbought': 70
    },
    'supertrend': {
        'period': 10,
        'multiplier': 3.0
    }
}

# Minimum score threshold
MIN_SCORE = 50  # Out of 100

# Display settings
MAX_RESULTS_DISPLAY = 50


# ============================================================================
# SETTINGS FILE SUPPORT
# ============================================================================

def load_user_settings() -> Dict[str, Any]:
    """
    Load user settings from ~/.trading_analyzer

    Settings file format (JSON):
    {
        "cache_settings": {
            "scan_results": 900
        },
        "rate_limit": {
            "workers": 3,
            "delay_ms": 100
        },
        "pillars": {
            "change": {"threshold": 10.0},
            "rel_vol": {"threshold": 5.0}
        },
        "api_keys": {
            "tradingview": "your_key_here"
        }
    }
    """
    if not SETTINGS_FILE.exists():
        return {}

    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        return settings
    except Exception as e:
        print(f"⚠️  Failed to load settings from {SETTINGS_FILE}: {e}")
        return {}


def apply_user_settings(settings: Dict[str, Any]):
    """Apply user settings to override defaults"""
    global CACHE_SETTINGS, RATE_LIMIT, PILLARS, MIN_SCORE, MAX_RESULTS_DISPLAY, API_KEYS

    # Apply cache settings
    if 'cache_settings' in settings:
        for key, value in settings['cache_settings'].items():
            if key in CACHE_SETTINGS:
                CACHE_SETTINGS[key] = value

    # Apply rate limit settings
    if 'rate_limit' in settings:
        for key, value in settings['rate_limit'].items():
            if key in RATE_LIMIT:
                RATE_LIMIT[key] = value

    # Apply pillar thresholds
    if 'pillars' in settings:
        for pillar, config in settings['pillars'].items():
            if pillar in PILLARS:
                PILLARS[pillar].update(config)

    # Apply display settings
    if 'min_score' in settings:
        MIN_SCORE = settings['min_score']

    if 'max_results_display' in settings:
        MAX_RESULTS_DISPLAY = settings['max_results_display']

    # Apply API keys
    if 'api_keys' in settings:
        for key, value in settings['api_keys'].items():
            if key in API_KEYS and value and value.strip():
                API_KEYS[key] = value.strip()


def create_default_settings_file():
    """Create default settings file with examples"""
    default_settings = {
        "_comment": "Trading Analyzer User Settings",
        "_note": "Customize these values to override defaults",
        "disclaimer_acknowledged": False,
        "pressure_cooker_disclaimer_acknowledged": False,
        "cache_settings": {
            "scan_results": 900,
            "microcap_list": 14400,
            "stock_data": 300
        },
        "rate_limit": {
            "workers": 3,
            "delay_every": 10,
            "delay_ms": 100,
            "batch_size": 500
        },
        "pillars": {
            "change": {
                "threshold": 10.0,
                "weight": 0.20
            },
            "rel_vol": {
                "threshold": 5.0,
                "weight": 0.20
            },
            "float": {
                "threshold": 20.0,
                "weight": 0.20
            },
            "price_range": {
                "min": 2.0,
                "max": 20.0,
                "weight": 0.20
            }
        },
        "min_score": 50,
        "max_results_display": 50,
        "api_keys": {
            "_note": "Add your API keys here to enable enhanced features",
            "finviz": "",
            "tradingview": "",
            "polygon": "",
            "alphavantage": "",
            "newsapi": "",
            "reddit_client_id": "",
            "reddit_client_secret": ""
        },
        "cron_jobs": {
            "_note": "Configure automated scans",
            "enabled": False,
            "daily_scan": {
                "enabled": False,
                "time": "16:30",
                "scan_types": ["momentum"],
                "markets": ["1"],
                "notify_on_results": True,
                "min_score_threshold": 70
            },
            "notification": {
                "desktop": True,
                "email": False,
                "email_address": ""
            }
        }
    }

    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(default_settings, f, indent=2)
        print(f"✅ Created default settings file: {SETTINGS_FILE}")
        print(f"   Edit this file to customize your settings")
        return True
    except Exception as e:
        print(f"❌ Failed to create settings file: {e}")
        return False


def save_user_settings(settings: Dict[str, Any]) -> bool:
    """
    Save user settings to ~/.trading_analyzer

    Args:
        settings: Settings dictionary to save

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ Failed to save settings: {e}")
        return False


def get_settings_info() -> Dict[str, Any]:
    """Get information about current settings"""
    # Create API key status (show configured but mask the actual keys)
    api_key_status = {}
    for key, value in API_KEYS.items():
        if value:
            # Show first 4 and last 4 characters
            if len(value) > 12:
                masked = f"{value[:4]}...{value[-4:]}"
            else:
                masked = f"{value[:2]}...{value[-2:]}"
            api_key_status[key] = f"✅ Configured ({masked})"
        else:
            api_key_status[key] = "❌ Not configured"

    return {
        'settings_file': str(SETTINGS_FILE),
        'exists': SETTINGS_FILE.exists(),
        'cache_settings': CACHE_SETTINGS.copy(),
        'rate_limit': RATE_LIMIT.copy(),
        'pillars': PILLARS.copy(),
        'min_score': MIN_SCORE,
        'max_results_display': MAX_RESULTS_DISPLAY,
        'api_keys': api_key_status
    }
