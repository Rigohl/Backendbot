# 🚂 BackendBot Pro - Railway Enhanced

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-0B0D0E?style=flat&logo=railway)](https://railway.app)

**BackendBot es una API avanzada construida con FastAPI para monitoreo y control de procesos del sistema, ahora potenciada con las características avanzadas de Railway para máxima performance y escalabilidad.**

## ✨ Características Destacadas

### 🚀 **Railway Advanced Features** (NUEVO)
- **Redis Cache Inteligente** - Cache de respuestas de IA y métricas del sistema
- **PostgreSQL Integrado** - Base de datos nativa de Railway con optimización automática
- **Monitoreo Proactivo** - Detección de anomalías y health checks avanzados
- **Webhooks Automatizados** - Integración completa con eventos de Railway
- **Cron Jobs Inteligentes** - Tareas programadas para mantenimiento y optimización
- **Rate Limiting** - Protección automática contra sobrecargas
- **Backup Automático** - Copias de seguridad programadas de base de datos
- **Optimización Continua** - Mejora automática del rendimiento del sistema

### 🔧 **Core Features**
- ✅ **Monitoreo de Procesos** - Seguimiento en tiempo real de CPU, memoria y disco
- ✅ **Health Checks Avanzados** - Verificación automática del estado del sistema
- ✅ **Gestión de Logs** - Logs estructurados con rotación automática
- ✅ **Optimización de Memoria** - Liberación inteligente de RAM
- ✅ **API RESTful Completa** - Endpoints documentados con OpenAPI/Swagger
- ✅ **Dashboard Web** - Interfaz moderna con gráficos en tiempo real
- ✅ **Automatización** - Scripts de PowerShell y Batch para Windows

## 🚀 Inicio Rápido

### Opción 1: Inicio Automático (Windows)
1. **Haz doble click** en `Start-BackendBot.bat`
2. **Abre el dashboard** con `Open-Dashboard.bat`
3. ¡Listo! El sistema está corriendo en `http://localhost:8000`

### Opción 2: Railway Cloud (Recomendado)
```bash
# Desplegar en Railway (automático)
railway deploy

# O usar Railway CLI
railway up
```

### Opción 3: Desarrollo Local
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar pruebas de Railway
python test_railway_advanced.py

# Iniciar el backend
uvicorn src.backendbot.main:app --reload
```

## 🌐 Dashboard y API

### Endpoints Principales
- **`/`** - Estado del sistema con info de Railway
- **`/health`** - Health check avanzado con métricas completas
- **`/optimize`** - Optimización automática del sistema
- **`/railway/status`** - Estado detallado de componentes Railway
- **`/railway/cache/stats`** - Estadísticas del cache Redis
- **`/railway/jobs/status`** - Estado de cron jobs
- **`/railway/webhook`** - Endpoint para webhooks de Railway

### Dashboard Web
- **Interfaz moderna** con Tailwind CSS
- **Gráficos en tiempo real** con Chart.js
- **Métricas de Railway** integradas
- **Navegación intuitiva** entre vistas

## 📁 Estructura del Proyecto

```
BackendBot/
├── src/backendbot/           # Código fuente principal
│   ├── cache.py             # Redis Cache avanzado
│   ├── monitor.py           # Monitoreo proactivo
│   ├── webhooks.py          # Webhooks de Railway
│   ├── cron_jobs.py         # Cron jobs automatizados
│   ├── railway_db.py        # PostgreSQL integrado
│   ├── railway_integration.py # Integración completa
│   ├── main.py              # Aplicación FastAPI
│   └── database.py          # Base de datos existente
├── dashboard/               # Interfaz web
├── scripts/                 # Scripts de automatización
├── tests/                   # Tests unitarios
├── config/                  # Configuraciones
├── docs/                    # Documentación
├── RAILWAY_ADVANCED.md      # Guía de Railway
├── RAILWAY_ADVANCED_GUIDE.md # Guía completa
├── test_railway_advanced.py # Script de pruebas
└── requirements.txt         # Dependencias actualizadas
```

## 🛠️ Tecnologías

### Backend
- **FastAPI** - Framework web moderno y rápido
- **Python 3.12+** - Última versión de Python
- **Railway PostgreSQL** - Base de datos integrada
- **Redis** - Cache de alto rendimiento
- **SQLAlchemy** - ORM asíncrono
- **Pydantic** - Validación de datos

### Railway Advanced
- **AsyncPG** - Cliente PostgreSQL asíncrono
- **APScheduler** - Scheduler de tareas programadas
- **AIOHTTP** - Cliente HTTP asíncrono
- **Psutil** - Monitoreo del sistema

### Frontend
- **HTML5/CSS3** - Interfaz moderna
- **Tailwind CSS** - Framework CSS utilitario
- **Chart.js** - Gráficos interactivos
- **JavaScript ES6+** - Lógica del cliente

### DevOps & Testing
- **Railway** - Plataforma de deployment
- **Nixpacks** - Build system de Railway
- **Pytest** - Framework de testing
- **Ruff** - Linter y formateador
- **Black** - Formateador de código

## 🚂 Características Avanzadas de Railway

### 1. **Cache Redis Inteligente**
```python
from src.backendbot.cache import cache

# Cache de respuestas de IA
cache.cache_ai_response('query', 'response', ttl=3600)

# Rate limiting automático
if cache.set_rate_limit('user_id', max_requests=100):
    # Procesar request
```

### 2. **Monitoreo Proactivo**
```python
from src.backendbot.monitor import monitor

# Métricas en tiempo real
metrics = await monitor.collect_system_metrics()

# Health check avanzado
health = await monitor.create_health_check_endpoint()
```

### 3. **PostgreSQL Integrado**
```python
from src.backendbot.railway_db import railway_db

# Guardar métricas automáticamente
await railway_db.save_metrics('cpu_usage', {'percent': 45.2})

# Obtener historial
history = await railway_db.get_process_history(hours=24)
```

### 4. **Cron Jobs Automatizados**
- **Limpieza de logs**: Diariamente a las 2:00 AM
- **Backup de BD**: Diariamente a las 3:00 AM
- **Optimización**: Cada 6 horas
- **Health checks**: Cada 5 minutos
- **Mantenimiento**: Semanalmente los domingos

### 5. **Webhooks de Automatización**
- **Deployments**: Éxito y fracaso
- **Servicios**: Caídas y recuperación
- **Backups**: Completados
- **Alertas**: Uso de recursos

## � Métricas y Monitoreo

### Métricas Recopiladas
- **Sistema**: CPU, memoria, disco, red, procesos
- **Railway**: Project ID, Environment, Service, Replica
- **Cache**: Conexiones, memoria usada, keys totales
- **Base de datos**: Tamaño, conexiones activas, estadísticas
- **Performance**: Latencia, throughput, error rates

### Health Checks Automáticos
- **Umbrales configurables** para alertas
- **Recomendaciones automáticas** de optimización
- **Detección de anomalías** en tiempo real
- **Reportes de estado** integrales

## � Configuración

### Variables de Entorno para Railway
```bash
# Base de datos
DATABASE_URL=postgresql://...

# Redis (opcional)
REDIS_URL=redis://...

# Webhooks
RAILWAY_WEBHOOK_SECRET=tu_secret

# Automáticas de Railway
RAILWAY_PROJECT_ID
RAILWAY_ENVIRONMENT_ID
RAILWAY_SERVICE_ID
```

### Configuración Local
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar variables
nano .env
```

## 🧪 Testing

### Ejecutar Todas las Pruebas
```bash
# Pruebas de Railway avanzado
python test_railway_advanced.py

# Pruebas unitarias
pytest tests/

# Con coverage
pytest --cov=src/backendbot tests/
```

### Pruebas de Integración
```bash
# Health check
curl http://localhost:8000/health

# Optimización
curl -X POST http://localhost:8000/optimize

# Estado de Railway
curl http://localhost:8000/railway/status
```

## 📖 Documentación

- **[🚂 Railway Advanced Guide](RAILWAY_ADVANCED_GUIDE.md)** - Guía completa de características avanzadas
- **[📚 Documentación Técnica](docs/README.md)** - Documentación detallada del proyecto
- **[🔧 API Docs](http://localhost:8000/docs)** - Documentación interactiva de la API
- **[📊 Railway Docs](https://docs.railway.app/)** - Documentación oficial de Railway

## 🚀 Deployment en Railway

### Deploy Automático
```bash
# Login en Railway
railway login

# Conectar proyecto
railway link

# Deploy
railway up
```

### Variables de Entorno en Railway
1. Ve a tu proyecto en Railway Dashboard
2. Configuración → Variables
3. Agrega las variables necesarias

### Monitoreo en Railway
- **Logs**: `railway logs`
- **Métricas**: Dashboard de Railway
- **Health**: Endpoints de health check
- **Alerts**: Configuración de alertas

## 🤝 Contribución

1. **Fork** el proyecto
2. **Crea** una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abre** un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- **Railway** por la plataforma increíble
- **FastAPI** por el framework moderno
- **La comunidad** de Python por las herramientas
- **Contribuidores** que hacen este proyecto posible

---

## 🎯 ¿Por Qué BackendBot + Railway?

✅ **Escalabilidad Automática** - Railway escala según la demanda
✅ **Base de Datos Integrada** - PostgreSQL sin configuración
✅ **Cache de Alto Rendimiento** - Redis para máxima velocidad
✅ **Monitoreo Proactivo** - Detección automática de problemas
✅ **Backup Automático** - Datos seguros con Railway
✅ **Deploy Instantáneo** - De código a producción en minutos
✅ **Costos Optimizados** - Paga solo por lo que usas
✅ **Integración Completa** - Webhooks y APIs nativas

**¡BackendBot en Railway es la combinación perfecta para aplicaciones modernas y escalables!** 🚀