
import json
import logging
import os
from enum import Enum
from datetime import datetime
from typing import Any, Dict, Optional
import abc
from pathlib import Path


class BotState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"



class BaseBot(abc.ABC):
    """Minimal BaseBot implementation used by worker classes in tests.

    This class intentionally provides a thin, test-friendly surface with
    common attributes used by the workers (ids, counters, config, logger).
    It is not a full production feature-complete implementation.
    """
    @abc.abstractmethod
    def validate_config(self, config: dict) -> bool:
        """Validar la configuración del bot. Obligatorio en todos los bots concretos."""
        pass

    def __init__(self, bot_id: str, name: str = "BaseBot", description: str = ""):
        self.bot_id: str = bot_id
        self.name: str = name
        self.description: str = description
        self.logger = logging.getLogger("backendbot")
        self.config: Dict[str, Any] = {}
        # Allow subclass to provide defaults by implementing _load_default_config
        try:
            defaults = self._load_default_config()
            if isinstance(defaults, dict):
                self.config.update(defaults)
        except Exception:
            # If subclass does not implement or raises, ignore and continue
            pass

        # Runtime metrics
        self.success_count: int = 0
        self.error_count: int = 0
        self.last_activity: Optional[datetime] = None
        self._state: BotState = BotState.STOPPED
        # Flexible stats store for recording bot-specific metrics
        self._stats: Dict[str, Any] = {}

        # Try to load persisted stats (non-fatal)
        try:
            self._load_persisted_stats()
        except Exception:
            # Avoid breaking tests if file system unavailable
            pass

    def _load_default_config(self) -> Dict[str, Any]:
        return {}

    def start(self) -> None:
        self._state = BotState.RUNNING
        self.on_starting()
        self.on_started()

    def stop(self) -> None:
        self.on_stopping()
        self._state = BotState.STOPPED
        self.on_stopped()

    def on_starting(self) -> None:
        pass

    def on_started(self) -> None:
        pass

    def on_stopping(self) -> None:
        pass

    def on_stopped(self) -> None:
        pass

    @property
    def state(self) -> BotState:
        """Public read-only property for bot state."""
        return self._state

    def should_run_in_background(self) -> bool:
        return False

    def get_execution_interval(self) -> int:
        return 0

    def execute_task(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError()

    def record_result(self, key: str, value: Any) -> None:
        """Record an arbitrary result/metric under `key` and persist stats.

        This is a light-weight helper used by tests and workers to accumulate
        metrics without forcing a DB dependency.
        """
        # update counters when common keys are used
        if key == "success":
            try:
                if bool(value):
                    self.success_count += 1
                else:
                    self.error_count += 1
            except Exception:
                pass

        # store value
        self._stats[key] = value
        self.last_activity = datetime.utcnow()
        # attempt to persist; failures are non-fatal during tests
        try:
            self._persist_stats()
        except Exception:
            pass

    def get_stats(self) -> Dict[str, Any]:
        """Return a snapshot of runtime metrics and recorded stats."""
        return {
            "bot_id": self.bot_id,
            "name": self.name,
            "state": self._state.value if isinstance(self._state, Enum) else str(self._state),
            "success_count": self.success_count,
            "error_count": self.error_count,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "stats": dict(self._stats),
        }

    def _stats_file_path(self) -> Path:
        base = Path.cwd() / "data" / "bots"
        base.mkdir(parents=True, exist_ok=True)
        return base / f"{self.bot_id}.json"

    def _persist_stats(self) -> None:
        path = self._stats_file_path()
        payload = {
            "bot_id": self.bot_id,
            "name": self.name,
            "state": self._state.value if isinstance(self._state, Enum) else str(self._state),
            "success_count": self.success_count,
            "error_count": self.error_count,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "stats": self._stats,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def _load_persisted_stats(self) -> None:
        path = self._stats_file_path()
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as f:
            try:
                payload = json.load(f)
                # merge known fields
                self.success_count = int(payload.get("success_count", self.success_count))
                self.error_count = int(payload.get("error_count", self.error_count))
                la = payload.get("last_activity")
                if la:
                    try:
                        self.last_activity = datetime.fromisoformat(la)
                    except Exception:
                        self.last_activity = None
                self._stats.update(payload.get("stats", {}))
            except Exception:
                # ignore malformed files
                pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self.bot_id}', name='{self.name}')"


__all__ = ["BaseBot", "BotState"]
