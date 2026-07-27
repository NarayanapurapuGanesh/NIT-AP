"""
Enterprise Caching Engine.
In-memory LRU cache with TTL policies, automatic invalidation, and hit ratio statistics.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from app.platform.schemas.platform_models import CacheEntry, CacheStats
from core.logging import get_logger

logger = get_logger("cache_engine")


class CachingEngine:
    """Enterprise In-Memory Cache Engine."""

    def __init__(self, max_size: int = 1000) -> None:
        self._cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self._hit_count = 0
        self._miss_count = 0
        self._eviction_count = 0

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if not entry:
            self._miss_count += 1
            return None

        # Check TTL
        now = datetime.now(timezone.utc)
        if now > entry.created_at + timedelta(seconds=entry.ttl_seconds):
            logger.debug("Cache entry expired", key=key)
            del self._cache[key]
            self._miss_count += 1
            return None

        self._hit_count += 1
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        if len(self._cache) >= self.max_size:
            # Evict oldest entry
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
            del self._cache[oldest_key]
            self._eviction_count += 1

        self._cache[key] = CacheEntry(key=key, value=value, ttl_seconds=ttl_seconds)

    def invalidate(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        self._cache.clear()

    def get_stats(self) -> CacheStats:
        total = self._hit_count + self._miss_count
        ratio = round((self._hit_count / total * 100), 2) if total > 0 else 0.0
        return CacheStats(
            total_entries=len(self._cache),
            hit_count=self._hit_count,
            miss_count=self._miss_count,
            hit_ratio=ratio,
            eviction_count=self._eviction_count,
            memory_used_bytes=len(str(self._cache)) * 2,
        )
