"""Paquete de compatibilidad `modes`.

Este paquete reexporta componentes desde `core` para mantener imports históricos.
"""

from ..core.operation_mode_manager import OperationModeManager, mode_manager

__all__ = ["OperationModeManager", "mode_manager"]
