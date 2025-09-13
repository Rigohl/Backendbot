# BackendBot Activity Monitor Configuration
# Copy this file to activity_monitor_config.ps1 and modify as needed

# Activity Monitoring Settings
$ActivityMonitorConfig = @{
    # Inactivity Detection
    InactivityThresholdMinutes = 5      # Minutes before showing inactivity warning
    ResponseTimeoutMinutes     = 3          # Minutes to wait for user response before shutdown

    # Backend Control
    BackendPath                = "src\backendbot\main.py"
    PythonPath                 = "python"
    AutoStartBackend           = $true
    AutoStopBackend            = $true

    # Notification Settings
    ShowNotifications          = $true
    NotificationTimeout        = 60            # Seconds to show notification
    UseSystemNotifications     = $true      # Try Windows notifications first
    FallbackToPopup            = $true             # Use PowerShell popup if Windows notifications fail

    # Logging
    LogFile                    = "logs\activity_monitor.log"
    LogLevel                   = "INFO"                   # DEBUG, INFO, WARN, ERROR
    MaxLogSizeMB               = 10
    MaxLogFiles                = 5

    # Advanced Settings
    CheckIntervalSeconds       = 30           # How often to check for activity
    CpuThresholdPercent        = 5             # CPU usage threshold to consider as activity
    ProcessCheckEnabled        = $true         # Check for active processes as activity indicator

    # System Integration
    RunAsService               = $false               # Install as Windows service (requires admin)
    ServiceName                = "BackendBotActivityMonitor"
    ServiceDisplayName         = "BackendBot Activity Monitor Service"

    # Security
    RequireAdminForService     = $true      # Require admin privileges for service installation
    SecureLogging              = $false              # Obfuscate sensitive information in logs
}

# Environment-specific overrides
$EnvironmentConfig = @{
    Development = @{
        InactivityThresholdMinutes = 10
        LogLevel                   = "DEBUG"
        ShowNotifications          = $false
    }

    Production  = @{
        InactivityThresholdMinutes = 5
        LogLevel                   = "INFO"
        RunAsService               = $true
        SecureLogging              = $true
    }

    Testing     = @{
        InactivityThresholdMinutes = 1
        ResponseTimeoutMinutes     = 1
        LogLevel                   = "DEBUG"
        ShowNotifications          = $false
    }
}

# Function to get current environment
function Get-CurrentEnvironment {
    # Check for environment indicators
    if ($env:COMPUTERNAME -like "*DEV*" -or $env:USERNAME -like "*dev*") {
        return "Development"
    }
    elseif (Test-Path "production.flag") {
        return "Production"
    }
    elseif (Test-Path "testing.flag") {
        return "Testing"
    }
    else {
        return "Production"  # Default to production
    }
}

# Function to apply environment-specific configuration
function Set-EnvironmentConfig {
    $environment = Get-CurrentEnvironment

    if ($EnvironmentConfig.ContainsKey($environment)) {
        $envConfig = $EnvironmentConfig[$environment]

        foreach ($key in $envConfig.Keys) {
            if ($ActivityMonitorConfig.ContainsKey($key)) {
                $ActivityMonitorConfig[$key] = $envConfig[$key]
                Write-Host "Applied environment override: $key = $($envConfig[$key])" -ForegroundColor Yellow
            }
        }

        Write-Host "Environment: $environment" -ForegroundColor Green
    }
}

# Function to validate configuration
function Test-Configuration {
    $isValid = $true
    $errors = @()

    # Validate paths
    if (-not (Test-Path $ActivityMonitorConfig.BackendPath)) {
        $errors += "Backend path not found: $($ActivityMonitorConfig.BackendPath)"
        $isValid = $false
    }

    # Validate Python
    try {
        $pythonVersion = & $ActivityMonitorConfig.PythonPath --version 2>$null
        if (-not $pythonVersion) {
            $errors += "Python not found at: $($ActivityMonitorConfig.PythonPath)"
            $isValid = $false
        }
    }
    catch {
        $errors += "Python not accessible: $($ActivityMonitorConfig.PythonPath)"
        $isValid = $false
    }

    # Validate numeric values
    if ($ActivityMonitorConfig.InactivityThresholdMinutes -le 0) {
        $errors += "InactivityThresholdMinutes must be greater than 0"
        $isValid = $false
    }

    if ($ActivityMonitorConfig.ResponseTimeoutMinutes -le 0) {
        $errors += "ResponseTimeoutMinutes must be greater than 0"
        $isValid = $false
    }

    if ($ActivityMonitorConfig.CheckIntervalSeconds -le 0) {
        $errors += "CheckIntervalSeconds must be greater than 0"
        $isValid = $false
    }

    # Validate log level
    $validLogLevels = @("DEBUG", "INFO", "WARN", "ERROR")
    if ($ActivityMonitorConfig.LogLevel -notin $validLogLevels) {
        $errors += "Invalid LogLevel. Must be one of: $($validLogLevels -join ', ')"
        $isValid = $false
    }

    # Report errors
    if ($errors.Count -gt 0) {
        Write-Host "Configuration validation failed:" -ForegroundColor Red
        foreach ($err in $errors) {
            Write-Host "  - $err" -ForegroundColor Red
        }
    }
    else {
        Write-Host "Configuration validation passed" -ForegroundColor Green
    }

    return $isValid
}

# Function to display current configuration
function Show-Configuration {
    Write-Host "=== BackendBot Activity Monitor Configuration ===" -ForegroundColor Cyan
    Write-Host ""

    foreach ($key in $ActivityMonitorConfig.Keys | Sort-Object) {
        $value = $ActivityMonitorConfig[$key]
        $displayValue = if ($value -is [bool]) {
            if ($value) { "True" } else { "False" }
        }
        elseif ($value -is [int]) {
            $value.ToString()
        }
        else {
            $value
        }

        Write-Host ("{0,-30}: {1}" -f $key, $displayValue) -ForegroundColor White
    }

    Write-Host ""
    Write-Host "Environment: $(Get-CurrentEnvironment)" -ForegroundColor Yellow
}

# Apply environment configuration on load
Set-EnvironmentConfig

# Export configuration for use in other scripts
Export-ModuleMember -Variable ActivityMonitorConfig
Export-ModuleMember -Function Get-CurrentEnvironment, Set-EnvironmentConfig, Test-Configuration, Show-Configuration