# Uvicorn — Opciones y Uso

- Ejecutar en desarrollo:

```bash
uvicorn main:app --reload
```

- Opciones importantes:

  - `--workers`: número de procesos worker.
  - `--proxy-headers`: confiar en cabeceras `X-Forwarded-*` detrás de proxy.
  - `--root-path`: configurar raíz cuando se sirve desde un sub-path.

- Uso programático:

```python
import uvicorn

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=4)
```

Referencias: [Uvicorn - encode/uvicorn](https://www.uvicorn.org/)
