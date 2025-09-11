# BackendBot Verification Script
# Runs multiple verification tasks in parallel using PowerShell jobs

param(
    [string]$ProjectPath = $PSScriptRoot,
    [int]$TestTimeout = 300,
    [int]$ServerTimeout = 60
)

Write-Host "=== BackendBot Verification ===" -ForegroundColor Cyan
Write-Host "Project Path: $ProjectPath" -ForegroundColor Yellow

# Function to run tests
function Test-BackendTests {
    param([string]$TestFile)
    Write-Host "Running tests for $TestFile..." -ForegroundColor Green
    try {
        $output = & python -m pytest $TestFile -v --tb=short 2>&1
        return @{
            File = $TestFile
            Output = $output
            Success = $LASTEXITCODE -eq 0
        }
    } catch {
        return @{
            File = $TestFile
            Output = $_.Exception.Message
            Success = $false
        }
    }
}

# Function to start backend server
function Start-BackendServer {
    Write-Host "Starting backend server..." -ForegroundColor Green
    try {
        $process = Start-Process -FilePath "python" -ArgumentList "-m uvicorn src.backendbot.main:app --host 127.0.0.1 --port 8000 --reload" -NoNewWindow -PassThru
        Start-Sleep -Seconds 5  # Wait for server to start
        if (!$process.HasExited) {
            return @{
                Process = $process
                Success = $true
                Output = "Server started successfully on port 8000"
            }
        } else {
            return @{
                Process = $null
                Success = $false
                Output = "Server failed to start"
            }
        }
    } catch {
        return @{
            Process = $null
            Success = $false
            Output = $_.Exception.Message
        }
    }
}

# Function to test API endpoints
function Test-APIEndpoints {
    Write-Host "Testing API endpoints..." -ForegroundColor Green
    try {
        # Test health endpoint
        $healthResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/docs" -Method GET -TimeoutSec 10
        $apiTest = @{
            HealthCheck = $healthResponse.StatusCode -eq 200
            Response = $healthResponse.Content
        }
        return @{
            Success = $apiTest.HealthCheck
            Output = "API test completed. Health check: $($apiTest.HealthCheck)"
            Details = $apiTest
        }
    } catch {
        return @{
            Success = $false
            Output = "API test failed: $($_.Exception.Message)"
            Details = $null
        }
    }
}

# Function to simulate process monitoring
function Test-ProcessMonitoring {
    Write-Host "Simulating process monitoring..." -ForegroundColor Green
    try {
        # Create a test process that uses CPU
        $testScript = @"
import time
import psutil
import os

# Simulate high CPU usage for 10 seconds
def cpu_intensive():
    for _ in range(1000000):
        pass

start_time = time.time()
while time.time() - start_time < 10:
    cpu_intensive()

print("Test process completed")
"@

        $testScript | Out-File -FilePath "test_process.py" -Encoding UTF8
        $process = Start-Process -FilePath "python" -ArgumentList "test_process.py" -NoNewWindow -PassThru

        # Wait for monitoring to detect it
        Start-Sleep -Seconds 15

        # Check logs for monitoring activity
        if (Test-Path "logs/backend.log") {
            $logContent = Get-Content "logs/backend.log" -Tail 20
            $monitoringDetected = $logContent | Select-String -Pattern "alto consumo|suspendido|ignorado"
            return @{
                Success = $true
                Output = "Process monitoring simulation completed. Log entries found: $($monitoringDetected.Count)"
                LogEntries = $logContent
            }
        } else {
            return @{
                Success = $false
                Output = "Log file not found"
                LogEntries = $null
            }
        }
    } catch {
        return @{
            Success = $false
            Output = "Process monitoring simulation failed: $($_.Exception.Message)"
            LogEntries = $null
        }
    } finally {
        # Cleanup
        if (Test-Path "test_process.py") { Remove-Item "test_process.py" }
        if ($process -and !$process.HasExited) { $process.Kill() }
    }
}

# Function to check notifications
function Test-Notifications {
    Write-Host "Checking notification system..." -ForegroundColor Green
    try {
        # This would require platform-specific checks
        # For now, just check if notification functions are callable
        $notificationTest = python -c "
from src.backendbot.utils import notify
notify('Test Notification', 'This is a test from verification script')
print('Notification function executed successfully')
" 2>&1

        return @{
            Success = $LASTEXITCODE -eq 0
            Output = "Notification test: $($notificationTest)"
        }
    } catch {
        return @{
            Success = $false
            Output = "Notification check failed: $($_.Exception.Message)"
        }
    }
}

# Main verification logic
Write-Host "Starting parallel verification tasks..." -ForegroundColor Cyan

# Start jobs for different verification tasks
$testJob = Start-Job -ScriptBlock ${function:Run-Tests} -ArgumentList "tests/test_api_routes.py"
$serverJob = Start-Job -ScriptBlock ${function:Start-BackendServer}
$apiJob = Start-Job -ScriptBlock ${function:Test-APIEndpoints}
$monitoringJob = Start-Job -ScriptBlock ${function:Simulate-ProcessMonitoring}
$notificationJob = Start-Job -ScriptBlock ${function:Check-Notifications}

# Wait for all jobs to complete with timeout
$jobs = @($testJob, $serverJob, $apiJob, $monitoringJob, $notificationJob)
$timeout = 300  # 5 minutes timeout
$startTime = Get-Date

Write-Host "Waiting for verification tasks to complete..." -ForegroundColor Yellow

while ((Get-Date) - $startTime).TotalSeconds -lt $timeout) {
    $completedJobs = $jobs | Where-Object { $_.State -eq "Completed" }
    if ($completedJobs.Count -eq $jobs.Count) {
        break
    }
    Start-Sleep -Seconds 5
    Write-Host "Progress: $($completedJobs.Count)/$($jobs.Count) tasks completed..." -ForegroundColor Yellow
}

# Collect results
$results = @{}
foreach ($job in $jobs) {
    if ($job.State -eq "Completed") {
        $result = Receive-Job -Job $job
        $results[$job.Name] = $result
    } else {
        $results[$job.Name] = @{
            Success = $false
            Output = "Job timed out or failed"
        }
    }
    Remove-Job -Job $job
}

# Display results
Write-Host "`n=== Verification Results ===" -ForegroundColor Cyan
$overallSuccess = $true

foreach ($key in $results.Keys) {
    $result = $results[$key]
    $status = if ($result.Success) { "✅ PASS" } else { "❌ FAIL" }
    Write-Host "$key : $status" -ForegroundColor (if ($result.Success) { "Green" } else { "Red" })
    Write-Host "  Output: $($result.Output)" -ForegroundColor Gray
    if (!$result.Success) { $overallSuccess = $false }
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
if ($overallSuccess) {
    Write-Host "🎉 All verification tasks passed! Backend is working correctly." -ForegroundColor Green
} else {
    Write-Host "⚠️ Some verification tasks failed. Check the details above." -ForegroundColor Red
}

# Cleanup
Write-Host "`nCleaning up..." -ForegroundColor Yellow
Get-Job | Remove-Job -Force

Write-Host "Verification complete." -ForegroundColor Cyan
