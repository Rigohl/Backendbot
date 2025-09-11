"""
Backendbot API
==============

Este backend está construido con FastAPI y sirve como núcleo para monitoreo y control de procesos.

Endpoints:
- GET / : Verifica que el backend está corriendo.
- GET /system : Obtiene información del sistema (CPU, memoria, disco).
- GET /health : Health check detallado con uptime y métricas.
- GET /logs : Obtiene logs recientes del sistema.
- GET /processes/top : Lista procesos top por CPU o memoria.
- GET /config : Obtiene configuración actual del backend.
- POST /procesos : Lista procesos activos (desde process_routes).
- POST /apagar/{pid} : Termina un proceso.
- POST /kill/{pid} : Mata un proceso.
- POST /resume/{pid} : Reanuda un proceso suspendido.
- POST /optimize : Optimiza memoria cerrando procesos no esenciales.
- POST /set-modo/{modo} : Configura modo de operación.
- POST /restore-important : Restaura procesos importantes.

Requisitos:
- Python 3.11+
- FastAPI, Uvicorn, Pillow, psutil, psycopg2-binary, pydantic-settings, ruff, black, sqlalchemy

Despliegue:
- Compatible con Railway, Render, Fly.io
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from collections import defaultdict
import json
import shutil
import secrets
import logging
import uvicorn
import subprocess

# Configurar logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.getenv('LOG_FILE', 'backend.log'))
    ]
)
logger = logging.getLogger(__name__)

# Rate limiting simple
rate_limit_store = defaultdict(list)
# Usar límite más bajo para pruebas si estamos en modo test
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 10 if 'pytest' in os.sys.argv[0] else 100))
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 60))

def check_rate_limit(client_ip: str) -> bool:
    """Verifica el rate limit para una IP."""
    now = time.time()
    # Limpiar requests antiguos
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip]
        if now - req_time < RATE_LIMIT_WINDOW
    ]

    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False

    rate_limit_store[client_ip].append(now)
    return True

async def rate_limit_middleware(request: Request, call_next):
    """Middleware para rate limiting."""
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit excedido para IP: {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"detail": "Demasiadas solicitudes"}
        )
    response = await call_next(request)
    return response

# Modelos Pydantic
class SystemInfo(BaseModel):
    """Modelo para información del sistema."""
    cpu_percent: float
    memory_total: int
    memory_available: int
    memory_percent: float
    disk_total: int
    disk_free: int
    disk_percent: float
    user: str
    timestamp: str

class StatusResponse(BaseModel):
    """Modelo para respuesta de estado."""
    message: str
    user: str
    timestamp: str
    version: Optional[str] = "1.0.0"

class HealthResponse(BaseModel):
    """Modelo para respuesta de health check."""
    status: str
    uptime_seconds: float
    active_processes: int
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    timestamp: str

class LogEntry(BaseModel):
    """Modelo para entrada de log."""
    timestamp: str
    level: str
    message: str

class AlertConfig(BaseModel):
    """Modelo para configuración de alertas."""
    cpu_threshold: float = 80.0
    memory_threshold: float = 80.0
    disk_threshold: float = 90.0
    enabled: bool = True

class Alert(BaseModel):
    """Modelo para alerta."""
    type: str
    message: str
    value: float
    threshold: float
    timestamp: str

class MetricHistory(BaseModel):
    """Modelo para historial de métricas."""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_processes: int

class ConfigResponse(BaseModel):
    """Modelo para respuesta de configuración."""
    username: str
    rate_limit_requests: int
    rate_limit_window: int
    cors_origins: str
    log_level: str
    log_file: str

class TopProcess(BaseModel):
    """Modelo para proceso top."""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float

class GPUInfo(BaseModel):
    """Modelo para información de GPU."""
    id: int
    name: str
    memory_total: float
    memory_used: float
    memory_free: float
    memory_util_percent: float
    gpu_util_percent: float
    temperature: Optional[float] = None

class HardwareInfo(BaseModel):
    """Modelo para información detallada de hardware."""
    cpu_name: str
    cpu_cores: int
    cpu_threads: int
    total_ram_gb: float
    motherboard: str
    os_version: str
    gpus: List[GPUInfo]

class SystemExtendedInfo(BaseModel):
    """Modelo extendido para información del sistema."""
    cpu_percent: float
    memory_total: int
    memory_available: int
    memory_percent: float
    disk_total: int
    disk_free: int
    disk_percent: float
    gpu_info: Optional[List[GPUInfo]] = None
    hardware_info: Optional[HardwareInfo] = None
    user: str
    timestamp: str

class BackupConfig(BaseModel):
    """Modelo para configuración de backup."""
    include_logs: bool = True
    include_metrics: bool = True
    include_alerts: bool = True
    max_backups: int = 10
    backup_interval_hours: int = 24

class TrendAnalysis(BaseModel):
    """Modelo para análisis de tendencias."""
    metric: str
    period_hours: int
    trend: str  # increasing, decreasing, stable
    average: float
    min_value: float
    max_value: float
    change_percent: float
    prediction: Optional[str] = None

class SafeCommand(BaseModel):
    """Modelo para comando seguro."""
    command: str
    timeout_seconds: int = 30
    allowed_commands: List[str] = ["systeminfo", "tasklist", "netstat", "ping", "tracert"]

class CommandResult(BaseModel):
    """Modelo para resultado de comando."""
    command: str
    output: str
    exit_code: int
    execution_time: float
    timestamp: str

# Variables globales para alertas y métricas
alert_config = AlertConfig()
alerts_history = []
metrics_history = []
MAX_HISTORY = 100

backup_config = BackupConfig()
last_backup = None

def check_alerts(cpu_percent: float, memory_percent: float, disk_percent: float) -> List[Alert]:
    """Verifica si se deben generar alertas basadas en umbrales."""
    alerts = []
    now = datetime.now(timezone.utc).isoformat()
    
    if alert_config.enabled:
        if cpu_percent > alert_config.cpu_threshold:
            alerts.append(Alert(
                type="cpu",
                message=f"Uso de CPU alto: {cpu_percent}%",
                value=cpu_percent,
                threshold=alert_config.cpu_threshold,
                timestamp=now
            ))
            logger.warning(f"Alerta CPU: {cpu_percent}% > {alert_config.cpu_threshold}%")
        
        if memory_percent > alert_config.memory_threshold:
            alerts.append(Alert(
                type="memory",
                message=f"Uso de memoria alto: {memory_percent}%",
                value=memory_percent,
                threshold=alert_config.memory_threshold,
                timestamp=now
            ))
            logger.warning(f"Alerta Memoria: {memory_percent}% > {alert_config.memory_threshold}%")
        
        if disk_percent > alert_config.disk_threshold:
            alerts.append(Alert(
                type="disk",
                message=f"Uso de disco alto: {disk_percent}%",
                value=disk_percent,
                threshold=alert_config.disk_threshold,
                timestamp=now
            ))
            logger.warning(f"Alerta Disco: {disk_percent}% > {alert_config.disk_threshold}%")
    
    return alerts

def store_metrics(cpu_percent: float, memory_percent: float, disk_percent: float, active_processes: int):
    """Almacena métricas en el historial."""
    if len(metrics_history) >= MAX_HISTORY:
        metrics_history.pop(0)
    
    metrics_history.append(MetricHistory(
        timestamp=datetime.now(timezone.utc).isoformat(),
        cpu_percent=cpu_percent,
        memory_percent=memory_percent,
        disk_percent=disk_percent,
        active_processes=active_processes
    ))

# Variable para uptime
start_time = time.time()

# Configurar CORS
cors_origins = os.getenv('CORS_ORIGINS', '*')
if cors_origins == '*':
    allow_origins = ["*"]
else:
    allow_origins = [origin.strip() for origin in cors_origins.split(',')]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestor de ciclo de vida de la aplicación."""
    # Startup
    logger.info("Backendbot API iniciando...")
    yield
    # Shutdown
    logger.info("Backendbot API apagándose...")

