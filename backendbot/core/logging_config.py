"""
BackendBot - Sistema de Logging Estructurado
Logging centralizado y configurable para toda la aplicación
"""

import logging
import logging.config
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger

from .config import get_settings


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Formateador JSON personalizado para logs estructurados"""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        # Añadir campos personalizados
        log_record["timestamp"] = datetime.utcnow().isoformat()
        log_record["service"] = "backendbot"
        s = get_settings()
        log_record["environment"] = s.environment
        log_record["version"] = getattr(s, "version", "1.0.0")

        # Añadir contexto si existe
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
        if hasattr(record, "correlation_id"):
            log_record["correlation_id"] = record.correlation_id


class LoggerAdapter(logging.LoggerAdapter):
    """Adaptador de logger con contexto adicional"""

    def __init__(self, logger: logging.Logger, extra: Optional[Dict[str, Any]] = None):
        super().__init__(logger, extra or {})

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        # Añadir contexto del adapter a cada log
        kwargs["extra"] = {**self.extra, **kwargs.get("extra", {})}
        return msg, kwargs


def setup_logging() -> logging.Logger:
    """Configurar el sistema de logging"""

    # Configuración base
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": StructuredFormatter,
                "format": "%(timestamp)s %(levelname)s %(service)s %(name)s %(message)s",
            },
            "console": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
                "level": "INFO",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": str(get_settings().logs_dir / "backendbot.log"),
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "level": "DEBUG",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": str(get_settings().logs_dir / "backendbot_error.log"),
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "level": "ERROR",
            },
        },
            "root": {
            "level": get_settings().monitoring.log_level,
            "handlers": ["console", "file", "error_file"],
        },
        "loggers": {
            "backendbot": {
                "level": get_settings().monitoring.log_level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
    }

    # Aplicar configuración
    logging.config.dictConfig(log_config)

    # Crear logger principal
    logger = logging.getLogger("backendbot")

    # Log de inicialización
    s = get_settings()
    logger.info(
        "Sistema de logging inicializado",
        extra={
            "environment": s.environment,
            "log_level": s.monitoring.log_level,
            "logs_dir": str(s.logs_dir),
        },
    )

    return logger


# Lazy module-level logger. We configure logging on first use so importing
# the module doesn't force Settings creation.
_logger: logging.Logger | None = None


def _ensure_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        _logger = setup_logging()
    return _logger


def get_logger(name: str, extra: Optional[Dict[str, Any]] = None) -> LoggerAdapter:
    """Obtener un logger con contexto adicional"""
    _ensure_logger()
    base_logger = logging.getLogger(f"backendbot.{name}")
    return LoggerAdapter(base_logger, extra)


def log_request(
    request_id: str, method: str, path: str, status_code: int, duration: float
):
    """Log específico para requests HTTP"""
    _ensure_logger().info(
        "HTTP Request",
        extra={
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            "type": "http_request",
        },
    )


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Log específico para errores"""
    _ensure_logger().error(
        "Application Error",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "type": "application_error",
        },
        exc_info=True,
    )


def log_performance(
    operation: str, duration: float, metadata: Optional[Dict[str, Any]] = None
):
    """Log específico para métricas de rendimiento"""
    _ensure_logger().info(
        "Performance Metric",
        extra={
            "operation": operation,
            "duration_ms": round(duration * 1000, 2),
            "metadata": metadata or {},
            "type": "performance",
        },
    )


# Funciones de conveniencia para logging contextual
def create_request_logger(
    request_id: str, user_id: Optional[str] = None
) -> LoggerAdapter:
    """Crear logger con contexto de request"""
    extra = {"request_id": request_id}
    if user_id:
        extra["user_id"] = user_id
    return get_logger("request", extra)


def create_bot_logger(bot_name: str, bot_id: Optional[str] = None) -> LoggerAdapter:
    """Crear logger con contexto de bot"""
    extra = {"bot_name": bot_name}
    if bot_id:
        extra["bot_id"] = bot_id
    return get_logger("bot", extra)
