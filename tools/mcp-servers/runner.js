// MCP runner supervisor - clean single implementation
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const http = require('http');

const workspace = path.resolve(__dirname);
const logsDir = path.join(workspace, 'logs');
fs.mkdirSync(logsDir, { recursive: true });

const pidFile = path.join(workspace, 'runner.pid');
const configPath = path.join(workspace, 'mcp_servers.json');
const internalLog = path.join(logsDir, 'runner_internal.log');

function safeAppend(file, txt) {
  try { fs.appendFileSync(file, txt); } catch (e) { try { fs.appendFileSync(path.join(logsDir, 'runner_internal.err'), e.stack + '\n'); } catch (_) {} }
}

function loadConfig() {
  if (!fs.existsSync(configPath)) return [];
  try { return JSON.parse(fs.readFileSync(configPath, 'utf8')); } catch (e) { safeAppend(internalLog, `[${new Date().toISOString()}] config load error: ${e.stack}\n`); return []; }
}

const servers = loadConfig();
const procs = {};

function startServer(s) {
  const name = s.name;
  const outStream = fs.createWriteStream(path.join(logsDir, `${name}.log`), { flags: 'a' });
  const errStream = fs.createWriteStream(path.join(logsDir, `${name}.err`), { flags: 'a' });
  try {
    const child = spawn(s.cmd, s.args || [], { cwd: workspace, shell: true });
    procs[name] = { child, cfg: s };
    outStream.write(`[${new Date().toISOString()}] START ${name} ${s.cmd} ${(s.args || []).join(' ')}\n`);
    child.stdout.on('data', d => outStream.write(d));
    child.stderr.on('data', d => errStream.write(d));
    child.on('exit', (code, sig) => {
      outStream.write(`[${new Date().toISOString()}] EXIT ${name} code=${code} sig=${sig}\n`);
      if (!s.optional) {
        setTimeout(() => startServer(s), 3000);
      }
    });
  } catch (e) {
    try { errStream.write(`${new Date().toISOString()} FAILED ${name} ${e.stack}\n`); } catch (_) {}
  }
}

function isPackageAvailable(pkg) {
  return new Promise((resolve) => {
    if (!pkg) return resolve(false);
    const check = spawn('npm', ['view', pkg, 'version'], { shell: true });
    let out = '';
    check.stdout.on('data', d => out += d.toString());
    check.on('close', code => resolve(code === 0 && out.trim().length > 0));
    check.on('error', () => resolve(false));
  });
}

async function startAll() {
  for (const s of servers) {
    if (s.optional && s.pkg) {
      const ok = await isPackageAvailable(s.pkg);
      if (!ok) { safeAppend(internalLog, `[${new Date().toISOString()}] optional pkg ${s.pkg} not found, skipping ${s.name}\n`); continue; }
    }
    startServer(s);
  }
}

function writePid() { try { fs.writeFileSync(pidFile, String(process.pid)); } catch (e) {} }

function createHealthServer(port = 3010) {
  const server = http.createServer((req, res) => {
    if (req.url === '/health') {
      const status = {};
      for (const s of servers) status[s.name] = procs[s.name] && procs[s.name].child && !procs[s.name].child.killed ? 'running' : 'stopped';
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ pid: process.pid, status }));
      return;
    }
    if (req.url === '/status') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ children: Object.keys(procs) }));
      return;
    }
    res.writeHead(404); res.end('not found');
  });
  server.listen(port, () => { safeAppend(internalLog, `[${new Date().toISOString()}] health listening ${port}\n`); console.log('health', port); });
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));

function shutdown(reason) {
  safeAppend(internalLog, `[${new Date().toISOString()}] shutdown ${reason}\n`);
  for (const k of Object.keys(procs)) {
    try { procs[k].child.kill(); } catch (e) {}
  }
  try { fs.unlinkSync(pidFile); } catch (e) {}
  process.exit(0);
}

(async () => {
  writePid();
  await startAll();
  createHealthServer(process.env.MCP_RUNNER_PORT ? parseInt(process.env.MCP_RUNNER_PORT, 10) : 3010);
})();
// MCP runner supervisor (única implementación limpia)
// MCP runner supervisor (única implementación limpia)
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const http = require('http');

const workspace = path.resolve(__dirname);
const logsDir = path.join(workspace, 'logs');
if (!fs.existsSync(logsDir)) fs.mkdirSync(logsDir, { recursive: true });

