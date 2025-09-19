param(
    [string]$MemoryFilePath = "$PSScriptRoot\\..\\.mcp_memory_store.json",
    [int]$Port = 0
)

Write-Host "Iniciando MCP memory con archivo: $MemoryFilePath"

if (-not (Test-Path $MemoryFilePath)) {
    Write-Host "Archivo de memoria no encontrado. Creando: $MemoryFilePath"
    "[]" | Out-File -Encoding utf8 -FilePath $MemoryFilePath
}

# Establecer variable de entorno usada por la configuración MCP
$env:MEMORY_FILE_PATH = $MemoryFilePath

Write-Host "Lanzando MCP memory server (npx @modelcontextprotocol/server-memory)"
try {
    npx -y @modelcontextprotocol/server-memory
} catch {
    Write-Error "Falló al lanzar MCP memory. Asegúrate de tener Node.js y npx disponibles. Error: $_"
    exit 1
}
