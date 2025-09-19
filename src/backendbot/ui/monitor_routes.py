from fastapi import APIRouter
from src.backendbot.monitor.system_monitor import get_system_stats
from src.backendbot.utils.logging_config import logger

router = APIRouter(
    prefix="/api/v1/monitor",
    tags=["Monitoring"],
)

@router.get("/stats")
async def get_current_system_stats():
    """Devuelve las estadísticas actuales del sistema (CPU, RAM, etc.) en tiempo real."""
    logger.info("Acceso al endpoint de estadísticas de monitoreo (local).")
    stats = get_system_stats()
    return stats.model_dump()