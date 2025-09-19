"""
Contenedor de dependencias - Dependency Inversion Principle
"""
from typing import Dict, Any, Optional
import sys
import os

# Añadir path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.backendbot.core.interfaces.interfaces import IBot, ILogger, IConfigManager, IDataRepository, ITaskScheduler
from src.backendbot.core.implementations.implementations import Logger, ConfigManager, DataRepository


class DependencyContainer:
    """Contenedor de dependencias para inyección de dependencias"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}

        # Registrar implementaciones por defecto
        self._register_defaults()

    def _register_defaults(self):
        """Registrar implementaciones por defecto"""
        self.register(ILogger, Logger, singleton=True)
        self.register(IConfigManager, ConfigManager, singleton=True)
        self.register(IDataRepository, DataRepository, singleton=True)

    def register(self, interface: type, implementation: type, singleton: bool = True):
        """Registrar una implementación para una interfaz"""
        key = f"{interface.__name__}"
        self._services[key] = (implementation, singleton)

    def register_instance(self, interface: type, instance: Any):
        """Registrar una instancia específica"""
        key = f"{interface.__name__}"
        self._singletons[key] = instance

    def resolve(self, interface: type) -> Any:
        """Resolver una dependencia"""
        key = f"{interface.__name__}"

        # Si ya tenemos una instancia singleton
        if key in self._singletons:
            return self._singletons[key]

        # Si está registrado como servicio
        if key in self._services:
            implementation, singleton = self._services[key]
            instance = implementation()

            if singleton:
                self._singletons[key] = instance

            return instance

        raise ValueError(f"No se encontró implementación para {interface.__name__}")

    def get_bot(self, bot_name: str) -> Optional[IBot]:
        """Obtener un bot específico"""
        try:
            return self.resolve(IBot)  # Esto necesitaría ser más específico
        except:
            return None

    def get_logger(self) -> ILogger:
        """Obtener el logger"""
        return self.resolve(ILogger)

    def get_config_manager(self) -> IConfigManager:
        """Obtener el gestor de configuración"""
        return self.resolve(IConfigManager)

    def get_data_repository(self) -> IDataRepository:
        """Obtener el repositorio de datos"""
        return self.resolve(IDataRepository)

    def get_task_scheduler(self) -> ITaskScheduler:
        """Obtener el programador de tareas"""
        return self.resolve(ITaskScheduler)


# Instancia global del contenedor
container = DependencyContainer()