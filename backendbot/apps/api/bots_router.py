"""
BackendBot API - Bots Router
Gestión completa de los bots del sistema (Monitor, Organizer, Indexer, Guardian)
"""
from datetime import datetime
from typing import List, Optional, Dict

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backendbot.packages.models.models import (
    BotStatus, BotInfo, SystemMetrics, SecurityAlert, SecurityEvent,
    FileOrganizationResult
)
from backendbot.packages.bots.monitor_worker import MonitorWorker
from backendbot.packages.bots.organizer_worker import OrganizerWorker
from backendbot.packages.bots.indexer_worker import IndexerWorker
from backendbot.packages.bots.guardian_worker import GuardianWorker
from backendbot.core.di.container import container
from backendbot.core.orchestrator import Orchestrator

router = APIRouter(prefix="/api/v1/bots", tags=["bots"])

# Orchestrator lazily instantiated to avoid side-effects on import
_orchestrator_instance: Orchestrator | None = None

def get_orchestrator() -> Orchestrator:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance

# Modelos de respuesta
class BotListResponse(BaseModel):
    success: bool
    message: str
    bots: List[Dict]
    timestamp: datetime

class BotStatusResponse(BaseModel):
    success: bool
    message: str
    bot_info: Dict
    timestamp: datetime

class BotCommandResponse(BaseModel):
    success: bool
    message: str
    command_id: str
    timestamp: datetime

# Instancias de bots (serán gestionadas por el orquestador)
# monitor_bot = MonitorWorker(bot_id="monitor-001", name="Monitor Bot")
# organizer_bot = OrganizerWorker(bot_id="organizer-001", name="Organizer Bot")
# indexer_bot = IndexerWorker(bot_id="indexer-001", name="Indexer Bot")
# guardian_bot = GuardianWorker(bot_id="guardian-001", name="Guardian Bot")

# bots = {
#     "monitor": monitor_bot,
#     "organizer": organizer_bot,
#     "indexer": indexer_bot,
#     "guardian": guardian_bot
# }

@router.get("/", response_model=BotListResponse)
async def get_all_bots():
    """
    Obtener información de todos los bots del sistema.
    """
    try:
        bot_statuses = get_orchestrator().get_system_status()['bots']
        bot_list = []
        for bot_name, bot_status in bot_statuses.items():
            bot_info = {
                "name": bot_name,
                "status": bot_status,
                "description": get_bot_description(bot_name)
            }
            bot_list.append(bot_info)

        return BotListResponse(
            success=True,
            message="Bots retrieved successfully",
            bots=bot_list,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving bots: {str(e)}")

@router.get("/{bot_name}", response_model=BotStatusResponse)
async def get_bot_status(bot_name: str):
    """
    Obtener estado detallado de un bot específico.
    """
    bot_status = get_orchestrator().get_system_status()['bots'].get(bot_name)
    if not bot_status:
        return BotStatusResponse(
            success=False,
            message=f"Bot '{bot_name}' not found",
            bot_info={},
            timestamp=datetime.now()
        )

    try:
        bot_info = {
            "name": bot_name,
            "status": bot_status,
            "description": get_bot_description(bot_name)
        }
        return BotStatusResponse(
            success=True,
            message=f"Bot '{bot_name}' status retrieved successfully",
            bot_info=bot_info,
            timestamp=datetime.now()
        )
    except Exception as e:
        return BotStatusResponse(
            success=False,
            message=f"Error retrieving bot status: {str(e)}",
            bot_info={},
            timestamp=datetime.now()
        )

@router.post("/{bot_name}/start", response_model=BotCommandResponse)
async def start_bot(bot_name: str, background_tasks: BackgroundTasks):
    """
    Iniciar un bot específico.
    """
    if bot_name not in get_orchestrator().bot_manager.bots:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_name}' not found")

    try:
        # La lógica de inicio ahora es manejada por el orquestador/botmanager
        get_orchestrator().bot_manager.get_bot(bot_name).start()
        return BotCommandResponse(
            success=True,
            message=f"Bot '{bot_name}' start command issued",
            command_id=f"start_{bot_name}_{datetime.now().timestamp()}",
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting bot: {str(e)}")

@router.post("/{bot_name}/stop", response_model=BotCommandResponse)
async def stop_bot(bot_name: str):
    """
    Detener un bot específico.
    """
    if bot_name not in get_orchestrator().bot_manager.bots:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_name}' not found")

    try:
        # La lógica de detención ahora es manejada por el orquestador/botmanager
        get_orchestrator().bot_manager.get_bot(bot_name).stop()
        return BotCommandResponse(
            success=True,
            message=f"Bot '{bot_name}' stop command issued",
            command_id=f"stop_{bot_name}_{datetime.now().timestamp()}",
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping bot: {str(e)}")

@router.post("/{bot_name}/restart", response_model=BotCommandResponse)
async def restart_bot(bot_name: str, background_tasks: BackgroundTasks):
    """
    Reiniciar un bot específico.
    """
    if bot_name not in get_orchestrator().bot_manager.bots:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_name}' not found")

    try:
        # La lógica de reinicio ahora es manejada por el orquestador/botmanager
        bot = get_orchestrator().bot_manager.get_bot(bot_name)
        bot.stop()
        background_tasks.add_task(bot.start)
        return BotCommandResponse(
            success=True,
            message=f"Bot '{bot_name}' restart command issued",
            command_id=f"restart_{bot_name}_{datetime.now().timestamp()}",
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restarting bot: {str(e)}")

@router.get("/{bot_name}/metrics")
async def get_bot_metrics(bot_name: str):
    """
    Obtener métricas específicas de un bot.
    """
    if bot_name not in get_orchestrator().bot_manager.bots:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_name}' not found")

    try:
        bot_instance = get_orchestrator().bot_manager.get_bot(bot_name)
        if hasattr(bot_instance, 'get_current_metrics'):
            metrics = bot_instance.get_current_metrics()
        else:
            metrics = {}

        return {
            "success": True,
            "message": f"Metrics for bot '{bot_name}' retrieved successfully",
            "metrics": metrics,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving bot metrics: {str(e)}")


@router.post("/enable_extras")
async def enable_extra_bots():
    """Habilitar bots adicionales (auditor, chat) en tiempo de ejecución."""
    try:
        orch = get_orchestrator()
        added_before = set(orch.bot_manager.bots.keys())
        orch.bot_manager.enable_extra_bots()
        added_after = set(orch.bot_manager.bots.keys())
        added = list(added_after - added_before)
        return {"success": True, "message": "Extra bots enabled", "added": added}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disable_extras")
async def disable_extra_bots():
    """Deshabilitar bots adicionales cargados previamente."""
    try:
        orch = get_orchestrator()
        removed = orch.bot_manager.disable_extra_bots()
        return {"success": True, "message": "Extra bots disabled", "removed": removed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_bot_description(bot_name: str) -> str:
    """
    Obtener descripción de un bot.
    """
    descriptions = {
        "monitor": "Monitorea el sistema en tiempo real, CPU, memoria, disco y red",
        "organizer": "Organiza y clasifica archivos automáticamente según reglas configuradas",
        "indexer": "Indexa archivos y crea metadatos para búsqueda rápida",
        "guardian": "Protege el sistema contra amenazas y anomalías de seguridad"
    }
    return descriptions.get(bot_name, f"Bot {bot_name}")