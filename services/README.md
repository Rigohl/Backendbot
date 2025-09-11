# README - Sistema de Auto-Inicio BackendBot

## Descripción
Este sistema garantiza que BackendBot esté **SIEMPRE ACTIVO** y solo pueda ser detenido por usuarios autorizados.

## Componentes

### 1. BackendBot Service (backendbot_service.py)
- Servicio de Windows que inicia automáticamente con el sistema
- Monitorea el backend y lo reinicia si se detiene
- Registra todas las actividades en logs

### 2. BackendBot Monitor (backendbot_monitor.py)
- Script de monitoreo continuo
- Reinicia el backend automáticamente si detecta fallos
- Control de frecuencia de reinicios para evitar bucles

### 3. Sistema de Autenticación (backendbot_auth.py)
- Control de acceso basado en usuarios y roles
- Solo administradores pueden detener el backend
- Sistema de contraseñas hasheadas

### 4. Script de Control (backendbot_control.py)
- Interfaz de línea de comandos para controlar el backend
- Requiere autenticación para todas las operaciones
- Menú intuitivo con opciones seguras

## Instalación

### Opción 1: Servicio de Windows (Recomendado)
```bash
# Instalar servicio
python services/install_service.py install

# El servicio se iniciará automáticamente con Windows
```

### Opción 2: Script de Inicio Automático
```bash
# Crear script de inicio
python services/install_service.py startup

# El monitor se ejecutará al iniciar sesión
```

## Uso

### Control del Backend
```bash
# Ejecutar panel de control
python services/backendbot_control.py
```

### Credenciales por Defecto
- **Usuario:** admin
- **Contraseña:** backendbot2025

⚠️ **IMPORTANTE:** Cambia la contraseña por defecto inmediatamente después de la instalación.

## Comandos Disponibles

### Para Todos los Usuarios
- Ver estado del backend
- Cambiar contraseña propia

### Solo Administradores
- Detener backend
- Reiniciar backend
- Agregar nuevos usuarios

## Seguridad

- ✅ Contraseñas hasheadas con SHA-256
- ✅ Logs de todas las operaciones
- ✅ Control de roles (admin/user)
- ✅ Validación de comandos peligrosos
- ✅ Confirmación para operaciones críticas

## Monitoreo

### Logs
- `logs/monitor.log` - Actividad del monitor
- `C:\ProgramData\BackendBot\service.log` - Actividad del servicio

### Estados
- 🟢 **Running** - Backend activo
- 🔴 **Stopped** - Backend detenido
- 🟡 **Restarting** - Reiniciando automáticamente

## Solución de Problemas

### Backend no se inicia
1. Verificar logs en `logs/monitor.log`
2. Comprobar que Python esté en PATH
3. Verificar permisos de archivos

### Servicio no se instala
1. Ejecutar como administrador
2. Verificar dependencias de Windows
3. Revisar logs de instalación

### No puede detener el backend
1. Verificar credenciales de administrador
2. Comprobar conexión a la base de datos
3. Revisar logs de autenticación

## Configuración Avanzada

### Archivo `config/monitor_config.json`
```json
{
    "max_restarts": 10,        // Máximo reinicios por hora
    "restart_window": 3600,    // Ventana de tiempo (segundos)
    "check_interval": 30,      // Intervalo de verificación (segundos)
    "log_level": "INFO",       // Nivel de logging
    "auto_restart": true       // Habilitar reinicio automático
}
```

## Desinstalación

### Servicio de Windows
```bash
python services/install_service.py uninstall
```

### Limpiar archivos
```bash
# Eliminar configuración
rm -rf config/monitor_config.json
rm -rf config/auth.json

# Eliminar logs
rm -rf logs/monitor.log
```

## Soporte

Si encuentras problemas:
1. Revisa los logs
2. Verifica la configuración
3. Ejecuta como administrador
4. Contacta al administrador del sistema

---

**Nota:** Este sistema garantiza que BackendBot esté siempre disponible, pero con control total sobre quién puede detenerlo.