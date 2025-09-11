import json
import os
import subprocess
import time
from typing import AsyncGenerator, Optional

import psutil
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from .config import settings

# --- DB setup ---
# Adjust DATABASE_URL for aiosqlite if it's a sqlite path
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("sqlite:///"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

# Crear engine solo si hay una URL de base de datos válida
async_engine = None
AsyncSessionLocal = None

if DATABASE_URL and DATABASE_URL != "sqlite:///":
    try:
        async_engine = create_async_engine(DATABASE_URL, echo=True)
        AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)
    except Exception as e:
        print(f"Error configurando base de datos: {e}")
        async_engine = None

Base = declarative_base()

# Add a to_dict method to the Base class for easy serialization
def to_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

Base.to_dict = to_dict

class ProcessHistory(Base):
    __tablename__ = "process_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[float]
    pid: Mapped[int]
    name: Mapped[str]
    ram_mb: Mapped[float]
    cpu_percent: Mapped[float]

class OptimizationEvent(Base):
    __tablename__ = "optimization_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[float]
    freed_ram_mb: Mapped[float]

class WatchdogDecision(Base):
    __tablename__ = "watchdog_decisions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[float]
    program_name: Mapped[str]
    action: Mapped[str]
    cpu_usage: Mapped[float | None]
    ram_usage: Mapped[float | None]

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def notify(msg, subtle=True):
    try:
        toaster.show_toast(
            "BackendBot", msg, duration=4 if subtle else 8, threaded=True
        )
    except Exception as e:
        log_event(f"Error en notificación: {e}")


def log_event(msg, notify_user=False):
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    with open(settings.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    if notify_user:
        notify(msg)


def load_memory():
    if os.path.exists(settings.MEMORY_FILE):
        try:
            with open(settings.MEMORY_FILE, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            log_event(
                f"Error: El archivo de memoria '{settings.MEMORY_FILE}' está corrupto o vacío. Se creará uno nuevo."
            )
            return {}
        except OSError as e:
            log_event(f"Error de E/S al cargar la memoria: {e}")
            return {}
    return {}


def save_memory(memory):
    with open(settings.MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


# --- Funciones para almacenar datos históricos ---


async def store_process_data(pid: int, name: str, ram_mb: float, cpu_percent: float):
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


async def store_optimization_event(freed_ram_mb: float):
    async with AsyncSessionLocal() as session:
        new_entry = OptimizationEvent(
            timestamp=time.time(), freed_ram_mb=freed_ram_mb
        )
        session.add(new_entry)
        await session.commit()


async def store_watchdog_decision(
    program_name: str, action: str, cpu_usage: float = None, ram_usage: float = None
):
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


def restore_closed_processes(modo):
    # Aquí puedes definir cómo restaurar procesos cerrados, por ejemplo, abrir apps importantes si no están corriendo
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


def _get_process_info(p):
    """Helper to get process info and handle common errors."""
    try:
        pid, name = p.info["pid"], p.info["name"]
        ram_mb = round(p.info["memory_info"].rss / 1024 / 1024, 2)
        cpu_percent = p.info["cpu_percent"](interval=0.1)
        store_process_data(pid, name, ram_mb, cpu_percent)
        return {"pid": pid, "name": name, "ram_mb": ram_mb, "cpu_percent": cpu_percent}
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        log_event(f"Error al procesar PID {p.info.get('pid', 'N/A')}: {e}")
        return None
    except Exception as e:
        log_event(f"Error inesperado al obtener info de proceso: {e}")
        return None


def _optimize_processes():
    """Helper to suspend hibernatable processes."""
    freed = 0
    for p in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            if p.info["name"] in settings.HIBERNABLES:
                psutil.Process(p.info["pid"]).suspend()
                freed += p.info["memory_info"].rss
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            log_event(
                f"Error al suspender proceso {p.info.get('name', 'N/A')} (PID {p.info.get('pid', 'N/A')}): {e}"
            )
        except Exception as e:
            log_event(f"Error inesperado al optimizar proceso: {e}")
    return freed
