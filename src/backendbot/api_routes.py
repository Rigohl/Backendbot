import os
import time
from datetime import datetime, timezone
from typing import Any

import psutil
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_api_key
from .config import settings
from .process_routes import process_router
from .repositories.history_repository import HistoryRepository
from .services.history_service import HistoryService
from .utils import (
    async_get_db,
    load_memory,
    log_event,
    save_memory,
)

router = APIRouter()


# Dependency to provide HistoryRepository
async def get_history_repository(
    session: AsyncSession = Depends(async_get_db),
) -> HistoryRepository:
    """Provide a HistoryRepository instance."""
    return HistoryRepository(session)


# Dependency to provide HistoryService
async def get_history_service(
    repository: HistoryRepository = Depends(get_history_repository),
) -> HistoryService:
    """Provide a HistoryService instance."""
    return HistoryService(repository)


router.include_router(process_router)


@router.post("/decision/{programa}/{accion}", dependencies=[Depends(get_api_key)])
def guardar_decision(programa: str, accion: str) -> dict[str, Any]:
    """Guarda la decisión de suspender o rechazar un programa en la memoria.

    Args:
        programa (str): El nombre del programa.
        accion (str): La acción realizada ('suspender' o 'rechazar').

    Returns:
        dict[str, Any]: Información actualizada de decisiones para programa.

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
def ver_memoria() -> dict[str, Any]:
    """Retorna el contenido actual de la memoria de decisiones.

    Returns:
        dict[str, Any]: El diccionario que contiene la memoria de decisiones.

    """
    return load_memory()


@router.post("/reset-memoria", dependencies=[Depends(get_api_key)])
def reset_memoria() -> dict[str, str]:
    """Resetea la memoria de decisiones a un estado vacío.

    Returns:
        dict[str, str]: Un diccionario con el estado de la operación.

    """
    save_memory({})
    log_event("🧹 Memoria de decisiones reseteada", notify_user=True)
    return {"status": "ok", "msg": "Memoria reiniciada"}


# === Autodiagnóstico (/self) ===
_app_start = time.time()


@router.get("/self", dependencies=[Depends(get_api_key)])
def self_metrics() -> dict[str, Any]:
    """Retorna métricas de autodiagnóstico del proceso del backend.

    Returns:
        dict[str, Any]: Diccionario con métricas como PID, RAM, hilos, CPU.

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
            "started_at": datetime.fromtimestamp(
                _app_start, tz=timezone.utc
            ).isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener métricas de autodiagnóstico: {e}",
        ) from e


# --- Endpoints para datos históricos ---


@router.get("/history/processes", dependencies=[Depends(get_api_key)])
async def get_process_history(
    limit: int = 100,
    offset: int = 0,
    history_service: HistoryService = Depends(get_history_service),
) -> list[dict[str, Any]]:
    """Retorna el historial de procesos registrados.

    Args:
        limit (int): El número máximo de registros a retornar.
        offset (int): El número de registros a omitir desde el inicio.
        history_service: Servicio de historial inyectado.

    Returns:
        list[dict[str, Any]]: Lista de diccionarios con info de procesos.

    """
    return await history_service.get_process_history(limit, offset)


@router.get("/history/optimizations", dependencies=[Depends(get_api_key)])
async def get_optimization_history(
    limit: int = 100,
    offset: int = 0,
    history_service: HistoryService = Depends(get_history_service),
) -> list[dict[str, Any]]:
    """Retorna el historial de eventos de optimización de RAM.

    Args:
        limit (int): El número máximo de registros a retornar.
        offset (int): El número de registros a omitir desde el inicio.
        history_service: Servicio de historial inyectado.

    Returns:
        list[dict[str, Any]]: Lista de diccionarios con info de eventos.

    """
    return await history_service.get_optimization_history(limit, offset)


@router.get("/history/decisions", dependencies=[Depends(get_api_key)])
async def get_decision_history(
    limit: int = 100,
    offset: int = 0,
    history_service: HistoryService = Depends(get_history_service),
) -> list[dict[str, Any]]:
    """Retorna el historial de decisiones del watchdog.

    Args:
        limit (int): El número máximo de registros a retornar.
        offset (int): El número de registros a omitir desde el inicio.
        history_service: Servicio de historial inyectado.

    Returns:
        list[dict[str, Any]]: Lista de diccionarios con info de decisiones.

    """
    return await history_service.get_decision_history(limit, offset)


@router.get("/get-modo", dependencies=[Depends(get_api_key)])
def get_modo() -> dict[str, str]:
    """Retorna el modo de operación actual del BackendBot.

    Returns:
        dict[str, str]: Diccionario con la clave "modo" y el modo actual.

    """
    return {"modo": settings.MODO}


@router.get("/logs", dependencies=[Depends(get_api_key)])
def get_logs(limit: int = 100) -> list[dict[str, Any]]:
    """Retorna los logs más recientes del backend.

    Args:
        limit (int): El número máximo de líneas de log a retornar.

    Returns:
        list[dict[str, Any]]: Lista de diccionarios con info de logs.

    """
    try:
        if not os.path.exists(settings.LOG_FILE):
            return []

        logs = []
        with open(settings.LOG_FILE, encoding="utf-8") as f:
            lines = f.readlines()[-limit:]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Parsear el formato: [YYYY-MM-DD HH:MM:SS] mensaje
            if line.startswith("[") and "]" in line:
                timestamp_str, message = line.split("]", 1)
                timestamp_str = timestamp_str[1:]  # Remover el '[' inicial
                try:
                    # Intentar parsear la fecha
                    timestamp = datetime.strptime(
                        timestamp_str, "%Y-%m-%d %H:%M:%S"
                    ).replace(tzinfo=timezone.utc).isoformat()
                except ValueError:
                    timestamp = timestamp_str

                # Determinar el nivel del log basado en el contenido
                level = "info"
                if "❌" in message or "Error" in message.lower():
                    level = "error"
                elif "⚠️" in message or "Warning" in message.lower():
                    level = "warning"
                elif "✅" in message or "Success" in message.lower():
                    level = "info"
                elif "🔄" in message or "Debug" in message.lower():
                    level = "debug"

                logs.append(
                    {
                        "timestamp": timestamp,
                        "level": level,
                        "message": message.strip(),
                    }
                )
            else:
                # Si no tiene el formato esperado, agregarlo como info
                logs.append(
                    {
                        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                        "level": "info",
                        "message": line,
                    }
                )

        return logs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener logs: {e}",
        ) from e
