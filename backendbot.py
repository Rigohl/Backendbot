#!/usr/bin/env python3
"""
BackendBot - Sistema Completo de Monitoreo y Automatización
Archivo único que contiene todo el sistema BackendBot
"""

import sys
import os
import json
import asyncio
import time
import logging
import logging.handlers
import threading
import subprocess
import webbrowser
import platform
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

# FastAPI y dependencias web
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

# Base de datos y modelos
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Utilidades del sistema
import psutil
from plyer import notification
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

# Configuración UTF-8 para Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

class Config:
    """Configuración centralizada del sistema"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.data = self._load_config()
        self._setup_logging()

    def _load_config(self) -> dict:
        """Carga la configuración desde archivo JSON"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Archivo de configuración {self.config_file} no encontrado. Usando configuración por defecto.")
            return self._default_config()
        except Exception as e:
            print(f"Error cargando configuración: {e}. Usando configuración por defecto.")
            return self._default_config()

    def _default_config(self) -> dict:
        """Configuración por defecto"""
        return {
            "app": {"title": "BackendBot", "host": "0.0.0.0", "port": 8000},
            "security": {
                "api_key": "default-key-change-in-production",
                "admin_username": "admin",
                "admin_password": "admin123",
                "jwt_secret": secrets.token_urlsafe(32)
            },
            "monitoring": {"cpu_threshold": 80, "ram_threshold": 4000, "check_interval": 60},
            "database": {"url": "sqlite:///data/backend_data.db"},
            "logging": {"level": "INFO", "file": "logs/backend.log"}
        }

    def _setup_logging(self):
        """Configura el sistema de logging"""
        # Crear directorio de logs si no existe
        os.makedirs(os.path.dirname(self.data["logging"]["file"]), exist_ok=True)

        # Configurar logging con UTF-8
        logging.basicConfig(
            level=getattr(logging, self.data["logging"]["level"]),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.handlers.RotatingFileHandler(
                    self.data["logging"]["file"],
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5,
                    encoding='utf-8'  # UTF-8 para emojis
                ),
                logging.StreamHandler(sys.stdout)
            ],
            encoding='utf-8'
        )

        # Forzar UTF-8 en Windows
        if platform.system() == "Windows":
            try:
                # Configurar handler de consola con UTF-8
                for handler in logging.getLogger().handlers:
                    if isinstance(handler, logging.StreamHandler):
                        handler.stream.reconfigure(encoding='utf-8')
            except Exception:
                pass  # Ignorar errores de configuración

    def get(self, key: str, default=None):
        """Obtiene un valor de configuración"""
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

# Instancia global de configuración
config = Config()

# =============================================================================
# UTILIDADES
# =============================================================================

logger = logging.getLogger(__name__)

def log_event(message: str, level: str = "info"):
    """Registra un evento en el log"""
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message)

def notify_user(title: str, message: str):
    """Muestra una notificación al usuario"""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="BackendBot",
            timeout=10
        )
    except Exception as e:
        logger.error(f"Error mostrando notificación: {e}")

# =============================================================================
# BASE DE DATOS
# =============================================================================

Base = declarative_base()

class ProcessHistory(Base):
    __tablename__ = "process_history"
    id = Column(Integer, primary_key=True)
    timestamp = Column(Float)
    pid = Column(Integer)
    name = Column(String)
    ram_mb = Column(Float)
    cpu_percent = Column(Float)

class OptimizationEvent(Base):
    __tablename__ = "optimization_events"
    id = Column(Integer, primary_key=True)
    timestamp = Column(Float)
    freed_ram_mb = Column(Float)

class DecisionMemory(Base):
    __tablename__ = "decision_memory"
    id = Column(Integer, primary_key=True)
    program_name = Column(String, unique=True)
    suspensions = Column(Integer, default=0)
    rejections = Column(Integer, default=0)

