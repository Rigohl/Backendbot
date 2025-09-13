# BackendBot Activity Monitor

Sistema avanzado de monitoreo de actividad del usuario que controla automáticamente el inicio y apagado del backend de BackendBot.

## Características

- **Detección Inteligente de Actividad**: Monitorea teclado, mouse y procesos activos
- **Notificaciones de Inactividad**: Muestra advertencias cuando detecta inactividad
- **Apagado Automático**: Detiene el backend después de un período de inactividad
- **Reinicio por Movimiento**: Reinicia el backend cuando detecta actividad del usuario
- **Configuración Flexible**: Parámetros personalizables para diferentes escenarios
- **Logging Completo**: Registra todas las actividades y eventos
- **Modo Servicio**: Puede ejecutarse como servicio de Windows

## Requisitos

- Windows 10/11
- PowerShell 5.1 o superior
- Python 3.8+
- BackendBot instalado y configurado

## Instalación

1. Asegúrate de que BackendBot esté instalado en `c:\Users\DELL\Desktop\BackendBot`
2. Verifica que el archivo `activity_monitor.ps1` tenga permisos de ejecución
3. Configura las variables de entorno si es necesario

## Uso Básico

### Iniciar Monitoreo Interactivo

```powershell
.\activity_monitor.ps1 -Monitor
```

### Iniciar Backend Manualmente

```powershell
.\activity_monitor.ps1 -Start
```

### Detener Backend Manualmente

```powershell
.\activity_monitor.ps1 -Stop
```

### Ver Estado del Sistema

```powershell
.\activity_monitor.ps1 -Status
```

## Parámetros de Configuración

| Parámetro | Descripción | Valor por Defecto |
|-----------|-------------|-------------------|
| `InactivityThresholdMinutes` | Minutos antes de mostrar advertencia | 5 |
| `ResponseTimeoutMinutes` | Minutos para esperar respuesta del usuario | 3 |
| `BackendPath` | Ruta al archivo main.py del backend | `src\backendbot\main.py` |
| `PythonPath` | Comando para ejecutar Python | `python` |
| `LogFile` | Archivo de log | `logs\activity_monitor.log` |

## Ejemplos de Uso Avanzado

### Monitoreo con Configuración Personalizada

```powershell
.\activity_monitor.ps1 -Monitor -InactivityThresholdMinutes 10 -ResponseTimeoutMinutes 5
```

### Monitoreo en Segundo Plano

```powershell
Start-Job -ScriptBlock { .\activity_monitor.ps1 -Monitor } -Name "BackendMonitor"
```

### Instalación como Servicio (Requiere privilegios de administrador)

```powershell
# Crear el servicio
New-Service -Name "BackendBotActivityMonitor" -BinaryPathName "powershell.exe -ExecutionPolicy Bypass -File C:\Users\DELL\Desktop\BackendBot\activity_monitor.ps1 -Monitor" -DisplayName "BackendBot Activity Monitor" -StartupType Automatic

# Iniciar el servicio
Start-Service -Name "BackendBotActivityMonitor"
```

## API REST del Backend

El sistema también expone endpoints REST para control remoto:

### Ver Estado de Actividad
```http
GET /activity/status
```

### Iniciar Monitoreo
```http
POST /activity/start
```

### Detener Monitoreo
```http
POST /activity/stop
```

### Responder a Advertencia
```http
POST /activity/respond
```

## Configuración del Backend

Asegúrate de que el archivo `src/backendbot/config.py` tenga las siguientes configuraciones:

```python
# Activity monitoring configuration
ACTIVITY_MONITORING_ENABLED: bool = True
INACTIVITY_WARNING_TIME: int = 300  # 5 minutes
INACTIVITY_SHUTDOWN_TIME: int = 480  # 8 minutes total
ACTIVITY_CHECK_INTERVAL: int = 1
BACKEND_AUTO_START: bool = True
BACKEND_AUTO_STOP: bool = True
```

## Logs y Depuración

Los logs se guardan en `logs\activity_monitor.log`. Los niveles de log son:

- `INFO`: Eventos normales del sistema
- `WARN`: Advertencias y eventos no críticos
- `ERROR`: Errores que requieren atención
- `DEBUG`: Información detallada para depuración

## Solución de Problemas

### El backend no se inicia automáticamente
1. Verifica que Python esté en el PATH
2. Confirma que la ruta al archivo `main.py` sea correcta
3. Revisa los logs para errores específicos

### Las notificaciones no aparecen
1. Asegúrate de que las notificaciones de Windows estén habilitadas
2. Verifica que no haya bloqueadores de popups
3. El sistema tiene fallback a popups de PowerShell

### Detección de actividad no funciona
1. Verifica que el script tenga permisos para acceder a la API de Windows
2. Algunos entornos virtuales pueden interferir con la detección
3. El sistema tiene métodos alternativos de detección

### Error de permisos
1. Ejecuta PowerShell como administrador para funcionalidades completas
2. Para instalación como servicio, se requieren privilegios de administrador

## Arquitectura

El sistema consta de varios componentes:

1. **activity_monitor.ps1**: Script principal de PowerShell
2. **src/backendbot/services/activity_monitor.py**: Servicio Python para monitoreo avanzado
3. **src/backendbot/main.py**: Endpoints REST para control remoto
4. **src/backendbot/config.py**: Configuración centralizada

## Seguridad

- El sistema no almacena información sensible
- Las comunicaciones locales usan HTTP básico si está configurado
- Los logs no contienen información personal
- El monitoreo respeta la privacidad del usuario

## Contribución

Para contribuir al desarrollo:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa tus cambios
4. Agrega tests si corresponde
5. Envía un pull request

## Licencia

Este proyecto está bajo la licencia MIT. Ver archivo LICENSE para más detalles.