from fastapi import APIRouter, Depends, HTTPException
import json
from src.backendbot.utils.logging_config import logger
from src.backendbot.utils.db_messaging import get_bot_state

router = APIRouter(
    prefix="/api/v1/monitor",
    tags=["Monitoring"],
)

@router.get("/stats")
async def get_current_system_stats():
    """Devuelve las últimas estadísticas del sistema leídas desde la base de datos."""
    logger.info("Acceso al endpoint de estadísticas de monitoreo.")
    latest_stats = get_bot_state(bot_name="Bot Monitor", state_key="system_stats_latest")
    if not latest_stats:
        logger.warning("No hay estadísticas de monitoreo disponibles todavía en la DB.")
        raise HTTPException(status_code=404, detail="No hay estadísticas de monitoreo disponibles todavía.")
    return latest_stats