$pidFile = Join-Path $PSScriptRoot 'runner.pid'
if (Test-Path $pidFile) {
  $runnerPid = Get-Content $pidFile | Select-Object -First 1
  Write-Host "Stopping runner pid $runnerPid"
  try { Stop-Process -Id $runnerPid -Force -ErrorAction Stop } catch { Write-Warning "No se pudo detener el proceso: $_" }
  Remove-Item $pidFile -ErrorAction SilentlyContinue
} else {
  Write-Host "No se encontró runner.pid, buscando procesos node con runner.js"
  Get-Process node -ErrorAction SilentlyContinue | ForEach-Object {
    try {
      $p = $_
      $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)").CommandLine
      if ($cmd -and $cmd -like '*runner.js*') { Write-Host "Found candidate PID: $($p.Id) -> $cmd"; Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
    } catch { }
  }
}
