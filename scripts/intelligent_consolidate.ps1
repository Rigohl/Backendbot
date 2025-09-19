# Intelligent consolidation script for BackendBot project

$destinationRoot = ".\backendbot"

Write-Host "Starting intelligent project consolidation..."

# --- Step 1: Find all Python files in src and app directories ---
$sourceDirs = @(".\src", ".\app")
$pyFiles = Get-ChildItem -Path $sourceDirs -Filter *.py -Recurse

Write-Host "Found $($pyFiles.Count) Python files to consolidate."

# --- Step 2: Move each file to the correct destination ---
foreach ($file in $pyFiles) {
    $relativePath = $file.FullName.Substring($pwd.Path.Length)
    
    # Determine the new path by removing 'src/backendbot' or 'app'
    $newRelativePath = $relativePath -replace '^\\src\\backendbot\\', '\' -replace '^\\app\\', '\'
    $newDestination = Join-Path -Path $destinationRoot -ChildPath $newRelativePath

    # Ensure the destination directory exists
    $destDir = Split-Path -Path $newDestination -Parent
    if (-not (Test-Path -Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }

    # Move the file
    Write-Host "Moving '$($file.FullName)' to '$newDestination'"
    Move-Item -Path $file.FullName -Destination $newDestination -Force
}

# --- Step 3: Clean up old directories ---
Write-Host "Cleaning up old source directories..."
if (Test-Path -Path ".\src") {
    Remove-Item -Path ".\src" -Recurse -Force
    Write-Host "Removed 'src' directory."
}
if (Test-Path -Path -Path ".\app") {
    Remove-Item -Path ".\app" -Recurse -Force
    Write-Host "Removed 'app' directory."
}

Write-Host "Project consolidation finished successfully."
