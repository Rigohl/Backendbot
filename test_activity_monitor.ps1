# Test Script for BackendBot Activity Monitor
# This script tests the activity monitoring functionality

param(
    [int]$TestDurationMinutes = 2,
    [switch]$QuickTest,
    [switch]$FullTest
)

Write-Host "=== BackendBot Activity Monitor Test ===" -ForegroundColor Cyan
Write-Host "Test Duration: $TestDurationMinutes minutes" -ForegroundColor Yellow
Write-Host ""

# Import required functions from the main script
. ".\activity_monitor.ps1"

# Test 1: Backend status check
Write-Host "Test 1: Backend Status Check" -ForegroundColor Green
$backendRunning = Test-BackendRunning
Write-Host "Backend running: $backendRunning" -ForegroundColor $(if ($backendRunning) { "Green" } else { "Red" })

# Test 2: Idle time detection
Write-Host "`nTest 2: Idle Time Detection" -ForegroundColor Green
$idleTime = Get-IdleTimeMinutes
Write-Host "Current idle time: $([math]::Round($idleTime, 2)) minutes" -ForegroundColor Green

# Test 3: Notification system
Write-Host "`nTest 3: Notification System" -ForegroundColor Green
Write-Host "Testing notification (will show for 5 seconds)..." -ForegroundColor Yellow
Show-InactivityNotification -TimeoutMinutes 1 | Out-Null
Write-Host "Notification test completed" -ForegroundColor Green

# Test 4: Backend start/stop (only if not running)
if (-not $backendRunning) {
    Write-Host "`nTest 4: Backend Start/Stop" -ForegroundColor Green
    Write-Host "Starting backend for test..." -ForegroundColor Yellow
    $job = Start-BackendProcess

    if ($job) {
        Write-Host "Backend started successfully" -ForegroundColor Green
        Start-Sleep -Seconds 5

        Write-Host "Stopping backend..." -ForegroundColor Yellow
        Stop-BackendProcess
        Write-Host "Backend stopped" -ForegroundColor Green
    }
    else {
        Write-Host "Failed to start backend" -ForegroundColor Red
    }
}
else {
    Write-Host "`nTest 4: Backend Start/Stop - SKIPPED (Backend already running)" -ForegroundColor Yellow
}

# Test 5: Activity simulation (if QuickTest is specified)
if ($QuickTest) {
    Write-Host "`nTest 5: Activity Simulation" -ForegroundColor Green
    Write-Host "Move mouse or press a key within 10 seconds to simulate activity..." -ForegroundColor Yellow

    $startTime = Get-Date
    $activityDetected = $false

    while ((Get-Date) - $startTime).TotalSeconds -lt 10) {
    $currentIdle = Get-IdleTimeMinutes
    if ($currentIdle -lt 0.1) {
        $activityDetected = $true
        break
    }
    Start-Sleep -Seconds 1
}

if ($activityDetected) {
    Write-Host "Activity detected successfully!" -ForegroundColor Green
}
else {
    Write-Host "No activity detected within timeout" -ForegroundColor Red
}
}

# Test 6: Configuration validation
Write-Host "`nTest 6: Configuration Validation" -ForegroundColor Green
$requiredFiles = @(
    "src\backendbot\main.py",
    "src\backendbot\config.py",
    "src\backendbot\services\activity_monitor.py"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file exists" -ForegroundColor Green
    }
    else {
        Write-Host "✗ $file missing" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if ($allFilesExist) {
    Write-Host "All required files present" -ForegroundColor Green
}
else {
    Write-Host "Some required files are missing" -ForegroundColor Red
}

# Test 7: Full monitoring simulation (if FullTest is specified)
if ($FullTest) {
    Write-Host "`nTest 7: Full Monitoring Simulation" -ForegroundColor Green
    Write-Host "This will run a $TestDurationMinutes minute monitoring simulation..." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop early" -ForegroundColor Yellow

    try {
        # Simulate monitoring for the specified duration
        $endTime = (Get-Date).AddMinutes($TestDurationMinutes)
        $activityCount = 0

        while ((Get-Date) -lt $endTime) {
            $idleTime = Get-IdleTimeMinutes
            $backendStatus = Test-BackendRunning

            if ($idleTime -lt 1) {
                $activityCount++
            }

            Write-Host "$(Get-Date -Format 'HH:mm:ss') - Idle: $([math]::Round($idleTime, 1))m, Backend: $backendStatus, Activity Count: $activityCount" -ForegroundColor Gray
            Start-Sleep -Seconds 10
        }

        Write-Host "Monitoring simulation completed" -ForegroundColor Green
        Write-Host "Total activity detections: $activityCount" -ForegroundColor Green

    }
    catch {
        Write-Host "`nMonitoring simulation interrupted" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "Activity Monitor tests completed" -ForegroundColor Green
Write-Host "Check the log file for detailed information" -ForegroundColor Yellow
Write-Host ""
Write-Host "To run the actual monitor:" -ForegroundColor White
Write-Host "  .\activity_monitor.ps1 -Monitor" -ForegroundColor White
Write-Host ""
Write-Host "To run with custom settings:" -ForegroundColor White
Write-Host "  .\activity_monitor.ps1 -Monitor -InactivityThresholdMinutes 10 -ResponseTimeoutMinutes 5" -ForegroundColor White