"""
Sistema de Modos de Operación para BackendBot
Gestiona diferentes configuraciones según el contexto de uso del sistema.
Implementa Open/Closed Principle permitiendo extensión sin modificación.
"""
import psutil
import os
from typing import List, Dict, Any, Protocol, Type
from abc import ABC, abstractmethod
from ..config.config import OperationMode, settings
from ..utils.logging_config import logger

class IModeStrategy(Protocol):
    """Interfaz para estrategias de modo (Interface Segregation Principle)"""

    @property
    def mode_name(self) -> str:
        """Nombre del modo"""
        ...

    @property
    def focus_processes(self) -> List[str]:
        """Procesos foco para este modo"""
        ...

    def apply_configurations(self, manager: 'OperationModeManager') -> None:
        """Aplicar configuraciones específicas del modo"""
        ...

    def get_monitoring_thresholds(self) -> Dict[str, float]:
        """Obtener umbrales de monitoreo para este modo"""
        ...

    def should_enable_background_tasks(self) -> bool:
        """Determinar si habilitar tareas en background"""
        ...

class BaseModeStrategy(ABC):
    """Clase base para estrategias de modo (Template Method Pattern)"""

    def __init__(self, mode_name: str, focus_processes: List[str] = None):
        self._mode_name = mode_name
        self._focus_processes = focus_processes or []

    @property
    def mode_name(self) -> str:
        return self._mode_name

    @property
    def focus_processes(self) -> List[str]:
        return self._focus_processes.copy()

    @abstractmethod
    def apply_configurations(self, manager: 'OperationModeManager') -> None:
        """Aplicar configuraciones específicas del modo"""
        pass

    @abstractmethod
    def get_monitoring_thresholds(self) -> Dict[str, float]:
        """Obtener umbrales de monitoreo para este modo"""
        pass

    def should_enable_background_tasks(self) -> bool:
        """Por defecto, habilitar tareas en background"""
        return True

class EditorModeStrategy(BaseModeStrategy):
    """Estrategia para modo Editor"""

    def __init__(self):
        super().__init__(
            "editor",
            ["code.exe", "pycharm.exe", "vscode.exe", "notepad++.exe", "sublime_text.exe"]
        )

    def apply_configurations(self, manager: 'OperationModeManager') -> None:
        logger.info("Aplicando configuraciones de modo Editor")
        # Configuraciones específicas para desarrollo

    def get_monitoring_thresholds(self) -> Dict[str, float]:
        return {
            'cpu': 70.0,
            'memory': 80.0,
            'disk': 85.0,
            'gpu': 75.0
        }

class StreamingModeStrategy(BaseModeStrategy):
    """Estrategia para modo Streaming"""

    def __init__(self):
        super().__init__(
            "streaming",
            ["obs.exe", "streamlabs.exe", "discord.exe", "chrome.exe", "firefox.exe"]
        )

    def apply_configurations(self, manager: 'OperationModeManager') -> None:
        logger.info("Aplicando configuraciones de modo Streaming")
        # Configuraciones específicas para streaming

    def get_monitoring_thresholds(self) -> Dict[str, float]:
        return {
            'cpu': 60.0,
            'memory': 75.0,
            'disk': 80.0,
            'gpu': 70.0
        }

class RelaxModeStrategy(BaseModeStrategy):
    """Estrategia para modo Relax"""

    def __init__(self):
        super().__init__(
            "relax",
            ["spotify.exe", "vlc.exe", "chrome.exe", "firefox.exe"]
        )

    def apply_configurations(self, manager: 'OperationModeManager') -> None:
        logger.info("Aplicando configuraciones de modo Relax")
        # Configuraciones específicas para relax

    def get_monitoring_thresholds(self) -> Dict[str, float]:
        return {
            'cpu': 80.0,
            'memory': 90.0,
            'disk': 95.0,
            'gpu': 85.0
        }

    def should_enable_background_tasks(self) -> bool:
        return False  # Modo restrictivo

class GamingModeStrategy(BaseModeStrategy):
    """Estrategia para modo Gaming"""

    def __init__(self):
        super().__init__(
            "gaming",
            ["steam.exe", "epicgameslauncher.exe", "battle.net.exe", "origin.exe"]
        )

    def apply_configurations(self, manager: 'OperationModeManager') -> None:
        logger.info("Aplicando configuraciones de modo Gaming")
        # Configuraciones específicas para gaming

    def get_monitoring_thresholds(self) -> Dict[str, float]:
        return {
            'cpu': 50.0,
            'memory': 70.0,
            'disk': 75.0,
            'gpu': 60.0
        }

class DesarrolloModeStrategy(BaseModeStrategy):
    """Estrategia para modo Desarrollo"""

    def __init__(self):
        super().__init__(
            "desarrollo",
            ["code.exe", "pycharm.exe", "vscode.exe", "docker.exe", "git.exe", "python.exe"]
        )

    def apply_configurations(self, manager: 'OperationModeManager') -> None:
        logger.info("Aplicando configuraciones de modo Desarrollo")
        # Configuraciones específicas para desarrollo

    def get_monitoring_thresholds(self) -> Dict[str, float]:
        return {
            'cpu': 75.0,
            'memory': 85.0,
            'disk': 90.0,
            'gpu': 80.0
        }

