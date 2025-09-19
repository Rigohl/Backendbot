from typing import Any, Optional
from backendbot.core.interfaces import IConfigManager
from backendbot.core.config import get_settings


class ConfigService(IConfigManager):
    def __init__(self) -> None:
        self._settings = get_settings()

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        # Soporta nested keys separadas por punto
        parts = key.split('.')
        cur = self._settings
        try:
            for p in parts:
                cur = getattr(cur, p) if hasattr(cur, p) else cur[p]
            return cur
        except Exception:
            return default

    def set(self, key: str, value: Any) -> None:
        parts = key.split('.')
        cur = self._settings
        for p in parts[:-1]:
            cur = getattr(cur, p) if hasattr(cur, p) else cur[p]
        last = parts[-1]
        if hasattr(cur, last):
            setattr(cur, last, value)
        else:
            cur[last] = value

    def load(self) -> None:
        # Si get_settings implementa recarga, llamarla
        if hasattr(self._settings, 'load'):
            self._settings.load()
