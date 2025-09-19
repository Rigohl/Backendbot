"""
Interfaces para comunicación entre módulos - Interface Segregation Principle
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class IBot(ABC):
    """Interfaz base para todos los bots"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del bot"""
        pass

    @abstractmethod
    def execute(self, action: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Ejecutar una acción del bot"""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del bot"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Verificar si el bot está disponible"""
        pass


class ITaskScheduler(ABC):
    """Interfaz para el programador de tareas"""

    @abstractmethod
    def schedule_task(self, task_id: str, name: str, function: callable,
                     frequency: str, priority: int = 2) -> bool:
        """Programar una tarea"""
        pass

    @abstractmethod
    def cancel_task(self, task_id: str) -> bool:
        """Cancelar una tarea programada"""
        pass

    @abstractmethod
    def get_scheduled_tasks(self) -> list:
        """Obtener lista de tareas programadas"""
        pass


class ILogger(ABC):
    """Interfaz para logging"""

    @abstractmethod
    def info(self, message: str, source: str = None):
        """Log de información"""
        pass

    @abstractmethod
    def warning(self, message: str, source: str = None):
        """Log de advertencia"""
        pass

    @abstractmethod
    def error(self, message: str, source: str = None):
        """Log de error"""
        pass


class IConfigManager(ABC):
    """Interfaz para gestión de configuración"""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any):
        """Establecer valor de configuración"""
        pass

    @abstractmethod
    def save(self):
        """Guardar configuración"""
        pass


class IDataRepository(ABC):
    """Interfaz para repositorio de datos"""

    @abstractmethod
    def save_system_event(self, level: str, source: str, message: str, details: Optional[str] = None):
        """Guardar evento del sistema"""
        pass

    @abstractmethod
    def save_bot_action(self, bot_name: str, action_type: str, status: str,
                       target: Optional[str] = None, result: Optional[str] = None):
        """Guardar acción de bot"""
        pass

    @abstractmethod
    def get_recent_events(self, limit: int = 100) -> list:
        """Obtener eventos recientes"""
        pass