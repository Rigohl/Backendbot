# 📡 API REST de BackendBot

## 📋 Descripción General

La API REST de BackendBot proporciona endpoints para integraciones externas, automatización y control remoto del sistema. Está construida con **FastAPI** y ofrece documentación automática en `/docs`.

- **Base URL**: `http://localhost:8000`
- **Autenticación**: Ninguna (API local)
- **Formato**: JSON
- **Version**: 2.0.0

## 🚀 Inicio Rápido

### Ejecutar el Servidor API
```bash
# Desde el directorio raíz del proyecto
python api_server.py --host 127.0.0.1 --port 8000
```

### Acceder a la Documentación Interactiva
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📚 Endpoints Principales

### 🔍 Información del Sistema

#### `GET /`
**Descripción**: Endpoint raíz con información básica de la API.

**Respuesta**:
```json
{
  "message": "BackendBot API",
  "version": "2.0.0",
  "status": "running",
  "endpoints": [
    "/status",
    "/bots",
    "/backup",
    "/power",
    "/notifications",
    "/webhooks"
  ]
}
```

#### `GET /status`
**Descripción**: Obtiene el estado actual del sistema (CPU, RAM, disco, batería).

**Respuesta**:
```json
{
  "cpu_percent": 45.2,
  "memory_percent": 67.8,
  "disk_percent": 54.3,
  "battery_percent": 85.0,
  "temperature": null,
  "active_bots": ["monitor", "guardian"],
  "uptime": "2 days, 5:30:15"
}
```

### 🤖 Gestión de Bots

#### `GET /bots`
**Descripción**: Obtiene el estado de todos los bots del sistema.

**Respuesta**:
```json
{
  "bots": [
    {
      "name": "monitor",
      "status": "running",
      "last_activity": "2024-01-15T10:30:00"
    },
    {
      "name": "organizer",
      "status": "idle",
      "last_activity": "2024-01-15T09:45:00"
    }
  ]
}
```

#### `POST /bots/command`
**Descripción**: Ejecuta un comando específico en un bot.

**Cuerpo de la solicitud**:
```json
{
  "bot_name": "monitor",
  "action": "start_monitoring",
  "parameters": {
    "interval": 30,
    "threshold": 80
  }
}
```

**Respuesta**:
```json
{
  "status": "executed",
  "action": "start_monitoring",
  "result": "success"
}
```

### 💾 Sistema de Backup

#### `POST /backup`
**Descripción**: Crea un backup del sistema o archivos específicos.

**Cuerpo de la solicitud**:
```json
{
  "job_name": "daily_backup",
  "async_execution": true
}
```

**Respuesta (síncrona)**:
```json
{
  "status": "completed",
  "job_name": "daily_backup",
  "files_processed": 150,
  "size_mb": 45.2,
  "duration_seconds": 2
}
```

**Respuesta (asíncrona)**:
```json
{
  "status": "accepted",
  "message": "Backup iniciado en segundo plano"
}
```

### ⚡ Gestión de Energía

#### `POST /power/profile`
**Descripción**: Cambia el perfil de energía del sistema.

**Cuerpo de la solicitud**:
```json
{
  "profile": "balanced"
}
```

**Perfiles disponibles**:
- `high_performance`: Máximo rendimiento
- `balanced`: Equilibrio entre rendimiento y energía
- `power_saver`: Ahorro de energía máximo
- `ultra_low`: Modo ultra bajo consumo

**Respuesta**:
```json
{
  "status": "applied",
  "profile": "balanced"
}
```

### 🔔 Sistema de Notificaciones

#### `POST /notifications`
**Descripción**: Envía una notificación a través de múltiples canales.

**Cuerpo de la solicitud**:
```json
{
  "message": "Sistema optimizado correctamente",
  "priority": "info",
  "channels": ["desktop", "email"]
}
```

**Prioridades disponibles**:
- `info`: Información general
- `warning`: Advertencia
- `error`: Error
- `critical`: Crítico

**Canales disponibles**:
- `desktop`: Notificación de escritorio
- `email`: Correo electrónico
- `sound`: Alerta sonora

