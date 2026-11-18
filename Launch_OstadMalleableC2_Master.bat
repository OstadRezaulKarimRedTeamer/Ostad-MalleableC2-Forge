@echo off
title Ostad Malleable C2 Forge - Master Unified Dashboard
cd /d "%~dp0"
echo =====================================================================
echo 🦅 OSTAD MALLEABLE C2 FORGE - MASTER UNIFIED DASHBOARD
echo Founder: Ostad Rezaul Karim (Top 1% Red Teamer)
echo Organization: Ostad Red Team Forge
echo =====================================================================
echo.
echo [*] Launching Master Unified C2 Dashboard...

if exist "%~dp0MalleableC2\dist\OstadMalleableC2\OstadMalleableC2.exe" (
    start "" "%~dp0MalleableC2\dist\OstadMalleableC2\OstadMalleableC2.exe"
    exit /b 0
)

if exist "%~dp0MalleableC2\main.py" (
    cd /d "%~dp0MalleableC2"
    python main.py
    exit /b %ERRORLEVEL%
)

echo [!] Error: Executable or Python source not found.
pause
