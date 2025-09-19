# BackendBot API - Guía de Seguridad y Uso

## 🔒 Configuración de Seguridad Profesional

La API de BackendBot está configurada con múltiples capas de seguridad para acceso local exclusivo:

### Características de Seguridad Implementadas

1. **Binding Localhost Exclusivo**
   - Solo accesible desde `127.0.0.1` (localhost)
   - Puerto no estándar: `48732`
   - Sin acceso desde red externa

2. **Autenticación OAuth2**
   - JWT tokens para sesiones seguras
   - Rate limiting: 100 requests/minuto por IP
   - Credenciales por defecto (cambiar en producción):
     - Usuario: `admin`
     - Contraseña: `backendbot_secure_2024`

3. **HTTPS con Certificado Auto-Firmado**
   - Certificado válido por 1 año
   - Solo funciona en localhost
   - Requiere aceptación manual en navegador

4. **Rate Limiting**
   - 100 requests/minuto global
   - 5 requests/minuto para login
   - 10 requests/minuto para health check

## 🚀 Inicio del Servicio

### Opción 1: Script de Servicio (Recomendado)

```batch
# Iniciar servicio
api_service.bat start

# Ver estado
api_service.bat status

# Detener servicio
api_service.bat stop

# Reiniciar servicio
api_service.bat restart

# Ver logs
api_service.bat logs
```

### Opción 2: Ejecución Directa

```batch
# Modo seguro invisible (recomendado)
python api_server.py

# Modo visible para desarrollo
python api_server.py --visible

# Con HTTPS explícito
python api_server.py --https

# Puerto personalizado
python api_server.py --port 8080
```

## 📋 URLs de Acceso

Una vez iniciado el servicio:

- **Documentación API**: https://127.0.0.1:48732/docs
- **Health Check**: https://127.0.0.1:48732/api/v1/health
- **Login**: https://127.0.0.1:48732/token
- **API Root**: https://127.0.0.1:48732/

## 🔐 Autenticación

### Obtener Token de Acceso

```bash
curl -X POST "https://127.0.0.1:48732/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=backendbot_secure_2024" \
  --insecure
```

### Usar Token en Requests

```bash
curl -X GET "https://127.0.0.1:48732/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  --insecure
```

## ⚠️ Notas de Seguridad Importantes

1. **Certificado Auto-Firmado**: Acepta la advertencia de seguridad en tu navegador
2. **Credenciales por Defecto**: Cambia la contraseña por defecto en producción
3. **Firewall**: Asegúrate de que el puerto 48732 no esté expuesto externamente
4. **Logs**: Revisa los logs regularmente en `logs/api_service.log`

## 🛠️ Solución de Problemas

### Error: Certificados SSL no encontrados
```batch
python generate_ssl_cert.py
```

### Error: Puerto ocupado
```batch
# Cambiar puerto
python api_server.py --port 8080
```

### Error: No se puede acceder desde navegador
- Asegúrate de usar `https://` no `http://`
- Acepta el certificado auto-firmado
- Verifica que el servicio esté ejecutándose

## 📊 Monitoreo

### Health Check (sin autenticación)
```bash
curl https://127.0.0.1:48732/api/v1/health --insecure
```

### Ver Logs del Servicio
```batch
api_service.bat logs
```

## 🔧 Configuración Avanzada

### Variables de Entorno
```batch
set BACKENDBOT_SECRET_KEY=your_secret_key_here
set BACKENDBOT_LOG_LEVEL=INFO
```

### Configuración Personalizada
Edita `config/backendbot.yaml` para ajustes adicionales.

## 📚 Endpoints Disponibles

- `GET /api/v1/health` - Health check
- `POST /token` - Obtener token de acceso
- `GET /api/v1/auth/me` - Información del usuario
- `GET /` - API root (requiere autenticación)

Para documentación completa, visita: https://127.0.0.1:48732/docs

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs: `api_service.bat logs`
2. Verifica el estado: `api_service.bat status`
3. Reinicia el servicio: `api_service.bat restart`