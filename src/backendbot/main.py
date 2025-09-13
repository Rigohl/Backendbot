import asyncio
import time
import sys
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Agregar el directorio padre al path para imports relativos
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Función para imports seguros
def safe_import(module_path, fallback_name=None):
    """Importa un módulo de forma segura con fallback"""
    try:
        module = __import__(module_path, fromlist=[module_path.split('.')[-1]])
        return module
    except ImportError as e:
        print(f"Warning: Could not import {module_path}: {e}")
        if fallback_name:
            try:
                return __import__(fallback_name, fromlist=[fallback_name.split('.')[-1]])
            except ImportError:
                print(f"Warning: Fallback import {fallback_name} also failed")
        return None

# Imports con manejo seguro
api_routes = safe_import('backendbot.api_routes')
config = safe_import('backendbot.config')
database = safe_import('backendbot.database')
utils = safe_import('backendbot.utils')
watchdog_module = safe_import('backendbot.watchdog')
routers = safe_import('backendbot.routers')
staging_automation = safe_import('backendbot.staging_automation')
railway_integration = safe_import('backendbot.railway_integration')
cache_module = safe_import('backendbot.cache')
webhooks_module = safe_import('backendbot.webhooks')
rate_limit = safe_import('backendbot.rate_limit')
activity_monitor_module = safe_import('backendbot.services.activity_monitor')

# Definir rate_limit_store global para compatibilidad con tests
rate_limit_store = None
if rate_limit and hasattr(rate_limit, 'rate_limit_store'):
    rate_limit_store = rate_limit.rate_limit_store

# Configuración con fallback
if config and hasattr(config, 'Settings'):
    settings = config.Settings()
else:
    # Configuración básica por defecto
    class DefaultSettings:
        RATE_LIMIT_WINDOW = 60
        RATE_LIMIT_REQUESTS = 100
        ACTIVITY_MONITORING_ENABLED = True
        DEBUG = True
        DATABASE_URL = "sqlite:///backendbot.db"
        LOGGING_CONFIG = {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "simple"
                }
            },
            "formatters": {
                "simple": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "root": {"handlers": ["console"], "level": "INFO"}
        }
    settings = DefaultSettings()

app = FastAPI(
    title="BackendBot Pro", description="Monitoreo + Automatización + Dashboard"
)

# Inicializar componentes con verificación
if api_routes and hasattr(api_routes, 'router'):
    app.include_router(api_routes.router)

if routers and hasattr(routers, 'tasks_routes') and hasattr(routers.tasks_routes, 'router'):
    app.include_router(routers.tasks_routes.router, prefix="/celery", tags=["celery"])

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Middleware para rate limiting usando Redis."""
    client_ip = getattr(request.client, 'host', None) if request.client else "test_client"
    if not client_ip or client_ip == "testserver":
        client_ip = "test_client"

    # Verificar si rate_limit está disponible
    if rate_limit and hasattr(rate_limit, 'rate_limit_store'):
        rate_limit_store = rate_limit.rate_limit_store
        if hasattr(rate_limit_store, 'set_rate_limit'):
            if not rate_limit_store.set_rate_limit(
                identifier=client_ip,
                window_seconds=settings.RATE_LIMIT_WINDOW,
                max_requests=settings.RATE_LIMIT_REQUESTS
            ):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"}
                )
        else:
            print("Warning: rate_limit_store.set_rate_limit not available")
    else:
        print("Warning: rate_limit module not available, skipping rate limiting")

    return await call_next(request)

@app.get("/")
async def root():
    """Endpoint raíz para verificar que el backend está funcionando."""
    railway_info = None
    railway_enabled = False

    if railway_integration and hasattr(railway_integration, 'railway'):
        railway = railway_integration.railway
        if hasattr(railway, 'initialized') and railway.initialized:
            if hasattr(railway, 'get_railway_info'):
                railway_info = railway.get_railway_info()
        if hasattr(railway, 'is_railway_environment'):
            railway_enabled = railway.is_railway_environment()

    return {
        "message": "BackendBot is running",
        "status": "ok",
        "railway_enabled": railway_enabled,
        "railway_info": railway_info
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check avanzado con métricas de Railway."""
    if railway_integration and hasattr(railway_integration, 'railway'):
        railway = railway_integration.railway
        if hasattr(railway, 'initialized') and railway.initialized:
            if hasattr(railway, 'get_system_status'):
                return await railway.get_system_status()

    return {
        "status": "ok",
        "message": "BackendBot is running (Railway integration not initialized)",
        "timestamp": time.time()
    }

