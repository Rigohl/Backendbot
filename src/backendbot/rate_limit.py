"""
Rate limiting store for BackendBot
Handles rate limiting logic for both Redis and in-memory fallback
"""

import time
from typing import Dict, Tuple
from .cache import cache


class RateLimitStore:
    """Store for rate limiting data"""

    def __init__(self):
        # Fallback in-memory store for when Redis is not available
        self._memory_store: Dict[str, Tuple[int, float]] = {}

    def set_rate_limit(self, identifier: str, window_seconds: int = 60, max_requests: int = 100) -> bool:
        """
        Check if request is within rate limit
        Returns True if allowed, False if rate limited
        """
        current_time = time.time()

        # Try Redis first
        if cache.is_available():
            return cache.set_rate_limit(identifier, window_seconds, max_requests)

        # Fallback to memory
        key = f"ratelimit:{identifier}"

        if key in self._memory_store:
            count, window_start = self._memory_store[key]

            # Reset window if expired
            if current_time - window_start >= window_seconds:
                self._memory_store[key] = (1, current_time)
                return True

            # Check limit
            if count >= max_requests:
                return False

            # Increment counter
            self._memory_store[key] = (count + 1, window_start)
            return True
        else:
            # First request in window
            self._memory_store[key] = (1, current_time)
            return True

    def clear(self):
        """Clear all rate limiting data (for testing)"""
        self._memory_store.clear()

        # Also clear Redis if available
        if cache.is_available():
            try:
                # Clear all keys matching ratelimit:*
                redis_client = cache.redis
                if redis_client:
                    keys = redis_client.keys("ratelimit:*")
                    if keys:
                        redis_client.delete(*keys)
            except Exception:
                pass  # Ignore errors in clearing


# Global instance
rate_limit_store = RateLimitStore()