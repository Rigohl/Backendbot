# BackendBot - Guía de Acceso Directo con API Key
# ================================================
#
# Esta guía explica cómo usar el acceso directo con API key
# para interactuar con BackendBot sin necesidad de autenticación OAuth2.
#
# El acceso directo es ideal para:
# - Scripts de automatización
# - Integraciones con otros sistemas
# - Desarrollo y testing
# - Tareas programadas
#

## 📋 Requisitos Previos

### 1. API Key Configurada
Asegúrate de que tienes la API key configurada en tu archivo `.env`:

```bash
# En tu archivo .env
BACKENDBOT_MASTER_API_KEY=bb_master_2024_secure_key_local_only_48732
```

### 2. BackendBot Ejecutándose
```bash
# Iniciar API con HTTPS
python api_server.py --https

# O usar el servicio
api_service.bat start
```

### 3. Dependencias Instaladas
```bash
pip install requests python-dotenv
```

## 🚀 Uso Básico

### Cliente CLI
```bash
# Ver ayuda
python api_client.py --help

# Estado del sistema
python api_client.py system status

# Ejecutar bot
python api_client.py bot execute organizer scan --path "C:\Downloads"

# Crear backup
python api_client.py backup create daily_backup --strategy incremental

# Enviar notificación
python api_client.py notification send "Mensaje" --priority info --channels desktop
```

### Uso Programático
```python
from api_client import BackendBotAPIClient

# Crear cliente (carga API key automáticamente de .env)
client = BackendBotAPIClient()

# Health check
result = client.health_check()
print(f"Estado: {result['status']}")

# Estado del sistema
status = client.get_system_status()
print(f"CPU: {status['cpu_percent']}%")

# Ejecutar bot
result = client.execute_bot("organizer", "scan", path="/downloads")
print(f"Archivos procesados: {result['files_processed']}")
```

## 📚 Ejemplos Avanzados

### Automatización Diaria
```python
import schedule
from api_client import BackendBotAPIClient

client = BackendBotAPIClient()

def daily_tasks():
    # Backup diario
    client.create_backup("daily_backup", "incremental")

    # Organizar descargas
    client.execute_bot("organizer", "scan", path="~/Downloads")

    # Notificación de completado
    client.send_notification(
        "Tareas diarias completadas",
        priority="info",
        channels=["desktop"]
    )

# Programar para las 2 AM
schedule.every().day.at("02:00").do(daily_tasks)
```

### Monitoreo Continuo
```python
import time
from api_client import BackendBotAPIClient

client = BackendBotAPIClient()

def monitor_system():
    try:
        status = client.get_system_status()

        # Alertas de CPU alta
        if status['cpu_percent'] > 80:
            client.send_notification(
                f"CPU alta: {status['cpu_percent']}%",
                priority="warning",
                channels=["desktop", "email"]
            )

        # Alertas de memoria baja
        if status['memory_percent'] > 90:
            client.send_notification(
                f"Memoria baja: {status['memory_percent']}%",
                priority="high",
                channels=["desktop"]
            )

    except Exception as e:
        print(f"Error en monitoreo: {e}")

# Monitorear cada 5 minutos
while True:
    monitor_system()
    time.sleep(300)
```

### Integración con Dashboards
```python
from api_client import BackendBotAPIClient
import json

client = BackendBotAPIClient()

def get_dashboard_data():
    """Obtener datos para dashboard externo"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "health": client.health_check(),
        "system": client.get_system_status(),
        "bots": client.get_bots_status()
    }

    # Guardar en archivo JSON para dashboard
    with open('backendbot_dashboard.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)

    return data

# Actualizar cada minuto
import time
while True:
    dashboard_data = get_dashboard_data()
    print("Dashboard actualizado")
    time.sleep(60)
```

## 🔧 Configuración Avanzada

### Configuración Personalizada
```python
from api_client import BackendBotAPIClient

# Configuración personalizada
config = {
    "base_url": "https://localhost:8443",
    "timeout": 30,
    "verify_ssl": True,
    "retry_attempts": 3
}

client = BackendBotAPIClient(
    api_key="tu_api_key_aqui",
    config=config
)
```

### Manejo de Errores
```python
from api_client import BackendBotAPIClient
from requests.exceptions import RequestException, Timeout

client = BackendBotAPIClient()

def safe_api_call(func, *args, **kwargs):
    """Llamada segura a API con manejo de errores"""
    try:
        return func(*args, **kwargs)
    except Timeout:
        print("Timeout en la conexión")
        return None
    except RequestException as e:
        print(f"Error de conexión: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

# Uso
result = safe_api_call(client.health_check)
if result:
    print("API funcionando correctamente")
```

