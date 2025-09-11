
from fastapi import APIRouter
from celery.result import AsyncResult
from src.backendbot.tasks import add, get_ram_usage, get_detailed_ram_info

router = APIRouter()

@router.post("/tasks/add")
def run_add_task(x: int, y: int):
    """Runs the add task."""
    task = add.delay(x, y)
    return {"task_id": task.id}

@router.post("/tasks/ram_usage")
def run_ram_usage_task():
    """Runs the get_ram_usage task."""
    task = get_ram_usage.delay()
    return {"task_id": task.id}

@router.post("/tasks/detailed_ram_info")
def run_detailed_ram_info_task():
    """Runs the get_detailed_ram_info task."""
    task = get_detailed_ram_info.delay()
    return {"task_id": task.id}

@router.get("/tasks/status/{task_id}")
def get_task_status(task_id: str):
    """Gets the status of a task."""
    task_result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }
