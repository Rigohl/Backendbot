# BackendBot Activity Monitor Setup and Installation Script
# This script sets up the complete activity monitoring system

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Test,
    [switch]$Configure,
    [switch]$Start,
    [switch]$Stop,
    [string]$ConfigFile = "activity_monitor_config.ps1"
)

# Configuration
$ScriptName = "BackendBot Activity Monitor Setup"
$ProjectRoot = $PSScriptRoot
$LogFile = Join-Path $ProjectRoot "logs\setup.log"

# Required files
$RequiredFiles = @(
    "src\backendbot\main.py",
    "src\backendbot\config.py",
    "src\backendbot\services\activity_monitor.py",
    "activity_monitor.ps1",
    "activity_monitor_config.ps1",
    "complete_automation.ps1",
    "test_activity_monitor.ps1"
)

# Function to write to log
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "$Timestamp [$Level] - $Message"

    # Write to console with color
    switch ($Level) {
        "ERROR" { Write-Host $LogMessage -ForegroundColor Red }
        "WARN" { Write-Host $LogMessage -ForegroundColor Yellow }
        "INFO" { Write-Host $LogMessage -ForegroundColor Green }
        "DEBUG" { Write-Host $LogMessage -ForegroundColor Gray }
        default { Write-Host $LogMessage }
    }

    # Write to file
    try {
        if (-not (Test-Path (Split-Path $LogFile -Parent))) {
            New-Item -ItemType Directory -Path (Split-Path $LogFile -Parent) -Force | Out-Null
        }
        Add-Content -Path $LogFile -Value $LogMessage -ErrorAction SilentlyContinue
    }
    catch {
        Write-Host "Error writing to log file: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Log "Checking prerequisites..."

    $prerequisites = @(
        @{
            Name    = "PowerShell Version"
            Test    = { $PSVersionTable.PSVersion -ge [version]"5.1" }
            Message = "PowerShell 5.1 or higher required"
        },
        @{
            Name    = "Python Installation"
            Test    = { Get-Command python -ErrorAction SilentlyContinue }
            Message = "Python must be installed and in PATH"
        },
        @{
            Name    = "BackendBot Files"
            Test    = { Test-Path "src\backendbot\main.py" }
            Message = "BackendBot main.py not found"
        },
        @{
            Name    = "Activity Monitor Service"
            Test    = { Test-Path "src\backendbot\services\activity_monitor.py" }
            Message = "Activity monitor service not found"
        },
        @{
            Name    = "Execution Policy"
            Test    = { (Get-ExecutionPolicy) -ne "Restricted" }
            Message = "PowerShell execution policy should not be Restricted"
        }
    )

    $allPassed = $true
    foreach ($prereq in $prerequisites) {
        try {
            if (& $prereq.Test) {
                Write-Log "✓ $($prereq.Name): OK"
            }
            else {
                Write-Log "✗ $($prereq.Name): $($prereq.Message)" "ERROR"
                $allPassed = $false
            }
        }
        catch {
            Write-Log "✗ $($prereq.Name): Test failed - $($_.Exception.Message)" "ERROR"
            $allPassed = $false
        }
    }

    return $allPassed
}

# Function to check file integrity
function Test-FileIntegrity {
    Write-Log "Checking file integrity..."

    $missingFiles = @()
    $corruptedFiles = @()

    foreach ($file in $RequiredFiles) {
        if (-not (Test-Path $file)) {
            $missingFiles += $file
        }
        else {
            # Basic corruption check (file size > 0)
            $fileInfo = Get-Item $file
            if ($fileInfo.Length -eq 0) {
                $corruptedFiles += $file
            }
        }
    }

    if ($missingFiles.Count -gt 0) {
        Write-Log "Missing files:" "ERROR"
        foreach ($file in $missingFiles) {
            Write-Log "  - $file" "ERROR"
        }
        return $false
    }

    if ($corruptedFiles.Count -gt 0) {
        Write-Log "Corrupted files:" "ERROR"
        foreach ($file in $corruptedFiles) {
            Write-Log "  - $file" "ERROR"
        }
        return $false
    }

    Write-Log "All required files present and valid"
    return $true
}

