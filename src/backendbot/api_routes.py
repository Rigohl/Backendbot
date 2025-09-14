from fastapi import APIRouter
from .routers.history_routes import router as history_router

router = APIRouter()

router.include_router(history_router, prefix="/history", tags=["History"])
