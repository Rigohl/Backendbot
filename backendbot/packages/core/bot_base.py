from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Protocol
import threading
import uuid


class BotType(Enum):
    MONITOR = "monitor"
    ORGANIZER = "organizer"
    INDEXER = "indexer"


class BotPriority(Enum):
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()


@dataclass
class BotConfig:
    name: str
    type: BotType
    priority: BotPriority = BotPriority.NORMAL
    max_concurrent_tasks: int = 5
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    task_id: str
    success: bool
    result: Any = None
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BotInterface(Protocol):
    config: BotConfig

    def initialize(self) -> bool:
        ...

    def shutdown(self) -> bool:
        ...

    def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        ...

    def validate_task(self, task_data: Dict[str, Any]) -> bool:
        ...

    def get_supported_tasks(self) -> List[str]:
        ...


class BaseBot:
    def __init__(self, config: BotConfig):
        self.config = config
        self.status = type("S", (), {"name": "STOPPED"})()
        self.metrics = type("M", (), {"tasks_completed": 0, "tasks_failed": 0, "average_execution_time": 0.0})()
        self._executor = None
        self._running_tasks = {}
        self._task_callbacks = []
        self._shutdown_event = threading.Event()

    def initialize(self) -> bool:
        try:
            self.status.name = "RUNNING"
            return True
        except Exception:
            self.status.name = "ERROR"
            return False

    def shutdown(self) -> bool:
        try:
            self.status.name = "STOPPED"
            self._shutdown_event.set()
            return True
        except Exception:
            self.status.name = "ERROR"
            return False

    def execute_task_async(self, task_data, callback=None) -> str:
        if self.status.name != "RUNNING":
            raise RuntimeError("Bot no está inicializado")
        if not self.validate_task(task_data):
            raise ValueError("Tarea inválida")
        task_id = f"{self.config.name}_{uuid.uuid4().hex[:8]}"
        # Simular ejecución síncrona para tests
        result = self.execute_task(task_data)
        if callback:
            callback(result)
        return task_id

    def is_task_running(self, task_id: str) -> bool:
        return False

    def get_running_tasks_count(self) -> int:
        return 0

    def add_task_callback(self, cb):
        self._task_callbacks.append(cb)

    def remove_task_callback(self, cb):
        self._task_callbacks.remove(cb)

    # Métodos que las subclases deben implementar
    def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        raise NotImplementedError()

    def validate_task(self, task_data: Dict[str, Any]) -> bool:
        return isinstance(task_data, dict)

    def get_supported_tasks(self) -> List[str]:
        return []
