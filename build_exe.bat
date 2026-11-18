@echo off
title Build Ostad Malleable C2 Standalone Executable
cd /d "%~dp0"
echo =====================================================================
echo 🦅 COMPILING OSTAD MALLEABLE C2 FORGE TO STANDALONE EXE
echo Ostad Red Team Forge • Elite Offensive Security Edition
echo =====================================================================
echo.

where pyinstaller >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [!] PyInstaller not found. Installing...
    pip install pyinstaller
)

echo [*] Compiling OstadMalleableC2.exe with PyInstaller...
pyinstaller --noconfirm --onedir --windowed ^
    --name "OstadMalleableC2" ^
    --add-data "profiles;profiles" ^
    main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [✓] Build completed successfully!
    echo [✓] Binary location: dist\OstadMalleableC2\OstadMalleableC2.exe
) else (
    echo.
    echo [!] Build failed with error code %ERRORLEVEL%.
)
pause
