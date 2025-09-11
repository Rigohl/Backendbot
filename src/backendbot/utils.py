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


# Función de notificación multiplataforma
def notify(title: str, message: str, duration: int = 5):
    """
    Muestra una notificación al usuario.
    Compatible con Windows, Linux y macOS.
    """
    try:
        if os.name == 'nt':  # Windows
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=duration)
        elif os.name == 'posix':  # Linux/macOS
            # Usar notify-send en Linux
            subprocess.run(['notify-send', title, message], check=False)
        else:
            # Fallback: imprimir en consola
            print(f"NOTIFICATION: {title} - {message}")
    except ImportError:
        # Fallback si no hay librerías disponibles
        print(f"NOTIFICATION: {title} - {message}")
    except Exception as e:
        print(f"Error mostrando notificación: {e}")
        print(f"NOTIFICATION: {title} - {message}")


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
    """Almacena datos de proceso en la base de datos si está disponible."""
    if AsyncSessionLocal is None:
        log_event(f"DB no disponible - Proceso: {name} (PID: {pid}) - RAM: {ram_mb:.2f}MB - CPU: {cpu_percent:.2f}%")
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


async def store_optimization_event(freed_ram_mb: float):
    """Almacena evento de optimización en la base de datos si está disponible."""
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
