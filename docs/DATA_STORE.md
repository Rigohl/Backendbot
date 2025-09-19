Data Store Utility
===================

Descripción
-----------
`data_store` es un utilitario ligero que centraliza la lectura y escritura de archivos JSON en el directorio `.backendbot_data`.

Objetivos
---------
- Evitar excepciones por archivos vacíos o corruptos.
- Crear archivos por defecto si no existen.
- Proveer funciones simples: `read_json(name)`, `write_json(name, data)` e `initialize_defaults()`.

Uso
---
Desde Python:

```py
from src.backendbot.utils.data_store import read_json, write_json, initialize_defaults

# Asegurar que los archivos por defecto existen
initialize_defaults()

data = read_json('usage_patterns.json')
write_json('file_index.json', {'files': []})
```

Comportamiento
--------------
- Si el archivo no existe, `read_json` crea el archivo con un valor por defecto y lo retorna.
- Si el archivo existe pero está vacío o es inválido, `read_json` intenta respaldarlo y retorna el valor por defecto.
- `write_json` serializa JSON con identación y `ensure_ascii=False`.

Archivos por defecto
--------------------
- `usage_patterns.json` — {} por defecto
- `user_preferences.json` — {} por defecto
- `performance_metrics.json` — {} por defecto
- `scheduled_tasks.json` — [] por defecto
- `file_index.json` — {} por defecto

Notas
-----
Este utilitario se usa desde `AdaptiveLearningSystem`, `TaskScheduler` y `TaskIntegration` para mayor resiliencia en entornos de desarrollo y CI.
