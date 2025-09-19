#!/usr/bin/env node
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
  // Port precedence: CLI --port, env MCP_RUNNER_PORT, default 3010
  const cliPortIndex = process.argv.indexOf('--port');
  let port = process.env.MCP_RUNNER_PORT ? parseInt(process.env.MCP_RUNNER_PORT, 10) : 3010;
  if (cliPortIndex !== -1 && process.argv.length > cliPortIndex + 1) {
    const p = parseInt(process.argv[cliPortIndex + 1], 10);
    if (!Number.isNaN(p)) port = p;
  }
  createHealthServer(port);
})();
