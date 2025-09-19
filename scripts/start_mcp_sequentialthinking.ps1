Write-Host "Lanzando MCP Sequential Thinking via npx"
try {
    npx -y @modelcontextprotocol/server-sequential-thinking
} catch {
    Write-Error "Falló al lanzar Sequential Thinking. Asegúrate de tener Node.js y npx disponibles. Error: $_"
    exit 1
}
