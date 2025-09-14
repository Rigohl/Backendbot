from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from src.backendbot.main import templates
from src.backendbot.utils.logging_config import logger

router = APIRouter(
    tags=["Dashboard"],
)

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    logger.info("Acceso al endpoint del dashboard.")
    return templates.TemplateResponse("index.html", {"request": request})