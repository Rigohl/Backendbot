from fastapi import FastAPI
import psutil, subprocess, threading, time, os, json
from .config import Settings
from .utils import notify, log_event, load_memory, save_memory
from .api_routes import router

settings = Settings()

app = FastAPI(title="BackendBot Pro", description="Monitoreo + Automatización + Dashboard")

app.include_router(router)

from .watchdog import watchdog

threading.Thread(target=watchdog, daemon=True).start()

# === Auto-run oculto si se usa pythonw ===
if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run("src.backendbot.main:app", host="127.0.0.1", port=8000, log_level="info")
    except Exception as e:
        log_event(f"Error al iniciar backend: {e}")