@app.post("/optimize")
async def optimize_system():
    """Endpoint para ejecutar optimización del sistema."""
    if not (railway_integration and hasattr(railway_integration, 'railway')):
        return JSONResponse(
            status_code=503,
            content={"detail": "Railway integration not available"}
        )

    railway = railway_integration.railway
    if hasattr(railway, 'initialized') and not railway.initialized:
        return JSONResponse(
            status_code=503,
            content={"detail": "Railway integration not available"}
        )

    if hasattr(railway, 'optimize_system'):
        return await railway.optimize_system()

    return JSONResponse(
        status_code=503,
        content={"detail": "Railway optimization not available"}
    )

@app.get("/railway/status")
async def railway_status():
    """Obtener estado detallado de Railway."""
    if not (railway_integration and hasattr(railway_integration, 'railway')):
        return JSONResponse(
            status_code=503,
            content={"detail": "Railway integration not available"}
        )

    railway = railway_integration.railway
    if hasattr(railway, 'initialized') and not railway.initialized:
        return JSONResponse(
            status_code=503,
            content={"detail": "Railway integration not available"}
        )

    if hasattr(railway, 'get_system_status'):
        return await railway.get_system_status()

    return JSONResponse(
        status_code=503,
        content={"detail": "Railway status not available"}
    )

@app.get("/railway/cache/stats")
async def cache_stats():
    """Obtener estadísticas del cache Redis."""
    if not (railway_integration and hasattr(railway_integration, 'railway')):
        return JSONResponse(
            status_code=503,
            content={"detail": "Railway integration not available"}
        )

    railway = railway_integration.railway
    if hasattr(railway, 'initialized') and not railway.initialized:
        return JSONResponse(
            status_code=503,
            content={"detail": "Railway integration not available"}
        )

    if cache_module and hasattr(cache_module, 'cache') and hasattr(cache_module.cache, 'get_cache_stats'):
        return cache_module.cache.get_cache_stats()

    return JSONResponse(
        status_code=503,
        content={"detail": "Cache stats not available"}
    )

@app.post("/railway/webhook")
async def railway_webhook(request: Request):
    """Endpoint para webhooks de Railway."""
    if not (railway_integration and hasattr(railway_integration, 'railway')):
        return JSONResponse(
            status_code=503,
            content={"detail": "Railway integration not available"}
        )

    railway = railway_integration.railway
    if hasattr(railway, 'initialized') and not railway.initialized:
        return JSONResponse(
            status_code=503,
            content={"detail": "Railway integration not available"}
        )

    if webhooks_module and hasattr(webhooks_module, 'webhooks') and hasattr(webhooks_module.webhooks, 'handle_webhook'):
        return await webhooks_module.webhooks.handle_webhook(request)

    return JSONResponse(
        status_code=503,
        content={"detail": "Webhook handler not available"}
    )

@app.get("/activity/status")
async def get_activity_status():
    """Obtener estado del monitoreo de actividad."""
    if activity_monitor_module and hasattr(activity_monitor_module, 'activity_monitor'):
        activity_monitor = activity_monitor_module.activity_monitor
        if hasattr(activity_monitor, 'get_status'):
            return activity_monitor.get_status()

    return {"status": "not_available", "message": "Activity monitor not initialized"}

