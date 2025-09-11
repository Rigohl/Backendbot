import time
from typing import Dict

import psutil

from .config import settings
from .utils import load_memory, log_event, notify, store_watchdog_decision


def _handle_process_monitoring(
    p: psutil.Process, uso_alto: Dict[int, float], memory: Dict[str, Dict[str, int]]
) -> None:
    """Handles the monitoring and decision-making for a single process.

    Args:
        p (psutil.Process): The process object to monitor.
        uso_alto (Dict[int, float]): A dictionary tracking processes with high resource usage.
                                     Keys are PIDs, values are timestamps when high usage started.
        memory (Dict[str, Dict[str, int]]): The loaded memory of past decisions for programs.

    """
    try:
        pid, name = p.info["pid"], p.info["name"]
        cpu = p.info["cpu_percent"]
        ram = round(p.info["memory_info"].rss / 1024 / 1024, 2)
        acciones = memory.get(name, {"suspensiones": 0, "rechazos": 0})

        if cpu > settings.CPU_THRESHOLD or ram > settings.RAM_THRESHOLD:
            if pid not in uso_alto:
                uso_alto[pid] = time.time()
            elif time.time() - uso_alto[pid] > settings.CHECK_TIME:
                if (
                    acciones["suspensiones"] >= settings.SUSPENSION_THRESHOLD
                    and acciones["rechazos"] == 0
                ):
                    try:
                        psutil.Process(pid).suspend()
                        notify(f"🔄 {name} suspendido automáticamente")
                        store_watchdog_decision(name, "suspendido", cpu, ram)
                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        log_event(f"Error al suspender {name} (PID {pid}): {e}")
                elif acciones["rechazos"] >= settings.REJECTION_THRESHOLD:
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
        log_event(
            f"Error inesperado en _handle_process_monitoring para PID {p.info.get('pid', 'N/A')}: {e}"
        )


def watchdog() -> None:
    """Main watchdog function to continuously monitor processes.

    This function runs in a loop, periodically checking all running processes
    for high CPU or RAM usage. It uses a memory system to learn from past
    decisions (suspensions or rejections) and takes automated actions like
    suspending processes or notifying the user.
    """
    uso_alto: Dict[int, float] = {}
    while True:
        try:
            memory = load_memory()
            for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
                _handle_process_monitoring(p, uso_alto, memory)
            time.sleep(5)
        except Exception as e:
            log_event(f"Error en watchdog principal: {e}")
