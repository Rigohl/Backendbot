from fastapi import APIRouter, Depends, HTTPException, status
import psutil, os, time, subprocess
from datetime import datetime
from .config import settings
from .utils import log_event, notify, load_memory, save_memory, db # Removed store_process_data, store_optimization_event, restore_closed_processes
from .process_routes import process_router # New import

router = APIRouter()

# Dependency to check API Key
def get_api_key(api_key: str = Depends(HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"))):
    if api_key == settings.API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")

router.include_router(process_router) # Include the new router

@router.post("/decision/{programa}/{accion}", dependencies=[Depends(get_api_key)])
def guardar_decision(programa: str, accion: str):
    memory = load_memory()
    memory.setdefault(programa, {"suspensiones":0,"rechazos":0})
    if accion == "suspender": memory[programa]["suspensiones"] += 1
    elif accion == "rechazar": memory[programa]["rechazos"] += 1
    save_memory(memory)
    return memory.get(programa)

@router.get("/memoria", dependencies=[Depends(get_api_key)])
def ver_memoria():
    return load_memory()

@router.post("/reset-memoria", dependencies=[Depends(get_api_key)])
def reset_memoria():
    save_memory({})
    log_event("🧹 Memoria de decisiones reseteada", notify_user=True)
    return {"status":"ok","msg":"Memoria reiniciada"}

# === Autodiagnóstico (/self) ===
_app_start = time.time()

@router.get("/self", dependencies=[Depends(get_api_key)])
def self_metrics():
    try:
        p = psutil.Process(os.getpid())
        mem = p.memory_info()
        privados = getattr(mem, "private", None)
        privados_mb = None
        if privados is not None:
            privados_mb = round(privados/1024/1024, 2)
        return {
            "pid": p.pid,
            "ram_mb": round(mem.rss/1024/1024, 2),
            "privados_mb": privados_mb,
            "num_threads": p.num_threads(),
            "cpu_percent": p.cpu_percent(interval=0.1),
            "uptime_sec": round(time.time() - _app_start, 1),
            "started_at": datetime.fromtimestamp(_app_start).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener métricas de autodiagnóstico: {e}")

# --- Endpoints para datos históricos ---

@router.get("/history/processes", dependencies=[Depends(get_api_key)])
def get_process_history(limit: int = 100, offset: int = 0):
    table = db['process_history']
    return list(table.find(order_by='-timestamp', limit=limit, offset=offset))

@router.get("/history/optimizations", dependencies=[Depends(get_api_key)])
def get_optimization_history(limit: int = 100, offset: int = 0):
    table = db['optimization_events']
    return list(table.find(order_by='-timestamp', limit=limit, offset=offset))

@router.get("/history/decisions", dependencies=[Depends(get_api_key)])
def get_decision_history(limit: int = 100, offset: int = 0):
    table = db['watchdog_decisions']
    return list(table.find(order_by='-timestamp', limit=limit, offset=offset))

@router.get("/get-modo", dependencies=[Depends(get_api_key)])
def get_modo():
    return {"modo": settings.MODO}
