"""
Servicios de logging con mejores prácticas modernas
Implementa logging estructurado con inyección de dependencias
"""

import logging
import logging.config
from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from dependency_injector.wiring import inject, Provide


class LoggerService:
    """
    Servicio de logging moderno con configuración avanzada
    Implementa mejores prácticas de logging estructurado
    """

    def __init__(
        self,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializar servicio de logging

        Args:
            log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Archivo de log opcional
            config: Configuración adicional opcional
        """
        self.log_level = log_level.upper()
        self.log_file = log_file or "backendbot.log"
        self.config = config or {}

        # Configurar logging
        self._setup_logging()

        # Crear logger principal
        self.logger = logging.getLogger("BackendBot")

        # Configurar logging
        self._setup_logging()

        # Crear logger principal
        self.logger = logging.getLogger("BackendBot")

    def _setup_logging(self):
        """Configurar sistema de logging con mejores prácticas"""
        log_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'detailed': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(module)s:%(lineno)d'
                },
                'simple': {
                    'format': '%(levelname)s - %(message)s'
                },
                'json': {
                    'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s", "line": %(lineno)d}'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': self.log_level,
                    'formatter': 'simple',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': self.log_level,
                    'formatter': 'detailed',
                    'filename': self.log_file,
                    'maxBytes': 10 * 1024 * 1024,  # 10MB
                    'backupCount': 5
                }
            },
            'root': {
                'level': self.log_level,
                'handlers': ['console', 'file']
            },
            'loggers': {
                'BackendBot': {
                    'level': self.log_level,
                    'handlers': ['console', 'file'],
                    'propagate': False
                }
            }
        }

        # Aplicar configuración
        logging.config.dictConfig(log_config)

    def debug(self, message: str, module: str = ""):
        """Log mensaje de debug"""
        self.logger.debug(f"[{module}] {message}")

    def info(self, message: str, module: str = ""):
        """Log mensaje informativo"""
        self.logger.info(f"[{module}] {message}")

    def warning(self, message: str, module: str = ""):
        """Log mensaje de advertencia"""
        self.logger.warning(f"[{module}] {message}")

    def error(self, message: str, module: str = "", exc_info: bool = False):
        """Log mensaje de error"""
        self.logger.error(f"[{module}] {message}", exc_info=exc_info)

    def critical(self, message: str, module: str = "", exc_info: bool = True):
        """Log mensaje crítico"""
        self.logger.critical(f"[{module}] {message}", exc_info=exc_info)

    def log_performance(self, operation: str, duration: float, module: str = ""):
        """Log información de rendimiento"""
        self.logger.info(f"[{module}] Performance: {operation} took {duration:.2f} seconds")
    def log_error_with_context(self, error: Exception, context: Dict[str, Any], module: str = ""):
        """Log error con contexto adicional"""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        self.logger.error(f"[{module}] Error con contexto: {json.dumps(error_info)}", exc_info=True)

    def set_level(self, level: str):
        """Cambiar nivel de logging dinámicamente"""
        self.log_level = level.upper()
        self.logger.setLevel(getattr(logging, self.log_level))

        # Actualizar handlers
        for handler in self.logger.handlers:
            handler.setLevel(getattr(logging, self.log_level))

    def get_logger(self, name: str = "BackendBot") -> logging.Logger:
        """Obtener logger específico"""
        return logging.getLogger(name)