# Backendbot

Backendbot es una API construida con FastAPI para monitoreo y control de procesos, con funcionalidades avanzadas de health checks, logs y métricas.

## Características
- API REST con FastAPI
- Despliegue automático en Railway
- Estructura modular y buenas prácticas
- Autenticación básica HTTP
- Logging estructurado
- Rate limiting
- CORS configurado
- Validación con Pydantic
- Pruebas unitarias
- Información del sistema

## Instalación
```bash
pip install -r requirements.txt
```

## Configuración
Copia `.env.example` a `.env` y configura las variables de entorno:

```bash
cp .env.example .env
```

Variables importantes:
- `BACKENDBOT_USERNAME`: Usuario para autenticación básica
- `BACKENDBOT_PASSWORD`: Contraseña para autenticación básica
- `RATE_LIMIT_REQUESTS`: Número máximo de solicitudes por ventana
- `CORS_ORIGINS`: Orígenes permitidos para CORS

## Ejecución local
```bash
uvicorn main:app --reload
```

## Endpoints
- `GET /` : Verifica el estado del backend (requiere autenticación básica)
- `GET /system` : Obtiene información del sistema (CPU, memoria, disco)
- `GET /health` : Health check detallado con uptime y métricas del sistema
- `GET /logs` : Obtiene logs recientes del sistema
- `GET /processes/top` : Lista procesos top por uso de CPU o memoria
- `GET /config` : Obtiene configuración actual del backend
- `GET /alerts` : Obtiene alertas activas del sistema
- `GET /alerts/config` : Obtiene configuración de alertas
- `PUT /alerts/config` : Actualiza configuración de alertas
- `GET /metrics/history` : Obtiene historial de métricas del sistema
- `DELETE /alerts` : Limpia historial de alertas
- `GET /docs` : Documentación interactiva de la API

## Autenticación
Usa autenticación básica HTTP con credenciales configuradas en variables de entorno.

## Pruebas
```bash
pytest tests/
```

## Despliegue
Compatible con Railway, Render, Fly.io. El despliegue automático está configurado con GitHub Actions.

## Seguridad
- Autenticación básica HTTP
- Rate limiting (100 requests/min por defecto)
- CORS configurado
- Validación de inputs con Pydantic
- Logging de seguridad

## Base de datos
- Listo para integración con PostgreSQL/Neon
- Configurable via `DATABASE_URL`

## Licencia
MIT