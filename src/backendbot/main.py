import asyncio  # Added import

from fastapi import FastAPI

from .api_routes import router
from .config import Settings
from .utils import init_db, log_event  # Added init_db
from .watchdog import watchdog  # Moved import here
from .routers import tasks_routes
from .staging_automation import run_preview_workflow  # Added staging import

settings = Settings()

app = FastAPI(
    title="BackendBot Pro", description="Monitoreo + Automatización + Dashboard"
)

app.include_router(router)
app.include_router(tasks_routes.router, prefix="/celery", tags=["celery"])


@app.on_event("startup")
async def on_startup():
    await init_db()
    asyncio.create_task(watchdog())  # Start watchdog as an asyncio task
    # Run staging preview on startup (dry-run)
    plan = run_preview_workflow()
    log_event(f"Staging preview executed: {len(plan)} components")


# Log inicial para indicar que el backend se ha iniciado
log_event("🚀 BackendBot iniciado correctamente")

# Para Railway/Fly.io: expone 'app' para uvicorn
# No es necesario el bloque __main__ para producción
