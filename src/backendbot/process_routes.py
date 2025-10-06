"""Process management routes for BackendBot API."""

import psutil
from fastapi import APIRouter, Depends, HTTPException, status

from .auth import get_api_key
from .config import settings
from .utils import (
    _get_process_info,
    _optimize_processes,
    log_event,
    restore_closed_processes,
    store_optimization_event,
)

process_router = APIRouter()


@process_router.get("/procesos", dependencies=[Depends(get_api_key)])
def listar() -> list[dict]:
    """Lista todos los procesos activos del sistema.

    Returns:
        list[dict]: Lista de procesos con información de PID, nombre, RAM y CPU.

    """
    out = []
    for p in psutil.process_iter(["pid", "name", "memory_info", "cpu_percent"]):
        info = _get_process_info(p)
        if info:
            out.append(info)
    return out


@process_router.post("/apagar/{pid}", dependencies=[Depends(get_api_key)])
def apagar(pid: int) -> dict[str, str]:
    """Termina un proceso específico por su PID.

    Args:
        pid (int): El PID del proceso a terminar.

    Returns:
        dict[str, str]: Estado de la operación.

    Raises:
        HTTPException: Si el proceso no existe o no se puede terminar.

    """
    try:
        psutil.Process(pid).terminate()
        log_event(f"Proceso terminado PID {pid}", notify_user=True)
        return {"status": "ok"}
    except psutil.NoSuchProcess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proceso PID {pid} no encontrado.",
        )
    except psutil.AccessDenied:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado para terminar PID {pid}.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al apagar proceso: {e}",
        )


@process_router.post("/resume/{pid}", dependencies=[Depends(get_api_key)])
def resume(pid: int) -> dict[str, str]:
    """Reanuda un proceso suspendido por su PID.

    Args:
        pid (int): El PID del proceso a reanudar.

    Returns:
        dict[str, str]: Estado de la operación.

    Raises:
        HTTPException: Si el proceso no existe o no se puede reanudar.

    """
    try:
        psutil.Process(pid).resume()
        log_event(f"Proceso reanudado PID {pid}", notify_user=True)
        return {"status": "ok"}
    except psutil.NoSuchProcess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proceso PID {pid} no encontrado.",
        )
    except psutil.AccessDenied:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado para reanudar PID {pid}.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al reanudar proceso: {e}",
        )


@process_router.post("/kill/{pid}", dependencies=[Depends(get_api_key)])
def kill(pid: int) -> dict[str, str]:
    """Mata forzadamente un proceso por su PID.

    Args:
        pid (int): El PID del proceso a matar.

    Returns:
        dict[str, str]: Estado de la operación.

    Raises:
        HTTPException: Si el proceso no existe o no se puede matar.

    """
    try:
        psutil.Process(pid).kill()
        log_event(f"Proceso terminado (kill) PID {pid}", notify_user=True)
        return {"status": "ok"}
    except psutil.NoSuchProcess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proceso PID {pid} no encontrado.",
        )
    except psutil.AccessDenied:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado para terminar (kill) PID {pid}.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al terminar (kill) proceso: {e}",
        )


@process_router.post("/optimize", dependencies=[Depends(get_api_key)])
def optimize():
    freed = _optimize_processes()
    msg = f"Optimización automática: {round(freed/1024/1024,1)} MB liberados"
    log_event(msg, notify_user=True)
    store_optimization_event(round(freed / 1024 / 1024, 1))
    return {"status": "ok", "ram_liberada_mb": round(freed / 1024 / 1024, 1)}


@process_router.post("/set-modo/{modo}", dependencies=[Depends(get_api_key)])
def set_modo(modo: str):
    if modo not in settings.PROCESOS_A_CERRAR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Modo no válido"
        )
    closed = []
    for p in psutil.process_iter(["pid", "name"]):
        try:
            name = p.info["name"]
            if name.lower() in [
                proc.lower() for proc in settings.PROCESOS_A_CERRAR[modo]
            ] and name.lower() not in [
                imp.lower() for imp in settings.PROCESOS_IMPORTANTES
            ]:
                psutil.Process(p.info["pid"]).terminate()
                closed.append(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            log_event(
                f"Error al procesar PID {p.info.get('pid', 'N/A')} en set-modo: {e}"
            )
        except Exception as e:
            log_event(f"Error inesperado en set-modo: {e}")
    log_event(f"Modo {modo} activado, procesos cerrados: {closed}", notify_user=True)
    return {"status": "ok", "modo": modo, "procesos_cerrados": closed}


@process_router.post("/restore-important", dependencies=[Depends(get_api_key)])
def restore_important():
    restore_closed_processes(settings.MODO)
    return {"status": "ok"}


@process_router.get("/modos", dependencies=[Depends(get_api_key)])
def get_modos():
    """Retorna la lista de modos disponibles."""
    return list(settings.PROCESOS_A_CERRAR.keys())
