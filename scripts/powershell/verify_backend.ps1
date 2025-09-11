# Script PowerShell para verificar backend - Tests en paralelo + ejecución
param(
    [switch]$RunTests,
    [switch]$RunBackend,
    [switch]$VerifyEndpoints,
    [switch]$All
)

$projectPath = "c:\Users\DELL\Desktop\BackendBot"
$testResultsPath = "$projectPath\test_results"
$backendLogPath = "$projectPath\backend_log.txt"

# Función para ejecutar tests en paralelo
function Run-ParallelTests {
    Write-Host "🔬 Ejecutando tests en paralelo..." -ForegroundColor Cyan

    # Crear directorio para resultados
    if (!(Test-Path $testResultsPath)) {
        New-Item -ItemType Directory -Path $testResultsPath | Out-Null
    }

    # Obtener archivos de test
    $testFiles = Get-ChildItem "$projectPath\tests\*.py" | Select-Object -ExpandProperty FullName

    # Crear jobs para cada test file
    $jobs = @()
    foreach ($testFile in $testFiles) {
        $fileName = [System.IO.Path]::GetFileNameWithoutExtension($testFile)
        $outputFile = "$testResultsPath\$fileName`_result.txt"

        $job = Start-Job -ScriptBlock {
            param($testFile, $outputFile, $projectPath)

            Set-Location $projectPath
            $env:PYTHONPATH = "$projectPath\src"

            # Ejecutar pytest en el archivo específico
            & python -m pytest $testFile -v --tb=short 2>&1 | Out-File $outputFile

            # Retornar código de salida
            $LASTEXITCODE
        } -ArgumentList $testFile, $outputFile, $projectPath

        $jobs += $job
    }

    # Esperar a que terminen todos los jobs
    Write-Host "⏳ Esperando que terminen los tests..." -ForegroundColor Yellow
    $jobs | Wait-Job | Out-Null

    # Recopilar resultados
    Write-Host "`n📊 RESULTADOS DE TESTS:" -ForegroundColor Green
    $totalPassed = 0
    $totalFailed = 0

    foreach ($job in $jobs) {
        $result = Receive-Job $job
        $fileName = [System.IO.Path]::GetFileNameWithoutExtension($job.Name)
        $outputFile = "$testResultsPath\$fileName`_result.txt"

        if (Test-Path $outputFile) {
            $content = Get-Content $outputFile -Raw
            Write-Host "`n--- $fileName ---" -ForegroundColor Magenta
            Write-Host $content

            # Contar passed/failed
            $passed = ($content | Select-String -Pattern "PASSED" -AllMatches).Matches.Count
            $failed = ($content | Select-String -Pattern "FAILED" -AllMatches).Matches.Count
            $totalPassed += $passed
            $totalFailed += $failed
        }

        Remove-Job $job
    }

    Write-Host "`n📈 RESUMEN TOTAL:" -ForegroundColor Cyan
    Write-Host "✅ Tests pasados: $totalPassed" -ForegroundColor Green
    Write-Host "❌ Tests fallidos: $totalFailed" -ForegroundColor Red

    return ($totalFailed -eq 0)
}

# Función para ejecutar el backend
function Start-BackendProcess {
    Write-Host "🚀 Iniciando backend..." -ForegroundColor Cyan

    Set-Location $projectPath
    $env:PYTHONPATH = "$projectPath\src"

    # Iniciar backend en background
    $backendJob = Start-Job -ScriptBlock {
        param($projectPath)
        Set-Location $projectPath
        $env:PYTHONPATH = "$projectPath\src"
        & python -m uvicorn backendbot.main:app --host 0.0.0.0 --port 8000 --reload 2>&1
    } -ArgumentList $projectPath

    # Esperar un poco para que inicie
    Start-Sleep -Seconds 5

    Write-Host "✅ Backend iniciado en http://localhost:8000" -ForegroundColor Green
    return $backendJob
}

# Función para verificar endpoints
function Test-BackendEndpoints {
    Write-Host "🔍 Verificando endpoints del backend..." -ForegroundColor Cyan

    $endpoints = @(
        "http://localhost:8000/",
        "http://localhost:8000/docs",
        "http://localhost:8000/system/info",
        "http://localhost:8000/processes",
        "http://localhost:8000/memory"
    )

    $results = @()

    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint -TimeoutSec 10
            $status = "✅ OK ($($response.StatusCode))"
            $results += @{Endpoint = $endpoint; Status = $status}
        } catch {
            $status = "❌ ERROR: $($_.Exception.Message)"
            $results += @{Endpoint = $endpoint; Status = $status}
        }
    }

    Write-Host "`n📋 RESULTADOS DE ENDPOINTS:" -ForegroundColor Green
    foreach ($result in $results) {
        Write-Host "$($result.Endpoint): $($result.Status)"
    }

    return ($results | Where-Object { $_.Status -notlike "*OK*" }).Count -eq 0
}

# Función principal
function Main {
    $allGood = $true

    if ($RunTests -or $All) {
        $testsPassed = Run-ParallelTests
        if (!$testsPassed) {
            $allGood = $false
            Write-Host "❌ Tests fallaron - revisar resultados en $testResultsPath" -ForegroundColor Red
        } else {
            Write-Host "✅ Todos los tests pasaron" -ForegroundColor Green
        }
    }

    if ($RunBackend -or $All) {
        $backendJob = Start-BackendProcess

        if ($VerifyEndpoints -or $All) {
            $endpointsOk = Test-BackendEndpoints
            if (!$endpointsOk) {
                $allGood = $false
                Write-Host "❌ Algunos endpoints fallaron" -ForegroundColor Red
            } else {
                Write-Host "✅ Todos los endpoints funcionan correctamente" -ForegroundColor Green
            }
        }

        # Detener backend
        Stop-Job $backendJob
        Remove-Job $backendJob
        Write-Host "🛑 Backend detenido" -ForegroundColor Yellow
    }

    if ($allGood) {
        Write-Host "`n🎉 ¡VERIFICACIÓN COMPLETA! El backend funciona correctamente." -ForegroundColor Green
        exit 0
    } else {
        Write-Host "`n⚠️  Hay problemas que requieren atención." -ForegroundColor Red
        exit 1
    }
}

# Ejecutar función principal
Main
