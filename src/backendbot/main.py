import asyncio # Added import

from fastapi import FastAPI

from .api_routes import router
from .config import Settings
from .utils import log_event, init_db # Added init_db
from .watchdog import watchdog # Moved import here

settings = Settings()

app = FastAPI(
    title="BackendBot Pro", description="Monitoreo + Automatización + Dashboard"
)

app.include_router(router)

@app.on_event("startup")
async def on_startup():
    await init_db()
    asyncio.create_task(watchdog()) # Start watchdog as an asyncio task

# Log inicial para indicar que el backend se ha iniciado
log_event("🚀 BackendBot iniciado correctamente")

# Para Railway/Fly.io: expone 'app' para uvicorn
# No es necesario el bloque __main__ para producción
