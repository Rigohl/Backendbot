"""Minimal OperationModeManager implementation for src package compatibility.

This module provides a tiny OperationModeManager and a module-level
`mode_manager` instance to satisfy imports from `src.backendbot.modes` and
other modules during tests. It intentionally keeps behavior minimal.
"""

from typing import Any


class OperationModeManager:
    def __init__(self) -> None:
        self._mode = "default"

    def get_mode(self) -> str:
        return self._mode

    def set_mode(self, mode: str) -> None:
        self._mode = mode

    def _configure_monitoring_thresholds(self):
        if self._mode == "aggressive":
            return {"cpu": 70, "memory": 75, "disk": 80}
        return {"cpu": 80, "memory": 85, "disk": 90}

    def get_mode_info(self):
        return {"mode": self._mode}

    def get_monitoring_interval(self) -> float:
        return 2.0 if self._mode == "aggressive" else 5.0


mode_manager = OperationModeManager()

__all__ = ["OperationModeManager", "mode_manager"]
