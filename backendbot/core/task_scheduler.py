import threading
import uuid
from typing import Any, Callable, Dict, List, Optional


class TaskScheduler:
    """Lightweight in-process scheduler for test compatibility.

    Implementa lo mínimo necesario para los tests: agregar tareas, ejecutarlas,
    habilitar/deshabilitar y listar. No pretende ser un scheduler completo.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tasks: Dict[str, Dict[str, Any]] = {}

    @property
    def tasks(self) -> Dict[str, Dict[str, Any]]:
        """Backward compatibility property for tests."""
        with self._lock:
            return dict(self._tasks)

    def add_task(self, name: str, func: Callable, schedule: str = "once") -> str:
        tid = str(uuid.uuid4())
        with self._lock:
            self._tasks[tid] = {
                "name": name,
                "func": func,
                "schedule": schedule,
                "enabled": True,
            }
        return tid

    # backward-compat name used in some scripts/tests
    def add_task_compat(self, name: str, func: Callable, schedule: str = "once") -> str:
        return self.add_task(name, func, schedule)

    def execute_task(self, task_id: str) -> Optional[Any]:
        with self._lock:
            t = self._tasks.get(task_id)
        if not t:
            raise KeyError(f"Unknown task {task_id}")
        if not t.get("enabled", True):
            return None
        return t["func"]()

    def get_task_stats(self) -> Dict[str, int]:
        with self._lock:
            total = len(self._tasks)
            enabled = sum(1 for t in self._tasks.values() if t.get("enabled", True))
        return {"total_tasks": total, "enabled_tasks": enabled}

    def get_tasks_list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [{"id": k, **v} for k, v in self._tasks.items()]

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


# Module-level instance and compatibility exports
task_scheduler = TaskScheduler()


class _SchedulePlaceholder:
    """Placeholder minimal para permitir parches en tests que esperan `schedule`.

    Guarda referencias simples en memoria.
    """

    def __init__(self):
        self._scheduled: Dict[str, Any] = {}

    def add(self, task_id: str, when: Any):
        self._scheduled[task_id] = when

    def remove(self, task_id: str):
        if task_id in self._scheduled:
            del self._scheduled[task_id]

    def list(self):
        return dict(self._scheduled)


schedule = _SchedulePlaceholder()


# Expose tasks mapping for backward compatibility
try:
    tasks = task_scheduler.get_tasks_list()
except Exception:
    tasks = {}

__all__ = ["TaskScheduler", "task_scheduler", "schedule", "tasks"]
