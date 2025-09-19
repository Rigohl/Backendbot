"""
BackendBot Core Package
Paquete central con utilidades compartidas para toda la aplicación
"""

from .di.container import container as _lazy_container_proxy

# Expose a lazy container proxy and a helper to access it.
# Avoid instantiating heavy objects at import time (Settings, DB connections)
container = _lazy_container_proxy

# Exponer componentes clave del core para fácil acceso mediante funciones
from .config import get_settings
from .logging_config import get_logger, log_error, log_performance, log_request
from .database.manager import DatabaseManager
from .database.models import Base, create_tables, drop_tables, create_indexes

__all__ = [
    "get_settings",
    "container",
    "get_logger",
    "log_error",
    "log_performance",
    "log_request",
]
