# Operación del proyecto BackendBot

Este documento describe el comportamiento real en ejecución y cómo las funcionalidades del README se mapean al código.

## Resumen
- El proyecto expone una superficie HTTP usando FastAPI en `src/backendbot/core/routers.py` con prefijo `/api/v1/`.
- Persistencia ligera: archivos JSON en la carpeta de datos `.backendbot_data/`.
- `src/backendbot/utils/data_store.py` centraliza lectura/escritura y garantiza creación de defaults para evitar errores por archivos vacíos o corruptos.
- `TaskScheduler` ahora acepta `load_persisted` (default False) para evitar cargar persistencia en ambientes de prueba; un singleton runtime se crea con `load_persisted=True`.

## Archivos de datos y defaults
- `.backendbot_data/usage_patterns.json` : {} por defecto
- `.backendbot_data/user_preferences.json` : {} por defecto
- `.backendbot_data/performance_metrics.json` : {} por defecto
- `.backendbot_data/scheduled_tasks.json` : [] por defecto
- `.backendbot_data/file_index.json` : {} por defecto

`initialize_defaults()` crea estos archivos si no existen o si están vacíos/corruptos.

## Cómo el README se relaciona con el código
- Las secciones de monitor, indexer, organizer y history del README mapean a endpoints de `routers.py`. Los tests verifican las formas exactas de respuesta; el código se ajustó para que las respuestas cumplan esas expectativas.
- La UI de escritorio (PyQt5) es un lanzador independiente (`src/backendbot/main_ui_launcher.py`) que se integra con el backend local.

## Recomendaciones operativas
- En CI se ejecuta `initialize_defaults()` antes de correr tests para evitar fallos por archivos vacíos.
- Para métricas reales, instale `psutil` en el entorno (ya incluido en `requirements.txt`).
- Para despliegue en producción, considere usar una base de datos ligera (SQLite/Postgres) en vez de JSON si se requiere integridad multi-instancia.

## Cómo contribuir
- Mantener el README sin quitar información; enriquecer con secciones que documenten nuevos comportamientos (por ejemplo, `OPERATION.md`).
- Antes de abrir PRs, correr `pytest -q` localmente y asegurarse de que `initialize_defaults()` se ejecuta en el entorno de CI.
