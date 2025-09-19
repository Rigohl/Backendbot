"""
Servicio de configuración avanzado con mejores prácticas modernas
Implementa configuración multi-fuente con inyección de dependencias
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

from dependency_injector.wiring import inject, Provide


@dataclass
class DatabaseConfig:
    """Configuración de base de datos"""
    url: str = "sqlite:///backendbot.db"
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class LoggingConfig:
    """Configuración de logging"""
    level: str = "INFO"
    file: str = "backendbot.log"
    max_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class UIConfig:
    """Configuración de interfaz de usuario"""
    theme: str = "dark"
    language: str = "es"
    tray_icon: bool = True
    notifications: bool = True


@dataclass
class BotConfig:
    """Configuración de bots"""
    max_concurrent: int = 3
    timeout: int = 300
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class BackendBotConfig:
    """Configuración completa de BackendBot"""
    database: DatabaseConfig
    logging: LoggingConfig
    ui: UIConfig
    bot: BotConfig
    api_port: int = 8000
    api_host: str = "localhost"
    ssl_enabled: bool = False
    debug_mode: bool = False


class ConfigProvider(ABC):
    """Proveedor abstracto de configuración"""

    @abstractmethod
    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración desde la fuente específica"""
        pass

    @abstractmethod
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Guardar configuración en la fuente específica"""
        pass


class YamlConfigProvider(ConfigProvider):
    """Proveedor de configuración YAML"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración desde archivo YAML"""
        if not self.file_path.exists():
            return {}

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading YAML config: {e}")
            return {}

    def save_config(self, config: Dict[str, Any]) -> bool:
        """Guardar configuración en archivo YAML"""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"Error saving YAML config: {e}")
            return False


class JsonConfigProvider(ConfigProvider):
    """Proveedor de configuración JSON"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración desde archivo JSON"""
        if not self.file_path.exists():
            return {}

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON config: {e}")
            return {}

    def save_config(self, config: Dict[str, Any]) -> bool:
        """Guardar configuración en archivo JSON"""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving JSON config: {e}")
            return False


class EnvConfigProvider(ConfigProvider):
    """Proveedor de configuración desde variables de entorno"""

    def __init__(self, prefix: str = "BACKENDBOT_"):
        self.prefix = prefix

    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración desde variables de entorno"""
        config = {}
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                # Remover prefijo y convertir a nested dict
                clean_key = key[len(self.prefix):].lower()
                keys = clean_key.split('_')
                self._set_nested_value(config, keys, value)
        return config

    def save_config(self, config: Dict[str, Any]) -> bool:
        """Las variables de entorno no se pueden guardar automáticamente"""
        print("Warning: Environment variables cannot be saved automatically")
        return False

    def _set_nested_value(self, config: Dict[str, Any], keys: list, value: str):
        """Establecer valor anidado en diccionario"""
        if len(keys) == 1:
            # Convertir tipos básicos
            if value.lower() in ('true', 'false'):
                config[keys[0]] = value.lower() == 'true'
            elif value.isdigit():
                config[keys[0]] = int(value)
            elif value.replace('.', '').isdigit():
                config[keys[0]] = float(value)
            else:
                config[keys[0]] = value
        else:
            if keys[0] not in config:
                config[keys[0]] = {}
            self._set_nested_value(config[keys[0]], keys[1:], value)


class ConfigService:
    """
    Servicio de configuración avanzado con múltiples proveedores
    Implementa mejores prácticas de configuración moderna
    """

    def __init__(
        self,
        config_file: Optional[str] = None,
        config_dir: str = "config",
        providers: Optional[list] = None
    ):
        """
        Inicializar servicio de configuración

        Args:
            config_file: Archivo de configuración principal
            config_dir: Directorio de configuración
            providers: Lista de proveedores de configuración
        """
        self.config_dir = Path(config_dir)
        self.config_file = config_file or "backendbot.yaml"

        # Configuración por defecto
        self._default_config = self._create_default_config()

        # Proveedores de configuración (orden de precedencia)
        self.providers = providers or [
            EnvConfigProvider(),  # Variables de entorno (mayor precedencia)
            YamlConfigProvider(self.config_dir / self.config_file),
            JsonConfigProvider(self.config_dir / "backendbot.json")
        ]

        # Configuración cargada
        self._config = {}
        self._load_config()

    def _create_default_config(self) -> BackendBotConfig:
        """Crear configuración por defecto"""
        return BackendBotConfig(
            database=DatabaseConfig(),
            logging=LoggingConfig(),
            ui=UIConfig(),
            bot=BotConfig()
        )

    def _load_config(self):
        """Cargar configuración desde todos los proveedores"""
        # Empezar con configuración por defecto
        self._config = asdict(self._default_config)

        # Aplicar configuración de cada proveedor (orden de precedencia)
        for provider in self.providers:
            provider_config = provider.load_config()
            if provider_config:
                self._merge_config(self._config, provider_config)

    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]):
        """Fusionar configuraciones recursivamente"""
        for key, value in override.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración"""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> bool:
        """Establecer valor de configuración"""
        keys = key.split('.')
        config = self._config

        # Navegar hasta el penúltimo nivel
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Establecer valor
        config[keys[-1]] = value

        # Intentar guardar en el primer proveedor que soporte escritura
        for provider in self.providers:
            if hasattr(provider, 'save_config') and provider.save_config(self._config):
                return True

        return False

    def get_all(self) -> Dict[str, Any]:
        """Obtener toda la configuración"""
        return self._config.copy()

    def reload(self):
        """Recargar configuración"""
        self._load_config()

    def get_database_config(self) -> DatabaseConfig:
        """Obtener configuración de base de datos"""
        db_config = self.get('database', {})
        return DatabaseConfig(**db_config)

    def get_logging_config(self) -> LoggingConfig:
        """Obtener configuración de logging"""
        log_config = self.get('logging', {})
        return LoggingConfig(**log_config)

    def get_ui_config(self) -> UIConfig:
        """Obtener configuración de UI"""
        ui_config = self.get('ui', {})
        return UIConfig(**ui_config)

    def get_bot_config(self) -> BotConfig:
        """Obtener configuración de bots"""
        bot_config = self.get('bot', {})
        return BotConfig(**bot_config)

    def get_api_config(self) -> Dict[str, Any]:
        """Obtener configuración de API"""
        return {
            'port': self.get('api_port', 8000),
            'host': self.get('api_host', 'localhost'),
            'ssl_enabled': self.get('ssl_enabled', False)
        }

    def is_debug_mode(self) -> bool:
        """Verificar si está en modo debug"""
        return self.get('debug_mode', False)