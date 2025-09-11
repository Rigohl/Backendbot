@echo off`ncall "%~dp0stop_backend.bat"`ntimeout /t 1 >nul`ncall "%~dp0start_backend.bat"
