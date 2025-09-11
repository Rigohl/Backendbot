# 🖥️ BackendBot – Supervisor Autónomo de Procesos

**BackendBot** es un sistema local y cloud-ready que mantiene tu backend siempre en ejecución, optimiza recursos y te da control desde la bandeja del sistema o dashboard web. Soporta almacenamiento local (SQLite) y remoto (Neon/Postgres).

## 📋 Características

- Monitoreo en tiempo real de procesos y recursos del sistema.
- Optimización automática de RAM suspendiendo/cerrando procesos hibernables.
- Watchdog inteligente con aprendizaje basado en decisiones previas.
- Dashboard web y API para visualizar procesos, métricas y reportes.
- Icono en bandeja del sistema para control rápido y cambio de modos.
- Soporte para despliegue local y en la nube (Railway, Fly.io, Neon).
- Historial y reportes guardados en Neon/Postgres o SQLite.

## 🛠️ Instalación y Despliegue

### Local (Windows/Linux)
1. Clona o descarga el repositorio.
2. Instala dependencias (incluye soporte Neon/Postgres):
   ```
   pip install -r requirements.txt
   # requirements.txt incluye psycopg2-binary para Neon/Postgres
   ```
3. Ejecuta el backend:
   ```
   python -m src.backendbot.main
   ```
4. Usa los scripts y el dashboard como antes.

### Railway / Fly.io / Neon
1. Sube el proyecto a Railway/Fly.io.
2. Configura la variable de entorno `DATABASE_URL` con la URL de Neon/Postgres. Ejemplo:
   ```
   DATABASE_URL=postgresql://usuario:contraseña@ep-neon-db.neon.tech:5432/backendbot
   ```
   Si no se define, se usará SQLite local automáticamente.
3. El backend se inicia automáticamente con:
   ```
   web: uvicorn src.backendbot.main:app --host 0.0.0.0 --port 8000
   ```
   (Procfile ya incluido)
4. Accede al dashboard/API en la URL pública del servicio.

## ⚙️ Configuración

- Umbrales: CPU >80%, RAM >4000 MB por 60s.
- Procesos hibernables y modos configurables en `config.py`.
- Historial y reportes en Neon/Postgres si `DATABASE_URL` está definido, o SQLite local.

## 🗄️ Base de datos
- **Local:** SQLite (`data/backend_data.db`) (fallback automático si no hay `DATABASE_URL`)
- **Cloud:** Neon/Postgres (`DATABASE_URL`)
- Tablas: `process_history`, `optimization_events`, `watchdog_decisions`

## 🚀 Modos de Operación
- Diario, Editor, Videojuego, Streaming, Multimedia, Focus.
- Cambia modos desde la bandeja o API `/set-modo/{modo}`.

## 📚 API Endpoints
- `/procesos`, `/apagar/{pid}`, `/resume/{pid}`, `/kill/{pid}`, `/optimize`, `/set-modo/{modo}`, `/restore-important`, `/self`, `/memoria`, `/reset-memoria`.

## 🗑️ Sugerencias de Desinstalación
- (Ver recomendaciones previas)


## 🧪 Pruebas y Cobertura
- Tests unitarios en `tests/` para módulos principales (`utils`, `api_routes`, etc).
- Ejecuta los tests con:
   ```
   pytest tests/
   ```

## 🚀 Próximas Mejoras y Hoja de Ruta
- Dashboard avanzado, suspensión inteligente, gestión dinámica, integración GPU, reportes exportables, etc.


## ☁️ Despliegue No Local (Opciones de Backend Remoto)

## 🛠️ Troubleshooting Railway/Fly.io/Neon
- Verifica que `DATABASE_URL` esté correctamente configurada.
- Revisa los logs del servicio para errores de conexión.
- Asegúrate de que `psycopg2-binary` esté instalado (ver `requirements.txt`).
- Si falla la conexión Neon, el sistema usará SQLite local automáticamente.
- Railway, Fly.io, Neon/Postgres, Render.com, Docker.

---

**Para dudas o soporte, consulta la documentación o abre un issue.**