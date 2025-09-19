import asyncio
import json
import time

import psutil

from backendbot.utils.logging_config import logger

# Intentar importar monitoreo de GPU
try:
    from backendbot.utils.gpu_monitor import getGPUs

    gpu_monitoring = True
except ImportError:
    gpu_monitoring = False

STATS_LATEST_KEY = "system_stats_latest"


async def monitor_worker():
    """Worker que monitorea y publica estadísticas del sistema."""
    logger.info("🤖 Bot Monitor: Iniciando...")

    if gpu_monitoring:
        logger.info("✅ Monitoreo de GPU disponible")
    else:
        logger.warning("⚠️ Monitoreo de GPU no disponible")

    while True:
        try:
            # Recolectar estadísticas básicas
            cpu_usage = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            stats = {
                "cpu_usage": cpu_usage,
                "ram_usage_percent": ram.percent,
                "ram_used_gb": ram.used / (1024**3),
                "ram_total_gb": ram.total / (1024**3),
                "disk_usage_percent": disk.percent,
                "disk_used_gb": disk.used / (1024**3),
                "disk_total_gb": disk.total / (1024**3),
                "timestamp": time.time(),
            }

            # Agregar información de GPU si está disponible
            if gpu_monitoring:
                try:
                    gpus = getGPUs()
                    gpu_stats = []
                    for i, gpu in enumerate(gpus):
                        gpu_info = {
                            "id": gpu.id,
                            "name": gpu.name,
                            "memory_used_mb": gpu.memoryUsed,
                            "memory_total_mb": gpu.memoryTotal,
                            "memory_free_mb": gpu.memoryFree,
                            "temperature": gpu.temperature,
                        }
                        gpu_stats.append(gpu_info)

                    stats["gpus"] = gpu_stats
                    stats["gpu_count"] = len(gpus)

                except Exception as e:
                    logger.warning(f"Error obteniendo información de GPU: {e}")
                    stats["gpu_error"] = str(e)

            json.dumps(stats)

            # Log local
            logger.info(
                f"🤖 Bot Monitor: Estadísticas: CPU {cpu_usage}%, RAM {ram.percent}%, Disco {disk.percent}%"
            )
            if gpu_monitoring and "gpus" in stats:
                gpu_info = stats["gpus"][0] if stats["gpus"] else None
                if gpu_info and gpu_info["memory_total_mb"] > 0:
                    vram_percent = (
                        gpu_info["memory_used_mb"] / gpu_info["memory_total_mb"]
                    ) * 100
                    logger.info(
                        f"🤖 Bot Monitor: GPU {gpu_info['name'][:20]}... VRAM {vram_percent:.1f}%"
                    )

            await asyncio.sleep(1)  # Publicar cada segundo

        except Exception as e:
            logger.error(f"🤖 Bot Monitor: Error - {e}. Reintentando en 5 segundos...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(monitor_worker())
