"""
Dependency Injection Container for BackendBot.
"""
from ..config import Settings
from ..config_manager import DatabaseConfigManager
from backendbot.core.database.manager import DatabaseManager
# Import other services as needed

class Container:
    def get_data_repository(self):
        # Retorna un repositorio dummy para compatibilidad
        class DummyRepo:
            def save_bot_action(self, **kwargs):
                return None
            def save_system_event(self, **kwargs):
                return None
        return DummyRepo()
    def get_logger(self):
        # Retorna un logger dummy para compatibilidad
        import logging
        return logging.getLogger("backendbot.dummy")

    def __init__(self):
        self._settings = Settings()
        self._config_manager = DatabaseConfigManager(self._settings)
        self._db_manager = DatabaseManager()
        # Initialize other services here

    def get_settings(self) -> Settings:
        return self._config_manager.get_settings()

    def get_config_manager(self) -> DatabaseConfigManager:
        return self._config_manager

    def get_db_manager(self) -> DatabaseManager:
        return self._db_manager

    # Add methods to get other services

# Global container instance
container = Container()
