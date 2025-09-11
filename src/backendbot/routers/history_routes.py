from typing import Any, List, Dict

from fastapi import APIRouter, Depends

from ..utils import db
from ..dependencies import get_api_key

router = APIRouter()


@router.get("/history/processes", dependencies=[Depends(get_api_key)])
def get_process_history(limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
    """Retorna el historial de procesos registrados.

    Args:
        limit (int): El número máximo de registros a retornar.
        offset (int): El número de registros a omitir desde el inicio.

    Returns:
        list[Dict[str, Any]]: Una lista de diccionarios con la información de los procesos.

    """
    table = db["process_history"]
    return list(table.find(order_by="-timestamp", limit=limit, offset=offset))


@router.get("/history/optimizations", dependencies=[Depends(get_api_key)])
def get_optimization_history(limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
    """Retorna el historial de eventos de optimización de RAM.

    Args:
        limit (int): El número máximo de registros a retornar.
        offset (int): El número de registros a omitir desde el inicio.

    Returns:
        list[Dict[str, Any]]: Una lista de diccionarios con la información de los eventos de optimización.

    """
    table = db["optimization_events"]
    return list(table.find(order_by="-timestamp", limit=limit, offset=offset))


@router.get("/history/decisions", dependencies=[Depends(get_api_key)])
def get_decision_history(limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
    """Retorna el historial de decisiones del watchdog.

    Args:
        limit (int): El número máximo de registros a retornar.
        offset (int): El número de registros a omitir desde el inicio.

    Returns:
        list[Dict[str, Any]]: Una lista de diccionarios con la información de las decisiones del watchdog.

    """
    table = db["watchdog_decisions"]
    return list(table.find(order_by="-timestamp", limit=limit, offset=offset))
