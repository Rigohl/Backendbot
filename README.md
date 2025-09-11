# BackendBot – Supervisor Autónomo de Procesos

## Descripción
BackendBot es un sistema inteligente para monitoreo y optimización de procesos y recursos en Windows, con soporte para despliegue local y en la nube (Railway, Fly.io, Neon/Postgres). Permite suspender, restaurar y priorizar procesos, gestionar modos de uso, y visualizar métricas desde un dashboard web o la bandeja del sistema.

## Instalación Rápida

### Local (Windows/Linux)
1. Clona el repositorio.
2. Instala dependencias (incluye soporte Neon/Postgres):
   ```
   pip install -r requirements.txt
   # requirements.txt incluye psycopg2-binary para Neon/Postgres
   ```
3. Ejecuta el backend:
   ```
   python -m src.backendbot.main
   ```

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
   (Procfile incluido)
4. Accede al dashboard/API en la URL pública del servicio.

## Configuración
- Modos y procesos configurables en `src/backendbot/config.py`.
- Umbrales de RAM/CPU ajustables.
- Base de datos: SQLite local (fallback automático) o Neon/Postgres remoto.

## Uso
- Control desde bandeja del sistema (`tray_icon.py`) o dashboard web (`dashboard/index.html`).
- API REST para gestión avanzada de procesos y modos.

## Endpoints principales
- `/procesos`, `/apagar/{pid}`, `/resume/{pid}`, `/kill/{pid}`, `/optimize`, `/set-modo/{modo}`, `/restore-important`, `/self`, `/memoria`, `/reset-memoria`

## Despliegue en la nube
- Railway, Fly.io, Neon/Postgres, Render.com, Docker.
- Solo necesitas configurar `DATABASE_URL` y subir el proyecto.


## Pruebas y Cobertura
- Tests unitarios en `tests/` para módulos principales (`utils`, `api_routes`, etc).
- Ejecuta los tests con:
   ```
   pytest tests/
   ```

## Documentación
- Consulta `docs/README.md` para detalles avanzados, configuración, y hoja de ruta.

## Dashboard Web
- Visualiza el estado del backend, RAM, CPU, modo actual y procesos.
- Gráficos en tiempo real y acciones rápidas (optimizar, resetear memoria, cambiar modo).
- Consulta la documentación avanzada en `docs/README.md` para ejemplos visuales y personalización.


**BackendBot está listo para uso local y cloud, con integración Neon/Postgres y despliegue sencillo en Railway/Fly.io.**

## Troubleshooting Railway/Fly.io/Neon
- Verifica que `DATABASE_URL` esté correctamente configurada.
- Revisa los logs del servicio para errores de conexión.
- Asegúrate de que `psycopg2-binary` esté instalado (ver `requirements.txt`).
- Si falla la conexión Neon, el sistema usará SQLite local automáticamente.