# Function to create necessary directories
function New-RequiredDirectories {
    Write-Log "Creating required directories..."

    $directories = @(
        "logs",
        "data",
        "scripts",
        "config"
    )

    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            try {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
                Write-Log "Created directory: $dir"
            }
            catch {
                Write-Log "Failed to create directory $dir : $($_.Exception.Message)" "ERROR"
                return $false
            }
        }
        else {
            Write-Log "Directory already exists: $dir"
        }
    }

    return $true
}

# Function to install the system
function Install-ActivityMonitor {
    Write-Log "Installing BackendBot Activity Monitor..."

    # 1. Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Log "Prerequisites check failed. Installation aborted." "ERROR"
        return $false
    }

    # 2. Check file integrity
    if (-not (Test-FileIntegrity)) {
        Write-Log "File integrity check failed. Installation aborted." "ERROR"
        return $false
    }

    # 3. Create directories
    if (-not (New-RequiredDirectories)) {
        Write-Log "Directory creation failed. Installation aborted." "ERROR"
        return $false
    }

    # 4. Configure system
    Write-Log "Configuring system..."
    try {
        # Import configuration
        . ".\$ConfigFile"

        # Test configuration
        if (Test-Configuration) {
            Write-Log "Configuration validated successfully"
        }
        else {
            Write-Log "Configuration validation failed" "WARN"
        }

        # Create desktop shortcut (optional)
        $shortcutPath = [Environment]::GetFolderPath("Desktop") + "\BackendBot Activity Monitor.lnk"
        if (-not (Test-Path $shortcutPath)) {
            $wshell = New-Object -ComObject WScript.Shell
            $shortcut = $wshell.CreateShortcut($shortcutPath)
            $shortcut.TargetPath = "powershell.exe"
            $shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$PSScriptRoot\complete_automation.ps1`" -Start -Background"
            $shortcut.WorkingDirectory = $PSScriptRoot
            $shortcut.Description = "BackendBot Activity Monitor"
            $shortcut.Save()
            Write-Log "Created desktop shortcut"
        }

        # Create startup script
        $startupScript = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup\BackendBot_Activity_Monitor.ps1"
        if (-not (Test-Path $startupScript)) {
            $startupContent = @"
# BackendBot Activity Monitor Startup Script
# This script starts the activity monitor when Windows starts

Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -File `"$PSScriptRoot\complete_automation.ps1`" -Start -Background" -WindowStyle Hidden
"@
            $startupContent | Out-File -FilePath $startupScript -Encoding UTF8
            Write-Log "Created startup script"
        }

    }
    catch {
        Write-Log "Configuration failed: $($_.Exception.Message)" "ERROR"
        return $false
    }

    # 5. Create installation log
    $installInfo = @{
        InstallDate       = Get-Date
        Version           = "1.0.0"
        InstallPath       = $PSScriptRoot
        ConfigFile        = $ConfigFile
        PowerShellVersion = $PSVersionTable.PSVersion.ToString()
    }

    $installInfo | ConvertTo-Json | Out-File -FilePath "config\installation.json" -Encoding UTF8
    Write-Log "Installation information saved"

    Write-Log "BackendBot Activity Monitor installed successfully!" "INFO"
    Write-Log "Run '.\complete_automation.ps1 -Start' to start the system" "INFO"

    return $true
}

