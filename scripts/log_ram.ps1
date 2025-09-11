$csv = Join-Path $PSScriptRoot "..\logs\backend_ram.csv"
"timestamp,pid,ram_mb,privados_mb" | Out-File $csv -Encoding ascii
while ($true) {
  $p = Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('pythonw.exe','python.exe') -and $_.CommandLine -like '*BackendBot\backend.py*' }
  if ($p) {
    $line = "{0},{1},{2},{3}" -f (Get-Date -Format s), $p.ProcessId, ([math]::Round($p.WorkingSetSize/1MB,2)), ([math]::Round($p.PrivatePageCount/1MB,2))
    Add-Content $csv $line
  }
  Start-Sleep 5
}
