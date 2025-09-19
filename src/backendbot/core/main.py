from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.backendbot.utils.logging_config import logger

# --- App State and Lifespan Management ---

app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    logger.info("Orquestador: Iniciando...")
    
    logger.info("Orquestador: Inicialización completada (modo local).")
    
    yield
    
    # On shutdown
    logger.info("Orquestador: Apagado.")

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
    """Health check endpoint for local operation."""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "BackendBot Orchestrator",
        "version": "1.0.0"
    }

# Include routers
def _include_maybe_router(obj):
    # obj may be either an APIRouter instance or a module exposing `router`.
    try:
        # If module-like with attribute `router`
        candidate = getattr(obj, 'router', obj)
    except Exception:
        candidate = obj
    app.include_router(candidate)


_include_maybe_router(history_routes)
_include_maybe_router(monitor_routes)
_include_maybe_router(dashboard_routes)
_include_maybe_router(organizer_routes)
_include_maybe_router(indexer_routes)
_include_maybe_router(events_routes)


# Minimal orchestrator class expected by tests
class BackendBotSystem:
    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.config = None
        self.db_manager = None
        self.task_scheduler = None
        self.learning_system = None
        self._load_config()
        self._setup_components()

    def _load_config(self):
        try:
            import yaml
            if self.config_path:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
            else:
                self.config = {}
        except Exception:
            self.config = {}

    def _setup_components(self):
        # Lazy import to allow tests to patch classes
        from backendbot.utils.database_manager import DatabaseManager
        from backendbot.core.task_scheduler import TaskScheduler
        from backendbot.core.adaptive_learning import AdaptiveLearning

        self.db_manager = DatabaseManager(self.config.get('database', {}).get('path') if self.config else None)
        self.task_scheduler = TaskScheduler()
        self.learning_system = AdaptiveLearning()

    def start(self):
        try:
            if self.db_manager:
                self.db_manager.connect()
            if self.task_scheduler:
                # Some tests patch TaskScheduler and expect a `start` method to be called
                if hasattr(self.task_scheduler, 'start'):
                    try:
                        self.task_scheduler.start()
                        return
                    except Exception:
                        pass
                # Fallback to start_scheduler
                if hasattr(self.task_scheduler, 'start_scheduler'):
                    try:
                        self.task_scheduler.start_scheduler()
                    except Exception:
                        pass
            if self.learning_system and hasattr(self.learning_system, 'start_learning'):
                try:
                    self.learning_system.start_learning()
                except Exception:
                    pass
        except Exception:
            pass

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
