# Consolidate project structure by moving content from src/backendbot to backendbot

# --- Configuration ---
$sourceDir = "src/backendbot"
$destinationDir = "backendbot"

# --- Main Script ---
if (-not (Test-Path -Path $sourceDir)) {
    Write-Host "Source directory $sourceDir does not exist. Nothing to do."
    exit 0
}

Write-Host "Consolidating project structure..."
Write-Host "Source: $sourceDir"
Write-Host "Destination: $destinationDir"

# Move contents of source to destination
Get-ChildItem -Path $sourceDir -Force | ForEach-Object {
    $destinationPath = Join-Path -Path $destinationDir -ChildPath $_.Name
    if (Test-Path -Path $destinationPath) {
        Write-Host "Conflict: $($_.Name) already exists in destination. Merging..."
        if ($_.PSIsContainer) {
            Move-Item -Path "$($_.FullName)/*" -Destination $destinationPath -Force
        } else {
            Move-Item -Path $_.FullName -Destination $destinationPath -Force
        }
    } else {
        Move-Item -Path $_.FullName -Destination $destinationPath -Force
    }
}

# Remove the now-empty source directory
Remove-Item -Path "src" -Recurse -Force

Write-Host "Project structure consolidated successfully."
