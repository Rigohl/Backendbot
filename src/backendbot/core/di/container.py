"""
Container de dependencias simple para BackendBot
"""

from typing import Any, Dict
from ..config import config


class SimpleContainer:
    """Container simple de dependencias"""

    def __init__(self):
        self._services = {}
        self._register_defaults()

    def _register_defaults(self):
        """Registrar servicios por defecto"""
        self._services['config'] = config
        self._services['logger'] = SimpleLogger()
        self._services['data_repository'] = SimpleDataRepository()

    def get_config_manager(self):
        """Obtener gestor de configuración"""
        return self._services['config']

    def get_logger(self):
        """Obtener logger"""
        return self._services['logger']

    def get_data_repository(self):
        """Obtener repositorio de datos"""
        return self._services['data_repository']


class SimpleLogger:
    """Logger simple"""

    def info(self, message: str, source: str = ""):
        print(f"[INFO] {source}: {message}")

    def error(self, message: str, source: str = ""):
        print(f"[ERROR] {source}: {message}")

    def warning(self, message: str, source: str = ""):
        print(f"[WARNING] {source}: {message}")


class SimpleDataRepository:
    """Repositorio de datos simple (en memoria por ahora)"""

    def __init__(self):
        self._data = {}

    def save_bot_action(self, bot_name: str, action_type: str, status: str, target: str, result: str):
        """Guardar acción de bot"""
        if 'bot_actions' not in self._data:
            self._data['bot_actions'] = []
        self._data['bot_actions'].append({
            'bot_name': bot_name,
            'action_type': action_type,
            'status': status,
            'target': target,
            'result': result,
            'timestamp': 'now'  # Simplificado
        })

    def save_system_event(self, level: str, source: str, message: str, details: str = ""):
        """Guardar evento del sistema"""
        if 'system_events' not in self._data:
            self._data['system_events'] = []
        self._data['system_events'].append({
            'level': level,
            'source': source,
            'message': message,
            'details': details,
            'timestamp': 'now'
        })


# Instancia global
container = SimpleContainer()