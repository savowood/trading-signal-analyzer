"""
Trading Analyzer Utilities Package

High-performance utilities for:
- Parallel processing
- Smart pre-filtering
- Advanced technical analysis (S/R, Volume Profile)
- ASCII charts with colors
- Export functionality (CSV/Excel/PDF)
- Data validation
"""

from .parallel import parallel_analyze, ParallelProcessor, ParallelConfig
from .prefilter import (
    SmartPreFilter,
    FilterCriteria,
    create_pressure_cooker_prefilter,
    create_momentum_prefilter,
    create_darkflow_prefilter
)
from .technical import (
    TechnicalAnalyzer,
    SupportResistance,
    VolumeProfile
)
from .charts import ASCIIChartGenerator, ChartConfig
from .export import ResultExporter
from .validation import DataValidator, ValidationResult, ValidationIssue
from .ticker_utils import normalize_ticker, is_crypto_ticker, normalize_ticker_list

__all__ = [
    # Parallel processing
    'parallel_analyze',
    'ParallelProcessor',
    'ParallelConfig',

    # Pre-filtering
    'SmartPreFilter',
    'FilterCriteria',
    'create_pressure_cooker_prefilter',
    'create_momentum_prefilter',
    'create_darkflow_prefilter',

    # Technical analysis
    'TechnicalAnalyzer',
    'SupportResistance',
    'VolumeProfile',

    # Charts
    'ASCIIChartGenerator',
    'ChartConfig',

    # Export
    'ResultExporter',

    # Validation
    'DataValidator',
    'ValidationResult',
    'ValidationIssue',

    # Ticker utilities
    'normalize_ticker',
    'is_crypto_ticker',
    'normalize_ticker_list',
]
