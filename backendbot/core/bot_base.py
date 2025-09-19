"""Base classes and helpers for bots."""
from __future__ import annotations

import threading
import time
from typing import Any, Dict
import json
from pathlib import Path

# Directory to persist bot stats
_BOT_STATS_DIR = Path(__file__).resolve().parents[2] / "data" / "bot_stats"
_BOT_STATS_DIR.mkdir(parents=True, exist_ok=True)


class BaseBot:
    """Base bot minimal para estandarizar lifecycle y métricas.

    - start/stop: control básico de ejecución
    - execute(action): método a implementar por subclases
    - record_result: almacena resultados simples en memoria para "aprendizaje"
    """

    def __init__(self, name: str):
        self.name = name
        self._running = False
        self._thread = None
        self._stats: Dict[str, Any] = {}

    def start(self):
        if self._running:
            return "already running"
        self._running = True
        # No iniciar hilo por defecto; los bots pueden optar por hacerlo
        return "started"

    def stop(self):
        if not self._running:
            return "not running"
        self._running = False
        # Si hubiera hilo, esperar terminación
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
        return "stopped"

    def execute(self, action: str) -> Any:
        raise NotImplementedError()

    def record_result(self, key: str, value: Any):
        """Registrar un resultado simple en memoria para aprendizaje.

        Este método es intencionalmente simple: sirve para acumular
        métricas/ejemplos que luego puedan persistirse.
        """
        bucket = self._stats.setdefault(key, [])
        entry = {"ts": time.time(), "value": value}
        bucket.append(entry)

        # Persist simple snapshot to disk (overwrite file for simplicity)
        try:
            file_path = _BOT_STATS_DIR / f"{self.name}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self._stats, f, default=str, indent=2)
        except Exception:
            pass

    def get_stats(self) -> Dict[str, Any]:
        return self._stats

    def learn(self) -> Dict[str, Any]:
        """Hook de aprendizaje simple: devolver insights basados en stats.

        Subclases pueden sobrescribir para ajustar su comportamiento.
        """
        # Por defecto no hace nada
        return {}
