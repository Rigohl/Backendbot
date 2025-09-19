from fastapi import APIRouter

def get_system_stats():
    # Mock: Devuelve métricas de sistema simuladas
    return type('Stats', (), {
        'model_dump': lambda self=None: {
            'cpu_usage': 42,
            'ram_usage_percent': 55,
            'ram_used_gb': 8,
            'ram_total_gb': 16
        }
    })()
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
