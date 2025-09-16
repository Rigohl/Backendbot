import asyncio
import psutil
import json
import time
from src.backendbot.utils.logging_config import logger
from src.backendbot.utils.db_logger import log_system_event
from src.backendbot.utils.db_messaging import set_bot_state

STATS_LATEST_KEY = "system_stats_latest"

async def monitor_worker():
    """Worker que monitorea y publica estadísticas del sistema en la DB."""
    logger.info("🤖 Bot Monitor: Iniciando...")
    log_system_event(level="INFO", source="Bot Monitor", message="Bot Monitor iniciado.")
    
    while True:
        try:
            # Recolectar estadísticas
            cpu_usage = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            stats = {
                "cpu_usage": cpu_usage,
                "ram_usage_percent": ram.percent,
                "timestamp": time.time()
            }
            stats_json = json.dumps(stats)

            # Publicar en la DB
            set_bot_state(bot_name="Bot Monitor", state_key=STATS_LATEST_KEY, state_value=stats)
            logger.info(f"🤖 Bot Monitor: Estadísticas publicadas: {stats_json}")
            
            await asyncio.sleep(1) # Publicar cada segundo

        except Exception as e:
            logger.error(f"🤖 Bot Monitor: Error - {e}. Reintentando en 5 segundos...")
            log_system_event(level="ERROR", source="Bot Monitor", message=f"Error en bucle principal: {e}", details=str(e))
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(monitor_worker())