class ModeStrategyRegistry:
    """Registro de estrategias de modo (Registry Pattern - Open/Closed Principle)"""

    def __init__(self):
        self._strategies: Dict[str, Type[IModeStrategy]] = {}
        self._register_builtin_strategies()

    def _register_builtin_strategies(self):
        """Registrar estrategias incorporadas"""
        self.register_strategy("editor", EditorModeStrategy)
        self.register_strategy("streaming", StreamingModeStrategy)
        self.register_strategy("relax", RelaxModeStrategy)
        self.register_strategy("gaming", GamingModeStrategy)
        self.register_strategy("desarrollo", DesarrolloModeStrategy)

    def register_strategy(self, mode_name: str, strategy_class: Type[IModeStrategy]):
        """Registrar una nueva estrategia de modo (Open/Closed Principle)"""
        self._strategies[mode_name] = strategy_class
        logger.info(f"Estrategia registrada: {mode_name}")

    def get_strategy(self, mode_name: str) -> IModeStrategy:
        """Obtener estrategia para un modo"""
        strategy_class = self._strategies.get(mode_name)
        if not strategy_class:
            # Fallback a estrategia por defecto
            strategy_class = self._strategies.get("editor", EditorModeStrategy)
        return strategy_class()

    def get_available_modes(self) -> List[str]:
        """Obtener lista de modos disponibles"""
        return list(self._strategies.keys())

class OperationModeManager:
    """Manager de modos refactorizado con Open/Closed Principle"""

    def __init__(self):
        self.current_mode = settings.current_mode
        self.strategy_registry = ModeStrategyRegistry()
        self.current_strategy = self.strategy_registry.get_strategy(self.current_mode.value)
        logger.info(f"OperationModeManager inicializado en modo: {self.current_mode.value}")

    def set_mode(self, mode: OperationMode):
        """Cambiar el modo de operación"""
        self.current_mode = mode
        settings.set_mode(mode)
        self.current_strategy = self.strategy_registry.get_strategy(mode.value)
        logger.info(f"Modo cambiado a: {mode.value}")

        # Aplicar configuraciones específicas del modo
        self.current_strategy.apply_configurations(self)

    def register_custom_mode(self, mode_name: str, strategy_class: Type[IModeStrategy]):
        """Permitir registro de modos personalizados (Open/Closed Principle)"""
        self.strategy_registry.register_strategy(mode_name, strategy_class)
        logger.info(f"Modo personalizado registrado: {mode_name}")

    def _apply_mode_configurations(self):
        """Aplicar configuraciones específicas del modo actual (delegado a estrategia)"""
        self.current_strategy.apply_configurations(self)

    def _adjust_process_priorities(self):
        """Ajustar prioridades de procesos según procesos foco del modo"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(focus_proc.lower() in proc_name for focus_proc in self.current_strategy.focus_processes):
                        # Aumentar prioridad para procesos foco
                        proc.nice(psutil.HIGH_PRIORITY_CLASS if os.name == 'nt' else -10)
                        logger.debug(f"Prioridad aumentada para proceso foco: {proc_name}")
                    elif not self.current_strategy.should_enable_background_tasks():
                        # Reducir prioridad para procesos no esenciales en modos restrictivos
                        if proc_name not in ['system', 'idle', 'svchost.exe', 'explorer.exe']:
                            proc.nice(psutil.IDLE_PRIORITY_CLASS if os.name == 'nt' else 10)
                            logger.debug(f"Prioridad reducida para proceso: {proc_name}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Error ajustando prioridades de procesos: {e}")

    def _configure_monitoring_thresholds(self):
        """Configurar umbrales de monitoreo según el modo (delegado a estrategia)"""
        thresholds = self.current_strategy.get_monitoring_thresholds()
        logger.info(f"Umbrales configurados para modo {self.current_mode.value}: {thresholds}")
        return thresholds

    def _manage_background_tasks(self):
        """Gestionar tareas en background según el modo (delegado a estrategia)"""
        background_enabled = self.current_strategy.should_enable_background_tasks()
        if not background_enabled:
            logger.info("Modo restrictivo: minimizando tareas en background")
        else:
            logger.info("Modo normal: permitiendo tareas en background")

    def get_mode_info(self) -> Dict[str, Any]:
        """Obtener información del modo actual"""
        return {
            'mode': self.current_mode.value,
            'description': f"Modo {self.current_mode.value}",
            'focus_processes': self.current_strategy.focus_processes,
            'thresholds': self.current_strategy.get_monitoring_thresholds(),
            'background_tasks_enabled': self.current_strategy.should_enable_background_tasks()
        }

    def is_focus_process(self, process_name: str) -> bool:
        """Verificar si un proceso es de foco para el modo actual"""
        return any(focus_proc.lower() in process_name.lower()
                  for focus_proc in self.current_strategy.focus_processes)

    def get_monitoring_interval(self) -> int:
        """Obtener intervalo de monitoreo para el modo actual"""
        # Mantener compatibilidad con configuración existente
        return settings.get_mode_settings().get('monitoring_interval', 5)

    def should_cleanup(self) -> bool:
        """Determinar si se debe ejecutar limpieza según el modo"""
        return settings.get_mode_settings().get('cleanup_enabled', True)

    def should_optimize(self) -> bool:
        """Determinar si se debe ejecutar optimización según el modo"""
        return settings.get_mode_settings().get('optimization_enabled', True)

    def get_available_modes(self) -> List[str]:
        """Obtener lista de modos disponibles (incluyendo personalizados)"""
        return self.strategy_registry.get_available_modes()

# Instancia global del manager
mode_manager = OperationModeManager()