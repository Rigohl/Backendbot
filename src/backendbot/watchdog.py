import asyncio
import time

import psutil

from .config import settings
from .utils import load_memory, log_event, notify, store_watchdog_decision


async def _handle_process_monitoring(
    p: psutil.Process, uso_alto: dict[int, float], memory: dict[str, dict[str, int]]
) -> None:
    """Handle the monitoring and decision-making for a single process.

    Args:
        p: The process object to monitor.
        uso_alto: A dictionary tracking processes with high resource usage.
                 Keys are PIDs, values are timestamps when high usage started.
        memory: The loaded memory of past decisions for programs.
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
                        await store_watchdog_decision(
                            name, "suspendido", cpu, ram
                        )
                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        log_event(f"Error al suspender {name} (PID {pid}): {e}")
                elif acciones["rechazos"] >= settings.REJECTION_THRESHOLD:
                    log_event(f"{name} ignorado")
                    await store_watchdog_decision(name, "ignorado", cpu, ram)
                else:
                    notify(f"⚠️ {name} alto consumo. Revisa dashboard.", duration=10)
                    await store_watchdog_decision(
                        name, "notificado", cpu, ram
                    )
        else:
            if pid in uso_alto:
                del uso_alto[pid]

    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        log_event(f"Error monitoreando proceso PID {p.info.get('pid', 'N/A')}: {e}")
    except Exception as e:
        log_event(f"Error inesperado en _handle_process_monitoring para PID {p.info.get('pid', 'N/A')}: {e}")


async def watchdog() -> None:
    """Main watchdog function to continuously monitor processes.

    This function runs in a loop, periodically checking all running processes
    for high CPU or RAM usage. It uses a memory system to learn from past
    decisions (suspensions or rejections) and takes automated actions like
    suspending processes or notifying the user.
    """
    uso_alto: dict[int, float] = {}
    while True:
        try:
            memory = load_memory()
            for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
                await _handle_process_monitoring(p, uso_alto, memory)

            await asyncio.sleep(settings.CHECK_TIME)

        except Exception as e:
            log_event(f"Error en watchdog principal: {e}")
            await asyncio.sleep(settings.CHECK_TIME)
        try:
            memory = load_memory()
            for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
                await _handle_process_monitoring(p, uso_alto, memory)  # Awaited
            await asyncio.sleep(5)  # Awaited
        except Exception as e:
            log_event(f"Error en watchdog principal: {e}")
        except Exception as e:
            log_event(f"Error en watchdog principal: {e}")
