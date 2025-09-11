
import psutil
from .celery_app import celery_app

@celery_app.task
def add(x, y):
    """A simple task to add two numbers."""
    return x + y

@celery_app.task
def get_ram_usage():
    """Returns the current RAM usage as a dictionary."""
    memory = psutil.virtual_memory()
    return {
        "total": memory.total,
        "available": memory.available,
        "percent": memory.percent,
        "used": memory.used,
        "free": memory.free,
    }

@celery_app.task
def get_detailed_ram_info():
    """Returns detailed RAM information."""
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "virtual_memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free,
            "active": memory.active,
            "inactive": memory.inactive,
            "buffers": memory.buffers,
            "cached": memory.cached,
            "shared": memory.shared,
            "slab": memory.slab,
        },
        "swap_memory": {
            "total": swap.total,
            "used": swap.used,
            "free": swap.free,
            "percent": swap.percent,
            "sin": swap.sin,
            "sout": swap.sout,
        },
    }
