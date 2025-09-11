import os
import time
from datetime import datetime, timezone
from typing import Any, Dict

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

# Import staging automation functions
from .staging_automation import (
    schedule_optimizations,
    list_recommended_powershell_commands,
    prepare_background_command,
    optimize_ram,
    perform_disk_cleanup_preview,
    write_plan_to_file,
    run_preview_workflow,
)

router = APIRouter()


from .dependencies import get_api_key
from .routers import history_routes

router.include_router(process_router)  # Include the new router
router.include_router(history_routes.router) # Include the history router


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
        with open(settings.LOG_FILE, encoding="utf-8") as f:
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

                    timestamp = datetime.strptime(
                        timestamp_str, "%Y-%m-%d %H:%M:%S"
                    ).isoformat()
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


# Integrated staging automation endpoints
@router.post("/schedule-optimizations", dependencies=[Depends(get_api_key)])
def api_schedule_optimizations(name: str = "backendbot_opt", command: str = "python main.py", schedule: str = "daily", dry_run: bool = True):
    """Schedule optimization tasks. Defaults to dry-run mode for safety."""
    try:
        plan = schedule_optimizations(name=name, command=command, schedule=schedule, dry_run=dry_run)
        log_event(f"Optimization scheduling plan created: {name}", notify_user=True)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling optimizations: {e}")


@router.get("/powershell-commands", dependencies=[Depends(get_api_key)])
def api_get_powershell_commands():
    """Get recommended PowerShell commands for automation."""
    try:
        cmds = list_recommended_powershell_commands()
        return {"commands": cmds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting PowerShell commands: {e}")


@router.post("/background-command", dependencies=[Depends(get_api_key)])
def api_prepare_background_command(script_path: str = "scripts/start_staging.ps1"):
    """Prepare a PowerShell command to run scripts in background."""
    try:
        cmd = prepare_background_command(script_path=script_path)
        return {"command": cmd, "note": "Execute this command in PowerShell to run in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error preparing background command: {e}")


@router.post("/optimize-ram", dependencies=[Depends(get_api_key)])
def api_optimize_ram(dry_run: bool = True, max_processes: int = 10):
    """Optimize RAM usage by identifying and optionally terminating processes."""
    try:
        plan = optimize_ram(dry_run=dry_run, max_processes=max_processes)
        if not dry_run:
            log_event(f"RAM optimization executed: {plan.get('estimated_freed_mb', 0)} MB estimated", notify_user=True)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing RAM: {e}")


@router.post("/disk-cleanup-preview", dependencies=[Depends(get_api_key)])
def api_disk_cleanup_preview(directories: list = None, dry_run: bool = True):
    """Preview disk cleanup operations."""
    try:
        if directories is None:
            directories = [os.environ.get("TEMP", r"C:\\Windows\\Temp")]
        plan = perform_disk_cleanup_preview(directories=directories, dry_run=dry_run)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error previewing disk cleanup: {e}")


@router.post("/run-preview-workflow", dependencies=[Depends(get_api_key)])
def api_run_preview_workflow(out_path: str = "data/optimization_plan.json"):
    """Run complete preview workflow and save plan to file."""
    try:
        plan = run_preview_workflow(out_path=out_path)
        log_event("Preview workflow completed and saved", notify_user=True)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running preview workflow: {e}")


@router.get("/automation-status", dependencies=[Depends(get_api_key)])
def get_automation_status():
    """Get current automation status and available features."""
    try:
        return {
            "staging_automation_available": True,
            "features": [
                "schedule_optimizations",
                "powershell_commands",
                "background_execution",
                "ram_optimization",
                "disk_cleanup",
                "preview_workflow"
            ],
            "safety_mode": "dry_run_default",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting automation status: {e}")
