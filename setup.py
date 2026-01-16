"""
Trading Signal Analyzer - Setup Script
Modular version (v2.0+) with pip installation support
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
else:
    requirements = [
        "yfinance>=0.2.28",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "tradingview-screener>=0.1.0",
        "rich>=13.0.0",
        "openpyxl>=3.1.0",
        "reportlab>=4.0.0",
    ]

# Optional dependencies
extras_require = {
    "polygon": ["polygon-api-client>=1.14.0"],
    "news": ["requests>=2.31.0"],
    "social": ["praw>=7.7.0"],
    "dev": [
        "pytest>=7.4.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
    ],
    "all": [
        "polygon-api-client>=1.14.0",
        "requests>=2.31.0",
        "praw>=7.7.0",
    ],
}

setup(
    # Package Metadata
    name="trading-signal-analyzer",
    version="2.0.0",
    description="Advanced multi-asset technical analysis and scanning tool for day trading",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # Author Information
    author="Michael Johnson",
    author_email="",  # Add if desired
    url="https://github.com/savowood/trading-signal-analyzer",

    # License
    license="GPL-3.0",

    # Classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Operating System :: OS Independent",
    ],

    # Package Discovery
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),

    # Python Version
    python_requires=">=3.8",

    # Dependencies
    install_requires=requirements,
    extras_require=extras_require,

    # Package Data
    package_data={
        "trading_analyzer": [
            "*.md",
            "data/*.json",
            "data/*.db",
        ],
    },

    # Entry Points (CLI commands)
    entry_points={
        "console_scripts": [
            "trading-analyzer=trading_analyzer.main:main",
            "tsa=trading_analyzer.main:main",  # Short alias
        ],
    },

    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/savowood/trading-signal-analyzer/issues",
        "Source": "https://github.com/savowood/trading-signal-analyzer",
        "Documentation": "https://github.com/savowood/trading-signal-analyzer/blob/v2.0-dev/README.md",
        "Changelog": "https://github.com/savowood/trading-signal-analyzer/blob/v2.0-dev/CHANGELOG.md",
        "Donate": "https://buymeacoffee.com/savowood",
    },

    # Keywords for PyPI search
    keywords=[
        "trading",
        "stocks",
        "forex",
        "cryptocurrency",
        "technical-analysis",
        "day-trading",
        "scanner",
        "momentum",
        "dark-flow",
        "short-squeeze",
        "vwap",
        "macd",
        "rsi",
        "financial-analysis",
    ],

    # Zip Safety
    zip_safe=False,
)