# Function to uninstall the system
function Uninstall-ActivityMonitor {
    Write-Log "Uninstalling BackendBot Activity Monitor..."

    try {
        # Stop running processes
        Write-Log "Stopping running processes..."
        & ".\complete_automation.ps1" -Stop

        # Remove desktop shortcut
        $shortcutPath = [Environment]::GetFolderPath("Desktop") + "\BackendBot Activity Monitor.lnk"
        if (Test-Path $shortcutPath) {
            Remove-Item $shortcutPath -Force
            Write-Log "Removed desktop shortcut"
        }

        # Remove startup script
        $startupScript = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup\BackendBot_Activity_Monitor.ps1"
        if (Test-Path $startupScript) {
            Remove-Item $startupScript -Force
            Write-Log "Removed startup script"
        }

        # Remove installation info
        if (Test-Path "config\installation.json") {
            Remove-Item "config\installation.json" -Force
            Write-Log "Removed installation information"
        }

        # Remove logs (optional - ask user)
        $removeLogs = Read-Host "Remove log files? (y/N)"
        if ($removeLogs -eq "y" -or $removeLogs -eq "Y") {
            if (Test-Path "logs") {
                Remove-Item "logs" -Recurse -Force
                Write-Log "Removed log files"
            }
        }

        Write-Log "BackendBot Activity Monitor uninstalled successfully"
        return $true

    }
    catch {
        Write-Log "Uninstallation failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Function to run tests
function Invoke-SetupTests {
    Write-Log "Running setup tests..."

    # Run activity monitor tests
    if (Test-Path "test_activity_monitor.ps1") {
        Write-Log "Running activity monitor tests..."
        & ".\test_activity_monitor.ps1" -QuickTest
    }

    # Test configuration
    if (Test-Path $ConfigFile) {
        Write-Log "Testing configuration..."
        . ".\$ConfigFile"
        Test-Configuration
    }

    Write-Log "Setup tests completed"
}

# Function to show configuration
function Show-SetupConfiguration {
    Write-Log "=== BackendBot Activity Monitor Setup Configuration ==="

    if (Test-Path $ConfigFile) {
        Write-Log "Loading configuration from $ConfigFile..."
        . ".\$ConfigFile"
        Show-Configuration
    }
    else {
        Write-Log "Configuration file not found: $ConfigFile" "ERROR"
    }

    Write-Log "Required Files:"
    foreach ($file in $RequiredFiles) {
        $status = if (Test-Path $file) { "✓" } else { "✗" }
        Write-Log "  $status $file"
    }

    if (Test-Path "config\installation.json") {
        Write-Log "Installation Information:"
        $installInfo = Get-Content "config\installation.json" | ConvertFrom-Json
        Write-Log "  Installed: $($installInfo.InstallDate)"
        Write-Log "  Version: $($installInfo.Version)"
        Write-Log "  Path: $($installInfo.InstallPath)"
    }

    Write-Log "=================================="
}

# Main execution
Write-Log "=== $ScriptName ==="

try {
    if ($Install) {
        Write-Log "Command: Install System"
        if (Install-ActivityMonitor) {
            Write-Log "Installation completed successfully"
        }
        else {
            Write-Log "Installation failed" "ERROR"
            exit 1
        }
    }
    elseif ($Uninstall) {
        Write-Log "Command: Uninstall System"
        if (Uninstall-ActivityMonitor) {
            Write-Log "Uninstallation completed successfully"
        }
        else {
            Write-Log "Uninstallation failed" "ERROR"
            exit 1
        }
    }
    elseif ($Test) {
        Write-Log "Command: Run Tests"
        Invoke-SetupTests
    }
    elseif ($Configure) {
        Write-Log "Command: Show Configuration"
        Show-SetupConfiguration
    }
    elseif ($Start) {
        Write-Log "Command: Start System"
        & ".\complete_automation.ps1" -Start -Background
    }
    elseif ($Stop) {
        Write-Log "Command: Stop System"
        & ".\complete_automation.ps1" -Stop
    }
    else {
        Write-Log "Command: Show Status"
        Show-SetupConfiguration
    }

}
catch {
    Write-Log "Error: $($_.Exception.Message)" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "DEBUG"
    exit 1
}

# Usage information
if (-not ($Install -or $Uninstall -or $Test -or $Configure -or $Start -or $Stop)) {
    Write-Host ""
    Write-Host "Usage: $PSCommandPath [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor White
    Write-Host "  -Install     Install the activity monitor system" -ForegroundColor Gray
    Write-Host "  -Uninstall   Uninstall the activity monitor system" -ForegroundColor Gray
    Write-Host "  -Test        Run system tests" -ForegroundColor Gray
    Write-Host "  -Configure   Show current configuration" -ForegroundColor Gray
    Write-Host "  -Start       Start the complete system" -ForegroundColor Gray
    Write-Host "  -Stop        Stop the complete system" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "  $PSCommandPath -Install" -ForegroundColor Gray
    Write-Host "  $PSCommandPath -Test" -ForegroundColor Gray
    Write-Host "  $PSCommandPath -Start" -ForegroundColor Gray
    Write-Host ""
    Write-Host "For more information, see ACTIVITY_MONITOR_README.md" -ForegroundColor Yellow
}