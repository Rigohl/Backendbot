import threading

from fastapi import FastAPI

from .api_routes import router
from .config import Settings

settings = Settings()

app = FastAPI(
    title="BackendBot Pro", description="Monitoreo + Automatización + Dashboard"
)

app.include_router(router)

from .watchdog import watchdog

threading.Thread(target=watchdog, daemon=True).start()

# Para Railway/Fly.io: expone 'app' para uvicorn
# No es necesario el bloque __main__ para producción
