# HTTPX — Cliente HTTP asíncrono

- Uso básico asíncrono:

```python
import httpx

async def fetch(url):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r.json()
```

- Reintentos y timeouts recomendados para llamadas externas.

Referencias: [HTTPX (encode/httpx)](https://www.python-httpx.org/)
