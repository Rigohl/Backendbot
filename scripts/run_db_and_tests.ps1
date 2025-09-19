# Advanced PowerShell script to run database migrations and tests in parallel.

# --- Configuration ---
$maxConcurrentJobs = 2
$jobs = @()

# --- Helper Functions ---
function Start-JobWithLogging {
    param(
        [string]$Name,
        [scriptblock]$ScriptBlock
    )

    Write-Host "Starting job: $Name"
    $job = Start-Job -Name $Name -ScriptBlock $ScriptBlock
    $jobs += $job
    return $job
}

function Wait-AllJobs {
    Write-Host "Waiting for all jobs to complete..."
    Wait-Job -Job $jobs | Out-Null
    Write-Host "All jobs completed."
}

function Get-JobResults {
    Write-Host "--- Job Results ---"
    foreach ($job in $jobs) {
        Write-Host "Results for job: $($job.Name)"
        $result = Receive-Job -Job $job
        if ($result) {
            Write-Host $result
        }
        if ($job.State -eq 'Failed') {
            Write-Host "Job $($job.Name) failed. Reason:"
            Write-Host $job.ChildJobs[0].JobStateInfo.Reason.Message
        }
    }
    Write-Host "-------------------"
}

# --- Main Script ---
# 1. Run Database Migrations
$migrationJob = Start-JobWithLogging -Name "DB_Migrations" -ScriptBlock {
    Write-Host "Running Alembic migrations..."
    alembic upgrade head
    if ($LASTEXITCODE -ne 0) {
        throw "Alembic migration failed."
    }
    Write-Host "Alembic migrations completed."
}

# 2. Run Pytest Tests
$testJob = Start-JobWithLogging -Name "Pytest_Tests" -ScriptBlock {
    Write-Host "Running Pytest..."
    pytest
    if ($LASTEXITCODE -ne 0) {
        throw "Pytest execution failed."
    }
    Write-Host "Pytest completed."
}

# Wait for jobs to finish and get results
Wait-AllJobs
Get-JobResults

# Clean up jobs
Remove-Job -Job $jobs
