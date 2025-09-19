"""Paquete de utilidades de BackendBot.

Archivo ligero: evita importar submódulos pesados para prevenir ciclos
de importación. Los submódulos deben importarse explícitamente cuando se usan,
por ejemplo `from src.backendbot.utils import advanced_command_processor` o
`import src.backendbot.utils.advanced_command_processor as acp`.
"""

__all__ = []

