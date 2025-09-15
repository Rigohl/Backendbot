from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.backendbot.utils.logging_config import logger
from src.backendbot.utils.db_logger import log_system_event, create_db_tables
from src.backendbot.utils.db_messaging import create_messaging_tables
from src.backendbot.templates import templates

# --- App State and Lifespan Management ---

app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    logger.info("Orquestador: Iniciando...")
    try:
        log_system_event(level="INFO", source="Orquestador", message="Iniciando Orquestador.")
    except Exception as e:
        logger.warning(f"No se pudo loggear el inicio: {e}")
    
    try:
        # Crear tablas de la base de datos si no existen
        create_db_tables()
        create_messaging_tables()
        logger.info("Orquestador: Tablas de base de datos verificadas/creadas.")
        try:
            log_system_event(level="INFO", source="Orquestador", message="Tablas de base de datos verificadas/creadas.")
        except Exception as e:
            logger.warning(f"No se pudo loggear la creación de tablas: {e}")
    except Exception as e:
        logger.error(f"Orquestador: Error al conectar con DB o crear tablas - {e}")
        logger.error("Orquestador: Asegúrate de que la DB está en ejecución y configurada.")
        try:
            log_system_event(level="ERROR", source="Orquestador", message=f"Error de inicio: {e}", details=str(e))
        except Exception as log_e:
            logger.warning(f"No se pudo loggear el error: {log_e}")
    
    yield
    
    # On shutdown
    logger.info("Orquestador: Apagado.")
    try:
        log_system_event(level="INFO", source="Orquestador", message="Orquestador apagado.")
    except Exception as e:
        logger.warning(f"No se pudo loggear el apagado: {e}")

# --- FastAPI App Initialization ---

app = FastAPI(title="BackendBot Orchestrator", lifespan=lifespan)

# Import routers after app initialization to avoid circular dependencies
from .routers import history_routes, monitor_routes, dashboard_routes, organizer_routes, indexer_routes, events_routes

@app.get("/", tags=["Root"])
def read_root():
    logger.info("Acceso al endpoint raíz.")
    return {"message": "Welcome to BackendBot Orchestrator"}

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for Railway deployment monitoring."""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "BackendBot Orchestrator",
        "version": "1.0.0"
    }

# Include routers
app.include_router(history_routes.router)
app.include_router(monitor_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(organizer_routes.router)
app.include_router(indexer_routes.router)
app.include_router(events_routes.router)

# --- Server Startup ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando servidor FastAPI en http://localhost:8000")
    uvicorn.run(
        "src.backendbot.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
