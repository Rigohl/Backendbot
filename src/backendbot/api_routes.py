import os
import time
from datetime import datetime, timezone
from typing import Any, Dict

import GPUtil
import psutil
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import wmi

from .config import settings
from .process_routes import process_router  # New import
from .utils import (
    async_get_db,
    db,
    load_memory,
    log_event,
    save_memory,
    _optimize_processes,
    ProcessHistory,
    OptimizationEvent,
    WatchdogDecision
)  # Removed store_process_data, store_optimization_event, restore_closed_processes
from .repositories.history_repository import HistoryRepository # New import
from .services.history_service import HistoryService # New import

router = APIRouter()

# Dependency to provide HistoryRepository
async def get_history_repository(session: AsyncSession = Depends(async_get_db)) -> HistoryRepository:
    """Provides a HistoryRepository instance."""
    return HistoryRepository(session)

# Dependency to provide HistoryService
async def get_history_service(
    repository: HistoryRepository = Depends(get_history_repository)
) -> HistoryService:
    """Provides a HistoryService instance."""
    return HistoryService(repository)


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
def ver_memoria() -> dict[str, Any]:
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
def self_metrics() -> dict[str, Any]:
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

        # GPU info
        gpu_info = GPUtil.getGPUs()
        gpu_percent = gpu_info[0].load * 100 if gpu_info else 0
        gpu_memory_used = gpu_info[0].memoryUsed if gpu_info else 0

        # Temperature (CPU)
        w = wmi.WMI()
        temp_info = w.query("SELECT * FROM Win32_TemperatureProbe")
        cpu_temp = temp_info[0].CurrentReading / 10 if temp_info else None

        return {
            "pid": p.pid,
            "ram_mb": round(mem.rss / 1024 / 1024, 2),
            "privados_mb": privados_mb,
            "num_threads": p.num_threads(),
            "cpu_percent": p.cpu_percent(interval=0.1),
            "uptime_sec": round(time.time() - _app_start, 1),
            "started_at": datetime.fromtimestamp(_app_start, tz=timezone.utc).isoformat(),
            "gpu_percent": gpu_percent,
            "gpu_memory_used": gpu_memory_used,
            "cpu_temp": cpu_temp
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
    history_service: HistoryService = Depends(get_history_service) # Injected service
) -> list[dict[str, Any]]:
    """Retorna el historial de procesos registrados.

    Args:
        limit (int): El número máximo de registros a retornar.
        offset (int): El número de registros a omitir desde el inicio.

    Returns:
        list[Dict[str, Any]]: Una lista de diccionarios con la información de los procesos.

    """
    return await history_service.get_process_history(limit, offset)


@router.get("/history/optimizations", dependencies=[Depends(get_api_key)])
async def get_optimization_history(
    limit: int = 100,
    offset: int = 0,
    history_service: HistoryService = Depends(get_history_service) # Injected service
) -> list[dict[str, Any]]:
    """Retorna el historial de eventos de optimización de RAM.

    Args:
        limit (int): El número máximo de registros a retornar.
        offset (int): El número de registros a omitir desde el inicio.

    Returns:
        list[Dict[str, Any]]: Una lista de diccionarios con la información de los eventos de optimización.

    """
    return await history_service.get_optimization_history(limit, offset)


@router.get("/history/decisions", dependencies=[Depends(get_api_key)])
async def get_decision_history(
    limit: int = 100,
    offset: int = 0,
    history_service: HistoryService = Depends(get_history_service) # Injected service
) -> list[dict[str, Any]]:
    """Retorna el historial de decisiones del watchdog.

    Args:
        limit (int): El número máximo de registros a retornar.
        offset (int): El número de registros a omitir desde el inicio.

    Returns:
        list[Dict[str, Any]]: Una lista de diccionarios con la información de las decisiones del watchdog.

    """
    return await history_service.get_decision_history(limit, offset)


# === Autodiagnóstico (/self) ===
_app_start = time.time()


