"""Compatibility stub for task_scheduler expected under src.backendbot.cron_jobs

This module provides a minimal, in-memory task scheduler API used by the UI
and some tests. It intentionally implements only the small subset of the
real scheduler API so the test-suite and UI can import it when a full
implementation is not present in the repository layout.

The stub is non-persistent and single-process; it's safe for unit tests.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List


class _StubScheduler:
    def __init__(self):
        self.running = False
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def start_scheduler(self):
        with self._lock:
            self.running = True

    def stop_scheduler(self):
        with self._lock:
            self.running = False

    def get_task_stats(self) -> Dict[str, int]:
        with self._lock:
            total = len(self._tasks)
            enabled = sum(1 for t in self._tasks.values() if t.get("enabled", True))
        return {"total_tasks": total, "enabled_tasks": enabled}

    def get_tasks_list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [dict(id=k, **v) for k, v in self._tasks.items()]

    def enable_task(self, task_id: str) -> bool:
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["enabled"] = True
                return True
            return False

    def disable_task(self, task_id: str) -> bool:
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["enabled"] = False
                return True
            return False


task_scheduler = _StubScheduler()

__all__ = ["task_scheduler"]
