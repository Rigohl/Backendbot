"""Compatibilidad: módulo `modes` mantenido para imports antiguos.

Reexporta `mode_manager` y `OperationModeManager` desde `core.operation_mode_manager`.
"""
from src.backendbot.core.operation_mode_manager import OperationModeManager, mode_manager

__all__ = ["OperationModeManager", "mode_manager"]
