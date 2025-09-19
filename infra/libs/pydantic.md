# Pydantic / pydantic-settings — Configuración y Settings

- Definir `Settings` con `pydantic_settings.BaseSettings` y centralizar en `config.py`.

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    debug: bool = False
    database_url: str

settings = Settings()
```

- Evitar instanciar `Settings()` repetidamente en peticiones; cachear la instancia.

Referencias: [Pydantic](https://github.com/pydantic/pydantic)
