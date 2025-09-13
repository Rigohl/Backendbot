import asyncio
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api_routes import router
from .config import Settings
from .database import init_db
from .utils import log_event
from .watchdog import watchdog
from .routers import tasks_routes
from .staging_automation import run_preview_workflow
from .railway_integration import railway, init_railway
from .cache import cache
from .webhooks import webhooks
from .rate_limit import rate_limit_store
from .services.activity_monitor import activity_monitor

settings = Settings()

app = FastAPI(
    title="BackendBot Pro", description="Monitoreo + Automatización + Dashboard"
)

app.include_router(router)
app.include_router(tasks_routes.router, prefix="/celery", tags=["celery"])

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Middleware para rate limiting usando Redis."""
    client_ip = getattr(request.client, 'host', None) if request.client else "test_client"
    if not client_ip or client_ip == "testserver":
        client_ip = "test_client"

    if not rate_limit_store.set_rate_limit(
        identifier=client_ip,
        window_seconds=settings.RATE_LIMIT_WINDOW,
        max_requests=settings.RATE_LIMIT_REQUESTS
    ):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )
    return await call_next(request)

@app.get("/")
async def root():
    """Endpoint raíz para verificar que el backend está funcionando."""
    railway_info = railway.get_railway_info() if railway.initialized else None
    return {
        "message": "BackendBot is running",
        "status": "ok",
        "railway_enabled": railway.is_railway_environment(),
        "railway_info": railway_info
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check avanzado con métricas de Railway."""
    if railway.initialized:
        return await railway.get_system_status()
    else:
        return {
            "status": "ok",
            "message": "BackendBot is running (Railway integration not initialized)",
            "timestamp": time.time()
        }

@app.post("/optimize")
async def optimize_system():
    """Endpoint para ejecutar optimización del sistema."""
    if not railway.initialized:
        return JSONResponse(
            status_code=503,
            content={"detail": "Railway integration not available"}
        )

    return await railway.optimize_system()

@app.get("/railway/status")
async def railway_status():
    """Obtener estado detallado de Railway."""
    if not railway.initialized:
        return JSONResponse(
            status_code=503,
            content={"detail": "Railway integration not available"}
        )

    return await railway.get_system_status()

@app.get("/railway/cache/stats")
async def cache_stats():
    """Obtener estadísticas del cache Redis."""
    if not railway.initialized:
        return JSONResponse(
            status_code=503,
            content={"detail": "Railway integration not available"}
        )

    return cache.get_cache_stats()

@app.post("/railway/webhook")
async def railway_webhook(request: Request):
    """Endpoint para webhooks de Railway."""
    if not railway.initialized:
        return JSONResponse(
            status_code=503,
            content={"detail": "Railway integration not available"}
        )

    return await webhooks.handle_webhook(request)

@app.get("/activity/status")
async def get_activity_status():
    """Obtener estado del monitoreo de actividad."""
    return activity_monitor.get_status()

@app.post("/activity/start")
async def start_activity_monitoring():
    """Iniciar monitoreo de actividad."""
    activity_monitor.start_monitoring()
    return {"message": "Activity monitoring started"}

@app.post("/activity/stop")
async def stop_activity_monitoring():
    """Detener monitoreo de actividad."""
    activity_monitor.stop_monitoring()
    return {"message": "Activity monitoring stopped"}

@app.post("/activity/respond")
async def respond_to_activity_warning():
    """Responder a la advertencia de inactividad."""
    if not activity_monitor.is_active:
        activity_monitor._resume_activity()
        return {"message": "Activity resumed"}
    return {"message": "No inactivity warning active"}

@app.on_event("startup")
async def on_startup():
    await init_db()

    # Inicializar integración de Railway
    if await init_railway():
        log_event("Railway integration initialized successfully")
    else:
        log_event("Railway integration failed to initialize")

    asyncio.create_task(watchdog())  # Start watchdog as an asyncio task

    # Iniciar monitoreo de actividad si está habilitado
    if settings.ACTIVITY_MONITORING_ENABLED:
        activity_monitor.start_monitoring()
        log_event("Activity monitoring started")

    # Run staging preview on startup (dry-run)
    plan = run_preview_workflow()
    log_event(f"Staging preview executed: {len(plan)} components")


# Log inicial para indicar que el backend se ha iniciado
log_event("BackendBot iniciado correctamente")

# Para Railway/Fly.io: expone 'app' para uvicorn
# No es necesario el bloque __main__ para producción
