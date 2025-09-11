import asyncio
import time

import psutil

try:
    from .config import settings
    from .utils import load_memory, log_event, notify, store_watchdog_decision
except ImportError:
    # Fallback for when running from tests
    from config import settings
    from utils import load_memory, log_event, notify, store_watchdog_decision


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
        pid = p.pid
        name = p.name()
        cpu = p.cpu_percent()
        ram = round(p.memory_info().rss / 1024 / 1024, 2)
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
                    notify(f"⚠️ {name} alto consumo. Revisa dashboard.") # Removed duration
                    await store_watchdog_decision(
                        name, "notificado", cpu, ram
                    )
        else:
            if pid in uso_alto:
                del uso_alto[pid]

    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        log_event(f"Error monitoreando proceso PID {p.pid}: {e}")
    except Exception as e:
        log_event(f"Error inesperado en _handle_process_monitoring para PID {p.pid}: {e}")


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
            memory = await load_memory() # Await the call
            for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
                await _handle_process_monitoring(p, uso_alto, memory)

            await asyncio.sleep(settings.CHECK_TIME)

        except Exception as e:
            log_event(f"Error en watchdog principal: {e}", level="error") # Explicitly set level
            await asyncio.sleep(settings.CHECK_TIME) # Continue after error

