"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

from typing import Dict, List, Any
from collections import LRUCache
import threading
import time
import logging

class PerformanceOptimizer:
    """
    Performance optimization for EPOCH5 components
    """
    def __init__(self, cache_size: int = 1000):
        self._cache = LRUCache(cache_size)
        self._locks: Dict[str, threading.Lock] = {}
        self._metrics: Dict[str, List[float]] = {}
        self.logger = logging.getLogger(__name__)
    
    def cache_result(self, key: str, value: Any, ttl: int = 300) -> None:
        """Cache a result with TTL"""
        expires = time.time() + ttl
        self._cache[key] = (value, expires)
    
    def get_cached(self, key: str) -> Any:
        """Get cached result if not expired"""
        if key in self._cache:
            value, expires = self._cache[key]
            if time.time() < expires:
                return value
            del self._cache[key]
        return None
    
    def get_lock(self, resource_id: str) -> threading.Lock:
        """Get or create a lock for a resource"""
        if resource_id not in self._locks:
            self._locks[resource_id] = threading.Lock()
        return self._locks[resource_id]
    
    def record_metric(self, operation: str, duration: float) -> None:
        """Record operation duration for performance tracking"""
        if operation not in self._metrics:
            self._metrics[operation] = []
        self._metrics[operation].append(duration)
        
        # Log if performance degrades
        avg = sum(self._metrics[operation]) / len(self._metrics[operation])
        if duration > avg * 2:
            self.logger.warning(
                f"Performance degradation detected for {operation}. "
                f"Duration: {duration:.2f}s, Avg: {avg:.2f}s"
            )
