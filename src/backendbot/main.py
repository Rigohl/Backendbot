import asyncio # Added import

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as FastAPIHTTPException # Alias to avoid conflict

from .api_routes import router
from .config import Settings
from .utils import log_event, init_db # Added init_db
from .watchdog import watchdog # Moved import here
from .exceptions import ServiceException, InternalServerErrorException # Import custom exceptions

settings = Settings()

app = FastAPI(
    title="BackendBot Pro", description="Monitoreo + Automatización + Dashboard"
)

app.include_router(router)

@app.on_event("startup")
async def on_startup():
    await init_db()
    asyncio.create_task(watchdog()) # Start watchdog as an asyncio task

# Global Exception Handlers
@app.exception_handler(ServiceException)
async def service_exception_handler(request: Request, exc: ServiceException):
    """Handles custom ServiceException and returns a standardized JSON response."""
    log_event(f"ServiceException caught: {exc.code} - {exc.detail}", notify_user=False)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.detail,
        },
    )

@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    """Handles FastAPI's HTTPException and returns a standardized JSON response."""
    log_event(f"HTTPException caught: {exc.status_code} - {exc.detail}", notify_user=False)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": "HTTP_ERROR", # Generic code for standard HTTP errors
            "message": exc.detail,
        },
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handles any unhandled exceptions and returns a generic 500 error."""
    log_event(f"Unhandled exception caught: {exc}", notify_user=True) # Notify user for unhandled errors
    internal_error = InternalServerErrorException()
    return JSONResponse(
        status_code=internal_error.status_code,
        content={
            "code": internal_error.code,
            "message": internal_error.detail,
        },
    )

# Log inicial para indicar que el backend se ha iniciado
log_event("🚀 BackendBot iniciado correctamente")

# Para Railway/Fly.io: expone 'app' para uvicorn
# No es necesario el bloque __main__ para producción
