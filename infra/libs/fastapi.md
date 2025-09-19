# FastAPI — Resumen y Guías Relevantes

- Instalación recomendada (incluye Uvicorn):

```bash
pip install "fastapi[standard]" "uvicorn[standard]" gunicorn
```

- Ejecución en desarrollo (autoreload):

```bash
uvicorn main:app --reload
```

- Producción con Uvicorn (ejemplo):

```bash
uvicorn main:app --host 0.0.0.0 --port 80 --proxy-headers
```

- Producción con Gunicorn + Uvicorn workers (proceso manager):

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80
```

- Pydantic Settings (archivo `config.py`):

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Awesome API"
    admin_email: str
    items_per_user: int = 50

settings = Settings()
```

- Dockerfile (ejemplo básico):

```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
```

Referencias: [FastAPI (tiangolo/fastapi)](https://github.com/tiangolo/fastapi)
