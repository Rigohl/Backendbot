import os
import subprocess
import time
import logging
import logging.config

import psutil
from plyer import notification
from sqlalchemy import select

try:
    from .config import settings
    from .database import AsyncSessionLocal, DecisionMemory, ProcessHistory, OptimizationEvent, WatchdogDecision
except ImportError:
    # Fallback for when running from tests
    from config import settings
    from database import AsyncSessionLocal, DecisionMemory, ProcessHistory, OptimizationEvent, WatchdogDecision


# Global logger instance
_logger_initialized = False
_logger = None

def get_logger():
    """Initializes and returns the logger instance."""
    global _logger_initialized, _logger
    if not _logger_initialized:
        try:
            # Ensure console handler uses utf-8 encoding
            if "handlers" in settings.LOGGING_CONFIG and "console" in settings.LOGGING_CONFIG["handlers"]:
                settings.LOGGING_CONFIG["handlers"]["console"]["encoding"] = "utf-8"
            
            logging.config.dictConfig(settings.LOGGING_CONFIG)
            _logger = logging.getLogger("backendbot")
            _logger_initialized = True
        except Exception as e:
            print(f"ERROR: Failed to configure logger: {e}")
            # Fallback to a basic logger if config fails
            logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            _logger = logging.getLogger("backendbot_fallback")
            _logger_initialized = True
    return _logger

def notify(title: str, message: str):
    """Shows a desktop notification using plyer."""
    logger = get_logger()
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="BackendBot",
            timeout=10  # Notification will disappear after 10 seconds
        )
        logger.info(f"NOTIFICATION SENT: {title} - {message}")
    except Exception as e:
        logger.error(f"Failed to send desktop notification: {e}")

def log_event(msg: str, notify_user: bool = False, level: str = "info") -> None:
    """Registra un evento y opcionalmente notifica al usuario."""
    logger = get_logger()
    log_map = {
        "debug": logger.debug,
        "info": logger.info,
        "warning": logger.warning,
        "error": logger.error,
        "critical": logger.critical
    }
    log_func = log_map.get(level.lower(), logger.info)
    log_func(msg)

    if notify_user:
        notify(title="BackendBot", message=msg)


async def load_memory() -> dict:
    """Carga la memoria desde la base de datos."""
    if AsyncSessionLocal is None:
        log_event("DB no disponible - No se puede cargar la memoria de decisiones.")
        return {}

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(DecisionMemory))
            decisions = result.scalars().all()
            memory = {}
            for decision in decisions:
                memory[decision.program_name] = {
                    "suspensiones": decision.suspensions,
                    "rechazos": decision.rejections,
                }
            return memory
    except Exception as e:
        log_event(f"Error al cargar la memoria de decisiones desde la DB: {e}", level="error")
        return {}


async def save_memory(memory: dict) -> None:
    """Guarda la memoria en la base de datos."""
    if AsyncSessionLocal is None:
        log_event("DB no disponible - No se puede guardar la memoria de decisiones.")
        return

    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                for program_name, data in memory.items():
                    stmt = select(DecisionMemory).where(DecisionMemory.program_name == program_name)
                    result = await session.execute(stmt)
                    decision = result.scalars().first()

                    if decision:
                        decision.suspensions = data.get("suspensiones", 0)
                        decision.rejections = data.get("rechazos", 0)
                    else:
                        new_decision = DecisionMemory(
                            program_name=program_name,
                            suspensions=data.get("suspensiones", 0),
                            rejections=data.get("rechazos", 0),
                        )
                        session.add(new_decision)
                await session.commit()
    except Exception as e:
        log_event(f"Error al guardar la memoria de decisiones en la DB: {e}", level="error")


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


async def store_process_data(pid: int, name: str, ram_mb: float, cpu_percent: float) -> None:
    """Almacena datos de proceso en la base de datos si está disponible."""
    if AsyncSessionLocal is None:
        log_event(f"DB no disponible - Proceso: {name} (PID: {pid}) - RAM: {ram_mb:.2f}MB - CPU: {cpu_percent:.2f}%")
        return
    try:
        async with AsyncSessionLocal() as session:
            new_entry = ProcessHistory(timestamp=time.time(), pid=pid, name=name, ram_mb=ram_mb, cpu_percent=cpu_percent)
            session.add(new_entry)
            await session.commit()
    except Exception as e:
        log_event(f"Error almacenando datos de proceso: {e}")


async def store_optimization_event(freed_ram_mb: float) -> None:
    """Almacena evento de optimización en la base de datos si está disponible."""
    if AsyncSessionLocal is None:
        log_event(f"DB no disponible - Optimización: {freed_ram_mb:.2f}MB liberados")
        return
    try:
        async with AsyncSessionLocal() as session:
            new_entry = OptimizationEvent(timestamp=time.time(), freed_ram_mb=freed_ram_mb)
            session.add(new_entry)
            await session.commit()
    except Exception as e:
        log_event(f"Error almacenando evento de optimización: {e}")


async def store_watchdog_decision(program_name: str, action: str, cpu_usage: float | None = None, ram_usage: float | None = None) -> None:
    """Almacena decisión del watchdog en la base de datos."""
    if AsyncSessionLocal is None:
        log_event(f"DB no disponible - Decisión watchdog: {program_name} - {action}")
        return
    try:
        async with AsyncSessionLocal() as session:
            new_entry = WatchdogDecision(timestamp=time.time(), program_name=program_name, action=action, cpu_usage=cpu_usage, ram_usage=ram_usage)
            session.add(new_entry)
            await session.commit()
    except Exception as e:
        log_event(f"Error almacenando decisión del watchdog: {e}")
