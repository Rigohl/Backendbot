import os
import time
from datetime import datetime, timezone
from typing import Any

import psutil
from fastapi import APIRouter, Depends, HTTPException, status

from .config import settings
from .process_routes import process_router  # New import
from .utils import (
    db,
    load_memory,
    log_event,
    save_memory,
)  # Removed store_process_data, store_optimization_event, restore_closed_processes

router = APIRouter()


# Dependency to check API Key
def get_api_key(
    api_key: str = Depends(
        HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    )
) -> str:
    """Dependency to validate the API Key provided in the request header.

    Args:
        api_key (str): The API key from the request header.

    Returns:
        str: The API key if valid.

    Raises:
        HTTPException: If the API key is invalid.

    """
    if api_key == settings.API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key"
    )


router.include_router(process_router)  # Include the new router


@router.post("/decision/{programa}/{accion}", dependencies=[Depends(get_api_key)])
def guardar_decision(programa: str, accion: str) -> Dict[str, Any]:
    """Guarda la decisión de suspender o rechazar un programa en la memoria.

    Args:
        programa (str): El nombre del programa.
        accion (str): La acción realizada ('suspender' o 'rechazar').

    Returns:
        Dict[str, Any]: La información actualizada de las decisiones para el programa.

    """
    memory = load_memory()
    memory.setdefault(programa, {"suspensiones": 0, "rechazos": 0})
    if accion == "suspender":
        memory[programa]["suspensiones"] += 1
    elif accion == "rechazar":
        memory[programa]["rechazos"] += 1
    save_memory(memory)
    return memory.get(programa)


@router.get("/memoria", dependencies=[Depends(get_api_key)])
def ver_memoria() -> Dict[str, Any]:
    """Retorna el contenido actual de la memoria de decisiones.

    Returns:
        Dict[str, Any]: El diccionario que contiene la memoria de decisiones.

    """
    return load_memory()


@router.post("/reset-memoria", dependencies=[Depends(get_api_key)])
def reset_memoria() -> Dict[str, str]:
    """Resetea la memoria de decisiones a un estado vacío.

    Returns:
        Dict[str, str]: Un diccionario con el estado de la operación.

    """
    save_memory({})
    log_event("🧹 Memoria de decisiones reseteada", notify_user=True)
    return {"status": "ok", "msg": "Memoria reiniciada"}


# === Autodiagnóstico (/self) ===
_app_start = time.time()


@router.get("/self", dependencies=[Depends(get_api_key)])
def self_metrics() -> Dict[str, Any]:
    """Retorna métricas de autodiagnóstico del proceso del backend.

    Returns:
        Dict[str, Any]: Un diccionario con métricas como PID, uso de RAM, hilos, CPU, etc.

    Raises:
        HTTPException: Si ocurre un error al obtener las métricas.

    """
    try:
        p = psutil.Process(os.getpid())
        mem = p.memory_info()
        privados = getattr(mem, "private", None)
        privados_mb = None
        if privados is not None:
            privados_mb = round(privados / 1024 / 1024, 2)
        return {
            "pid": p.pid,
            "ram_mb": round(mem.rss / 1024 / 1024, 2),
            "privados_mb": privados_mb,
            "num_threads": p.num_threads(),
            "cpu_percent": p.cpu_percent(interval=0.1),
            "uptime_sec": round(time.time() - _app_start, 1),
            "started_at": datetime.fromtimestamp(_app_start, tz=timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener métricas de autodiagnóstico: {e}",
        ) from e


# --- Endpoints para datos históricos ---


@router.get("/history/processes", dependencies=[Depends(get_api_key)])
def get_process_history(limit: int = 100, offset: int = 0) -> list[Dict[str, Any]]:
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
def get_optimization_history(limit: int = 100, offset: int = 0) -> list[Dict[str, Any]]:
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
def get_decision_history(limit: int = 100, offset: int = 0) -> list[Dict[str, Any]]:
    """Retorna el historial de decisiones del watchdog.

    Args:
        limit (int): El número máximo de registros a retornar.
        offset (int): El número de registros a omitir desde el inicio.

    Returns:
        list[Dict[str, Any]]: Una lista de diccionarios con la información de las decisiones del watchdog.

    """
    table = db["watchdog_decisions"]
    return list(table.find(order_by="-timestamp", limit=limit, offset=offset))


@router.get("/get-modo", dependencies=[Depends(get_api_key)])
def get_modo() -> dict[str, str]:
    """Retorna el modo de operación actual del BackendBot.

    Returns:
        Dict[str, str]: Un diccionario con la clave "modo" y el modo actual como valor.

    """
    return {"modo": settings.MODO}
