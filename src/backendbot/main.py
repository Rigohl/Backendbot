import asyncio  # Added import
import time
from collections import defaultdict
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api_routes import router
from .config import Settings
from .database import init_db
from .utils import log_event
from .watchdog import watchdog  # Moved import here
from .routers import tasks_routes
from .staging_automation import run_preview_workflow  # Added staging import

settings = Settings()

app = FastAPI(
    title="BackendBot Pro", description="Monitoreo + Automatización + Dashboard"
)

app.include_router(router)
app.include_router(tasks_routes.router, prefix="/celery", tags=["celery"])

# Rate limiting simple
rate_limit_store = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Middleware para rate limiting."""
    # Para pruebas, usar una IP fija
    client_ip = getattr(request.client, 'host', None) if request.client else "test_client"
    if not client_ip or client_ip == "testserver":  # En pruebas FastAPI usa "testserver"
        client_ip = "test_client"
    
    now = time.time()
    
    # Limpiar requests antiguos (fuera de la ventana)
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip]
        if now - req_time < settings.RATE_LIMIT_WINDOW
    ]
    
    # Verificar límite
    if len(rate_limit_store[client_ip]) >= settings.RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )
    
    # Agregar timestamp actual
    rate_limit_store[client_ip].append(now)
    
    # Continuar con la solicitud
    return await call_next(request)

@app.get("/")
async def root():
    """Endpoint raíz para verificar que el backend está funcionando."""
    return {"message": "BackendBot is running", "status": "ok"}

@app.on_event("startup")
async def on_startup():
    await init_db()
    asyncio.create_task(watchdog())  # Start watchdog as an asyncio task
    # Run staging preview on startup (dry-run)
    plan = run_preview_workflow()
    log_event(f"Staging preview executed: {len(plan)} components")


# Log inicial para indicar que el backend se ha iniciado
log_event("BackendBot iniciado correctamente")

# Para Railway/Fly.io: expone 'app' para uvicorn
# No es necesario el bloque __main__ para producción
