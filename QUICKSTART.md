# 🚀 Inicio Rápido - BackendBot

## ⚡ Inicio Automático (Recomendado)

```bash
# Desde la carpeta raíz del proyecto:
python start.py
```

Este comando:
- ✅ Verifica Python y dependencias
- ✅ Configura la base de datos automáticamente
- ✅ Inicia el servidor FastAPI
- ✅ Abre el dashboard en tu navegador

## 🎯 Usar BackendBot

Una vez iniciado, accede a:

- **Dashboard Web**: http://localhost:8000/dashboard
- **Documentación API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📋 Comandos Útiles

```bash
# Solo configurar base de datos
python start.py --db-only

# Solo configurar (sin iniciar servidor)
python start.py --setup-only

# Ver información del proyecto
python start.py --info

# Ejecutar con configuración específica
python -m src.backendbot.main
```

## 🗄️ Base de Datos

El sistema detecta automáticamente:
- **PostgreSQL** (si está disponible en localhost:5432)
- **SQLite** (como respaldo)

## 🏗️ Arquitectura

BackendBot usa una arquitectura de **microservicios (bots)**:
- **Orquestador**: API principal y coordinación
- **Bot Guardián**: Supervisa y reinicia otros bots
- **Bot Monitor**: Monitoreo de sistema
- **Bot Organizador**: Gestión de archivos
- **Bot Indexador**: Indexación de archivos

## 📊 Endpoints Principales

| Endpoint | Descripción |
|----------|-------------|
| `GET /` | Mensaje de bienvenida |
| `GET /health` | Estado del servicio |
| `GET /dashboard` | Dashboard web |
| `GET /api/v1/monitor/stats` | Estadísticas del sistema |
| `POST /api/v1/organizer/scan` | Escanear duplicados |
| `POST /api/v1/indexer/start_indexing` | Indexar archivos |

## 🛠️ Desarrollo

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar pruebas
python -m pytest tests/

# Ver logs
tail -f logs/backend.log
```

## 📞 Soporte

Si tienes problemas:
1. Verifica que Python 3.8+ esté instalado
2. Asegúrate de que las dependencias estén instaladas
3. Revisa los logs en `logs/backend.log`
4. Usa `python start.py --info` para diagnóstico