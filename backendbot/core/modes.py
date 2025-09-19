"""Modos de operación para BackendBot - Strategy Pattern."""

from abc import ABC, abstractmethod

from backendbot.core.di.container import container


class BaseModeStrategy(ABC):
    """Estrategia base para modos de operación."""

    def __init__(self, mode_name: str, focus_processes: list) -> None:
        self.mode_name = mode_name
        self.focus_processes = focus_processes
        self.logger = container.get_logger()
        self.config = container.get_config_manager()

    @abstractmethod
    def apply_configurations(self, manager):
        """Aplicar configuraciones específicas del modo."""
        pass

    @abstractmethod
    def get_monitoring_thresholds(self) -> dict:
        """Obtener umbrales de monitoreo para este modo."""
        pass


class EditorModeStrategy(BaseModeStrategy):
    """Modo Editor - Optimizado para edición de código."""

    def __init__(self) -> None:
        super().__init__("editor", ["code.exe", "vscode.exe", "sublime_text.exe"])

    def apply_configurations(self, manager):
        """Configuraciones para modo editor."""
        self.logger.info("Aplicando configuraciones de modo Editor", "EditorMode")

    def get_monitoring_thresholds(self):
        return {
            "cpu": 70.0,  # Más CPU para compilación
            "memory": 75.0,  # Más RAM para editores
            "disk": 80.0,  # Más I/O para guardado
            "gpu": 60.0,  # Menos GPU
        }


class StreamingModeStrategy(BaseModeStrategy):
    """Modo Streaming - Optimizado para transmisión en vivo."""

    def __init__(self) -> None:
        super().__init__("streaming", ["obs.exe", "streamlabs.exe", "discord.exe"])

    def apply_configurations(self, manager):
        """Configuraciones para modo streaming."""
        self.logger.info("Aplicando configuraciones de modo Streaming", "StreamingMode")

    def get_monitoring_thresholds(self):
        return {
            "cpu": 80.0,  # Alta CPU para encoding
            "memory": 70.0,  # RAM moderada
            "disk": 85.0,  # Alto I/O para grabación
            "gpu": 90.0,  # Alta GPU para efectos
        }


class RelaxModeStrategy(BaseModeStrategy):
    """Modo Relax - Optimizado para navegación y multimedia."""

    def __init__(self) -> None:
        super().__init__("relax", ["chrome.exe", "firefox.exe", "vlc.exe"])

    def apply_configurations(self, manager):
        """Configuraciones para modo relax."""
        self.logger.info("Aplicando configuraciones de modo Relax", "RelaxMode")

    def get_monitoring_thresholds(self):
        return {
            "cpu": 60.0,  # CPU moderada
            "memory": 65.0,  # RAM moderada
            "disk": 70.0,  # I/O normal
            "gpu": 70.0,  # GPU moderada para video
        }


class GamingModeStrategy(BaseModeStrategy):
    """Modo Gaming - Optimizado para juegos."""

    def __init__(self) -> None:
        super().__init__("gaming", ["game.exe", "steam.exe", "epicgames.exe"])

    def apply_configurations(self, manager):
        """Configuraciones para modo gaming."""
        self.logger.info("Aplicando configuraciones de modo Gaming", "GamingMode")

    def get_monitoring_thresholds(self):
        return {
            "cpu": 85.0,  # Alta CPU para juegos
            "memory": 80.0,  # Alta RAM para juegos
            "disk": 75.0,  # I/O para carga de niveles
            "gpu": 95.0,  # Máxima GPU para juegos
        }


class DesarrolloModeStrategy(BaseModeStrategy):
    """Modo Desarrollo - Optimizado para desarrollo de software."""

    def __init__(self) -> None:
        super().__init__("desarrollo", ["code.exe", "terminal.exe", "docker.exe"])

    def apply_configurations(self, manager):
        """Configuraciones para modo desarrollo."""
        self.logger.info(
            "Aplicando configuraciones de modo Desarrollo", "DesarrolloMode"
        )

    def get_monitoring_thresholds(self):
        return {
            "cpu": 75.0,  # Alta CPU para compilación/testing
            "memory": 80.0,  # Alta RAM para VMs/IDEs
            "disk": 85.0,  # Alto I/O para builds
            "gpu": 65.0,  # GPU moderada
        }


class ModeStrategyRegistry:
    """Registro de estrategias de modo - Open/Closed Principle."""

    def __init__(self) -> None:
        self._strategies = {}
        self._register_defaults()

    def _register_defaults(self):
        """Registrar estrategias por defecto."""
        self.register_strategy("editor", EditorModeStrategy)
        self.register_strategy("streaming", StreamingModeStrategy)
        self.register_strategy("relax", RelaxModeStrategy)
        self.register_strategy("gaming", GamingModeStrategy)
        self.register_strategy("desarrollo", DesarrolloModeStrategy)

    def register_strategy(self, name: str, strategy_class):
        """Registrar nueva estrategia."""
        self._strategies[name] = strategy_class

    def get_strategy(self, name: str) -> BaseModeStrategy:
        """Obtener estrategia por nombre."""
        if name not in self._strategies:
            raise ValueError(f"Modo '{name}' no registrado")
        return self._strategies[name]()

    def get_available_modes(self) -> list:
        """Obtener lista de modos disponibles."""
        return list(self._strategies.keys())


class OperationModeManager:
    """Manager de modos de operación - Strategy Pattern."""

    def __init__(self) -> None:
        self.logger = container.get_logger()
        self.config = container.get_config_manager()
        self.registry = ModeStrategyRegistry()

        # Modo actual
        default_mode = self.config.get("modes.default", "relax")
        self.current_mode = self._create_mode(default_mode)

        self.logger.info(
            f"OperationModeManager inicializado en modo: {self.current_mode.mode_name}",
            "ModeManager",
        )

    def _create_mode(self, mode_name: str) -> BaseModeStrategy:
        """Crear instancia de modo."""
        return self.registry.get_strategy(mode_name)

    def set_mode(self, mode_name: str):
        """Cambiar modo de operación."""
        try:
            new_mode = self._create_mode(mode_name)
            self.current_mode = new_mode

            # Aplicar configuraciones del nuevo modo
            new_mode.apply_configurations(self)

            self.logger.info(f"Modo cambiado a: {mode_name}", "ModeManager")

            # Guardar en config
            self.config.set("modes.current", mode_name)
            self.config.save()

        except ValueError as e:
            self.logger.error(f"Error cambiando modo: {e}", "ModeManager")
            raise

    def get_current_mode(self) -> str:
        """Obtener modo actual."""
        return self.current_mode.mode_name

    def get_available_modes(self) -> list:
        """Obtener modos disponibles."""
        return self.registry.get_available_modes()

    def get_monitoring_thresholds(self) -> dict:
        """Obtener umbrales de monitoreo del modo actual."""
        return self.current_mode.get_monitoring_thresholds()
