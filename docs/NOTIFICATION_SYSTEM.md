# 🔔 Sistema de Notificaciones Inteligente

## 📋 Descripción General

El Sistema de Notificaciones Inteligente de BackendBot proporciona un marco completo para enviar notificaciones a través de múltiples canales con reglas inteligentes, historial completo y sistema de cooldown para evitar spam.

## 🚀 Características Principales

- **Múltiples Canales**: Desktop, email, sonido y webhooks
- **Reglas Inteligentes**: Notificaciones basadas en condiciones del sistema
- **Historial Completo**: Seguimiento de todas las notificaciones enviadas
- **Sistema de Cooldown**: Evita spam de notificaciones repetidas
- **Prioridades**: info, warning, error, critical
- **Integración**: Funciona con todos los demás sistemas de BackendBot

## 📁 Estructura del Sistema

```
notification_system/
├── __init__.py
├── notification_manager.py      # Gestor principal de notificaciones
├── notification_rule.py         # Definición de reglas de notificación
├── channels/                    # Canales de notificación
│   ├── __init__.py
│   ├── desktop_channel.py       # Notificaciones de escritorio
│   ├── email_channel.py         # Notificaciones por email
│   ├── sound_channel.py         # Notificaciones sonoras
│   └── webhook_channel.py       # Notificaciones webhook
├── models/                      # Modelos de datos
│   ├── __init__.py
│   └── notification_models.py   # Modelos Pydantic
└── storage/                     # Almacenamiento de historial
    ├── __init__.py
    └── notification_storage.py  # SQLite para historial
```

## 🛠️ Uso Básico

### Inicialización
```python
from notification_system import NotificationManager

# Crear instancia del gestor
manager = NotificationManager()
```

### Enviar Notificación Simple
```python
# Notificación básica
manager.send_notification(
    message="Sistema optimizado correctamente",
    priority="info",
    channels=["desktop"]
)
```

### Notificación con Múltiples Canales
```python
# Notificación a múltiples canales
manager.send_notification(
    message="Alerta: CPU al 95%",
    priority="warning",
    channels=["desktop", "email", "sound"]
)
```

### Notificación con Webhook
```python
# Notificación con webhook
manager.send_notification(
    message="Backup completado",
    priority="info",
    channels=["webhook"],
    webhook_url="https://myapp.com/notifications"
)
```

## 🎯 Sistema de Reglas

### Crear Regla de Notificación
```python
from notification_system import NotificationRule

# Regla para CPU alta
cpu_rule = NotificationRule(
    name="cpu_high",
    condition=lambda metrics: metrics.cpu_percent > 90,
    message="CPU usage is above 90%",
    priority="warning",
    channels=["desktop", "email"],
    cooldown_minutes=5
)

# Registrar regla
manager.add_rule(cpu_rule)
```

### Reglas Predefinidas
```python
# Regla para memoria baja
memory_rule = NotificationRule(
    name="memory_low",
    condition=lambda metrics: metrics.memory_percent > 85,
    message="Memory usage above 85%",
    priority="warning",
    channels=["desktop"]
)

# Regla para disco lleno
disk_rule = NotificationRule(
    name="disk_full",
    condition=lambda metrics: metrics.disk_percent > 90,
    message="Disk usage above 90%",
    priority="critical",
    channels=["desktop", "email", "sound"]
)
```

### Gestión de Reglas
```python
# Agregar regla
manager.add_rule(cpu_rule)

# Remover regla
manager.remove_rule("cpu_high")

# Listar reglas activas
active_rules = manager.get_active_rules()

# Habilitar/deshabilitar regla
manager.enable_rule("memory_low")
manager.disable_rule("disk_full")
```

## 📊 Historial de Notificaciones

### Consultar Historial
```python
# Obtener últimas 10 notificaciones
recent_notifications = manager.get_notification_history(limit=10)

# Filtrar por prioridad
warnings = manager.get_notifications_by_priority("warning")

# Filtrar por canal
desktop_notifications = manager.get_notifications_by_channel("desktop")

# Buscar por fecha
from datetime import datetime, timedelta
yesterday = datetime.now() - timedelta(days=1)
recent = manager.get_notifications_since(yesterday)
```

### Estadísticas
```python
# Estadísticas generales
stats = manager.get_notification_stats()
print(f"Total notifications: {stats['total']}")
print(f"By priority: {stats['by_priority']}")
print(f"By channel: {stats['by_channel']}")
```

## 🔧 Configuración Avanzada

### Configuración de Canales

#### Email Channel
```python
# Configurar SMTP
email_config = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
    "from_email": "backendbot@yourdomain.com"
}

manager.configure_email_channel(email_config)
```

#### Webhook Channel
```python
# Configurar webhook global
webhook_config = {
    "url": "https://your-app.com/webhook",
    "headers": {"Authorization": "Bearer your-token"},
    "timeout": 10
}

manager.configure_webhook_channel(webhook_config)
```

#### Desktop Channel
```python
# Configurar notificaciones desktop
desktop_config = {
    "app_name": "BackendBot",
    "icon_path": "path/to/icon.png",
    "timeout": 5000  # milisegundos
}

manager.configure_desktop_channel(desktop_config)
```

