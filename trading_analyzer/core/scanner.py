"""
Core Scanner Interfaces and Data Structures
Base classes for all scanner implementations
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class ScanMode(Enum):
    """Scan mode enumeration"""
    QUICK = "quick"
    SMART = "smart"
    DEEP = "deep"


@dataclass
class ScanResult:
    """Standardized scan result"""
    ticker: str
    price: float
    score: int  # Pillars met (0-5)

    # Metrics
    rel_vol: float
    float_m: float
    change_pct: float

    # Optional fields
    week_change: float = 0.0
    catalyst: str = "PRESENT"
    low_float: bool = False
    description: str = ""
    source: str = "UNKNOWN"
    exchange: str = ""

    # Raw metrics for scoring
    volume: int = 0
    market_cap: float = 0

    def __post_init__(self):
        """Calculate derived fields"""
        self.low_float = self.float_m < 20

    def to_dict(self) -> Dict:
        """Convert to dictionary for display"""
        return {
            'Ticker': self.ticker,
            'Price': self.price,
            'RelVol': self.rel_vol,
            'Float(M)': self.float_m,
            'Score': self.score,
            'Week%': self.week_change,
            'Today%': self.change_pct,
            'Catalyst': self.catalyst,
            'LowFloat': self.low_float,
            'Description': self.description
        }


@dataclass
class ScanParameters:
    """Scan parameters"""
    market_choice: str = '1'
    min_price: float = 2.0
    max_price: float = 20.0
    mode: ScanMode = ScanMode.SMART

    # 5 Pillars thresholds
    min_change: float = 10.0
    min_rel_vol: float = 5.0
    max_float: float = 20.0

    def to_cache_key(self) -> str:
        """Generate cache key"""
        return f"{self.market_choice}_{self.min_price}_{self.max_price}_{self.mode.value}"

    def to_dict(self) -> Dict:
        """Convert to dictionary for caching"""
        return {
            'market_choice': self.market_choice,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'mode': self.mode.value,
            'min_change': self.min_change,
            'min_rel_vol': self.min_rel_vol,
            'max_float': self.max_float
        }


class Scanner(ABC):
    """Base scanner interface"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def scan(self, params: ScanParameters) -> List[ScanResult]:
        """
        Perform scan with given parameters

        Args:
            params: Scan parameters

        Returns:
            List of scan results
        """
        pass

    def _validate_params(self, params: ScanParameters) -> bool:
        """Validate scan parameters"""
        if params.min_price >= params.max_price:
            raise ValueError("min_price must be less than max_price")
        if params.min_change < 0:
            raise ValueError("min_change must be positive")
        if params.min_rel_vol < 0:
            raise ValueError("min_rel_vol must be positive")
        return True


class CompositeScanner(Scanner):
    """
    Scanner that combines results from multiple providers
    Implements the hybrid scanning approach
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.providers: List[Scanner] = []

    def add_provider(self, provider: Scanner):
        """Add a data provider"""
        self.providers.append(provider)

    def scan(self, params: ScanParameters) -> List[ScanResult]:
        """
        Scan using all providers and merge results

        Args:
            params: Scan parameters

        Returns:
            Merged and deduplicated results
        """
        self._validate_params(params)

        all_results = []
        seen_tickers = set()

        for provider in self.providers:
            try:
                results = provider.scan(params)

                # Deduplicate
                for result in results:
                    if result.ticker not in seen_tickers:
                        all_results.append(result)
                        seen_tickers.add(result.ticker)

            except Exception as e:
                print(f"⚠️  Provider {provider.name} failed: {e}")
                continue

        # Sort by score and today's change
        all_results.sort(key=lambda x: (x.score, x.change_pct), reverse=True)

        return all_results


def calculate_pillars_score(result: ScanResult, params: ScanParameters) -> int:
    """
    Calculate how many of the 5 pillars are met

    Args:
        result: Scan result
        params: Scan parameters

    Returns:
        Number of pillars met (0-5)
    """
    pillars_met = 0

    # Pillar 1: Change percentage
    if result.change_pct >= params.min_change:
        pillars_met += 1

    # Pillar 2: Relative volume
    if result.rel_vol >= params.min_rel_vol:
        pillars_met += 1

    # Pillar 3: Low float
    if result.float_m < params.max_float:
        pillars_met += 1

    # Pillar 4: Price range
    if params.min_price <= result.price <= params.max_price:
        pillars_met += 1

    # Pillar 5: Catalyst (if change and volume both good)
    if result.change_pct >= params.min_change and result.rel_vol >= params.min_rel_vol:
        pillars_met += 1

    return pillars_met


def calculate_quality_score(result: ScanResult) -> int:
    """
    Calculate 0-100 quality score based on metrics

    Args:
        result: Scan result

    Returns:
        Quality score (0-100)
    """
    score = 0

    # Change score (max 30 points)
    if result.change_pct >= 50:
        score += 30
    elif result.change_pct >= 25:
        score += 25
    elif result.change_pct >= 15:
        score += 20
    else:
        score += 15

    # Relative volume score (max 30 points)
    if result.rel_vol >= 20:
        score += 30
    elif result.rel_vol >= 10:
        score += 25
    elif result.rel_vol >= 7:
        score += 20
    else:
        score += 15

    # Float score (max 20 points)
    if result.float_m < 1:
        score += 20
    elif result.float_m < 5:
        score += 15
    elif result.float_m < 10:
        score += 10
    elif result.float_m < 20:
        score += 5

    # Price range bonus (max 10 points)
    if 5 <= result.price <= 15:
        score += 10
    elif 3 <= result.price <= 20:
        score += 5

    # Strong momentum bonus (max 10 points)
    if result.change_pct >= 20 and result.rel_vol >= 10:
        score += 10
    elif result.change_pct >= 15 and result.rel_vol >= 7:
        score += 5

    return score