const pidFile = path.join(workspace, 'runner.pid');
fs.writeFileSync(pidFile, String(process.pid));
const internalLog = path.join(logsDir, 'runner_internal.log');

// Leer configuración de servidores desde mcp_servers.json
let servers = [];
const configPath = path.join(workspace, 'mcp_servers.json');
try {
  const configRaw = fs.readFileSync(configPath, 'utf-8');
  servers = JSON.parse(configRaw);
} catch (e) {
  fs.appendFileSync(internalLog, `[${new Date().toISOString()}] ERROR: No se pudo leer mcp_servers.json: ${e.stack}\n`);
  process.exit(1);
}

const procs = {};

function safeAppend(file, txt) {
  try { fs.appendFileSync(file, txt); } catch (e) { try { fs.appendFileSync(path.join(logsDir, 'runner_internal.err'), e.stack + '\n'); } catch (_) {} }
}

function startServer(s) {
  const name = s.name;
  const outFile = path.join(logsDir, `${name}.log`);
  const errFile = path.join(logsDir, `${name}.err`);
  try {
    const p = spawn(s.cmd, s.args, { cwd: workspace, shell: true });
    procs[name] = { proc: p };
    safeAppend(internalLog, `[${new Date().toISOString()}] Starting ${name} ${s.cmd} ${s.args.join(' ')}\n`);
    p.stdout.on('data', d => { try { fs.appendFileSync(outFile, d); } catch (e) { safeAppend(internalLog, `stdout write ${name}: ${e.stack}\n`); } });
    p.stderr.on('data', d => { try { fs.appendFileSync(errFile, d); } catch (e) { safeAppend(internalLog, `stderr write ${name}: ${e.stack}\n`); } });
    p.on('exit', (code, sig) => {
      safeAppend(internalLog, `[${new Date().toISOString()}] ${name} exited code=${code} sig=${sig}\n`);
      if (!s.optional) setTimeout(() => startServer(s), 3000);
    });
  } catch (err) { safeAppend(errFile, `Failed to start ${name}: ${err.stack}\n`); }
}

