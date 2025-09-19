Write-Host "Lanzando MCP Pylance via npx"
try {
    npx -y @modelcontextprotocol/server-pylance@latest
} catch {
    Write-Error "Falló al lanzar Pylance MCP. Asegúrate de tener Node.js y npx disponibles. Error: $_"
    exit 1
}
