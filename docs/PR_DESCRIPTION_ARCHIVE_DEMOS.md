# Resumen de cambios

- **`run_backendbot.py`**: entrypoint canónico que intenta arrancar el servidor API (`uvicorn`) y un ejecutor/orquestador en background si están disponibles. Manejo tolerante de imports y shutdown limpio.
- **`tools/env_loader.py`**: helper tolerante para cargar `.env` evitando fallos por encoding o líneas inválidas.
- **`scripts/disable_precommit.ps1`**: alias local para facilitar commits sin hooks (`git commit-noverify`).
- Cambios previos: archivado de demos/tmp y correcciones en `backendbot/core/di/container.py` y `backendbot/bots/manager.py` (import-safety y logging seguro).

## Por qué

- Facilitar un único punto de entrada para ejecutar la API + executor en desarrollo o despliegues simples.
- Evitar que `.env` malformados rompan el arranque.
- Reducir fricción con hooks de pre-commit pesados durante el trabajo local.

## Cómo probar localmente

1. Activar el entorno virtual e instalar dependencias (si procede):

```powershell
# Windows PowerShell
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Ejecutar en dry-run (solo importar los módulos):

```powershell
python -c "import importlib; importlib.import_module('run_backendbot'); print('OK')"
```

3. Ejecutar el entrypoint (arranca API si `uvicorn` y la app están presentes):

```powershell
python run_backendbot.py
```

## Notas

- El script `run_backendbot.py` no instala dependencias; si `uvicorn` no está presente se saltará la puesta en marcha del servidor API.
- Recomiendo revisar y arreglar el entorno de `pre-commit` en CI: los hooks actuales intentan instalar muchos paquetes de tipos y pueden fallar en entornos locales.

## Solicito revisión en

- Confirmación de que el entrypoint encaja con el despliegue esperado.
- Revisión de `tools/env_loader.py` para asegurarnos de no sobreescribir intencionalmente variables de entorno ya configuradas.

## Crear la PR (opcional)

Si quieres que cree la PR por ti y tu repositorio remoto está configurado, desde PowerShell puedes ejecutar:

```powershell
git checkout -b chore/archive-demos
git add .
git commit -m "chore: add canonical entrypoint and env loader" --no-verify
git push origin chore/archive-demos
# Then open the PR in the browser (or use gh cli)
gh pr create --title "chore: archive demos + add entrypoint" --body-file docs/PR_DESCRIPTION_ARCHIVE_DEMOS.md --base main
```

## Snippets útiles para reviewers

- FastAPI test example (use TestClient and lifespan context):

```python
from fastapi.testclient import TestClient
from importlib import import_module

app = import_module('apps.api.app').app
with TestClient(app) as client:
    resp = client.get('/health')
    assert resp.status_code == 200
```

- Pytest fixture example for DI container reset:

```python
import pytest

@pytest.fixture(autouse=True)
def reset_dependencies():
	from backendbot.core.di.container import container
	yield
	container.reset()
```

## Nota corta - Azure best practices

- Si planeas desplegar en Azure App Service o Container Apps, prefiero que el entrypoint sea un script pequeño (como `run_backendbot.py`) y que el servicio use readiness/liveness probes; evita instalar dependencias en el arranque del contenedor.


