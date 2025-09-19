"""
Configuración simple para BackendBot
Configuración básica y modos de operación.
"""

import os
from enum import Enum
from typing import Dict, Any


class OperationMode(Enum):
    """Modos de operación de BackendBot"""
    EDITOR = "editor"
    STREAMING = "streaming"
    RELAX = "relax"


class Config:
    """Configuración simple de BackendBot"""

    def __init__(self):
        # Rutas básicas
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.data_dir = os.path.join(self.base_dir, "data")
        self.config_dir = os.path.join(self.base_dir, "config")

        # Asegurar que los directorios existan
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)

        # Configuración por defecto
        self.default_settings = {
            "window_size": (500, 400),
            "auto_start": False,
            "theme": "dark",
            "language": "es",
            "monitoring_interval": 5,  # segundos
            "max_messages": 1000,  # máximo mensajes en chat
        }

        # Modo actual
        self.current_mode = OperationMode.EDITOR

        # Configuraciones por modo
        self.mode_configs = self._get_mode_configs()

    def _get_mode_configs(self) -> Dict[OperationMode, Dict[str, Any]]:
        """Configuraciones específicas para cada modo"""
        return {
            OperationMode.EDITOR: {
                "cpu_threshold": 70,
                "memory_threshold": 80,
                "description": "Optimizado para edición de código"
            },
            OperationMode.STREAMING: {
                "cpu_threshold": 60,
                "memory_threshold": 75,
                "description": "Optimizado para streaming y multimedia"
            },
            OperationMode.RELAX: {
                "cpu_threshold": 80,
                "memory_threshold": 85,
                "description": "Modo relajado, menos monitoreo"
            }
        }

    def get_current_mode_config(self) -> Dict[str, Any]:
        """Obtener configuración del modo actual"""
        return self.mode_configs.get(self.current_mode, {})

    def set_mode(self, mode: OperationMode):
        """Cambiar modo de operación"""
        if mode in OperationMode:
            self.current_mode = mode
            print(f"✅ Modo cambiado a: {mode.value}")
        else:
            print(f"❌ Modo no válido: {mode}")

    def get_setting(self, key: str, default=None):
        """Obtener configuración"""
        return self.default_settings.get(key, default)

    def set_setting(self, key: str, value: Any):
        """Establecer configuración"""
        self.default_settings[key] = value

    @property
    def db_path(self) -> str:
        """Ruta de la base de datos local"""
        return os.path.join(self.data_dir, "backendbot.db")

    @property
    def log_path(self) -> str:
        """Ruta del archivo de logs"""
        return os.path.join(self.data_dir, "backendbot.log")


# Instancia global de configuración
config = Config()