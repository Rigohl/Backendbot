MCP Servers runner

- `runner.clean.js` : supervisor that launches MCP servers defined in `mcp_servers.json`.
- Logs: `logs/*.log` and `logs/*.err`.

Optional servers (pylance/context7)
- The public npm registry does not include `@modelcontextprotocol/server-pylance` or `server-context7`.
- To enable them, either:
  - Provide a tarball or git URL and edit `mcp_servers.json` `args` to point to it (e.g. `npx user/server-pylance`), or
  - Publish to a private registry and set npm to use it, or
  - Build locally and run via `node path/to/server.js`.

Running

PowerShell (background job):

```powershell
Start-Job -ScriptBlock { node c:\path\to\runner.clean.js --port 3020 > c:\path\to\logs\runner.log 2>&1 } | Out-Null
``` 

Or foreground:

```powershell
node c:\path\to\runner.clean.js --port 3020
```

Notes
- `mcp_servers.json` supports `pkg` to check availability (`npm view`) before starting optional servers.
- Each server entry can include `env` (object) and `restartDelayMs` (number).
