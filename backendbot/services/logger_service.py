from typing import Any, Dict, Optional
from backendbot.core.interfaces import ILogger
from backendbot.core.logging_config import get_logger


class LoggerService(ILogger):
    def __init__(self, name: str = 'app') -> None:
        self._adapter = get_logger(name)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._adapter.info(msg, *args, **kwargs)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._adapter.debug(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._adapter.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._adapter.error(msg, *args, **kwargs)
