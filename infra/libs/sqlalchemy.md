# SQLAlchemy — Notas rápidas

- Usar `create_engine` con pool y timeouts apropiados:

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://user:pass@db:5432/app",
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)
```

- En FastAPI, usar sesiones por-request y cerrar correctamente.

Referencias: [SQLAlchemy](https://www.sqlalchemy.org/)
