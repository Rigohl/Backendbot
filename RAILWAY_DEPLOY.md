# 🚂 Despliegue en Railway

## Pasos para desplegar BackendBot en Railway:

### 1. Preparación
- Asegúrate de tener una cuenta en [Railway.app](https://railway.app)
- Instala Railway CLI: `npm install -g @railway/cli`

### 2. Despliegue
```bash
# Login en Railway
railway login

# Conectar al proyecto (desde el directorio del proyecto)
cd /path/to/BackendBot
railway link

# Configurar variables de entorno
railway variables set API_KEY=tu-api-key-segura
railway variables set OPENAI_API_KEY=tu-openai-key
railway variables set ADMIN_USERNAME=admin
railway variables set ADMIN_PASSWORD=tu-password-seguro

# Desplegar
railway up
```

### 3. Configuración Post-Despliegue
- Obtén la URL de tu aplicación desde Railway Dashboard
- Actualiza tu frontend para usar esta URL en lugar de `http://localhost:8000`
- Configura dominios personalizados si es necesario

### 4. Variables de Entorno Requeridas
- `API_KEY`: Clave de autenticación (genera una segura)
- `OPENAI_API_KEY`: Para el agente IA
- `ADMIN_USERNAME`: Usuario admin
- `ADMIN_PASSWORD`: Contraseña admin
- `PORT`: Puerto (Railway lo asigna automáticamente)
- `HOST`: Host (siempre 0.0.0.0 en Railway)

### 5. Troubleshooting
- Si hay errores de build, revisa `railway logs`
- Para reiniciar: `railway restart`
- Para rollback: `railway rollback`
- Para ver logs: `railway logs`

### 6. Archivos de Configuración
- `railway.json`: Configuración principal
- `nixpacks.toml`: Configuración de build
- `railway_start.py`: Script de inicio optimizado
- `requirements.txt`: Dependencias Python
- `pyproject.toml`: Configuración del proyecto

## 🎯 URL del Backend
Después del despliegue, tu backend estará disponible en:
`https://your-project-name.railway.app`

### Actualizar Frontend
En tu `dashboard/dashboard.js`, cambia:
```javascript
const backendUrl = 'http://localhost:8000'; // Cambia esto
```
Por:
```javascript
const backendUrl = 'https://your-project-name.railway.app';
```