@router.get("/self", dependencies=[Depends(get_api_key)])
def self_metrics() -> dict[str, Any]:
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

        # GPU info
        gpu_info = GPUtil.getGPUs()
        gpu_percent = gpu_info[0].load * 100 if gpu_info else 0
        gpu_memory_used = gpu_info[0].memoryUsed if gpu_info else 0

        # Temperature (CPU)
        w = wmi.WMI()
        temp_info = w.query("SELECT * FROM Win32_TemperatureProbe")
        cpu_temp = temp_info[0].CurrentReading / 10 if temp_info else None

        return {
            "pid": p.pid,
            "ram_mb": round(mem.rss / 1024 / 1024, 2),
            "privados_mb": privados_mb,
            "num_threads": p.num_threads(),
            "cpu_percent": p.cpu_percent(interval=0.1),
            "uptime_sec": round(time.time() - _app_start, 1),
            "started_at": datetime.fromtimestamp(_app_start, tz=timezone.utc).isoformat(),
            "gpu_percent": gpu_percent,
            "gpu_memory_used": gpu_memory_used,
            "cpu_temp": cpu_temp
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener métricas de autodiagnóstico: {e}",
        ) from e


# --- Endpoints para datos históricos ---


@router.get("/history/processes", dependencies=[Depends(get_api_key)])
async def get_process_history(
    limit: int = 100, offset: int = 0, db: AsyncSession = Depends(async_get_db)
) -> list[dict[str, Any]]:
    """Retorna el historial de procesos registrados.

    Args:
        limit (int): El número máximo de registros a retornar.
        offset (int): El número de registros a omitir desde el inicio.

    Returns:
        list[Dict[str, Any]]: Una lista de diccionarios con la información de los procesos.

    """
    result = await db.execute(
        select(ProcessHistory)
        .order_by(ProcessHistory.timestamp.desc())
        .offset(offset)
        .limit(limit)
    )
    return [row.to_dict() for row in result.scalars().all()]


@router.get("/history/optimizations", dependencies=[Depends(get_api_key)])
async def get_optimization_history(
    limit: int = 100, offset: int = 0, db: AsyncSession = Depends(async_get_db)
) -> list[dict[str, Any]]:
    """Retorna el historial de eventos de optimización de RAM.

    Args:
        limit (int): El número máximo de registros a retornar.
        offset (int): El número de registros a omitir desde el inicio.

    Returns:
        list[Dict[str, Any]]: Una lista de diccionarios con la información de los eventos de optimización.

    """
    result = await db.execute(
        select(OptimizationEvent)
        .order_by(OptimizationEvent.timestamp.desc())
        .offset(offset)
        .limit(limit)
    )
    return [row.to_dict() for row in result.scalars().all()]


@router.get("/history/decisions", dependencies=[Depends(get_api_key)])
async def get_decision_history(
    limit: int = 100, offset: int = 0, db: AsyncSession = Depends(async_get_db)
) -> list[dict[str, Any]]:
    """Retorna el historial de decisiones del watchdog.

    Args:
        limit (int): El número máximo de registros a retornar.
        offset (int): El número de registros a omitir desde el inicio.

    Returns:
        list[Dict[str, Any]]: Una lista de diccionarios con la información de las decisiones del watchdog.

    """
    result = await db.execute(
        select(WatchdogDecision)
        .order_by(WatchdogDecision.timestamp.desc())
        .offset(offset)
        .limit(limit)
    )
    return [row.to_dict() for row in result.scalars().all()]
    return {"status": "ok", "msg": "Memoria reiniciada"}


# === Autodiagnóstico (/self) ===
_app_start = time.time()


