while ($true) {
  $p = Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('pythonw.exe','python.exe') -and $_.CommandLine -like '*BackendBot\backend.py*' }
  if ($p) {
    "$(Get-Date -Format HH:mm:ss) PID=$($p.ProcessId) RAM=$([math]::Round($p.WorkingSetSize/1MB,2)) MB Privados=$([math]::Round($p.PrivatePageCount/1MB,2)) MB"
  } else { "Backend no detectado..." }
  Start-Sleep 5
}
