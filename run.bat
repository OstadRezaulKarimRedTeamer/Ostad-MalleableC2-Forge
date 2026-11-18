@echo off
title Ostad Malleable C2 Forge - Launcher
cd /d "%~dp0"
echo =====================================================================
echo 🦅 OSTAD MALLEABLE C2 FORGE - ADVERSARY EMULATION & PROFILE SUITE
echo Official Tool by Ostad Red Team Forge (Founder: Ostad Rezaul Karim)
echo =====================================================================
echo.
echo [*] Launching Desktop GUI Workbench...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Application exited with error code %ERRORLEVEL%.
    pause
)