@router.get("/self", dependencies=[Depends(get_api_key)])
def self_metrics() -> dict[str, Any]:
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

        # GPU info
        gpu_info = GPUtil.getGPUs()
        gpu_percent = gpu_info[0].load * 100 if gpu_info else 0
        gpu_memory_used = gpu_info[0].memoryUsed if gpu_info else 0

        # Temperature (CPU)
        w = wmi.WMI()
        temp_info = w.query("SELECT * FROM Win32_TemperatureProbe")
        cpu_temp = temp_info[0].CurrentReading / 10 if temp_info else None

        return {
            "pid": p.pid,
            "ram_mb": round(mem.rss / 1024 / 1024, 2),
            "privados_mb": privados_mb,
            "num_threads": p.num_threads(),
            "cpu_percent": p.cpu_percent(interval=0.1),
            "uptime_sec": round(time.time() - _app_start, 1),
            "started_at": datetime.fromtimestamp(_app_start, tz=timezone.utc).isoformat(),
            "gpu_percent": gpu_percent,
            "gpu_memory_used": gpu_memory_used,
            "cpu_temp": cpu_temp
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener métricas de autodiagnóstico: {e}",
        ) from e


# --- Endpoints para datos históricos ---


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


@router.get("/get-modo", dependencies=[Depends(get_api_key)])
def get_modo() -> dict[str, str]:
    """Retorna el modo de operación actual del BackendBot.

    Returns:
        Dict[str, str]: Un diccionario con la clave "modo" y el modo actual como valor.

    """
    return {"modo": settings.MODO}


@router.get("/logs", dependencies=[Depends(get_api_key)])
def get_logs(limit: int = 100) -> list[dict[str, Any]]:
    """Retorna los logs más recientes del backend.

    Args:
        limit (int): El número máximo de líneas de log a retornar.

    Returns:
        list[Dict[str, Any]]: Una lista de diccionarios con la información de los logs.

    """
    try:
        if not os.path.exists(settings.LOG_FILE):
            return []

        logs = []
        with open(settings.LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]  # Obtener las últimas 'limit' líneas

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
                    from datetime import datetime

                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").isoformat()
                except ValueError:
                    timestamp = timestamp_str

                # Determinar el nivel del log basado en el contenido del mensaje
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
                        "timestamp": datetime.now().isoformat(),
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


@router.get("/startup-programs", dependencies=[Depends(get_api_key)])
def get_startup_programs():
    """Obtiene la lista de programas de inicio."""
    try:
        w = wmi.WMI()
        startups = w.Win32_StartupCommand()
        return [{"name": s.Name, "command": s.Command, "location": s.Location} for s in startups]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo startups: {e}")


