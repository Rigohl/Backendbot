"""
BackendBot - API Gateway
Microservicio principal que maneja todas las operaciones de BackendBot
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Modelos de datos
class BotStatus(BaseModel):
    name: str
    status: str
    last_execution: Optional[datetime]
    is_available: bool


class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent: int
    network_recv: int
    battery_percent: Optional[float]
    temperature: Optional[float]


class BotCommand(BaseModel):
    bot_name: str
    command: str
    parameters: Optional[Dict[str, Any]] = {}


# Servicios (simulados por ahora)
class BotService:
    def __init__(self):
        self.bots = {
            "monitor": {"status": "idle", "last_execution": None},
            "organizer": {"status": "idle", "last_execution": None},
            "indexer": {"status": "idle", "last_execution": None},
            "guardian": {"status": "idle", "last_execution": None},
            "auditor_files": {"status": "idle", "last_execution": None},
            "auditor_programs": {"status": "idle", "last_execution": None},
        }

    def get_bot_status(self, bot_name: str) -> BotStatus:
        if bot_name not in self.bots:
            raise HTTPException(status_code=404, detail=f"Bot {bot_name} not found")

        bot_data = self.bots[bot_name]
        return BotStatus(
            name=bot_name,
            status=bot_data["status"],
            last_execution=bot_data["last_execution"],
            is_available=True,
        )

    def get_all_bots_status(self) -> List[BotStatus]:
        return [
            BotStatus(
                name=name,
                status=data["status"],
                last_execution=data["last_execution"],
                is_available=True,
            )
            for name, data in self.bots.items()
        ]

    async def execute_bot_command(
        self, bot_name: str, command: str, parameters: Dict[str, Any]
    ):
        """Ejecutar comando en un bot (simulado)"""
        if bot_name not in self.bots:
            raise HTTPException(status_code=404, detail=f"Bot {bot_name} not found")

        # Simular ejecución
        self.bots[bot_name]["status"] = "running"
        self.bots[bot_name]["last_execution"] = datetime.now()

        # Simular procesamiento
        await asyncio.sleep(2)

        self.bots[bot_name]["status"] = "completed"

        return {
            "status": "success",
            "message": f"Command {command} executed on {bot_name}",
        }


class SystemService:
    def get_system_metrics(self) -> SystemMetrics:
        """Obtener métricas del sistema (simulado)"""
        import random

        import psutil

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            network = psutil.net_io_counters()

            battery = psutil.sensors_battery()
            battery_percent = battery.percent if battery else None

            # Temperatura simulada
            temperature = random.uniform(40, 80)

            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                network_sent=network.bytes_sent if network else 0,
                network_recv=network.bytes_recv if network else 0,
                battery_percent=battery_percent,
                temperature=temperature,
            )
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            # Retornar datos simulados en caso de error
            return SystemMetrics(
                cpu_percent=random.uniform(10, 90),
                memory_percent=random.uniform(20, 80),
                disk_percent=random.uniform(30, 70),
                network_sent=random.randint(1000000, 50000000),
                network_recv=random.randint(1000000, 50000000),
                battery_percent=(
                    random.uniform(20, 100) if random.choice([True, False]) else None
                ),
                temperature=random.uniform(40, 80),
            )


# Instancias de servicios
bot_service = BotService()
system_service = SystemService()


# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 BackendBot API Gateway starting up...")
    yield
    # Shutdown
    logger.info("🛑 BackendBot API Gateway shutting down...")


# Crear aplicación FastAPI
app = FastAPI(
    title="BackendBot API Gateway",
    description="API Gateway para el sistema BackendBot - Arquitectura escalable",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection
def get_bot_service():
    return bot_service


def get_system_service():
    return system_service


# Health check
@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "services": {"bots": len(bot_service.bots), "system": "available"},
    }


# API Routes - Bots
@app.get("/api/v1/bots", response_model=List[BotStatus])
async def get_bots_status(bot_service: BotService = Depends(get_bot_service)):
    """Obtener estado de todos los bots"""
    return bot_service.get_all_bots_status()


@app.get("/api/v1/bots/{bot_name}", response_model=BotStatus)
async def get_bot_status(
    bot_name: str, bot_service: BotService = Depends(get_bot_service)
):
    """Obtener estado de un bot específico"""
    return bot_service.get_bot_status(bot_name)


@app.post("/api/v1/bots/{bot_name}/execute")
async def execute_bot_command(
    bot_name: str,
    command_request: BotCommand,
    background_tasks: BackgroundTasks,
    bot_service: BotService = Depends(get_bot_service),
):
    """Ejecutar comando en un bot"""
    background_tasks.add_task(
        bot_service.execute_bot_command,
        bot_name,
        command_request.command,
        command_request.parameters,
    )

    return {
        "status": "accepted",
        "message": f"Command {command_request.command} queued for bot {bot_name}",
        "bot_name": bot_name,
        "command": command_request.command,
    }


# API Routes - System
@app.get("/api/v1/system/metrics", response_model=SystemMetrics)
async def get_system_metrics(
    system_service: SystemService = Depends(get_system_service),
):
    """Obtener métricas del sistema"""
    return system_service.get_system_metrics()


@app.get("/api/v1/system/info")
async def get_system_info():
    """Obtener información del sistema"""
    import platform

    import psutil

    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "disk_total": psutil.disk_usage("/").total,
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url),
        },
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
