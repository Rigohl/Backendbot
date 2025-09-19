# Robocopy-based project consolidation script
# This script is more robust for merging directory trees.

$source_src = ".\src\backendbot"
$source_packages = ".\packages"
$destination = ".\backendbot"

Write-Host "Starting project consolidation..."

# --- Step 1: Merge src/backendbot into backendbot ---
Write-Host "Merging '$source_src' into '$destination'..."
robocopy $source_src $destination /E /MOVE /NFL /NDL /NJH /NJS /nc /ns /np
if ($LASTEXITCODE -ge 8) {
    Write-Error "Robocopy failed to merge '$source_src'. Aborting."
    exit 1
}
Write-Host "Merge of '$source_src' completed."

# --- Step 2: Merge packages into backendbot ---
Write-Host "Merging '$source_packages' into '$destination'..."
robocopy $source_packages $destination /E /MOVE /NFL /NDL /NJH /NJS /nc /ns /np
if ($LASTEXITCODE -ge 8) {
    Write-Error "Robocopy failed to merge '$source_packages'. Aborting."
    exit 1
}
Write-Host "Merge of '$source_packages' completed."


# --- Step 3: Clean up empty source directories ---
Write-Host "Cleaning up old directories..."
if (Test-Path -Path ".\src") {
    Remove-Item -Path ".\src" -Recurse -Force
    Write-Host "Removed 'src' directory."
}
if (Test-Path -Path ".\packages") {
    Remove-Item -Path ".\packages" -Recurse -Force
    Write-Host "Removed 'packages' directory."
}

Write-Host "Project consolidation finished successfully."