### Sistema de Cooldown
```python
# Configurar cooldown global
manager.set_global_cooldown(60)  # 60 segundos entre notificaciones

# Configurar cooldown por regla
cpu_rule = NotificationRule(
    name="cpu_alert",
    condition=lambda m: m.cpu_percent > 90,
    message="High CPU usage",
    cooldown_minutes=10  # 10 minutos para esta regla específica
)
```

## 🔗 Integración con Otros Sistemas

### Con Power Management
```python
# Notificar cambios de perfil de energía
power_manager.on_profile_change(lambda profile: 
    manager.send_notification(
        f"Power profile changed to {profile}",
        "info",
        ["desktop"]
    )
)
```

### Con Backup System
```python
# Notificar backups completados
backup_manager.on_backup_complete(lambda result:
    manager.send_notification(
        f"Backup completed: {result['files_processed']} files",
        "info",
        ["desktop", "webhook"]
    )
)
```

### Con Dashboard
```python
# Notificar desde dashboard
dashboard.on_system_alert(lambda alert:
    manager.send_notification(
        alert.message,
        alert.priority,
        ["desktop", "email"]
    )
)
```

## 📈 Monitoreo y Debugging

### Logs de Notificaciones
```python
# Habilitar logging detallado
import logging
logging.getLogger('notification_system').setLevel(logging.DEBUG)

# Ver logs en tiempo real
manager.enable_debug_logging()
```

### Verificar Estado
```python
# Estado del sistema de notificaciones
status = manager.get_system_status()
print(f"Active rules: {status['active_rules_count']}")
print(f"Queued notifications: {status['queued_count']}")
print(f"Failed notifications: {status['failed_count']}")
```

## 🚨 Manejo de Errores

### Reintentos Automáticos
```python
# Configurar reintentos
manager.set_retry_policy(
    max_retries=3,
    backoff_factor=2,
    max_delay=300
)
```

### Notificaciones de Error
```python
# Notificar errores del sistema
try:
    # código que puede fallar
    risky_operation()
except Exception as e:
    manager.send_notification(
        f"System error: {str(e)}",
        "error",
        ["desktop", "email"]
    )
```

## 📚 API Reference

### Clase NotificationManager

#### Métodos Principales
- `send_notification(message, priority, channels, **kwargs)`: Envía notificación
- `add_rule(rule)`: Agrega regla de notificación
- `remove_rule(rule_name)`: Remueve regla
- `get_notification_history(limit=100)`: Obtiene historial
- `get_active_rules()`: Lista reglas activas

#### Métodos de Configuración
- `configure_email_channel(config)`: Configura canal email
- `configure_webhook_channel(config)`: Configura canal webhook
- `set_global_cooldown(seconds)`: Establece cooldown global

### Clase NotificationRule

#### Atributos
- `name`: Nombre único de la regla
- `condition`: Función que evalúa la condición
- `message`: Mensaje de notificación
- `priority`: Prioridad (info, warning, error, critical)
- `channels`: Lista de canales
- `cooldown_minutes`: Minutos de cooldown

## 🔍 Ejemplos Avanzados

### Sistema de Alertas Completo
```python
from notification_system import NotificationManager, NotificationRule

class SystemAlertManager:
    def __init__(self):
        self.notifications = NotificationManager()
        self.setup_alerts()
    
    def setup_alerts(self):
        # Alerta CPU
        cpu_alert = NotificationRule(
            name="cpu_critical",
            condition=lambda m: m.cpu_percent > 95,
            message="🚨 CRITICAL: CPU usage above 95%",
            priority="critical",
            channels=["desktop", "email", "sound"],
            cooldown_minutes=2
        )
        
        # Alerta memoria
        memory_alert = NotificationRule(
            name="memory_critical", 
            condition=lambda m: m.memory_percent > 90,
            message="⚠️ WARNING: Memory usage above 90%",
            priority="warning",
            channels=["desktop"],
            cooldown_minutes=5
        )
        
        # Alerta disco
        disk_alert = NotificationRule(
            name="disk_critical",
            condition=lambda m: m.disk_percent > 95,
            message="🚨 CRITICAL: Disk usage above 95%",
            priority="critical", 
            channels=["desktop", "email"],
            cooldown_minutes=15
        )
        
        self.notifications.add_rule(cpu_alert)
        self.notifications.add_rule(memory_alert)
        self.notifications.add_rule(disk_alert)
    
    def check_system(self, metrics):
        """Evalúa todas las reglas con las métricas actuales"""
        self.notifications.evaluate_rules(metrics)

# Uso
alert_manager = SystemAlertManager()

# En el loop de monitoreo
while True:
    metrics = get_system_metrics()
    alert_manager.check_system(metrics)
    time.sleep(30)
```

Este sistema proporciona una base sólida para notificaciones inteligentes que se integran perfectamente con todos los componentes de BackendBot.</content>
<parameter name="filePath">c:\Users\DELL\Desktop\BackendBot\docs\NOTIFICATION_SYSTEM.md