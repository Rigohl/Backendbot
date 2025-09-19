"""Small helper to run bots periodically in background threads."""
import threading
import time
from typing import Callable, Optional


class BotRunner:
    def __init__(self, interval_s: float, target: Callable, name: Optional[str] = None):
        self.interval = interval_s
        self.target = target
        self._thread = None
        self._stop = threading.Event()
        self.name = name or getattr(target, "__name__", "bot_runner")

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name=f"runner-{self.name}", daemon=True)
        self._thread.start()

    def _loop(self):
        while not self._stop.is_set():
            try:
                self.target()
            except Exception:
                pass
            self._stop.wait(self.interval)

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)
