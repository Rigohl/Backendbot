# python-dotenv

**Resumen**: `python-dotenv` carga variables desde un archivo `.env` a `os.environ` siguiendo las prácticas de 12-factor apps.

## Instalación

```bash
pip install python-dotenv
```

## Uso básico

```python
from dotenv import load_dotenv
load_dotenv()  # carga variables desde .env en el cwd o en padres
```

## Parsear a diccionario (sin modificar entorno)

```python
from dotenv import dotenv_values
config = dotenv_values('.env')
```

## CLI

```bash
pip install "python-dotenv[cli]"
dotenv set USER foo
dotenv run -- python app.py
```

## Notas de seguridad

- No commitear `.env` con secretos. Usar `gitignore` y/o secretos gestionados (KeyVault/Secret Manager).
- Para producción, preferir variables de entorno del entorno seguro o un secreto gestionado.
