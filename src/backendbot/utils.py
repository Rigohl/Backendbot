import json
import os
import subprocess
import time
from pathlib import Path

import psutil

from .config import settings
from .services.notification_service import notify # Import notify from its dedicated service

import logging
import logging.config

# Global logger instance
_logger_initialized = False
_logger = None

def log_event(msg: str, notify_user: bool = False, level: str = "info") -> None:
    """Registra un evento usando el módulo de logging estándar."""
    global _logger_initialized, _logger

    if not _logger_initialized:
        try:
            logging.config.dictConfig(settings.LOGGING_CONFIG)
            _logger = logging.getLogger("backendbot")
            _logger_initialized = True
        except Exception as e:
            print(f"ERROR: Failed to configure logger: {e}")
            # Fallback to print if logging setup fails
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")
            if notify_user:
                notify("BackendBot", msg)
            return

    if _logger_initialized:
        if level.lower() == "debug":
            _logger.debug(msg)
        elif level.lower() == "info":
            _logger.info(msg)
        elif level.lower() == "warning":
            _logger.warning(msg)
        elif level.lower() == "error":
            _logger.error(msg)
        elif level.lower() == "critical":
            _logger.critical(msg)
        else:
            _logger.info(msg) # Default to info

    if notify_user:
        notify("BackendBot", msg)


def load_memory() -> dict:
    """Carga la memoria desde el archivo JSON."""
    if Path(settings.MEMORY_FILE).exists():
        try:
            with open(settings.MEMORY_FILE, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            log_event(
                f"Error: El archivo de memoria '{settings.MEMORY_FILE}' "
                "está corrupto o vacío. Se creará uno nuevo."
            )
            return {}
        except OSError as e:
            log_event(f"Error de E/S al cargar la memoria: {e}")
            return {}
    return {}


def save_memory(memory: dict) -> None:
    """Guarda la memoria en el archivo JSON."""
    with open(settings.MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def _get_process_info(p: psutil.Process) -> dict | None:
    """Obtiene información de un proceso."""
    try:
        return {
            "pid": p.pid,
            "name": p.name(),
            "ram_mb": round(p.memory_info().rss / 1024 / 1024, 2),
            "cpu_percent": p.cpu_percent(interval=0.1),
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None

def restore_closed_processes(modo: str) -> None:

    """Restaura procesos importantes que no están corriendo."""
    for proc in settings.PROCESOS_IMPORTANTES:
        running = any(
            proc.lower() in p.info["name"].lower()
            for p in psutil.process_iter(["name"])
        )
        if not running:
            try:
                subprocess.Popen(proc)
                log_event(f"Proceso restaurado: {proc}")
            except Exception as e:
                log_event(f"Error al restaurar {proc}: {e}")


# --- Funciones para almacenar datos históricos ---
# These functions will be moved to a repository/service layer later


async def store_process_data(pid: int, name: str, ram_mb: float, cpu_percent: float) -> None:
    """Almacena datos de proceso en la base de datos si está disponible."""
    from .database import AsyncSessionLocal, log_event, ProcessHistory # Import here to avoid circular dependency

    if AsyncSessionLocal is None:
        log_event(
            f"DB no disponible - Proceso: {name} (PID: {pid}) - "
            f"RAM: {ram_mb:.2f}MB - CPU: {cpu_percent:.2f}%"
        )
        return

    try:
        async with AsyncSessionLocal() as session:
            new_entry = ProcessHistory(
                timestamp=time.time(),
                pid=pid,
                name=name,
                ram_mb=ram_mb,
                cpu_percent=cpu_percent,
            )
            session.add(new_entry)
            await session.commit()
    except Exception as e:
        log_event(f"Error almacenando datos de proceso: {e}")


async def store_optimization_event(freed_ram_mb: float) -> None:
    """Almacena evento de optimización en la base de datos si está disponible."""
    from .database import AsyncSessionLocal, log_event, OptimizationEvent # Import here to avoid circular dependency

    if AsyncSessionLocal is None:
        log_event(f"DB no disponible - Optimización: {freed_ram_mb:.2f}MB liberados")
        return

    try:
        async with AsyncSessionLocal() as session:
            new_entry = OptimizationEvent(
                timestamp=time.time(), freed_ram_mb=freed_ram_mb
            )
            session.add(new_entry)
            await session.commit()
    except Exception as e:
        log_event(f"Error almacenando evento de optimización: {e}")


async def store_watchdog_decision(
    program_name: str, action: str, cpu_usage: float | None = None, ram_usage: float | None = None
) -> None:
    """Almacena decisión del watchdog en la base de datos."""
    from .database import AsyncSessionLocal, log_event, WatchdogDecision # Import here to avoid circular dependency

    if AsyncSessionLocal is None:
        log_event(f"DB no disponible - Decisión watchdog: {program_name} - {action}")
        return

    try:
        async with AsyncSessionLocal() as session:
            new_entry = WatchdogDecision(
                timestamp=time.time(),
                program_name=program_name,
                action=action,
                cpu_usage=cpu_usage,
                ram_usage=ram_usage,
            )
            session.add(new_entry)
            await session.commit()
    except Exception as e:
        log_event(f"Error almacenando decisión del watchdog: {e}", level="error")
