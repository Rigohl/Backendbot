"""
Configuración avanzada usando mejores prácticas modernas de DI
Soporta YAML, JSON, variables de entorno y configuración programática
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Importar configuración moderna si está disponible
try:
    from dependency_injector import providers
    from dependency_injector.providers import Configuration
    MODERN_CONFIG_AVAILABLE = True
except ImportError:
    MODERN_CONFIG_AVAILABLE = False

from backendbot.core.config import Settings

logger = logging.getLogger(__name__)


class AdvancedConfiguration:
    """
    Configuración avanzada que soporta múltiples fuentes
    Implementa mejores prácticas modernas de configuración
    """

    def __init__(self):
        self._config_data: Dict[str, Any] = {}
        self._config_files: list[Path] = []
        self._modern_config: Optional[Configuration] = None

        if MODERN_CONFIG_AVAILABLE:
            self._modern_config = Configuration()
            self._setup_modern_config()

    def _setup_modern_config(self):
        """Configurar el sistema moderno de configuración"""
        if not self._modern_config:
            return

        # Configuración desde variables de entorno
        self._modern_config.api_key.from_env("BACKENDBOT_API_KEY", required=True)
        self._modern_config.database.connection_string.from_env(
            "DATABASE_URL", default="sqlite:///backendbot.db"
        )
        self._modern_config.database.pool_size.from_env(
            "DB_POOL_SIZE", as_=int, default=5
        )
        self._modern_config.logging.level.from_env(
            "LOG_LEVEL", default="INFO"
        )
        self._modern_config.ui.theme.from_env(
            "UI_THEME", default="dark"
        )

        # Configuración desde archivos
        config_file = os.getenv("CONFIG_FILE")
        if config_file and Path(config_file).exists():
            if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                self._modern_config.from_yaml(config_file)
            elif config_file.endswith('.json'):
                self._modern_config.from_json(config_file)

    def load_from_file(self, file_path: str | Path) -> None:
        """Cargar configuración desde archivo"""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Config file not found: {file_path}")
            return

        try:
            if MODERN_CONFIG_AVAILABLE and self._modern_config:
                if path.suffix in ['.yaml', '.yml']:
                    self._modern_config.from_yaml(str(path))
                elif path.suffix == '.json':
                    self._modern_config.from_json(str(path))
            else:
                # Fallback: cargar manualmente
                import json
                if path.suffix == '.json':
                    with open(path, 'r', encoding='utf-8') as f:
                        self._config_data.update(json.load(f))
                else:
                    logger.warning("YAML support requires dependency-injector")

            self._config_files.append(path)
            logger.info(f"Loaded config from {file_path}")

        except Exception as e:
            logger.error(f"Error loading config from {file_path}: {e}")

    def load_from_env(self, prefix: str = "BACKENDBOT_") -> None:
        """Cargar configuración desde variables de entorno"""
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower().replace('_', '.')
                if MODERN_CONFIG_AVAILABLE and self._modern_config:
                    # Set in modern config
                    self._set_nested_config(self._modern_config, config_key.split('.'), value)
                else:
                    # Set in legacy config
                    self._set_nested_dict(self._config_data, config_key.split('.'), value)

    def _set_nested_config(self, config_obj, keys: list, value: str):
        """Set nested configuration value in modern config"""
        current = config_obj
        for key in keys[:-1]:
            if not hasattr(current, key):
                setattr(current, key, Configuration())
            current = getattr(current, key)
        setattr(current, keys[-1], value)

    def _set_nested_dict(self, config_dict: dict, keys: list, value: str):
        """Set nested configuration value in dict"""
        current = config_dict
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def override(self, config_dict: Dict[str, Any]) -> None:
        """Override configuración con diccionario"""
        if MODERN_CONFIG_AVAILABLE and self._modern_config:
            self._modern_config.override(config_dict)
        else:
            self._merge_dicts(self._config_data, config_dict)

    def _merge_dicts(self, target: dict, source: dict) -> None:
        """Merge nested dictionaries"""
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._merge_dicts(target[key], value)
            else:
                target[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración"""
        if MODERN_CONFIG_AVAILABLE and self._modern_config:
            try:
                return self._get_nested_config(self._modern_config, key.split('.'))
            except:
                return default
        else:
            return self._get_nested_dict(self._config_data, key.split('.'), default)

    def _get_nested_config(self, config_obj, keys: list):
        """Get nested configuration value from modern config"""
        current = config_obj
        for key in keys:
            current = getattr(current, key)
        return current

    def _get_nested_dict(self, config_dict: dict, keys: list, default: Any = None):
        """Get nested configuration value from dict"""
        current = config_dict
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def get_all(self) -> Dict[str, Any]:
        """Obtener toda la configuración como diccionario"""
        if MODERN_CONFIG_AVAILABLE and self._modern_config:
            # Convert modern config to dict (simplified)
            return {"modern_config": "available"}
        else:
            return self._config_data.copy()

    def validate(self) -> bool:
        """Validar configuración requerida"""
        required_keys = ['api_key', 'database.connection_string']

        for key in required_keys:
            if not self.get(key):
                logger.error(f"Required configuration missing: {key}")
                return False

        logger.info("Configuration validation passed")
        return True

    def reload(self) -> None:
        """Recargar configuración desde archivos"""
        self._config_data.clear()
        for config_file in self._config_files:
            self.load_from_file(config_file)
        self.load_from_env()
        logger.info("Configuration reloaded")


# Instancia global de configuración avanzada
_advanced_config: Optional[AdvancedConfiguration] = None

def get_advanced_config() -> AdvancedConfiguration:
    """Obtener instancia global de configuración avanzada"""
    global _advanced_config
    if _advanced_config is None:
        _advanced_config = AdvancedConfiguration()
    return _advanced_config

def create_settings_from_config() -> Settings:
    """Crear Settings desde configuración avanzada"""
    config = get_advanced_config()

    # Crear settings con valores de configuración
    settings_dict = {
        'api_key': config.get('api_key'),
        'database_url': config.get('database.connection_string', 'sqlite:///backendbot.db'),
        'log_level': config.get('logging.level', 'INFO'),
        'ui_theme': config.get('ui.theme', 'dark'),
    }

    return Settings(**settings_dict)


# Ejemplo de archivo de configuración YAML
DEFAULT_CONFIG_YAML = """
api_key: "${BACKENDBOT_API_KEY}"
database:
  connection_string: "${DATABASE_URL:sqlite:///backendbot.db}"
  pool_size: "${DB_POOL_SIZE:5}"
logging:
  level: "${LOG_LEVEL:INFO}"
ui:
  theme: "${UI_THEME:dark}"
"""

# Ejemplo de archivo de configuración JSON
DEFAULT_CONFIG_JSON = """
{
  "api_key": "${BACKENDBOT_API_KEY}",
  "database": {
    "connection_string": "${DATABASE_URL:sqlite:///backendbot.db}",
    "pool_size": "${DB_POOL_SIZE:5}"
  },
  "logging": {
    "level": "${LOG_LEVEL:INFO}"
  },
  "ui": {
    "theme": "${UI_THEME:dark}"
  }
}
"""