## 📊 Endpoints Disponibles

### Sistema
- `GET /health` - Health check
- `GET /system/status` - Estado completo del sistema

### Bots
- `GET /bots/status` - Estado de todos los bots
- `POST /bots/{bot_name}/execute` - Ejecutar bot específico

### Backup
- `POST /backup/create` - Crear backup
- `GET /backup/list` - Listar backups
- `POST /backup/restore` - Restaurar backup

### Notificaciones
- `POST /notification/send` - Enviar notificación

### Energía
- `POST /power/profile` - Cambiar perfil de energía
- `GET /power/status` - Estado de energía

### Logs
- `GET /logs` - Obtener logs del sistema

## 🔒 Seguridad

### Mejores Prácticas
1. **Nunca expongas la API key** en logs o código público
2. **Usa HTTPS siempre** para conexiones seguras
3. **Limita el acceso** solo a localhost (127.0.0.1)
4. **Implementa rate limiting** en tus scripts
5. **Valida respuestas** antes de procesarlas

### Variables de Entorno
```bash
# Configuración segura
BACKENDBOT_MASTER_API_KEY=tu_clave_segura_aqui
BACKENDBOT_API_HOST=127.0.0.1
BACKENDBOT_API_PORT=8443
BACKENDBOT_SSL_VERIFY=true
```

## 🎯 Casos de Uso Comunes

### 1. Scripts de Mantenimiento
```bash
#!/bin/bash
# mantenimiento.sh

echo "Iniciando mantenimiento del sistema..."

# Usar Python para llamar a BackendBot
python -c "
from api_client import BackendBotAPIClient
client = BackendBotAPIClient()
client.execute_bot('organizer', 'scan', path='/home/user/Downloads')
client.create_backup('maintenance_backup', 'incremental')
print('Mantenimiento completado')
"

echo "Mantenimiento finalizado"
```

### 2. Monitoreo con Nagios/Icinga
```python
# nagios_check_backendbot.py
from api_client import BackendBotAPIClient

def check_backendbot():
    client = BackendBotAPIClient()

    try:
        health = client.health_check()
        if health['status'] == 'healthy':
            print("OK - BackendBot funcionando correctamente")
            return 0
        else:
            print("WARNING - BackendBot con problemas")
            return 1
    except Exception as e:
        print(f"CRITICAL - Error conectando a BackendBot: {e}")
        return 2

if __name__ == "__main__":
    exit(check_backendbot())
```

### 3. Integración con Jenkins/GitLab CI
```yaml
# .gitlab-ci.yml
stages:
  - test
  - deploy

test:
  script:
    - python -c "
from api_client import BackendBotAPIClient
client = BackendBotAPIClient()
result = client.execute_bot('auditor_files', 'scan')
print(f'Auditoría completada: {result}')
"

deploy:
  script:
    - python -c "
from api_client import BackendBotAPIClient
client = BackendBotAPIClient()
client.create_backup('pre_deploy_backup', 'full')
print('Backup pre-deploy creado')
"
```

## 🐛 Solución de Problemas

### Error: API Key no encontrada
```bash
# Verificar que existe en .env
cat .env | grep BACKENDBOT_MASTER_API_KEY

# Si no existe, añadirla
echo "BACKENDBOT_MASTER_API_KEY=bb_master_2024_secure_key_local_only_48732" >> .env
```

### Error: Conexión rechazada
```bash
# Verificar que BackendBot esté ejecutándose
curl -k https://localhost:8443/health

# Si no responde, iniciar el servicio
api_service.bat start
```

### Error: SSL Certificate
```bash
# Para desarrollo, deshabilitar verificación SSL
export BACKENDBOT_SSL_VERIFY=false

# O en código
client = BackendBotAPIClient(verify_ssl=False)
```

### Error: Timeout
```bash
# Aumentar timeout
export BACKENDBOT_API_TIMEOUT=60

# O en código
client = BackendBotAPIClient(timeout=60)
```

## 📞 Soporte

Para más información:
- Consulta `api_client.py` para ver todos los métodos disponibles
- Revisa `ejemplos_api_key.py` para casos de uso prácticos
- Lee `integracion_sistemas_externos.py` para integraciones avanzadas
- Consulta la documentación completa en `docs/API_DOCUMENTATION.md`

---

**¡El acceso directo con API key hace que BackendBot sea perfecto para automatización y integración!** 🚀