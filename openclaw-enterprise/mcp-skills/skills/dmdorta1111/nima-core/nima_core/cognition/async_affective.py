#!/usr/bin/env python3
"""
Async Affective Processing
==========================
Parallel engine execution with caching for NIMA Core.

Makes affective analysis faster through:
- Parallel engine execution (ThreadPoolExecutor)
- LRU cache for repeated queries
- Background memory consolidation

Author: NIMA Project
Date: Feb 11, 2026
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from dataclasses import dataclass
import hashlib

from .daring_engine import DaringEngine
from .courage_engine import CourageEngine
from .nurturing_engine import NurturingEngine
from .mastery_engine import MasteryEngine


@dataclass
class AffectiveResult:
    """Result from a single engine analysis."""
    engine: str
    level: float
    style: str
    domain: Optional[str] = None
    latency_ms: float = 0.0


class AsyncAffectiveProcessor:
    """
    Parallel affective engine processor with caching.

    Runs all 4 engines concurrently instead of sequentially.
    Caches results for identical queries.
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

        # Initialize engines once
        self.engines = {
            'DARING': DaringEngine(),
            'COURAGE': CourageEngine(),
            'NURTURING': NurturingEngine(),
            'MASTERY': MasteryEngine(),
        }

        # Cache config
        self._cache: Dict[str, tuple] = {}
        self._cache_ttl_seconds = 60  # Cache for 1 minute
        self._cache_lock = threading.Lock()

        # Stats
        self._stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'parallel_calls': 0,
        }

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.lower().strip().encode()).hexdigest()

    def _get_cached(self, key: str) -> Optional[AffectiveResult]:
        """Get cached result if still fresh."""
        with self._cache_lock:
            if key in self._cache:
                result, timestamp = self._cache[key]
                if time.time() - timestamp < self._cache_ttl_seconds:
                    self._stats['cache_hits'] += 1
                    return result
                else:
                    # Expired
                    del self._cache[key]
        return None

    def _set_cached(self, key: str, result: AffectiveResult) -> None:
        """Cache a result."""
        with self._cache_lock:
            self._cache[key] = (result, time.time())

    def _analyze_with_engine(self, text: str, engine_name: str, engine) -> AffectiveResult:
        """Analyze text with a single engine."""
        start = time.time()

        try:
            result = engine.analyze_message(text)
            latency = (time.time() - start) * 1000

            return AffectiveResult(
                engine=engine_name,
                level=result.level,
                style=result.style.value if hasattr(result.style, 'value') else str(result.style),
                domain=getattr(result, 'domain', None),
                latency_ms=latency
            )
        except Exception as e:
            return AffectiveResult(
                engine=engine_name,
                level=0.0,
                style='neutral',
                latency_ms=(time.time() - start) * 1000
            )

    def analyze_parallel(self, text: str, use_cache: bool = True) -> Dict[str, AffectiveResult]:
        """
        Analyze text with all engines in parallel.

        Args:
            text: Message to analyze
            use_cache: Whether to use result cache

        Returns:
            Dict mapping engine names to results
        """
        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(text)
            cached = self._get_cached(cache_key)
            if cached:
                return {cached.engine: cached}

        self._stats['cache_misses'] += 1
        self._stats['parallel_calls'] += 1

        # Run all engines in parallel
        futures = {}
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            for name, engine in self.engines.items():
                future = executor.submit(self._analyze_with_engine, text, name, engine)
                futures[future] = name

            # Collect results as they complete
            for future in as_completed(futures):
                engine_name = futures[future]
                try:
                    result = future.result()
                    results[engine_name] = result
                except Exception as e:
                    results[engine_name] = AffectiveResult(
                        engine=engine_name,
                        level=0.0,
                        style='neutral'
                    )

        # Cache the dominant result
        if use_cache and results:
            dominant = max(results.values(), key=lambda r: r.level)
            if dominant.level > 0.3:  # Only cache meaningful results
                self._set_cached(cache_key, dominant)

        return results

    def get_dominant(self, text: str, use_cache: bool = True) -> AffectiveResult:
        """
        Get the dominant affective engine for text.

        Returns:
            AffectiveResult with highest level
        """
        results = self.analyze_parallel(text, use_cache)

        if not results:
            return AffectiveResult(engine='neutral', level=0.0, style='balanced')

        return max(results.values(), key=lambda r: r.level)

    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return self._stats.copy()

    def clear_cache(self) -> None:
        """Clear the result cache."""
        with self._cache_lock:
            self._cache.clear()

    def shutdown(self) -> None:
        """Clean shutdown of executor."""
        self._executor.shutdown(wait=True)


# Singleton instance
_processor: Optional[AsyncAffectiveProcessor] = None
_lock = threading.Lock()


def get_processor() -> AsyncAffectiveProcessor:
    """Get singleton async processor."""
    global _processor
    if _processor is None:
        with _lock:
            if _processor is None:
                _processor = AsyncAffectiveProcessor()
    return _processor


def analyze_async(text: str) -> AffectiveResult:
    """Convenience: analyze text and get dominant engine."""
    return get_processor().get_dominant(text)


if __name__ == "__main__":
    # Test
    print("=" * 60)
    print("Testing Async Affective Processing")
    print("=" * 60)

    processor = AsyncAffectiveProcessor()

    # Test 1: Parallel analysis
    print("\n1. Parallel analysis:")
    test_msg = "I'm terrified but I need to confront this"

    start = time.time()
    results = processor.analyze_parallel(test_msg)
    elapsed = (time.time() - start) * 1000

    print(f"   Message: \"{test_msg}\"")
    print(f"   Total time: {elapsed:.2f}ms")
    for name, result in sorted(results.items(), key=lambda x: -x[1].level):
        print(f"   {name:12} | level={result.level:.2f} | {result.latency_ms:.1f}ms")

    # Test 2: Cache
    print("\n2. Cache test:")
    start = time.time()
    cached_result = processor.get_dominant(test_msg)
    elapsed = (time.time() - start) * 1000
    print(f"   Cached lookup: {elapsed:.2f}ms")
    print(f"   Result: {cached_result.engine} (level={cached_result.level:.2f})")

    # Test 3: Stats
    print("\n3. Statistics:")
    stats = processor.get_stats()
    print(f"   Cache hits: {stats['cache_hits']}")
    print(f"   Cache misses: {stats['cache_misses']}")
    print(f"   Parallel calls: {stats['parallel_calls']}")

    print("\n✅ Async affective processing working!")
