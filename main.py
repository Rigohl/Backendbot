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
import uvicorn
import secrets
import logging
import os
from datetime import datetime, timezone
from typing import Optional, List
from collections import defaultdict
import time

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

# Variables globales para alertas y métricas
alert_config = AlertConfig()
alerts_history = []
metrics_history = []
MAX_HISTORY = 100

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

        health = HealthResponse(
            status="healthy" if cpu_percent < 90 and memory.percent < 90 else "warning",
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

if __name__ == "__main__":
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    logger.info(f"Iniciando servidor Uvicorn en {host}:{port}")
    uvicorn.run("main:app", host=host, port=port)
