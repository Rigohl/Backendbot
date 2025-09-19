"""Compatibilidad mínima de mensajería en BD para tests.

Proporciona funciones stub que los tests esperan: get_pending_command,
complete_command, set_bot_state y send_result. Implementación ligera
para evitar dependencias en infra inexistente.
"""

import logging
from typing import Any

logger = logging.getLogger("backendbot.db_messaging")


def get_pending_command(bot_name: str) -> dict[str, Any] | None:
    """Retorna el siguiente comando pendiente para un bot (stub)."""
    logger.debug(f"get_pending_command stub called for {bot_name}")
    return None


def complete_command(command_id: str, success: bool, result: Any = None) -> bool:
    """Marcar comando como completado (stub)."""
    logger.debug(f"complete_command stub: {command_id} success={success}")
    return True


def set_bot_state(bot_name: str, state: dict[str, Any]) -> bool:
    """Establecer estado del bot (stub)."""
    logger.debug(f"set_bot_state stub for {bot_name}: {state}")
    return True


def send_result(bot_name: str, payload: dict[str, Any]) -> bool:
    """Enviar resultado de ejecución (stub)."""
    logger.debug(f"send_result stub for {bot_name}: {payload}")
    return True
