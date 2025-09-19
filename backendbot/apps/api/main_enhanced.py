"""
BackendBot API Gateway - Versión Mejorada con API Key Bypass
============================================================

API Gateway principal que expone todos los endpoints de BackendBot.
Incluye sistema de autenticación híbrido:
- OAuth2 + JWT para usuarios normales
- API Key bypass para desarrollo y automatización

Características de seguridad mejoradas:
- Autenticación OAuth2 con JWT
- API Key bypass desde .env
- Rate limiting por IP
- CORS restrictivo
- HTTPS con certificado auto-firmado
- Logging seguro
- Solo acceso localhost

Autor: BackendBot Team
Versión: 2.0.0
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import JWTError, jwt
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backendbot.core.orchestrator import Orchestrator

# Importar routers
from .bots_router import router as bots_router
from .system_router import router as system_router
from .config_router import router as config_router
from .ui_router import router as ui_router
from .notifications_router import router as notifications_router
from .power_router import router as power_router
from .backup_router import router as backup_router


# Configuración de seguridad
SECRET_KEY = os.getenv("BACKENDBOT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("BACKENDBOT_JWT_EXPIRE_HOURS", "24")) * 60

# API Key para bypass de autenticación
MASTER_API_KEY = os.getenv("BACKENDBOT_MASTER_API_KEY")

# Configuración de rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Configuración de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Configuración de la aplicación
app = FastAPI(
    title="BackendBot API",
    description="API Gateway para BackendBot - Sistema de monitoreo y gestión inteligente",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware para verificar API Key bypass"""

    def __init__(self, app, master_api_key: str = None):
        super().__init__(app)
        self.master_api_key = master_api_key

    async def dispatch(self, request: Request, call_next):
        # Verificar API key en header
        api_key = request.headers.get("X-API-Key")

        if api_key and self.master_api_key and api_key == self.master_api_key:
            # API key válida - crear usuario bypass
            request.state.user = User(
                username="api_key_user",
                email="api@backendbot.local",
                full_name="API Key User",
                disabled=False
            )
            request.state.auth_method = "api_key"

        response = await call_next(request)
        return response


# Rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# API Key middleware (antes de autenticación)
if MASTER_API_KEY:
    app.add_middleware(APIKeyMiddleware, master_api_key=MASTER_API_KEY)

# Middleware de hosts confiables (solo localhost)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])

# Configuración CORS restrictiva
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1", "http://localhost", "https://127.0.0.1", "https://localhost"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(bots_router)
app.include_router(system_router)
app.include_router(config_router)
app.include_router(ui_router)
app.include_router(notifications_router)
app.include_router(power_router)
app.include_router(backup_router)

# Instancia del orquestador
orchestrator = Orchestrator()


@app.on_event("startup")
async def startup_event():
    orchestrator.start()


@app.on_event("shutdown")
async def shutdown_event():
    orchestrator.stop()


# Modelos de seguridad
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


# Modelos de respuesta
class HealthResponse(BaseModel):
    """Respuesta del health check."""

    status: str
    timestamp: datetime
    version: str
    uptime: str
    auth_methods: list[str]


class APIResponse(BaseModel):
    """Respuesta genérica de la API."""

    success: bool
    message: str
    data: dict = {}
    auth_method: Optional[str] = None


# Funciones de seguridad
def verify_password(plain_password, hashed_password):
    """Verificar contraseña."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Generar hash de contraseña."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token de acceso."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request, token: Optional[str] = Depends(oauth2_scheme)):
    """Obtener usuario actual con soporte para API key bypass."""
    # Verificar si ya hay usuario por API key
    if hasattr(request.state, 'user'):
        return request.state.user

    # Autenticación OAuth2 normal
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # Usuario dummy para demo (en producción usar base de datos)
    user = User(username=token_data.username, email="admin@backendbot.local")
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


# Endpoints de autenticación
@app.post("/token", response_model=Token)
@limiter.limit("5/minute")  # Rate limiting estricto para login
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """Obtener token de acceso."""
    # Usuario dummy para demo (en producción validar contra BD)
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def authenticate_user(username: str, password: str):
    """Autenticar usuario (dummy para demo)."""
    # En producción, validar contra base de datos
    default_username = os.getenv("BACKENDBOT_DEFAULT_USERNAME", "admin")
    default_password = os.getenv("BACKENDBOT_DEFAULT_PASSWORD", "backendbot_secure_2024")

    if username == default_username and password == default_password:
        return User(username=username, email="admin@backendbot.local")
    return False


# Health check endpoint (sin autenticación para monitoreo)
@app.get("/api/v1/health", response_model=HealthResponse)
@limiter.limit("10/minute")
async def health_check(request: Request):
    """
    Health check endpoint.

    Returns:
        HealthResponse: Estado del sistema
    """
    auth_methods = ["oauth2"]
    if MASTER_API_KEY:
        auth_methods.append("api_key")

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="2.0.0",
        uptime="0d 0h 0m",  # TODO: Implementar uptime real
        auth_methods=auth_methods
    )


# Root endpoint compatible con legacy y arquitectura escalable
@app.get("/")
@limiter.limit("20/minute")
async def root(request: Request, current_user: User = Depends(get_current_user)):
    """
    Endpoint raíz de la API. Compatible con legacy y arquitectura escalable.
    """
    auth_method = getattr(request.state, 'auth_method', 'oauth2')

    return {
        "message": "BackendBot API Gateway v2.0 - Welcome to BackendBot Orchestrator",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "user": current_user.username,
        "auth_method": auth_method,
        "features": [
            "API Key Bypass",
            "OAuth2 Authentication",
            "Rate Limiting",
            "HTTPS Support",
            "Localhost Only"
        ]
    }


# Endpoint para verificar autenticación
@app.get("/api/v1/auth/me")
async def read_users_me(request: Request, current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual."""
    auth_method = getattr(request.state, 'auth_method', 'oauth2')

    return {
        "user": current_user,
        "auth_method": auth_method,
        "api_key_enabled": MASTER_API_KEY is not None
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")