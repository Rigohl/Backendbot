from fastapi import APIRouter, Depends, HTTPException, status
import psutil, os, time, subprocess
from datetime import datetime
from .config import settings
from .utils import log_event, notify, load_memory, save_memory, store_process_data, store_optimization_event, db, restore_closed_processes # <-- Import restore_closed_processes

router = APIRouter()

# Dependency to check API Key
def get_api_key(api_key: str = Depends(HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"))):
    if api_key == settings.API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")

def _get_process_info(p):
    """Helper to get process info and handle common errors."""
    try:
        pid, name = p.info['pid'], p.info['name']
        ram_mb = round(p.info['memory_info'].rss/1024/1024,2)
        cpu_percent = p.info['cpu_percent'](interval=0.1)
        store_process_data(pid, name, ram_mb, cpu_percent)
        return {
            "pid": pid,
            "name": name,
            "ram_mb": ram_mb,
            "cpu_percent": cpu_percent
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        log_event(f"Error al procesar PID {p.info.get('pid', 'N/A')}: {e}")
        return None
    except Exception as e:
        log_event(f"Error inesperado al obtener info de proceso: {e}")
        return None

@router.get("/procesos", dependencies=[Depends(get_api_key)])
def listar():
    out = []
    for p in psutil.process_iter(['pid','name','memory_info','cpu_percent']):
        info = _get_process_info(p)
        if info:
            out.append(info)
    return out

@router.post("/apagar/{pid}", dependencies=[Depends(get_api_key)])
def apagar(pid: int):
    try:
        psutil.Process(pid).terminate()
        log_event(f"Proceso terminado PID {pid}", notify_user=True)
        return {"status":"ok"}
    except psutil.NoSuchProcess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Proceso PID {pid} no encontrado.")
    except psutil.AccessDenied:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Acceso denegado para terminar PID {pid}.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error inesperado al apagar proceso: {e}")

@router.post("/resume/{pid}", dependencies=[Depends(get_api_key)])
def resume(pid: int):
    try:
        psutil.Process(pid).resume()
        log_event(f"Proceso reanudado PID {pid}", notify_user=True)
        return {"status":"ok"}
    except psutil.NoSuchProcess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Proceso PID {pid} no encontrado.")
    except psutil.AccessDenied:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Acceso denegado para reanudar PID {pid}.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error inesperado al reanudar proceso: {e}")

@router.post("/kill/{pid}", dependencies=[Depends(get_api_key)])
def kill(pid: int):
    try:
        psutil.Process(pid).kill()
        log_event(f"Proceso terminado (kill) PID {pid}", notify_user=True)
        return {"status":"ok"}
    except psutil.NoSuchProcess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Proceso PID {pid} no encontrado.")
    except psutil.AccessDenied:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Acceso denegado para terminar (kill) PID {pid}.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error inesperado al terminar (kill) proceso: {e}")

def _optimize_processes():
    """Helper to suspend hibernatable processes."""
    freed = 0
    for p in psutil.process_iter(['pid','name','memory_info']):
        try:
            if p.info['name'] in settings.HIBERNABLES:
                psutil.Process(p.info['pid']).suspend()
                freed += p.info['memory_info'].rss
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            log_event(f"Error al suspender proceso {p.info.get('name', 'N/A')} (PID {p.info.get('pid', 'N/A')}): {e}")
        except Exception as e:
            log_event(f"Error inesperado al optimizar proceso: {e}")
    return freed

@router.post("/optimize", dependencies=[Depends(get_api_key)])
def optimize():
    freed = _optimize_processes()
    msg = f"Optimización automática: {round(freed/1024/1024,1)} MB liberados"
    log_event(msg, notify_user=True)
    store_optimization_event(round(freed/1024/1024,1))
    return {"status":"ok","ram_liberada_mb":round(freed/1024/1024,1)}

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

@router.post("/set-modo/{modo}", dependencies=[Depends(get_api_key)])
def set_modo(modo: str):
    if modo not in settings.PROCESOS_A_CERRAR:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Modo no válido")
    closed = []
    for p in psutil.process_iter(['pid','name']):
        try:
            name = p.info['name']
            if name.lower() in [proc.lower() for proc in settings.PROCESOS_A_CERRAR[modo]] and name.lower() not in [imp.lower() for imp in settings.PROCESOS_IMPORTANTES]:
                psutil.Process(p.info['pid']).terminate()
                closed.append(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            log_event(f"Error al procesar PID {p.info.get('pid', 'N/A')} en set-modo: {e}")
        except Exception as e:
            log_event(f"Error inesperado en set-modo: {e}")
    log_event(f"Modo {modo} activado, procesos cerrados: {closed}", notify_user=True)
    return {"status": "ok", "modo": modo, "procesos_cerrados": closed}

@router.post("/restore-important", dependencies=[Depends(get_api_key)])
def restore_important():
    restore_closed_processes(settings.MODO)
    return {"status": "ok"}
