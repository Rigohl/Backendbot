#!/usr/bin/env python3
"""
BackendBot Launcher Unificado
============================
Arranque profesional único para BackendBot: inicia API (FastAPI/Uvicorn) y ejecutor principal (bots/orquestador).
Valida entorno, permite cierre limpio y logging robusto.
"""
import os
import sys
import logging
import asyncio
from pathlib import Path

# --- Validación de entorno ---
REQUIRED_PYTHON = (3, 12)
if sys.version_info < REQUIRED_PYTHON:
    sys.exit(f"[ERROR] Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+ requerido. Actualiza tu entorno.")

# --- Configuración de logging profesional ---
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("backendbot_launcher")

# --- Ajuste de paths para imports limpios ---
PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# --- Importar API y orquestador principal ---
try:
    from backendbot.apps.api.main import app as api_app
    from backendbot.core.orchestrator import Orchestrator
except ImportError as e:
    logger.error(f"Error importando módulos principales: {e}")
    sys.exit(1)

# --- Arranque de Uvicorn en background ---
def start_api_server():
    import uvicorn
    logger.info("Iniciando API BackendBot en http://127.0.0.1:8000 ...")
    config = uvicorn.Config(api_app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    return server

# --- Arranque del orquestador/bots ---
def start_orchestrator():
    logger.info("Iniciando Orquestador/Bots BackendBot ...")
    orchestrator = Orchestrator()
    orchestrator.start()  # Debe ser no bloqueante o ejecutarse en thread/hilo
    return orchestrator

async def main():
    logger.info("==== BackendBot Launcher Unificado ====")
    # Arrancar API y orquestador en paralelo
    server = start_api_server()
    loop = asyncio.get_event_loop()
    orchestrator = start_orchestrator()
    # Lanzar API en background
    api_task = loop.create_task(server.serve())
    try:
        await api_task
    except (KeyboardInterrupt, SystemExit):
        logger.info("Cierre solicitado. Terminando BackendBot...")
        # Aquí puedes agregar lógica de cierre limpio para el orquestador
        if hasattr(orchestrator, "stop"):
            orchestrator.stop()
        logger.info("BackendBot cerrado correctamente.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Error crítico en el launcher: {e}")
        sys.exit(1)
