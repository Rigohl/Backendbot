param(
  [int]$Port = 3010
)

$runnerPath = Join-Path $PSScriptRoot 'runner.clean.js'
if (-not (Test-Path $runnerPath)) { Write-Error "runner.js no encontrado en $PSScriptRoot"; exit 1 }

Write-Host "Starting MCP runner on port $Port"
$logsDir = Join-Path $PSScriptRoot 'logs'
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }
$outLog = Join-Path $logsDir 'runner.log'
$psCommand = "node `"$runnerPath`" > `"$outLog`" 2>&1"
Start-Process -FilePath 'powershell' -ArgumentList '-NoProfile','-WindowStyle','Hidden','-Command',$psCommand -PassThru | Out-Null
Start-Sleep -Seconds 1
Get-Content -Path $outLog -ErrorAction SilentlyContinue | Select-Object -Last 20