@router.post("/disable-startup/{name}", dependencies=[Depends(get_api_key)])
def disable_startup(name: str):
    """Deshabilita un programa de inicio."""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
        return {"status": "ok", "message": f"Programa {name} deshabilitado"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deshabilitando: {e}")


@router.post("/optimize-aggressive", dependencies=[Depends(get_api_key)])
def optimize_aggressive():
    """Optimización agresiva de RAM: cierra procesos inactivos y limpia cache."""
    try:
        freed = _optimize_processes()
        # Limpiar cache adicional
        import ctypes
        ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)  # Limpiar working set
        log_event("Optimización agresiva completada", notify_user=True)
        return {"status": "ok", "ram_liberada_mb": round(freed / 1024 / 1024, 1)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en optimización agresiva: {e}")


@router.post("/clean-disk", dependencies=[Depends(get_api_key)])
def clean_disk():
    """Limpia archivos temporales y cache del disco."""
    try:
        import shutil
        import os
        temp_dir = os.environ.get('TEMP', 'C:\\Windows\\Temp')
        shutil.rmtree(temp_dir, ignore_errors=True)
        os.makedirs(temp_dir, exist_ok=True)
        # Desfragmentar (opcional, requiere admin)
        import subprocess
        subprocess.run(['defrag', 'C:', '/O'], capture_output=True)
        log_event("Limpieza de disco completada", notify_user=True)
        return {"status": "ok", "message": "Disco limpiado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error limpiando disco: {e}")


@router.post("/clear-cache", dependencies=[Depends(get_api_key)])
def clear_cache():
    """Limpia cache del sistema."""
    try:
        import subprocess
        import os
        # Limpiar cache de Windows
        subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
        subprocess.run(['net', 'stop', 'wuauserv'], capture_output=True)
        subprocess.run(['net', 'start', 'wuauserv'], capture_output=True)
        # Limpiar archivos temporales
        temp_dir = os.environ.get('TEMP', 'C:\\Windows\\Temp')
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                try:
                    os.remove(os.path.join(root, file))
                except:
                    pass
        log_event("Cache del sistema limpiado", notify_user=True)
        return {"status": "ok", "message": "Cache limpiado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error limpiando cache: {e}")


@router.get("/disk-usage", dependencies=[Depends(get_api_key)])
def get_disk_usage():
    """Obtiene uso de disco por partición."""
    try:
        import psutil
        disks = []
        for partition in psutil.disk_partitions():
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent
            })
        return {"disks": disks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo uso de disco: {e}")


@router.get("/services", dependencies=[Depends(get_api_key)])
def get_services():
    """Obtiene lista de servicios de Windows."""
    try:
        import wmi
        c = wmi.WMI()
        services = []
        for service in c.Win32_Service():
            services.append({
                "name": service.Name,
                "display_name": service.DisplayName,
                "status": service.State,
                "start_mode": service.StartMode
            })
        return {"services": services}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo servicios: {e}")

@router.post("/service/{action}/{name}", dependencies=[Depends(get_api_key)])
def manage_service(action: str, name: str):
    """Inicia, detiene o reinicia un servicio."""
    try:
        import wmi
        c = wmi.WMI()
        service = c.Win32_Service(Name=name)[0]
        if action == "start":
            service.StartService()
        elif action == "stop":
            service.StopService()
        elif action == "restart":
            service.StopService()
            service.StartService()
        log_event(f"Servicio {name} {action}ed", notify_user=True)
        return {"status": "ok", "message": f"Servicio {action}ed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error gestionando servicio: {e}")


@router.get("/network", dependencies=[Depends(get_api_key)])
def get_network_info():
    """Obtiene información de red."""
    try:
        import psutil
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "errin": net_io.errin,
            "errout": net_io.errout
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo info de red: {e}")

@router.get("/network-connections", dependencies=[Depends(get_api_key)])
def get_network_connections():
    """Obtiene conexiones de red activas."""
    try:
        import psutil
        connections = []
        for conn in psutil.net_connections():
            connections.append({
                "fd": conn.fd,
                "family": conn.family,
                "type": conn.type,
                "laddr": str(conn.laddr),
                "raddr": str(conn.raddr) if conn.raddr else None,
                "status": conn.status,
                "pid": conn.pid
            })
        return {"connections": connections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo conexiones: {e}")


@router.get("/processes-detailed", dependencies=[Depends(get_api_key)])
def get_processes_detailed():
    """Obtiene lista detallada de procesos."""
    try:
        import psutil
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cpu_percent": proc.info['cpu_percent'],
                    "memory_percent": proc.info['memory_percent'],
                    "status": proc.info['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return {"processes": processes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo procesos: {e}")


@router.post("/kill-process/{pid}", dependencies=[Depends(get_api_key)])
def kill_process(pid: int):
    """Mata un proceso por PID."""
    try:
        import psutil
        p = psutil.Process(pid)
        p.terminate()
        log_event(f"Proceso {pid} terminado", notify_user=True)
        return {"status": "ok", "message": f"Proceso {pid} terminado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error terminando proceso: {e}")


@router.get("/battery", dependencies=[Depends(get_api_key)])
def get_battery_info():
    """Obtiene información de batería (si existe)."""
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            return {
                "percent": battery.percent,
                "secsleft": battery.secsleft,
                "power_plugged": battery.power_plugged
            }
        else:
            return {"message": "No battery detected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo info de batería: {e}")


@router.get("/system-info", dependencies=[Depends(get_api_key)])
def get_system_info():
    """Obtiene información general del sistema."""
    try:
        import psutil
        import platform
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "memory_total": psutil.virtual_memory().total,
            "disk_usage": psutil.disk_usage('/').total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo info del sistema: {e}")


@router.get("/temperatures", dependencies=[Depends(get_api_key)])
def get_temperatures():
    """Obtiene temperaturas del sistema."""
    try:
        import psutil
        temps = psutil.sensors_temperatures()
        result = {}
        for name, entries in temps.items():
            result[name] = [{"label": entry.label, "current": entry.current, "high": entry.high, "critical": entry.critical} for entry in entries]
        return {"temperatures": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo temperaturas: {e}")


@router.get("/fans", dependencies=[Depends(get_api_key)])
def get_fans():
    """Obtiene información de ventiladores."""
    try:
        import psutil
        fans = psutil.sensors_fans()
        result = {}
        for name, entries in fans.items():
            result[name] = [{"label": entry.label, "current": entry.current} for entry in entries]
        return {"fans": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo info de ventiladores: {e}")


@router.post("/power/{action}", dependencies=[Depends(get_api_key)])
def manage_power(action: str):
    """Gestiona acciones de energía del sistema."""
    try:
        import subprocess
        if action == "shutdown":
            subprocess.run(['shutdown', '/s', '/t', '0'], capture_output=True)
        elif action == "restart":
            subprocess.run(['shutdown', '/r', '/t', '0'], capture_output=True)
        elif action == "sleep":
            subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], capture_output=True)
        elif action == "hibernate":
            subprocess.run(['shutdown', '/h'], capture_output=True)
        log_event(f"Acción de energía: {action}", notify_user=True)
        return {"status": "ok", "message": f"Sistema {action}ing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en acción de energía: {e}")


@router.get("/power-plans", dependencies=[Depends(get_api_key)])
def get_power_plans():
    """Obtiene planes de energía disponibles."""
    try:
        import subprocess
        result = subprocess.run(['powercfg', '/list'], capture_output=True, text=True)
        return {"power_plans": result.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo planes de energía: {e}")


@router.get("/event-logs", dependencies=[Depends(get_api_key)])
def get_event_logs():
    """Obtiene logs de eventos del sistema."""
    try:
        import subprocess
        result = subprocess.run(['wevtutil', 'qe', 'System', '/c:10', '/f:text'], capture_output=True, text=True)
        return {"event_logs": result.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo logs de eventos: {e}")


@router.post("/schedule-task", dependencies=[Depends(get_api_key)])
def schedule_task(task_name: str, command: str, schedule: str):
    """Programa una tarea en el programador de tareas."""
    try:
        import subprocess
        # Crear tarea básica (ejemplo simple)
        subprocess.run(['schtasks', '/create', '/tn', task_name, '/tr', command, '/sc', schedule], capture_output=True)
        log_event(f"Tarea programada: {task_name}", notify_user=True)
        return {"status": "ok", "message": f"Tarea {task_name} programada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error programando tarea: {e}")


@router.post("/backup-config", dependencies=[Depends(get_api_key)])
def backup_config():
    """Crea backup de configuración del sistema."""
    try:
        import shutil
        import os
        from datetime import datetime
        
        backup_dir = "C:\\Backups"
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"system_backup_{timestamp}")
        
        # Backup de archivos de configuración comunes
        config_files = [
            "C:\\Windows\\System32\\drivers\\etc\\hosts",
            os.path.expanduser("~\\AppData\\Local\\Microsoft\\Windows\\Shell\\LayoutModification.xml")
        ]
        
        for file in config_files:
            if os.path.exists(file):
                shutil.copy2(file, backup_path)
        
        log_event(f"Backup creado en {backup_path}", notify_user=True)
        return {"status": "ok", "message": f"Backup creado en {backup_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando backup: {e}")


@router.get("/system-health", dependencies=[Depends(get_api_key)])
def get_system_health():
    """Obtiene estado general de salud del sistema."""
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_score = 100
        issues = []
        
        if cpu_percent > 80:
            health_score -= 20
            issues.append("CPU usage high")
        if memory.percent > 80:
            health_score -= 20
            issues.append("Memory usage high")
        if disk.percent > 90:
            health_score -= 20
            issues.append("Disk usage high")
        
        return {
            "health_score": max(0, health_score),
            "issues": issues,
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo salud del sistema: {e}")
