Get-Content (Join-Path $PSScriptRoot "..\logs\backend.log") -Tail 20 -Wait
