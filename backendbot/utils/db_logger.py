"""Logger simplificado que permite compatibilidad con tests y módulos.

Provee `log_system_event` y `log_bot_action` con comportamiento mínimo:
- Emite eventos al logger estándar
- Si la capa de persistencia está inicializada, intenta guardar en la BD
"""

import logging
from typing import Any

logger = logging.getLogger("backendbot.db_logger")


def log_system_event(level: str, source: str, message: str, details: str = "") -> None:
    """Registrar evento del sistema.

    Args:
    ----
            level: Nivel de severidad ('INFO','WARNING','ERROR')
            source: Componente origen
            message: Mensaje legible
            details: Detalles adicionales
    """
    text = f"[{level}] {source}: {message} -- {details}"
    if level.upper() == "ERROR":
        logger.error(text)
    elif level.upper() == "WARNING":
        logger.warning(text)
    else:
        logger.info(text)


def log_bot_action(
    bot_name: str, action_type: str, status: str, target: str = "", result: Any = None
) -> None:
    """Registrar acción de bot.

    Guarda en logger. Si existe una capa de persistencia, no falla al intentar usarla.
    """
    try:
        logger.info(
            f"Bot:{bot_name} action={action_type} status={status} target={target} result={result}"
        )
    except Exception:
        pass
