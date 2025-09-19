from contextlib import contextmanager
from typing import Generator, Optional


class DatabaseManager:
    """Minimal shim for DatabaseManager used in tests.

    Provides the methods expected by workers (log_metric) but implemented
    as no-ops so tests can import and run without a real DB backend.
    """

    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn

    def log_metric(self, metric):
        # No-op for test environment
        return None


@contextmanager
def get_db() -> Generator[DatabaseManager, None, None]:
    manager = DatabaseManager()
    try:
        yield manager
    finally:
        pass


__all__ = ["DatabaseManager", "get_db"]

# Minimal system metrics service shim used by API during tests
class _SystemMetricsService:
    def get_latest(self):
        return {}


system_metrics_service = _SystemMetricsService()

__all__.append("system_metrics_service")
