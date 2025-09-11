import os, json, time, subprocess
from win10toast import ToastNotifier
import dataset
from .config import settings

ttoaster = ToastNotifier()

# Inicializar la base de datos
db = dataset.connect(settings.DATABASE_URL)

def notify(msg, subtle=True):
    try:
        toaster.show_toast("BackendBot", msg, duration=4 if subtle else 8, threaded=True)
    except Exception as e:
        log_event(f"Error en notificación: {e}")

def log_event(msg, notify_user=False):
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    with open(settings.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    if notify_user:
        notify(msg)

def load_memory():
    if os.path.exists(settings.MEMORY_FILE):
        try:
            with open(settings.MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            log_event(f"Error: El archivo de memoria '{settings.MEMORY_FILE}' está corrupto o vacío. Se creará uno nuevo.")
            return {}
        except IOError as e:
            log_event(f"Error de E/S al cargar la memoria: {e}")
            return {}
    return {}

def save_memory(memory):
    with open(settings.MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

# --- Funciones para almacenar datos históricos ---

def store_process_data(pid: int, name: str, ram_mb: float, cpu_percent: float):
    table = db['process_history']
    table.insert(dict(timestamp=time.time(), pid=pid, name=name, ram_mb=ram_mb, cpu_percent=cpu_percent))

def store_optimization_event(freed_ram_mb: float):
    table = db['optimization_events']
    table.insert(dict(timestamp=time.time(), freed_ram_mb=freed_ram_mb))

def store_watchdog_decision(program_name: str, action: str, cpu_usage: float = None, ram_usage: float = None):
    table = db['watchdog_decisions']
    table.insert(dict(timestamp=time.time(), program_name=program_name, action=action, cpu_usage=cpu_usage, ram_usage=ram_usage))

def restore_closed_processes(modo):
    # Aquí puedes definir cómo restaurar procesos cerrados, por ejemplo, abrir apps importantes si no están corriendo
    for proc in settings.PROCESOS_IMPORTANTES:
        running = any(proc.lower() in p.info['name'].lower() for p in psutil.process_iter(['name']))
        if not running:
            try:
                subprocess.Popen(proc)
                log_event(f"Proceso restaurado: {proc}")
            except Exception as e:
                log_event(f"Error al restaurar {proc}: {e}")