**Respuesta**:
```json
{
  "status": "sent",
  "message": "Sistema optimizado correctamente",
  "priority": "info",
  "channels": ["desktop", "email"]
}
```

### 🔗 Webhooks

#### `GET /webhooks`
**Descripción**: Obtiene todos los webhooks configurados.

**Respuesta**:
```json
{
  "webhooks": [
    {
      "url": "https://example.com/webhook",
      "events": ["bot_command", "backup_completed"],
      "enabled": true
    }
  ]
}
```

#### `POST /webhooks`
**Descripción**: Registra un nuevo webhook para eventos del sistema.

**Cuerpo de la solicitud**:
```json
{
  "url": "https://example.com/webhook",
  "events": ["bot_command", "backup_completed", "system_alert"],
  "enabled": true
}
```

**Eventos disponibles**:
- `bot_command`: Cuando se ejecuta un comando en un bot
- `backup_completed`: Cuando se completa un backup
- `system_alert`: Alertas del sistema
- `power_profile_changed`: Cambio de perfil de energía

**Respuesta**:
```json
{
  "status": "registered",
  "id": "webhook_0"
}
```

#### `DELETE /webhooks/{webhook_id}`
**Descripción**: Elimina un webhook específico.

**Respuesta**:
```json
{
  "status": "removed"
}
```

## 📖 Ejemplos de Uso

### Monitoreo Continuo
```python
import requests
import time

def monitor_system():
    while True:
        response = requests.get("http://localhost:8000/status")
        status = response.json()
        
        if status["cpu_percent"] > 90:
            # Enviar alerta
            requests.post("http://localhost:8000/notifications", json={
                "message": f"CPU alto: {status['cpu_percent']}%",
                "priority": "warning",
                "channels": ["desktop"]
            })
        
        time.sleep(60)

monitor_system()
```

### Backup Automático
```python
import requests
from datetime import datetime

def daily_backup():
    job_name = f"backup_{datetime.now().strftime('%Y%m%d')}"
    
    response = requests.post("http://localhost:8000/backup", json={
        "job_name": job_name,
        "async_execution": True
    })
    
    print(f"Backup iniciado: {response.json()}")

daily_backup()
```

### Integración con Webhook
```python
import requests

def setup_webhook():
    webhook_config = {
        "url": "https://myapp.com/backendbot-events",
        "events": ["bot_command", "backup_completed"],
        "enabled": True
    }
    
    response = requests.post("http://localhost:8000/webhooks", json=webhook_config)
    print(f"Webhook registrado: {response.json()}")

setup_webhook()
```

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Puerto personalizado
export BACKENDBOT_API_PORT=8080

# Host personalizado
export BACKENDBOT_API_HOST=0.0.0.0
```

### Configuración CORS
La API incluye configuración CORS para integraciones web. En producción, limita los orígenes permitidos en `api_server.py`.

## 📊 Monitoreo y Logs

Los logs de la API se integran con el sistema de logging de BackendBot. Revisa los logs en:
- `logs/backendbot_api.log`
- Panel de control de BackendBot

## 🚨 Manejo de Errores

### Códigos de Error Comunes
- `400 Bad Request`: Datos inválidos en la solicitud
- `404 Not Found`: Endpoint o recurso no encontrado
- `500 Internal Server Error`: Error interno del servidor

### Respuesta de Error
```json
{
  "detail": "Descripción del error"
}
```

## 🔐 Seguridad

- **Uso Local**: La API está diseñada para uso local únicamente
- **Sin Autenticación**: No requiere credenciales (por diseño)
- **CORS Configurado**: Permite integraciones web controladas
- **Validación**: Todos los inputs se validan con Pydantic

## 📈 Próximas Funcionalidades

- Autenticación JWT para acceso remoto seguro
- Rate limiting para protección contra abuso
- Métricas detalladas de rendimiento
- Integración con bases de datos externas
- WebSockets para actualizaciones en tiempo real</content>
<parameter name="filePath">c:\Users\DELL\Desktop\BackendBot\docs\API_DOCUMENTATION.md