app = FastAPI(
    title="Backendbot API",
    description="API para monitoreo y control de procesos con health checks, logs y métricas avanzadas",
    version="1.0.0",
    lifespan=lifespan
)

# Agregar middleware de rate limiting
app.middleware("http")(rate_limit_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

# Credenciales desde variables de entorno
USERNAME = os.getenv('BACKENDBOT_USERNAME', 'admin')
PASSWORD = os.getenv('BACKENDBOT_PASSWORD', 'password')

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Función de autenticación básica.
    Verifica usuario y contraseña.

    Args:
        credentials: Credenciales HTTP Basic.

    Returns:
        str: Usuario autenticado.

    Raises:
        HTTPException: Si las credenciales son inválidas.
    """
    logger.info(f"Intento de autenticación para usuario: {credentials.username}")
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        logger.warning(f"Autenticación fallida para usuario: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    logger.info(f"Autenticación exitosa para usuario: {credentials.username}")
    return credentials.username

@app.get("/", summary="Estado del backend", response_description="Mensaje de estado", response_model=StatusResponse)
def read_root(user: str = Depends(authenticate)):
    """
    Endpoint raíz para verificar el estado del backend.
    Requiere autenticación básica.

    Args:
        user (str): Usuario autenticado.

    Returns:
        StatusResponse: Mensaje de estado.
    """
    logger.info(f"Acceso al endpoint raíz por usuario: {user}")
    return StatusResponse(
        message="Backendbot API is running!",
        user=user,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@app.get("/system", summary="Información del sistema", response_description="Información del sistema", response_model=SystemInfo)
def get_system_info(user: str = Depends(authenticate)):
    """
    Endpoint para obtener información del sistema.
    Requiere autenticación básica.

    Args:
        user (str): Usuario autenticado.

    Returns:
        SystemInfo: Información del sistema.
    """
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        system_info = SystemInfo(
            cpu_percent=cpu_percent,
            memory_total=memory.total,
            memory_available=memory.available,
            memory_percent=memory.percent,
            disk_total=disk.total,
            disk_free=disk.free,
            disk_percent=disk.percent,
            user=user,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

        logger.info(f"Información del sistema solicitada por usuario: {user}")
        return system_info
    except ImportError:
        logger.error("psutil no está instalado")
        raise HTTPException(status_code=500, detail="psutil no disponible")
    except Exception as e:
        logger.error(f"Error obteniendo información del sistema: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/health", summary="Health check detallado", response_description="Estado de salud del sistema", response_model=HealthResponse)
def get_health(user: str = Depends(authenticate)):
    """
    Endpoint para health check detallado.
    Requiere autenticación básica.

    Args:
        user (str): Usuario autenticado.

    Returns:
        HealthResponse: Información de salud del sistema.
    """
    try:
        import psutil
        uptime = time.time() - start_time
        active_processes = len(psutil.pids())
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Verificar alertas
        new_alerts = check_alerts(cpu_percent, memory.percent, disk.percent)
        alerts_history.extend(new_alerts)
        
        # Almacenar métricas
        store_metrics(cpu_percent, memory.percent, disk.percent, active_processes)
        
        health = HealthResponse(
            status="healthy" if not new_alerts else "warning",
            uptime_seconds=uptime,
            active_processes=active_processes,
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

        logger.info(f"Health check solicitado por usuario: {user}")
        return health
    except ImportError:
        logger.error("psutil no está instalado")
        raise HTTPException(status_code=500, detail="psutil no disponible")
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/logs", summary="Obtener logs recientes", response_description="Lista de entradas de log recientes", response_model=List[LogEntry])
def get_logs(user: str = Depends(authenticate), lines: int = 50):
    """
    Endpoint para obtener logs recientes.
    Requiere autenticación básica.

    Args:
        user (str): Usuario autenticado.
        lines (int): Número de líneas a retornar (máximo 100).

    Returns:
        List[LogEntry]: Lista de entradas de log.
    """
    try:
        log_file = os.getenv('LOG_FILE', 'backend.log')
        if not os.path.exists(log_file):
            return []

        lines = min(lines, 100)  # Máximo 100 líneas
        with open(log_file, 'r', encoding='utf-8') as f:
            log_lines = f.readlines()[-lines:]

        log_entries = []
        for line in log_lines:
            # Parsear línea de log (formato: timestamp - name - level - message)
            parts = line.strip().split(' - ', 3)
            if len(parts) >= 4:
                log_entries.append(LogEntry(
                    timestamp=parts[0],
                    level=parts[2],
                    message=parts[3]
                ))

        logger.info(f"Logs solicitados por usuario: {user}, líneas: {lines}")
        return log_entries
    except Exception as e:
        logger.error(f"Error obteniendo logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/processes/top", summary="Procesos top por uso", response_description="Lista de procesos top", response_model=List[TopProcess])
def get_top_processes(user: str = Depends(authenticate), limit: int = 10, sort_by: str = "cpu"):
    """
    Endpoint para obtener procesos top por CPU o memoria.
    Requiere autenticación básica.

    Args:
        user (str): Usuario autenticado.
        limit (int): Número de procesos a retornar.
        sort_by (str): Ordenar por 'cpu' o 'memory'.

    Returns:
        List[TopProcess]: Lista de procesos top.
    """
    try:
        import psutil
        processes = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
            try:
                info = p.info
                if info['cpu_percent'] is not None and info['memory_info'] is not None:
                    memory_mb = info['memory_info'].rss / 1024 / 1024 if info['memory_info'].rss else 0
                    processes.append(TopProcess(
                        pid=info['pid'],
                        name=info['name'] or 'Unknown',
                        cpu_percent=info['cpu_percent'],
                        memory_percent=info['memory_percent'] or 0,
                        memory_mb=memory_mb
                    ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Ordenar
        if sort_by == "memory":
            processes.sort(key=lambda x: x.memory_percent, reverse=True)
        else:
            processes.sort(key=lambda x: x.cpu_percent, reverse=True)

        logger.info(f"Procesos top solicitados por usuario: {user}, límite: {limit}, orden: {sort_by}")
        return processes[:limit]
    except ImportError:
        logger.error("psutil no está instalado")
        raise HTTPException(status_code=500, detail="psutil no disponible")
    except Exception as e:
        logger.error(f"Error obteniendo procesos top: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/config", summary="Obtener configuración actual", response_description="Configuración del backend", response_model=ConfigResponse)
def get_config(user: str = Depends(authenticate)):
    """
    Endpoint para obtener la configuración actual.
    Requiere autenticación básica.

    Args:
        user (str): Usuario autenticado.

    Returns:
        ConfigResponse: Configuración actual.
    """
    config = ConfigResponse(
        username=USERNAME,
        rate_limit_requests=RATE_LIMIT_REQUESTS,
        rate_limit_window=RATE_LIMIT_WINDOW,
        cors_origins=cors_origins,
        log_level=os.getenv('LOG_LEVEL', 'INFO'),
        log_file=os.getenv('LOG_FILE', 'backend.log')
    )

    logger.info(f"Configuración solicitada por usuario: {user}")
    return config

@app.get("/alerts", summary="Obtener alertas activas", response_description="Lista de alertas activas", response_model=List[Alert])
def get_alerts(user: str = Depends(authenticate), limit: int = 10):
    """
    Endpoint para obtener alertas activas.
    Requiere autenticación básica.

    Args:
        user (str): Usuario autenticado.
        limit (int): Número máximo de alertas a retornar.

    Returns:
        List[Alert]: Lista de alertas.
    """
    recent_alerts = alerts_history[-limit:] if alerts_history else []
    logger.info(f"Alertas solicitadas por usuario: {user}, retornando {len(recent_alerts)} alertas")
    return recent_alerts

@app.get("/alerts/config", summary="Obtener configuración de alertas", response_description="Configuración actual de alertas", response_model=AlertConfig)
def get_alert_config(user: str = Depends(authenticate)):
    """
    Endpoint para obtener configuración de alertas.
    Requiere autenticación básica.

    Args:
        user (str): Usuario autenticado.

    Returns:
        AlertConfig: Configuración de alertas.
    """
    logger.info(f"Configuración de alertas solicitada por usuario: {user}")
    return alert_config

@app.put("/alerts/config", summary="Actualizar configuración de alertas", response_description="Configuración actualizada")
def update_alert_config(config: AlertConfig, user: str = Depends(authenticate)):
    """
    Endpoint para actualizar configuración de alertas.
    Requiere autenticación básica.

    Args:
        config (AlertConfig): Nueva configuración.
        user (str): Usuario autenticado.

    Returns:
        dict: Confirmación de actualización.
    """
    global alert_config
    alert_config = config
    logger.info(f"Configuración de alertas actualizada por usuario: {user}")
    return {"message": "Configuración de alertas actualizada", "config": config}

@app.get("/metrics/history", summary="Obtener historial de métricas", response_description="Historial de métricas del sistema", response_model=List[MetricHistory])
def get_metrics_history(user: str = Depends(authenticate), limit: int = 50):
    """
    Endpoint para obtener historial de métricas.
    Requiere autenticación básica.

    Args:
        user (str): Usuario autenticado.
        limit (int): Número máximo de métricas a retornar.

    Returns:
        List[MetricHistory]: Lista de métricas históricas.
    """
    recent_metrics = metrics_history[-limit:] if metrics_history else []
    logger.info(f"Historial de métricas solicitado por usuario: {user}, retornando {len(recent_metrics)} métricas")
    return recent_metrics

@app.delete("/alerts", summary="Limpiar historial de alertas", response_description="Historial de alertas limpiado")
def clear_alerts(user: str = Depends(authenticate)):
    """
    Endpoint para limpiar historial de alertas.
    Requiere autenticación básica.

    Args:
        user (str): Usuario autenticado.

    Returns:
        dict: Confirmación de limpieza.
    """
    global alerts_history
    cleared_count = len(alerts_history)
    alerts_history.clear()
    logger.info(f"Historial de alertas limpiado por usuario: {user}, {cleared_count} alertas eliminadas")
    return {"message": f"Historial de alertas limpiado, {cleared_count} alertas eliminadas"}

def get_gpu_info() -> List[GPUInfo]:
    """Obtiene información de GPUs disponibles."""
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        gpu_list = []
        for i, gpu in enumerate(gpus):
            gpu_list.append(GPUInfo(
                id=gpu.id,
                name=gpu.name,
                memory_total=gpu.memoryTotal,
                memory_used=gpu.memoryUsed,
                memory_free=gpu.memoryFree,
                memory_util_percent=gpu.memoryUtil * 100,
                gpu_util_percent=gpu.load * 100,
                temperature=getattr(gpu, 'temperature', None)
            ))
        return gpu_list
    except ImportError:
        logger.warning("GPUtil no disponible, omitiendo información de GPU")
        return []
    except Exception as e:
        logger.error(f"Error obteniendo información de GPU: {str(e)}")
        return []

def get_hardware_info() -> HardwareInfo:
    """Obtiene información detallada del hardware."""
    try:
        import wmi
        import platform
        
        w = wmi.WMI()
        
        # CPU info
        cpu_info = w.Win32_Processor()[0]
        cpu_name = cpu_info.Name.strip()
        cpu_cores = cpu_info.NumberOfCores
        cpu_threads = cpu_info.NumberOfLogicalProcessors
        
        # Memory info
        memory_info = w.Win32_ComputerSystem()[0]
        total_ram_gb = round(int(memory_info.TotalPhysicalMemory) / (1024**3), 2)
        
        # Motherboard
        motherboard_info = w.Win32_BaseBoard()[0]
        motherboard = f"{motherboard_info.Manufacturer} {motherboard_info.Product}"
        
        # OS
        os_version = platform.platform()
        
        # GPUs
        gpus = get_gpu_info()
        
        return HardwareInfo(
            cpu_name=cpu_name,
            cpu_cores=cpu_cores,
            cpu_threads=cpu_threads,
            total_ram_gb=total_ram_gb,
            motherboard=motherboard,
            os_version=os_version,
            gpus=gpus
        )
    except ImportError:
        logger.warning("wmi no disponible, información de hardware limitada")
        return HardwareInfo(
            cpu_name="Desconocido",
            cpu_cores=0,
            cpu_threads=0,
            total_ram_gb=0,
            motherboard="Desconocido",
            os_version=platform.platform(),
            gpus=[]
        )
    except Exception as e:
        logger.error(f"Error obteniendo información de hardware: {str(e)}")
        return HardwareInfo(
            cpu_name="Error",
            cpu_cores=0,
            cpu_threads=0,
            total_ram_gb=0,
            motherboard="Error",
            os_version=platform.platform(),
            gpus=[]
        )

@app.get("/system/extended", summary="Información extendida del sistema", response_description="Información detallada del sistema con GPU y hardware", response_model=SystemExtendedInfo)
def get_system_extended_info(user: str = Depends(authenticate)):
    """
    Endpoint para obtener información extendida del sistema.
    Requiere autenticación básica.

    Args:
        user (str): Usuario autenticado.

    Returns:
        SystemExtendedInfo: Información extendida del sistema.
    """
    try:
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        gpu_info = get_gpu_info()
        hardware_info = get_hardware_info()

        system_info = SystemExtendedInfo(
            cpu_percent=cpu_percent,
            memory_total=memory.total,
            memory_available=memory.available,
            memory_percent=memory.percent,
            disk_total=disk.total,
            disk_free=disk.free,
            disk_percent=disk.percent,
            gpu_info=gpu_info if gpu_info else None,
            hardware_info=hardware_info,
            user=user,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

        logger.info(f"Información extendida del sistema solicitada por usuario: {user}")
        return system_info
    except ImportError:
        logger.error("psutil no está instalado")
        raise HTTPException(status_code=500, detail="psutil no disponible")
    except Exception as e:
        logger.error(f"Error obteniendo información extendida del sistema: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/system/performance", summary="Análisis de rendimiento", response_description="Análisis de rendimiento del sistema", response_model=Dict[str, Any])
def get_performance_analysis(user: str = Depends(authenticate)):
    """
    Endpoint para análisis de rendimiento del sistema.
    Requiere autenticación básica.

    Args:
        user (str): Usuario autenticado.

    Returns:
        Dict: Análisis de rendimiento.
    """
    try:
        import psutil
        
        # Análisis de CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_analysis = {
            "status": "good" if cpu_percent < 50 else "warning" if cpu_percent < 80 else "critical",
            "usage_percent": cpu_percent,
            "recommendation": "OK" if cpu_percent < 50 else "Monitorear" if cpu_percent < 80 else "Optimizar procesos"
        }
        
        # Análisis de memoria
        memory = psutil.virtual_memory()
        memory_analysis = {
            "status": "good" if memory.percent < 60 else "warning" if memory.percent < 80 else "critical",
            "usage_percent": memory.percent,
            "available_gb": round(memory.available / (1024**3), 2),
            "recommendation": "OK" if memory.percent < 60 else "Liberar memoria" if memory.percent < 80 else "Cerrar procesos innecesarios"
        }
        
        # Análisis de disco
        disk = psutil.disk_usage('/')
        disk_analysis = {
            "status": "good" if disk.percent < 70 else "warning" if disk.percent < 85 else "critical",
            "usage_percent": disk.percent,
            "free_gb": round(disk.free / (1024**3), 2),
            "recommendation": "OK" if disk.percent < 70 else "Liberar espacio" if disk.percent < 85 else "Limpiar disco urgentemente"
        }
        
        # Análisis de procesos
        processes = psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])
        high_cpu_processes = []
        high_memory_processes = []
        
        for p in processes:
            try:
                if p.info['cpu_percent'] and p.info['cpu_percent'] > 10:
                    high_cpu_processes.append({
                        "pid": p.info['pid'],
                        "name": p.info['name'],
                        "cpu_percent": p.info['cpu_percent']
                    })
                if p.info['memory_percent'] and p.info['memory_percent'] > 5:
                    high_memory_processes.append({
                        "pid": p.info['pid'],
                        "name": p.info['name'],
                        "memory_percent": p.info['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        analysis = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu_analysis": cpu_analysis,
            "memory_analysis": memory_analysis,
            "disk_analysis": disk_analysis,
            "high_cpu_processes": sorted(high_cpu_processes, key=lambda x: x['cpu_percent'], reverse=True)[:5],
            "high_memory_processes": sorted(high_memory_processes, key=lambda x: x['memory_percent'], reverse=True)[:5],
            "overall_status": "good" if all([
                cpu_analysis['status'] == 'good',
                memory_analysis['status'] == 'good', 
                disk_analysis['status'] == 'good'
            ]) else "warning" if any([
                cpu_analysis['status'] == 'warning',
                memory_analysis['status'] == 'warning',
                disk_analysis['status'] == 'warning'
            ]) else "critical"
        }
        
        logger.info(f"Análisis de rendimiento solicitado por usuario: {user}")
        return analysis
    except ImportError:
        logger.error("psutil no está instalado")
        raise HTTPException(status_code=500, detail="psutil no disponible")
    except Exception as e:
        logger.error(f"Error en análisis de rendimiento: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

def create_backup() -> str:
    """Crea un backup de configuraciones y datos."""
    global last_backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/backup_{timestamp}"
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        if backup_config.include_logs:
            # Backup de logs
            if os.path.exists('backend.log'):
                shutil.copy2('backend.log', f"{backup_dir}/backend.log")
        
        if backup_config.include_metrics:
            # Backup de métricas históricas
            with open(f"{backup_dir}/metrics_history.json", 'w') as f:
                json.dump([m.dict() for m in metrics_history], f, indent=2)
        
        if backup_config.include_alerts:
            # Backup de alertas
            with open(f"{backup_dir}/alerts_history.json", 'w') as f:
                json.dump([a.dict() for a in alerts_history], f, indent=2)
        
        # Backup de configuración
        config_data = {
            "alert_config": alert_config.dict(),
            "backup_config": backup_config.dict(),
            "rate_limits": {
                "requests": RATE_LIMIT_REQUESTS,
                "window": RATE_LIMIT_WINDOW
            }
        }
        with open(f"{backup_dir}/config.json", 'w') as f:
            json.dump(config_data, f, indent=2)
        
        last_backup = datetime.now(timezone.utc).isoformat()
        logger.info(f"Backup creado exitosamente en: {backup_dir}")
        return backup_dir
        
    except Exception as e:
        logger.error(f"Error creando backup: {str(e)}")
        raise

def analyze_trends(hours: int = 24) -> List[TrendAnalysis]:
    """Analiza tendencias en las métricas históricas."""
    if len(metrics_history) < 2:
        return []
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent_metrics = [m for m in metrics_history if datetime.fromisoformat(m.timestamp) > cutoff_time]
    
    if len(recent_metrics) < 2:
        return []
    
    trends = []
    
    # Análisis de CPU
    cpu_values = [m.cpu_percent for m in recent_metrics]
    cpu_trend = analyze_metric_trend(cpu_values)
    trends.append(TrendAnalysis(
        metric="cpu_percent",
        period_hours=hours,
        trend=cpu_trend["trend"],
        average=sum(cpu_values) / len(cpu_values),
        min_value=min(cpu_values),
        max_value=max(cpu_values),
        change_percent=cpu_trend["change_percent"],
        prediction=cpu_trend["prediction"]
    ))
    
    # Análisis de memoria
    memory_values = [m.memory_percent for m in recent_metrics]
    memory_trend = analyze_metric_trend(memory_values)
    trends.append(TrendAnalysis(
        metric="memory_percent",
        period_hours=hours,
        trend=memory_trend["trend"],
        average=sum(memory_values) / len(memory_values),
        min_value=min(memory_values),
        max_value=max(memory_values),
        change_percent=memory_trend["change_percent"],
        prediction=memory_trend["prediction"]
    ))
    
    # Análisis de disco
    disk_values = [m.disk_percent for m in recent_metrics]
    disk_trend = analyze_metric_trend(disk_values)
    trends.append(TrendAnalysis(
        metric="disk_percent",
        period_hours=hours,
        trend=disk_trend["trend"],
        average=sum(disk_values) / len(disk_values),
        min_value=min(disk_values),
        max_value=max(disk_values),
        change_percent=disk_trend["change_percent"],
        prediction=disk_trend["prediction"]
    ))
    
    return trends

def analyze_metric_trend(values: List[float]) -> Dict[str, Any]:
    """Analiza la tendencia de una métrica."""
    if len(values) < 2:
        return {"trend": "stable", "change_percent": 0, "prediction": "Datos insuficientes"}
    
    first_half = values[:len(values)//2]
    second_half = values[len(values)//2:]
    
    avg_first = sum(first_half) / len(first_half)
    avg_second = sum(second_half) / len(second_half)
    
    change_percent = ((avg_second - avg_first) / avg_first) * 100 if avg_first > 0 else 0
    
    if abs(change_percent) < 5:
        trend = "stable"
        prediction = "Se mantendrá estable"
    elif change_percent > 5:
        trend = "increasing"
        prediction = "Tendencia al alza, considere optimización"
    else:
        trend = "decreasing"
        prediction = "Mejorando, continúe monitoreando"
    
    return {
        "trend": trend,
        "change_percent": round(change_percent, 2),
        "prediction": prediction
    }

def execute_safe_command(command: SafeCommand) -> CommandResult:
    """Ejecuta un comando seguro del sistema."""
    import subprocess
    
    # Validar comando
    cmd_parts = command.command.split()
    base_cmd = cmd_parts[0].lower()
    
    if base_cmd not in [allowed.lower() for allowed in command.allowed_commands]:
        raise ValueError(f"Comando no permitido: {base_cmd}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            timeout=command.timeout_seconds,
            shell=False
        )
        
        execution_time = time.time() - start_time
        
        return CommandResult(
            command=command.command,
            output=result.stdout + result.stderr,
            exit_code=result.returncode,
            execution_time=round(execution_time, 2),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        return CommandResult(
            command=command.command,
            output=f"Comando timeout después de {command.timeout_seconds} segundos",
            exit_code=-1,
            execution_time=round(execution_time, 2),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        execution_time = time.time() - start_time
        return CommandResult(
            command=command.command,
            output=f"Error ejecutando comando: {str(e)}",
            exit_code=-1,
            execution_time=round(execution_time, 2),
            timestamp=datetime.now(timezone.utc).isoformat()
        )

if __name__ == "__main__":
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    logger.info(f"Iniciando servidor Uvicorn en {host}:{port}")
    uvicorn.run("main:app", host=host, port=port)
