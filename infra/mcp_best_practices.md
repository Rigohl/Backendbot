<!-- Auto-generated guidance collected via MCP tools on 2025-09-19 -->
# Azure & App Best Practices (MCP snapshot)

Resumen rápido

- **Autenticación**: usar Managed Identity cuando la app corre en Azure; no hardcodear credenciales; usar Key Vault para secretos.

- **IaC**: preferir Bicep (archivos en `infra/`) para describir recursos y validar con `what-if`/`azd provision --preview` antes de desplegar.

- **Errores y resiliencia**: retries con backoff exponencial, logging estructurado y circuit-breakers según sea necesario.

- **Rendimiento**: connection pooling para DBs, timeouts y límites de concurrencia; configurar workers (uvicorn/gunicorn) en contenedores.

- **Seguridad**: encriptar datos en tránsito y en reposo, aplicar least-privilege RBAC y revisar accesos periódicamente.

Consideraciones para este repo

- Colocar plantillas Bicep bajo `infra/` (p. ej. `infra/main.bicep`) y documentar parámetros en `infra/README.md`.

- Evitar incluir `venv` ni artefactos locales en el repositorio; `.gitignore` ya actualizado.

- Para despliegues automáticos desde CI, usar Service Principal con permisos mínimos, o mejor: Managed Identity en los recursos de Azure y permisos en Key Vault.

FastAPI / Uvicorn recomendaciones (recopiladas)

- Ejecutar con `uvicorn main:app --host 0.0.0.0 --port 80` en contenedores; añadir `--proxy-headers` y `--root-path` si hay proxy inverso.

- Para producción, usar múltiples procesos: `uvicorn main:app --workers 4` o `gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --workers 4`.

- Docker CMD recomendado para este repo (ejemplo):

```dockerfile
CMD ["uvicorn", "run_backendbot:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
```

-- Para pruebas locales usar `uvicorn main:app --reload` o `fastapi dev main.py`.

SQLAlchemy / DB

- Usar consultas parametrizadas, índices adecuados y pool de conexiones.

- Mantener migraciones con `alembic` y controlar versiones en `infra/` si se despliega a Azure SQL o PostgreSQL.

Implementación y seguridad

- Nunca poner secretos en archivos fuente. Guardar valores sensibles en Key Vault y referenciarlos desde App Service / Container Apps mediante Managed Identity.

- Revisar permisos de acceso a Storage y DB por recurso (scopes mínimos).

Referencias rápidas

- FastAPI (deployment + uvicorn): [tiangolo/fastapi](https://github.com/tiangolo/fastapi)

- Uvicorn: [encode/uvicorn](https://github.com/encode/uvicorn)

- SQLAlchemy docs: [sqlalchemy.org](https://www.sqlalchemy.org/)

Notas del snapshot
-- Recolectado con MCP tools el 2025-09-19. Si quieres que lo suba a un MCP server/servicio propio, indícame el endpoint o la ruta donde lo guardamos.