function checkOptionalAndStart(s) {
  if (!s.optional) { startServer(s); return; }
  // Verificar si el paquete opcional está disponible
  const spawnSync = require('child_process').spawnSync;
  const raw = s.args && s.args[0] ? String(s.args[0]) : '';
  let pkg = raw;
  const at = raw.lastIndexOf('@'); if (at > 0) pkg = raw.slice(0, at);
  try {
  // MCP runner supervisor - implementación limpia y única
  const { spawn } = require('child_process');
  const fs = require('fs');
  const path = require('path');
  const http = require('http');

  const workspace = path.resolve(__dirname);
  const logsDir = path.join(workspace, 'logs');
  fs.mkdirSync(logsDir, { recursive: true });

  const pidFile = path.join(workspace, 'runner.pid');
  const configPath = path.join(workspace, 'mcp_servers.json');
  const internalLog = path.join(logsDir, 'runner_internal.log');

  function safeAppend(file, txt) {
    try { fs.appendFileSync(file, txt); } catch (e) { try { fs.appendFileSync(path.join(logsDir, 'runner_internal.err'), e.stack + '\n'); } catch (_) {} }
  }

  function loadConfig() {
    if (!fs.existsSync(configPath)) return [];
    try { return JSON.parse(fs.readFileSync(configPath, 'utf8')); } catch (e) { safeAppend(internalLog, `[${new Date().toISOString()}] config load error: ${e.stack}\n`); return []; }
  }

  const servers = loadConfig();
  const procs = {};

  function startServer(s) {
    const name = s.name;
    const outStream = fs.createWriteStream(path.join(logsDir, `${name}.log`), { flags: 'a' });
    const errStream = fs.createWriteStream(path.join(logsDir, `${name}.err`), { flags: 'a' });
    try {
      const child = spawn(s.cmd, s.args || [], { cwd: workspace, shell: true });
      procs[name] = { child, cfg: s };
      outStream.write(`[${new Date().toISOString()}] START ${name} ${s.cmd} ${ (s.args || []).join(' ') }\n`);
      child.stdout.on('data', d => outStream.write(d));
      child.stderr.on('data', d => errStream.write(d));
      child.on('exit', (code, sig) => {
        outStream.write(`[${new Date().toISOString()}] EXIT ${name} code=${code} sig=${sig}\n`);
        if (!s.optional) setTimeout(() => startServer(s), 3000);
      });
    } catch (e) {
      try { errStream.write(`${new Date().toISOString()} FAILED ${name} ${e.stack}\n`); } catch (_) {}
    }
  }

  function isPackageAvailable(pkg) {
    return new Promise((resolve) => {
      if (!pkg) return resolve(false);
      const check = spawn('npm', ['view', pkg, 'version'], { shell: true });
      let out = '';
      check.stdout.on('data', d => out += d.toString());
      check.on('close', code => resolve(code === 0 && out.trim().length > 0));
      check.on('error', () => resolve(false));
    });
  }

  async function startAll() {
    for (const s of servers) {
      if (s.optional && s.pkg) {
        const ok = await isPackageAvailable(s.pkg);
        if (!ok) { safeAppend(internalLog, `[${new Date().toISOString()}] optional pkg ${s.pkg} not found, skipping ${s.name}\n`); continue; }
      }
      startServer(s);
    }
  }

  function writePid() { try { fs.writeFileSync(pidFile, String(process.pid)); } catch (e) {} }

  function createHealthServer(port = 3010) {
    const server = http.createServer((req, res) => {
      if (req.url === '/health') {
        const status = {};
        for (const s of servers) status[s.name] = procs[s.name] && procs[s.name].child && !procs[s.name].child.killed ? 'running' : 'stopped';
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ pid: process.pid, status }));
        return;
      }
      if (req.url === '/status') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ children: Object.keys(procs) }));
        return;
      }
      res.writeHead(404); res.end('not found');
    });
    server.listen(port, () => { safeAppend(internalLog, `[${new Date().toISOString()}] health listening ${port}\n`); console.log('health', port); });
  }

  process.on('SIGINT', () => shutdown('SIGINT'));
  process.on('SIGTERM', () => shutdown('SIGTERM'));

  function shutdown(reason) {
    safeAppend(internalLog, `[${new Date().toISOString()}] shutdown ${reason}\n`);
    for (const k of Object.keys(procs)) {
      try { procs[k].child.kill(); } catch (e) {}
    }
    try { fs.unlinkSync(pidFile); } catch (e) {}
    process.exit(0);
  }

  (async () => {
    writePid();
    await startAll();
    createHealthServer(process.env.MCP_RUNNER_PORT ? parseInt(process.env.MCP_RUNNER_PORT, 10) : 3010);
  })();
          startServer(s);
        }, 3000);
      }
    });
  } catch (err) {
    fs.appendFileSync(path.join(logsDir, `${name}.err`), `Failed to start ${name}: ${err.stack}\n`);
  }
}

function startAll() {
  servers.forEach(s => {
    // check optional existence: try 'npm view' quickly
    if (s.optional) {
      const spawnSync = require('child_process').spawnSync;
      const name = s.args[0];
      try {
        const r = spawnSync('npm', ['view', name, 'version'], { encoding: 'utf8' });
        if (r.status !== 0) {
          fs.appendFileSync(path.join(logsDir, 'runner.err'), `[${new Date().toISOString()}] Optional server ${s.name} not available: ${r.stderr}\n`);
          return;
        }
      } catch (e) {
        fs.appendFileSync(path.join(logsDir, 'runner.err'), `[${new Date().toISOString()}] npm view check failed: ${e.stack}\n`);
        return;
      }
    }
    startServer(s);
  });
}

startAll();

// simple HTTP healthcheck server
const port = process.env.MCP_RUNNER_PORT ? parseInt(process.env.MCP_RUNNER_PORT, 10) : 3010;
const server = http.createServer((req, res) => {
  if (req.url === '/health' || req.url === '/status') {
    const status = {};
    servers.forEach(s => {
      status[s.name] = procs[s.name] && procs[s.name].proc && !procs[s.name].proc.killed ? 'running' : 'stopped';
    });
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ pid: process.pid, status }, null, 2));
    return;
  }
  res.writeHead(404);
  res.end('not found');
});
server.listen(port, () => {
  fs.appendFileSync(path.join(logsDir, 'runner.log'), `[${new Date().toISOString()}] MCP runner listening on ${port}\n`);
  console.log('MCP runner listening on', port);
});

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));

function shutdown(reason) {
  fs.appendFileSync(path.join(logsDir, 'runner.log'), `[${new Date().toISOString()}] Shutting down: ${reason}\n`);
  Object.keys(procs).forEach(k => {
    try { procs[k].proc.kill(); } catch (e) {}
  });
  try { fs.unlinkSync(pidFile); } catch (e) {}
  process.exit(0);
}
