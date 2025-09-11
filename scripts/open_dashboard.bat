@echo off
setlocal

:: Define la URL del backend
set BACKEND_URL=http://127.0.0.1:8000/self

:: Define la ruta al script de inicio del backend
set START_BACKEND_SCRIPT="%~dp0start_backend.bat"

:: Define la ruta al dashboard
set DASHBOARD_PATH="%~dp0..\dashboard\index.html"

echo Verificando el estado del backend...

:: Función para verificar el backend
:check_backend
set "backend_up=0"

:: Intento con curl (si está disponible)
where curl >nul 2>nul
if %errorlevel% equ 0 (
    curl -s -o nul %BACKEND_URL%
    if %errorlevel% equ 0 (
        set "backend_up=1"
    )
) else (
    :: Si curl no esta, usa PowerShell
    powershell -command "try { Invoke-WebRequest -Uri %BACKEND_URL% -TimeoutSec 2 -ErrorAction Stop | Out-Null; exit 0 } catch { exit 1 }"
    if %errorlevel% equ 0 (
        set "backend_up=1"
    )
)

if %backend_up% equ 1 (
    echo Backend ya esta en ejecucion.
) else (
    echo Backend no esta en ejecucion. Iniciando...
    start "" %START_BACKEND_SCRIPT%
    timeout /t 5 >nul
    echo Esperando a que el backend se inicie...
    
    set "attempts=0"
    set "max_attempts=30" :: 30 attempts * 1 second sleep = 30 seconds timeout
    :wait_for_backend_loop
    if %attempts% ge %max_attempts% (
        echo El backend no se inicio a tiempo. Por favor, revisa los logs.
        goto :open_dashboard
    )

    :: Re-check backend status
    set "backend_up=0"
    where curl >nul 2>nul
    if %errorlevel% equ 0 (
        curl -s -o nul %BACKEND_URL%
        if %errorlevel% equ 0 (
            set "backend_up=1"
        )
    ) else (
        powershell -command "try { Invoke-WebRequest -Uri %BACKEND_URL% -TimeoutSec 2 -ErrorAction Stop | Out-Null; exit 0 } catch { exit 1 }"
        if %errorlevel% equ 0 (
            set "backend_up=1"
        )
    )

    if %backend_up% equ 0 (
        timeout /t 1 >nul
        set /a attempts+=1
        goto :wait_for_backend_loop
    )
    echo Backend iniciado.
)

:open_dashboard
echo Abriendo el dashboard...
start "" %DASHBOARD_PATH%

endlocal