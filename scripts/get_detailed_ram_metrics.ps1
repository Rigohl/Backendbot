# Get total physical memory
$totalMemory = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB

# Get available physical memory
$availableMemory = (Get-Counter '\Memory\Available MBytes').CounterSamples.Value / 1024

# Calculate used memory
$usedMemory = $totalMemory - $availableMemory

# Get top 5 processes by working set (RAM usage)
$topProcesses = Get-Process | Sort-Object -Property WS -Descending | Select-Object -First 5 Name, @{Name='WS_MB';Expression={$_.WS / 1MB}} | ConvertTo-Json -Compress

# Output as JSON
$output = @{
    TotalMemoryGB = [math]::Round($totalMemory, 2)
    AvailableMemoryGB = [math]::Round($availableMemory, 2)
    UsedMemoryGB = [math]::Round($usedMemory, 2)
    TopProcesses = $topProcesses | ConvertFrom-Json
}

$output | ConvertTo-Json -Compress