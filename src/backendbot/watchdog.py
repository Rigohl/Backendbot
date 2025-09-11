import psutil, time, threading
from .utils import load_memory, notify, log_event, store_watchdog_decision
from .config import settings

def _handle_process_monitoring(p, uso_alto, memory):
    """Handles the monitoring and decision-making for a single process."""
    try:
        pid, name = p.info['pid'], p.info['name']
        cpu = p.info['cpu_percent']
        ram = round(p.info['memory_info'].rss/1024/1024,2)
        acciones = memory.get(name, {"suspensiones":0,"rechazos":0})

        if cpu > settings.CPU_THRESHOLD or ram > settings.RAM_THRESHOLD:
            if pid not in uso_alto:
                uso_alto[pid] = time.time()
            elif time.time()-uso_alto[pid] > settings.CHECK_TIME:
                if acciones["suspensiones"]>=3 and acciones["rechazos"]==0:
                    try:
                        psutil.Process(pid).suspend()
                        notify(f"🔄 {name} suspendido automáticamente")
                        store_watchdog_decision(name, "suspendido", cpu, ram)
                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        log_event(f"Error al suspender {name} (PID {pid}): {e}")
                elif acciones["rechazos"]>=3:
                    log_event(f"{name} ignorado")
                    store_watchdog_decision(name, "ignorado", cpu, ram)
                else:
                    notify(f"⚠️ {name} alto consumo. Revisa dashboard.", subtle=True)
                    store_watchdog_decision(name, "notificado", cpu, ram)
                uso_alto.pop(pid, None)
        else:
            uso_alto.pop(pid, None)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        log_event(f"Error al procesar PID {p.info.get('pid', 'N/A')}: {e}")
    except Exception as e:
        log_event(f"Error inesperado en _handle_process_monitoring para PID {p.info.get('pid', 'N/A')}: {e}")

def watchdog():
    """Main watchdog function to monitor processes."""
    uso_alto = {}
    while True:
        try:
            memory = load_memory()
            for p in psutil.process_iter(['pid','name','cpu_percent','memory_info']):
                _handle_process_monitoring(p, uso_alto, memory)
            time.sleep(5)
        except Exception as e:
            log_event(f"Error en watchdog principal: {e}")
