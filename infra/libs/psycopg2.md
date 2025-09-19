# psycopg2 — Guía rápida y ejemplos

- **Resumen**: Psycopg2 es el adaptador PostgreSQL más usado en Python. Soporta sincronía, pooling, y APIs de replicación/advanced.
- **Referencia**: [psycopg docs](https://www.psycopg.org/docs/)

## Ejemplos importantes

### Conexión básica

```python
import psycopg2
conn = psycopg2.connect("dbname=test user=postgres password=secret")
cur = conn.cursor()
cur.execute("SELECT 1")
print(cur.fetchone())
cur.close()
conn.close()
```

### Uso de contexto para transacciones

```python
with psycopg2.connect(DSN) as conn:
    with conn.cursor() as curs:
        curs.execute(SQL)
```

### Connection Pooling (Threaded / Simple)

```python
from psycopg2.pool import ThreadedConnectionPool
pool = ThreadedConnectionPool(minconn=1, maxconn=10, dsn=DSN)
conn = pool.getconn()
try:
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
finally:
    pool.putconn(conn)
```

### Parámetros y DSN helpers

```python
from psycopg2.extensions import make_dsn, parse_dsn
dsn = make_dsn('dbname=foo host=example.com', password='s3cr3t')
params = parse_dsn(dsn)
```

### Notas de producción

- Preferir pooling en apps que manejan concurrencia (ThreadedConnectionPool o external pooler como PgBouncer).
- Usar `autocommit` solo para operaciones DDL o management fuera de transacciones.
- Evitar construir SQL con string formatting — usar parámetros (`%s`) o `psycopg2.sql` para identificadores.
