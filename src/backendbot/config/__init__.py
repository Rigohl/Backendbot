"""Módulo de configuración de BackendBot.

Este archivo re-exporta símbolos públicos desde `config.py` para facilitar las importaciones.
"""
from .config import OperationMode, Settings, settings

__all__ = ["OperationMode", "Settings", "settings"]
