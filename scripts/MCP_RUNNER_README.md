Breve guía para arrancar los servidores MCP locales usados por el proyecto.

- `start_mcp_memory.ps1` : Arranca el servidor `memory`. Usa la variable de entorno `MEMORY_FILE_PATH` (por defecto crea `..\\.mcp_memory_store.json`).
- `start_mcp_sequentialthinking.ps1` : Arranca el servidor `sequentialthinking`.
- `start_mcp_pylance.ps1` : Arranca el servidor `pylance`.

Requisitos:
- Node.js y `npx` disponibles en PATH.

Uso rápido (PowerShell):

```powershell
cd scripts
.\start_mcp_memory.ps1 -MemoryFilePath "C:\\Users\\DELL\\Desktop\\BackendBot\\.mcp_memory_store.json"
.\start_mcp_sequentialthinking.ps1
.\start_mcp_pylance.ps1
```

Si el `memory` parece bloquearse, revisa el archivo de memoria y permisos, y arranca solo el `memory` primero para aislar problemas.
