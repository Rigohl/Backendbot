"""
Paquete principal de BackendBot. Re-exporta módulos clave para importaciones desde `src.backendbot`.
"""
from . import config
from . import core
from . import ui
from . import bots
from . import utils

__all__ = ["config", "core", "ui", "bots", "utils"]
