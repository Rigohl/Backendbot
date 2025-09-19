from fastapi import APIRouter

from src.backendbot.utils.logging_config import logger

router = APIRouter(
    prefix="/api/v1/history",
    tags=["History"],
)


@router.get("/")
def get_history():
    logger.info("Acceso al endpoint de historial.")
    # Placeholder
    return [{"id": 1, "event": "System Start"}, {"id": 2, "event": "CPU usage high"}]
