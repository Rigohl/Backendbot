from fastapi import APIRouter
from .routers.history_routes import router as history_router
from .routers.modes_routes import router as modes_router

router = APIRouter()

router.include_router(history_router, prefix="/history", tags=["History"])
router.include_router(modes_router, prefix="/modes", tags=["Modes"])
