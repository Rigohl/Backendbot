# Configuración local para BackendBot (sin Railway ni base de datos externa)
import os
from enum import Enum
from typing import Dict, Any

class OperationMode(Enum):
    EDITOR = "editor"
    STREAMING = "streaming"
    RELAX = "relax"
    DESARROLLO = "desarrollo"
    GAMING = "gaming"

class ModeConfig:
    def __init__(self, mode: OperationMode):
        self.mode = mode
        self.settings = self._get_mode_settings()

    def _get_mode_settings(self) -> Dict[str, Any]:
        """Configuraciones específicas para cada modo de operación"""
        base_settings = {
            "cpu_threshold": 80,
            "memory_threshold": 85,
            "disk_threshold": 90,
            "gpu_threshold": 85,
            "monitoring_interval": 5,
            "cleanup_enabled": True,
            "optimization_enabled": True,
            "background_tasks": True
        }

        mode_specific = {
            OperationMode.EDITOR: {
                "cpu_threshold": 70,
                "memory_threshold": 80,
                "disk_threshold": 85,
                "gpu_threshold": 75,
                "monitoring_interval": 3,
                "cleanup_enabled": True,
                "optimization_enabled": False,  # Menos agresivo en modo edición
                "background_tasks": True,
                "focus_processes": ["code.exe", "pycharm.exe", "vscode.exe"],
                "description": "Optimizado para edición de código y desarrollo"
            },
            OperationMode.STREAMING: {
                "cpu_threshold": 60,
                "memory_threshold": 75,
                "disk_threshold": 80,
                "gpu_threshold": 70,
                "monitoring_interval": 2,
                "cleanup_enabled": False,  # Evitar interrupciones
                "optimization_enabled": True,
                "background_tasks": False,  # Minimizar procesos en background
                "focus_processes": ["obs.exe", "streamlabs.exe", "discord.exe"],
                "description": "Optimizado para streaming y grabación"
            },
            OperationMode.RELAX: {
                "cpu_threshold": 85,
                "memory_threshold": 90,
                "disk_threshold": 95,
                "gpu_threshold": 90,
                "monitoring_interval": 10,
                "cleanup_enabled": False,
                "optimization_enabled": False,
                "background_tasks": True,
                "focus_processes": ["chrome.exe", "firefox.exe", "spotify.exe"],
                "description": "Modo relajado para navegación y entretenimiento"
            },
            OperationMode.DESARROLLO: {
                "cpu_threshold": 75,
                "memory_threshold": 85,
                "disk_threshold": 90,
                "gpu_threshold": 80,
                "monitoring_interval": 4,
                "cleanup_enabled": True,
                "optimization_enabled": True,
                "background_tasks": True,
                "focus_processes": ["code.exe", "pycharm.exe", "docker.exe", "git.exe"],
                "description": "Optimizado para desarrollo intensivo y compilación"
            },
            OperationMode.GAMING: {
                "cpu_threshold": 50,
                "memory_threshold": 70,
                "disk_threshold": 75,
                "gpu_threshold": 60,
                "monitoring_interval": 1,
                "cleanup_enabled": False,
                "optimization_enabled": True,
                "background_tasks": False,
                "focus_processes": ["steam.exe", "epicgameslauncher.exe", "battle.net.exe"],
                "description": "Optimizado para gaming y aplicaciones de alto rendimiento"
            }
        }

        base_settings.update(mode_specific.get(self.mode, {}))
        return base_settings

class Settings:
    def __init__(self):
        self.debug = True
        self.app_name = "BackendBot"
        self.version = "1.0"
        self.current_mode = OperationMode.EDITOR  # Modo por defecto
        self.mode_config = ModeConfig(self.current_mode)

    def set_mode(self, mode: OperationMode):
        """Cambiar el modo de operación"""
        self.current_mode = mode
        self.mode_config = ModeConfig(mode)
        print(f"Modo cambiado a: {mode.value} - {self.mode_config.settings.get('description', '')}")

    def get_mode_settings(self) -> Dict[str, Any]:
        """Obtener configuraciones del modo actual"""
        return self.mode_config.settings

settings = Settings()