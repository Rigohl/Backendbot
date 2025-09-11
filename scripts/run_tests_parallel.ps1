# Parallel test runner for Windows PowerShell
# Creates a background job per test file and collects results.
param(
    [string]$TestDir = "$PSScriptRoot\..\tests",
    [int]$MaxJobs = 4
)

Set-StrictMode -Version Latest
$testFiles = Get-ChildItem -Path $TestDir -Filter "test_*.py" -File | Select-Object -ExpandProperty FullName
if (-not $testFiles) {
    Write-Error "No test files found in $TestDir"
    exit 2
}

$jobs = @()
$resultsDir = Join-Path -Path $PSScriptRoot -ChildPath "test_results"
if (-not (Test-Path $resultsDir)) { New-Item -Path $resultsDir -ItemType Directory | Out-Null }

$semaphore = [System.Threading.SemaphoreSlim]::new($MaxJobs, $MaxJobs)

foreach ($file in $testFiles) {
    $semaphore.Wait()
    $outFile = Join-Path $resultsDir ([IO.Path]::GetFileNameWithoutExtension($file) + ".log")
    $job = Start-Job -ScriptBlock {
        param($f, $out)
        $env:PYTHONPATH = Join-Path $PSScriptRoot "..\src"
        pytest -q $f *>&1 | Tee-Object -FilePath $out
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } -ArgumentList $file, $outFile -Name (Split-Path $file -Leaf)
    $jobs += @{ Job = $job; Semaphore = $semaphore }
}

# Wait for all jobs
Wait-Job -Job ($jobs | ForEach-Object { $_.Job })

$exitCode = 0
foreach ($entry in $jobs) {
    $job = $entry.Job
    $semaphore.Release() | Out-Null
    $state = $job.State
    $name = $job.Name
    $log = Join-Path $resultsDir ($name + ".log")
    Write-Host "=== $name [$state] ==="
    if (Test-Path $log) { Get-Content $log -Raw | Write-Host }
    $job | Receive-Job -Keep | Out-Null
    if ($job.ChildJobs[0].ExitCode -ne 0) {
        $exitCode = $job.ChildJobs[0].ExitCode
    }
    Remove-Job -Job $job -Force
}

if ($exitCode -ne 0) {
    Write-Error "One or more test jobs failed. Exit code: $exitCode"
}
exit $exitCode