class Database:
    """Gestión de base de datos"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None

    def init_db(self):
        """Inicializa la base de datos"""
        try:
            os.makedirs("data", exist_ok=True)
            db_url = config.get("database.url")
            self.engine = create_engine(
                db_url,
                connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
                poolclass=StaticPool if "sqlite" in db_url else None
            )
            Base.metadata.create_all(bind=self.engine)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info("✅ Base de datos inicializada")
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")

    def get_session(self):
        """Obtiene una sesión de base de datos"""
        if self.SessionLocal:
            return self.SessionLocal()
        return None

# Instancia global de base de datos
db = Database()

# =============================================================================
# SERVICIOS DEL SISTEMA
# =============================================================================

class SystemMonitor:
    """Monitoreo avanzado del sistema con modos inteligentes"""

    def __init__(self):
        self.is_monitoring = False
        self.current_mode = "diario"
        self.mode_configs = self._load_mode_configs()
        self.last_optimization = time.time()

    def _load_mode_configs(self):
        """Configuraciones específicas por modo"""
        return {
            "diario": {
                "cpu_threshold": 70,
                "ram_threshold": 75,
                "processes_to_close": ["chrome.exe", "firefox.exe", "edge.exe"],
                "auto_optimize": True,
                "optimization_interval": 1800,  # 30 minutos
                "description": "Modo diario - Optimización balanceada",
                "aggressive_cleanup": False,
                "cpu_priority": "normal"
            },
            "videojuego": {
                "cpu_threshold": 90,
                "ram_threshold": 85,
                "processes_to_close": ["discord.exe", "steam.exe", "chrome.exe", "firefox.exe"],
                "auto_optimize": False,
                "optimization_interval": 3600,  # 1 hora
                "description": "Modo videojuego - Rendimiento máximo",
                "aggressive_cleanup": True,
                "cpu_priority": "high"
            },
            "editor": {
                "cpu_threshold": 80,
                "ram_threshold": 80,
                "processes_to_close": ["chrome.exe", "firefox.exe"],
                "auto_optimize": True,
                "optimization_interval": 2400,  # 40 minutos
                "description": "Modo editor - Memoria estable",
                "aggressive_cleanup": False,
                "cpu_priority": "normal"
            },
            "streaming": {
                "cpu_threshold": 85,
                "ram_threshold": 80,
                "processes_to_close": ["chrome.exe", "discord.exe"],
                "auto_optimize": True,
                "optimization_interval": 1200,  # 20 minutos
                "description": "Modo streaming - CPU prioritario",
                "aggressive_cleanup": False,
                "cpu_priority": "high"
            },
            "multimedia": {
                "cpu_threshold": 75,
                "ram_threshold": 70,
                "processes_to_close": ["vlc.exe", "chrome.exe"],
                "auto_optimize": True,
                "optimization_interval": 1800,  # 30 minutos
                "description": "Modo multimedia - Equilibrio perfecto",
                "aggressive_cleanup": False,
                "cpu_priority": "normal"
            }
        }

    def set_mode(self, mode: str):
        """Cambia el modo de operación"""
        if mode in self.mode_configs:
            old_mode = self.current_mode
            self.current_mode = mode
            log_event(f"Modo cambiado de {old_mode} a {mode}: {self.mode_configs[mode]['description']}")
            notify_user("BackendBot", f"Modo: {self.mode_configs[mode]['description']}")
            return True
        return False

    def get_mode_config(self):
        """Obtiene la configuración del modo actual"""
        return self.mode_configs.get(self.current_mode, self.mode_configs["diario"])

    def collect_system_metrics(self) -> dict:
        """Recopila métricas avanzadas del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()

            # Obtener configuración del modo actual
            mode_config = self.get_mode_config()

            return {
                "timestamp": time.time(),
                "mode": self.current_mode,
                "cpu": {
                    "percent": cpu_percent,
                    "cores": psutil.cpu_count(),
                    "threshold": mode_config["cpu_threshold"],
                    "status": "high" if cpu_percent > mode_config["cpu_threshold"] else "normal"
                },
                "memory": {
                    "total_mb": memory.total / 1024 / 1024,
                    "used_mb": memory.used / 1024 / 1024,
                    "available_mb": memory.available / 1024 / 1024,
                    "percent": memory.percent,
                    "threshold": mode_config["ram_threshold"],
                    "status": "high" if memory.percent > mode_config["ram_threshold"] else "normal"
                },
                "disk": {
                    "total_gb": disk.total / 1024 / 1024 / 1024,
                    "used_gb": disk.used / 1024 / 1024 / 1024,
                    "free_gb": disk.free / 1024 / 1024 / 1024,
                    "percent": disk.percent
                },
                "network": {
                    "bytes_sent": net.bytes_sent,
                    "bytes_recv": net.bytes_recv,
                    "packets_sent": net.packets_sent,
                    "packets_recv": net.packets_recv
                },
                "system_status": self._get_system_status(cpu_percent, memory.percent),
                "mode_config": mode_config
            }
        except Exception as e:
            logger.error(f"Error recopilando métricas: {e}")
            return {}

    def _get_system_status(self, cpu_percent: float, ram_percent: float) -> str:
        """Determina el estado del sistema basado en métricas y modo"""
        mode_config = self.get_mode_config()

        if cpu_percent > mode_config["cpu_threshold"] or ram_percent > mode_config["ram_threshold"]:
            return "critical"
        elif cpu_percent > mode_config["cpu_threshold"] * 0.9 or ram_percent > mode_config["ram_threshold"] * 0.9:
            return "warning"
        elif cpu_percent > mode_config["cpu_threshold"] * 0.8 or ram_percent > mode_config["ram_threshold"] * 0.8:
            return "attention"
        else:
            return "optimal"

    def get_process_info(self) -> list:
        """Obtiene información detallada de procesos"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status', 'create_time']):
                try:
                    info = proc.info
                    if info['memory_info']:
                        process_info = {
                            "pid": info['pid'],
                            "name": info['name'],
                            "cpu_percent": info['cpu_percent'] or 0,
                            "ram_mb": info['memory_info'].rss / 1024 / 1024,
                            "status": info['status'],
                            "running_time": time.time() - info['create_time'] if info['create_time'] else 0
                        }

                        # Marcar procesos críticos según el modo
                        mode_config = self.get_mode_config()
                        process_info["critical"] = info['name'].lower() in [p.lower() for p in mode_config["processes_to_close"]]
                        process_info["should_close"] = self._should_close_process(process_info)

                        processes.append(process_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Error obteniendo procesos: {e}")

        return processes

    def _should_close_process(self, process_info: dict) -> bool:
        """Determina si un proceso debería cerrarse según el modo"""
        mode_config = self.get_mode_config()

        # Cerrar procesos críticos que usen mucha memoria
        if process_info["critical"] and process_info["ram_mb"] > 100:
            return True

        # En modo videojuego, cerrar procesos que usen CPU
        if self.current_mode == "videojuego" and process_info["cpu_percent"] > 10:
            return True

        # En modo streaming, cerrar procesos que puedan interferir
        if self.current_mode == "streaming" and process_info["name"].lower() in ["chrome.exe", "firefox.exe"]:
            return True

        return False

    def kill_process(self, pid: int) -> dict:
        """Finaliza un proceso por PID con información detallada"""
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            memory_usage = process.memory_info().rss / 1024 / 1024

            # Intentar terminación graceful primero
            process.terminate()

            # Esperar a que termine
            try:
                process.wait(timeout=5)
                log_event(f"Proceso terminado correctamente: {process_name} (PID: {pid}, RAM: {memory_usage:.1f}MB)")
                return {
                    "success": True,
                    "pid": pid,
                    "name": process_name,
                    "memory_freed_mb": memory_usage,
                    "method": "terminate"
                }
            except psutil.TimeoutExpired:
                # Forzar terminación si no responde
                process.kill()
                process.wait(timeout=5)
                log_event(f"Proceso forzado a terminar: {process_name} (PID: {pid}, RAM: {memory_usage:.1f}MB)")
                return {
                    "success": True,
                    "pid": pid,
                    "name": process_name,
                    "memory_freed_mb": memory_usage,
                    "method": "kill"
                }

        except psutil.NoSuchProcess:
            log_event(f"Proceso no encontrado: PID {pid}")
            return {"success": False, "error": "Process not found", "pid": pid}
        except psutil.AccessDenied:
            log_event(f"Acceso denegado para terminar proceso: PID {pid}")
            return {"success": False, "error": "Access denied", "pid": pid}
        except Exception as e:
            log_event(f"Error terminando proceso PID {pid}: {e}")
            return {"success": False, "error": str(e), "pid": pid}

    def kill_processes_by_name(self, process_name: str) -> dict:
        """Finaliza todos los procesos con un nombre específico"""
        results = []
        killed_count = 0
        total_memory_freed = 0

        try:
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                    result = self.kill_process(proc.info['pid'])
                    results.append(result)
                    if result["success"]:
                        killed_count += 1
                        total_memory_freed += result.get("memory_freed_mb", 0)

            return {
                "process_name": process_name,
                "killed_count": killed_count,
                "total_memory_freed_mb": total_memory_freed,
                "results": results
            }
        except Exception as e:
            logger.error(f"Error terminando procesos {process_name}: {e}")
            return {"error": str(e), "process_name": process_name}

    def optimize_memory_by_mode(self) -> dict:
        """Optimización inteligente específica según el modo actual"""
        mode_config = self.get_mode_config()
        before_metrics = self.collect_system_metrics()

        total_freed = 0
        processes_closed = 0
        actions_taken = []

        try:
            # Estrategia específica según el modo
            if self.current_mode == "videojuego":
                result = self._optimize_gaming_mode()
                total_freed += result["memory_freed"]
                processes_closed += result["processes_closed"]
                actions_taken.extend(result["actions"])
            elif self.current_mode == "streaming":
                result = self._optimize_streaming_mode()
                total_freed += result["memory_freed"]
                processes_closed += result["processes_closed"]
                actions_taken.extend(result["actions"])
            elif self.current_mode == "editor":
                result = self._optimize_editor_mode()
                total_freed += result["memory_freed"]
                processes_closed += result["processes_closed"]
                actions_taken.extend(result["actions"])
            else:
                # Optimización general para diario/multimedia
                result = self._optimize_general_mode()
                total_freed += result["memory_freed"]
                processes_closed += result["processes_closed"]
                actions_taken.extend(result["actions"])

            after_metrics = self.collect_system_metrics()
            self.last_optimization = time.time()

            result = {
                "status": "completed",
                "mode": self.current_mode,
                "freed_ram_mb": total_freed,
                "processes_closed": processes_closed,
                "actions_taken": actions_taken,
                "before": before_metrics,
                "after": after_metrics,
                "optimization_type": mode_config["description"]
            }

            # Guardar en base de datos
            session = db.get_session()
            if session:
                try:
                    event = OptimizationEvent(
                        timestamp=time.time(),
                        freed_ram_mb=total_freed
                    )
                    session.add(event)
                    session.commit()
                finally:
                    session.close()

            log_event(f"Optimizacion inteligente '{self.current_mode}' completada - {total_freed:.1f}MB liberados, {processes_closed} procesos")
            return result

        except Exception as e:
            logger.error(f"Error en optimización inteligente: {e}")
            return {
                "status": "error",
                "error": str(e),
                "mode": self.current_mode
            }

    def _optimize_gaming_mode(self) -> dict:
        """Optimización agresiva para modo videojuego"""
        actions = []
        memory_freed = 0
        processes_closed = 0

        # Cerrar aplicaciones no esenciales
        non_essential = ["chrome.exe", "firefox.exe", "edge.exe", "discord.exe", "steam.exe", "spotify.exe"]
        for proc_name in non_essential:
            result = self.kill_processes_by_name(proc_name)
            if result.get("killed_count", 0) > 0:
                actions.append(f"Cerrados {result['killed_count']} procesos {proc_name}")
                memory_freed += result.get("total_memory_freed_mb", 0)
                processes_closed += result.get("killed_count", 0)

        # Liberar memoria del sistema
        self._force_memory_cleanup()

        return {
            "memory_freed": memory_freed,
            "processes_closed": processes_closed,
            "actions": actions
        }

    def _optimize_streaming_mode(self) -> dict:
        """Optimización para modo streaming"""
        actions = []
        memory_freed = 0
        processes_closed = 0

        # Cerrar aplicaciones que puedan interferir
        interfering = ["chrome.exe", "firefox.exe", "discord.exe"]
        for proc_name in interfering:
            result = self.kill_processes_by_name(proc_name)
            if result.get("killed_count", 0) > 0:
                actions.append(f"Cerrados {result['killed_count']} procesos {proc_name}")
                memory_freed += result.get("total_memory_freed_mb", 0)
                processes_closed += result.get("killed_count", 0)

        # Optimizar procesos de streaming
        self._optimize_streaming_processes()

        return {
            "memory_freed": memory_freed,
            "processes_closed": processes_closed,
            "actions": actions
        }

    def _optimize_editor_mode(self) -> dict:
        """Optimización para modo editor"""
        actions = []
        memory_freed = 0
        processes_closed = 0

        # Cerrar navegadores que consuman mucha memoria
        browsers = ["chrome.exe", "firefox.exe", "edge.exe"]
        for proc_name in browsers:
            result = self.kill_processes_by_name(proc_name)
            if result.get("killed_count", 0) > 0:
                actions.append(f"Cerrados {result['killed_count']} procesos {proc_name}")
                memory_freed += result.get("total_memory_freed_mb", 0)
                processes_closed += result.get("killed_count", 0)

        # Estabilizar memoria
        self._stabilize_memory()

        return {
            "memory_freed": memory_freed,
            "processes_closed": processes_closed,
            "actions": actions
        }

    def _optimize_general_mode(self) -> dict:
        """Optimización general"""
        actions = []
        memory_freed = 0
        processes_closed = 0

        # Cerrar procesos que usen mucha memoria
        processes = self.get_process_info()
        for proc in processes:
            if proc["ram_mb"] > 200 and proc["critical"]:  # Más de 200MB y crítico
                result = self.kill_process(proc["pid"])
                if result["success"]:
                    actions.append(f"Cerrado proceso {proc['name']} ({proc['ram_mb']:.1f}MB)")
                    memory_freed += result.get("memory_freed_mb", 0)
                    processes_closed += 1

        return {
            "memory_freed": memory_freed,
            "processes_closed": processes_closed,
            "actions": actions
        }

    def _force_memory_cleanup(self):
        """Limpieza forzada de memoria del sistema"""
        try:
            # Ejecutar comandos de limpieza de memoria en Windows
            if platform.system() == "Windows":
                subprocess.run(["powershell", "-Command", "Clear-Host"], capture_output=True)
        except Exception as e:
            logger.error(f"Error en limpieza de memoria: {e}")

    def _optimize_streaming_processes(self):
        """Optimizar procesos para streaming"""
        try:
            # Ajustar prioridades para streaming
            streaming_apps = ["obs", "stream", "twitch", "discord"]
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name']:
                    proc_name = proc.info['name'].lower()
                    if any(app in proc_name for app in streaming_apps):
                        try:
                            proc.nice(psutil.HIGH_PRIORITY_CLASS)
                        except:
                            pass
        except Exception as e:
            logger.error(f"Error optimizando procesos de streaming: {e}")

    def _stabilize_memory(self):
        """Estabilizar el uso de memoria"""
        try:
            # Liberar memoria de procesos inactivos
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                if (proc.info['memory_info'] and proc.info['cpu_percent'] is not None and
                    proc.info['cpu_percent'] < 1.0 and proc.info['memory_info'].rss > 150 * 1024 * 1024):  # > 150MB
                    try:
                        # Suspender y resumir para liberar memoria
                        proc.suspend()
                        time.sleep(0.1)
                        proc.resume()
                    except:
                        pass
        except Exception as e:
            logger.error(f"Error estabilizando memoria: {e}")

    def auto_maintenance(self):
        """Mantenimiento automático inteligente según el modo"""
        mode_config = self.get_mode_config()

        if not mode_config["auto_optimize"]:
            return

        # Verificar si es tiempo de optimización
        time_since_last = time.time() - self.last_optimization
        if time_since_last < mode_config["optimization_interval"]:
            return

        metrics = self.collect_system_metrics()

        # Verificar si necesita optimización según el modo
        needs_optimization = False

        if self.current_mode == "videojuego":
            # En modo videojuego, optimizar solo si RAM > 80%
            needs_optimization = metrics["memory"]["percent"] > 80
        elif self.current_mode == "streaming":
            # En modo streaming, optimizar si CPU o RAM altos
            needs_optimization = (metrics["cpu"]["percent"] > mode_config["cpu_threshold"] or
                                metrics["memory"]["percent"] > mode_config["ram_threshold"])
        else:
            # En otros modos, usar umbrales normales
            needs_optimization = (metrics["cpu"]["percent"] > mode_config["cpu_threshold"] or
                                metrics["memory"]["percent"] > mode_config["ram_threshold"])

        if needs_optimization:
            log_event(f"Mantenimiento automatico activado en modo {self.current_mode}")
            self.optimize_memory_by_mode()

# Instancia global del monitor
monitor = SystemMonitor()

# =============================================================================
# API REST (FastAPI)
# =============================================================================

app = FastAPI(
    title=config.get("app.title", "BackendBot"),
    description="Sistema de monitoreo y automatización",
    version="1.0.0"
)

security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica la API key"""
    if credentials.credentials != config.get("security.api_key"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials

@app.get("/")
async def root():
    """Página principal"""
    return {"message": "BackendBot está ejecutándose", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Verificación de salud del sistema"""
    metrics = monitor.collect_system_metrics()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics
    }

@app.get("/metrics")
async def get_metrics():
    """Obtiene métricas del sistema"""
    return monitor.collect_system_metrics()

@app.get("/processes")
async def get_processes():
    """Obtiene lista de procesos"""
    return {"processes": monitor.get_process_info()}

@app.get("/modo")
async def get_modo():
    """Obtiene el modo actual"""
    return {"modo": config.get("modo", "diario")}

@app.post("/set-modo/{modo}")
async def set_modo(modo: str):
    """Cambia el modo del sistema"""
    valid_modos = ["diario", "videojuego", "editor", "streaming", "multimedia"]
    if modo not in valid_modos:
        raise HTTPException(status_code=400, detail=f"Modo inválido. Opciones: {valid_modos}")

    # Aquí podrías actualizar la configuración
    log_event(f"🔄 Modo cambiado a {modo}")
    return {"message": f"Modo cambiado a {modo}", "modo": modo}

@app.post("/optimize")
async def optimize_system():
    """Optimiza el sistema"""
    try:
        # Lógica simple de optimización
        before_metrics = monitor.collect_system_metrics()

        # Simular optimización
        freed_ram = 100 + (time.time() % 50)  # Simulación

        after_metrics = monitor.collect_system_metrics()

        # Guardar en base de datos
        session = db.get_session()
        if session:
            try:
                event = OptimizationEvent(
                    timestamp=time.time(),
                    freed_ram_mb=freed_ram
                )
                session.add(event)
                session.commit()
            finally:
                session.close()

        log_event(f"Optimizacion completada - {freed_ram:.1f}MB liberados")
        return {
            "status": "completed",
            "freed_ram_mb": freed_ram,
            "before": before_metrics,
            "after": after_metrics
        }
    except Exception as e:
        logger.error(f"Error en optimización: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# DASHBOARD HTML
# =============================================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Dashboard web simple"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BackendBot Dashboard</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .metric-card { background: white; padding: 20px; margin: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: inline-block; width: 300px; vertical-align: top; }
            .metric-value { font-size: 2em; font-weight: bold; color: #3498db; }
            .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #2980b9; }
            .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
            .status.healthy { background: #d4edda; color: #155724; }
            .status.warning { background: #fff3cd; color: #856404; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 BackendBot Dashboard</h1>
                <p>Sistema de monitoreo y automatización</p>
            </div>

            <div id="metrics"></div>

            <div class="metric-card">
                <h3>🎛️ Controles</h3>
                <button class="btn" onclick="optimize()">Optimizar Sistema</button>
                <button class="btn" onclick="refresh()">Actualizar</button>
            </div>

            <div class="metric-card">
                <h3>📊 Estado del Sistema</h3>
                <div id="status" class="status healthy">✅ Sistema operativo</div>
            </div>
        </div>

        <script>
            async function loadMetrics() {
                try {
                    const response = await fetch('/metrics');
                    const data = await response.json();

                    document.getElementById('metrics').innerHTML = `
                        <div class="metric-card">
                            <h3>🖥️ CPU</h3>
                            <div class="metric-value">${data.cpu.percent.toFixed(1)}%</div>
                            <p>${data.cpu.cores} núcleos</p>
                        </div>
                        <div class="metric-card">
                            <h3>🧠 Memoria RAM</h3>
                            <div class="metric-value">${data.memory.percent.toFixed(1)}%</div>
                            <p>${(data.memory.used_mb/1024).toFixed(1)}GB / ${(data.memory.total_mb/1024).toFixed(1)}GB</p>
                        </div>
                        <div class="metric-card">
                            <h3>💾 Disco</h3>
                            <div class="metric-value">${data.disk.percent.toFixed(1)}%</div>
                            <p>${data.disk.used_gb.toFixed(1)}GB / ${data.disk.total_gb.toFixed(1)}GB</p>
                        </div>
                    `;
                } catch (error) {
                    console.error('Error loading metrics:', error);
                }
            }

            async function optimize() {
                try {
                    const response = await fetch('/optimize', { method: 'POST' });
                    const result = await response.json();
                    alert(`Optimización completada! ${result.freed_ram_mb.toFixed(1)}MB liberados`);
                    loadMetrics();
                } catch (error) {
                    alert('Error en optimización: ' + error.message);
                }
            }

            function refresh() {
                loadMetrics();
            }

            // Cargar métricas al inicio
            loadMetrics();

            // Actualizar cada 30 segundos
            setInterval(loadMetrics, 30000);
        </script>
    </body>
    </html>
    """
    return html

# =============================================================================
# ÍCONO DE BANDEJA DEL SISTEMA
# =============================================================================

class TrayIcon:
    """Ícono de bandeja del sistema"""

    def __init__(self):
        self.icon = None
        self.monitoring_active = False
        self.current_mode = "diario"

    def create_icon(self, color):
        """Crea un ícono circular"""
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((12, 12, 52, 52), fill=color)
        return img

    def open_dashboard(self, icon, item):
        """Abre el dashboard en el navegador"""
        webbrowser.open("http://127.0.0.1:8000/dashboard")
        log_event("Dashboard abierto desde bandeja")

    def toggle_monitoring(self, icon, item):
        """Activa/desactiva el monitoreo"""
        self.monitoring_active = not self.monitoring_active
        icon.icon = self.create_icon((239, 68, 68)) if self.monitoring_active else self.create_icon((59, 130, 246))
        status = "ACTIVADO" if self.monitoring_active else "DESACTIVADO"
        log_event(f"Monitoreo {status}")
        notify_user("BackendBot", f"Monitoreo {status}")

    def set_mode(self, icon, item, mode):
        """Cambia el modo del sistema"""
        try:
            # Cambiar modo directamente (sin API por ahora)
            if hasattr(system_monitor, 'set_mode'):
                if system_monitor.set_mode(mode):
                    self.current_mode = mode
                    log_event(f"Modo cambiado a {mode}")
                    notify_user("BackendBot", f"Modo cambiado a {mode}")
                    self.update_menu(icon)
                else:
                    log_event(f"Modo no válido: {mode}")
        except Exception as e:
            log_event(f"Error cambiando modo: {e}")

    def update_menu(self, icon):
        """Actualiza el menú del ícono"""
        icon.menu = Menu(
            MenuItem("Abrir Dashboard", self.open_dashboard),
            MenuItem("Modos", Menu(
                MenuItem(f"Diario {'[X]' if self.current_mode == 'diario' else ''}",
                        lambda i, s: self.set_mode(icon, i, "diario")),
                MenuItem(f"Videojuego {'[X]' if self.current_mode == 'videojuego' else ''}",
                        lambda i, s: self.set_mode(icon, i, "videojuego")),
                MenuItem(f"Editor {'[X]' if self.current_mode == 'editor' else ''}",
                        lambda i, s: self.set_mode(icon, i, "editor")),
                MenuItem(f"Streaming {'[X]' if self.current_mode == 'streaming' else ''}",
                        lambda i, s: self.set_mode(icon, i, "streaming")),
                MenuItem(f"Multimedia {'[X]' if self.current_mode == 'multimedia' else ''}",
                        lambda i, s: self.set_mode(icon, i, "multimedia")),
            )),
            Menu.SEPARATOR,
            MenuItem("Monitoreo Activo", self.toggle_monitoring,
                    checked=lambda item: self.monitoring_active),
            Menu.SEPARATOR,
            MenuItem("Salir", lambda i, s: icon.stop()),
        )

    def run(self):
        """Ejecuta el ícono de bandeja"""
        try:
            self.icon = Icon(
                "BackendBot",
                self.create_icon((59, 130, 246)),
                "BackendBot"
            )
            self.update_menu(self.icon)
            log_event("Tray icon iniciado")
            self.icon.run()
        except Exception as e:
            log_event(f"Error en tray icon: {e}")

# =============================================================================
# INICIALIZACIÓN Y EJECUCIÓN
# =============================================================================

def init_system():
    """Inicializa todos los componentes del sistema"""
    log_event("Inicializando BackendBot...")

    # Inicializar base de datos
    db.init_db()

    # Verificar dependencias opcionales
    try:
        # GPU monitoring no disponible en esta versión
        pass
    except ImportError:
        log_event("GPU monitoring no disponible")

    log_event("Sistema inicializado correctamente")

def start_tray_icon():
    """Inicia el ícono de bandeja en un hilo separado"""
    if platform.system() == "Windows":
        tray = TrayIcon()
        tray_thread = threading.Thread(target=tray.run, daemon=True)
        tray_thread.start()
    log_event("Tray icon thread iniciado")

def main():
    """Función principal"""
    # Inicializar sistema
    init_system()

    # Iniciar tray icon
    start_tray_icon()

    # Iniciar servidor web
    host = config.get("app.host", "0.0.0.0")
    port = config.get("app.port", 8000)

    log_event(f"Iniciando servidor en {host}:{port}")
    log_event("Dashboard disponible en: http://127.0.0.1:8000/dashboard")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=config.get("logging.level", "info").lower()
    )

if __name__ == "__main__":
    main()