@app.post("/activity/start")
async def start_activity_monitoring():
    """Iniciar monitoreo de actividad."""
    if activity_monitor_module and hasattr(activity_monitor_module, 'activity_monitor'):
        activity_monitor = activity_monitor_module.activity_monitor
        if hasattr(activity_monitor, 'start_monitoring'):
            activity_monitor.start_monitoring()
            return {"message": "Activity monitoring started"}

    return JSONResponse(
        status_code=503,
        content={"detail": "Activity monitor not available"}
    )

@app.post("/activity/stop")
async def stop_activity_monitoring():
    """Detener monitoreo de actividad."""
    if activity_monitor_module and hasattr(activity_monitor_module, 'activity_monitor'):
        activity_monitor = activity_monitor_module.activity_monitor
        if hasattr(activity_monitor, 'stop_monitoring'):
            activity_monitor.stop_monitoring()
            return {"message": "Activity monitoring stopped"}

    return JSONResponse(
        status_code=503,
        content={"detail": "Activity monitor not available"}
    )

@app.post("/activity/respond")
async def respond_to_activity_warning():
    """Responder a la advertencia de inactividad."""
    if activity_monitor_module and hasattr(activity_monitor_module, 'activity_monitor'):
        activity_monitor = activity_monitor_module.activity_monitor
        if hasattr(activity_monitor, 'is_active') and not activity_monitor.is_active:
            if hasattr(activity_monitor, '_resume_activity'):
                activity_monitor._resume_activity()
                return {"message": "Activity resumed"}

    return {"message": "No inactivity warning active"}

@app.on_event("startup")
async def on_startup():
    """Inicializar componentes al iniciar la aplicación."""
    # Inicializar base de datos
    if database and hasattr(database, 'init_db'):
        try:
            await database.init_db()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Database initialization failed: {e}")

    # Inicializar integración de Railway
    if railway_integration and hasattr(railway_integration, 'init_railway'):
        try:
            if await railway_integration.init_railway():
                if utils and hasattr(utils, 'log_event'):
                    utils.log_event("Railway integration initialized successfully")
                else:
                    print("Railway integration initialized successfully")
            else:
                if utils and hasattr(utils, 'log_event'):
                    utils.log_event("Railway integration failed to initialize")
                else:
                    print("Railway integration failed to initialize")
        except Exception as e:
            print(f"Railway integration error: {e}")

    # Start watchdog
    if watchdog_module and hasattr(watchdog_module, 'watchdog'):
        try:
            asyncio.create_task(watchdog_module.watchdog())
            print("Watchdog started")
        except Exception as e:
            print(f"Watchdog start failed: {e}")

    # Iniciar monitoreo de actividad si está habilitado
    if hasattr(settings, 'ACTIVITY_MONITORING_ENABLED') and settings.ACTIVITY_MONITORING_ENABLED:
        if activity_monitor_module and hasattr(activity_monitor_module, 'activity_monitor'):
            activity_monitor = activity_monitor_module.activity_monitor
            if hasattr(activity_monitor, 'start_monitoring'):
                try:
                    activity_monitor.start_monitoring()
                    if utils and hasattr(utils, 'log_event'):
                        utils.log_event("Activity monitoring started")
                    else:
                        print("Activity monitoring started")
                except Exception as e:
                    print(f"Activity monitoring start failed: {e}")

    # Run staging preview on startup (dry-run)
    if staging_automation and hasattr(staging_automation, 'run_preview_workflow'):
        try:
            plan = staging_automation.run_preview_workflow()
            if utils and hasattr(utils, 'log_event'):
                utils.log_event(f"Staging preview executed: {len(plan)} components")
            else:
                print(f"Staging preview executed: {len(plan)} components")
        except Exception as e:
            print(f"Staging preview failed: {e}")

# Log inicial para indicar que el backend se ha iniciado
if utils and hasattr(utils, 'log_event'):
    utils.log_event("BackendBot iniciado correctamente")
else:
    print("BackendBot iniciado correctamente")

# Para Railway/Fly.io: expone 'app' para uvicorn
# No es necesario el bloque __main__ para producción
