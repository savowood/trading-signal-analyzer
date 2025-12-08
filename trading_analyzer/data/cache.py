"""
Unified Caching System
Handles all caching needs with TTL support
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from dataclasses import asdict

from ..config import CACHE_DIR, CACHE_SETTINGS


class Cache:
    """Single cache with TTL support"""

    def __init__(self, name: str, ttl_seconds: int):
        self.name = name
        self.ttl_seconds = ttl_seconds
        self.cache_file = CACHE_DIR / f"trading_analyzer_{name}.json"

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        try:
            if not self.cache_file.exists():
                return None

            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)

            # Check if key exists
            if key not in cache_data:
                return None

            entry = cache_data[key]

            # Check expiration
            last_updated = datetime.fromisoformat(entry['timestamp'])
            age_seconds = (datetime.now() - last_updated).total_seconds()

            if age_seconds >= self.ttl_seconds:
                return None

            return entry['data']

        except Exception as e:
            # Cache read failed - return None
            return None

    def set(self, key: str, value: Any) -> bool:
        """Set cached value with timestamp"""
        try:
            # Load existing cache
            cache_data = {}
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)

            # Add/update entry
            cache_data[key] = {
                'timestamp': datetime.now().isoformat(),
                'data': value
            }

            # Save cache
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

            return True

        except Exception as e:
            # Silently fail - caching is optional
            return False

    def clear(self, key: Optional[str] = None):
        """Clear cache (specific key or all)"""
        try:
            if key is None:
                # Clear entire cache
                if self.cache_file.exists():
                    self.cache_file.unlink()
            else:
                # Clear specific key
                if self.cache_file.exists():
                    with open(self.cache_file, 'r') as f:
                        cache_data = json.load(f)

                    if key in cache_data:
                        del cache_data[key]

                    with open(self.cache_file, 'w') as f:
                        json.dump(cache_data, f, indent=2)

        except Exception:
            pass

    def get_age(self, key: str) -> Optional[float]:
        """Get age of cached entry in minutes"""
        try:
            if not self.cache_file.exists():
                return None

            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)

            if key not in cache_data:
                return None

            last_updated = datetime.fromisoformat(cache_data[key]['timestamp'])
            age_seconds = (datetime.now() - last_updated).total_seconds()

            return age_seconds / 60

        except Exception:
            return None


class CacheManager:
    """Manages all application caches"""

    def __init__(self):
        self.caches: Dict[str, Cache] = {}

        # Initialize caches from config
        for name, ttl in CACHE_SETTINGS.items():
            self.caches[name] = Cache(name, ttl)

    def get(self, cache_name: str, key: str) -> Optional[Any]:
        """Get from specific cache"""
        if cache_name not in self.caches:
            raise ValueError(f"Unknown cache: {cache_name}")

        return self.caches[cache_name].get(key)

    def set(self, cache_name: str, key: str, value: Any) -> bool:
        """Set in specific cache"""
        if cache_name not in self.caches:
            raise ValueError(f"Unknown cache: {cache_name}")

        return self.caches[cache_name].set(key, value)

    def clear(self, cache_name: Optional[str] = None, key: Optional[str] = None):
        """Clear cache(s)"""
        if cache_name is None:
            # Clear all caches
            for cache in self.caches.values():
                cache.clear()
        else:
            # Clear specific cache
            if cache_name not in self.caches:
                raise ValueError(f"Unknown cache: {cache_name}")

            self.caches[cache_name].clear(key)

    def get_age(self, cache_name: str, key: str) -> Optional[float]:
        """Get age of cached entry in minutes"""
        if cache_name not in self.caches:
            raise ValueError(f"Unknown cache: {cache_name}")

        return self.caches[cache_name].get_age(key)

    def get_status(self) -> Dict[str, Any]:
        """Get status of all caches"""
        status = {}

        for name, cache in self.caches.items():
            try:
                if cache.cache_file.exists():
                    with open(cache.cache_file, 'r') as f:
                        cache_data = json.load(f)
                    status[name] = {
                        'entries': len(cache_data),
                        'file': str(cache.cache_file),
                        'ttl_minutes': cache.ttl_seconds / 60
                    }
                else:
                    status[name] = {
                        'entries': 0,
                        'file': str(cache.cache_file),
                        'ttl_minutes': cache.ttl_seconds / 60
                    }
            except Exception:
                status[name] = {'error': 'Failed to read cache'}

        return status


# Global cache manager instance
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager (singleton)"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
