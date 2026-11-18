@echo off
title Ostad Malleable C2 Forge - Master Build Suite
cd /d "%~dp0"
echo =====================================================================
echo 🦅 OSTAD MALLEABLE C2 FORGE - UNIFIED MASTER BUILD SCRIPT
echo Founder: Ostad Rezaul Karim (Top 1% Red Teamer)
echo Organization: Ostad Red Team Forge
echo =====================================================================
echo.

echo [1/2] Compiling Python Master GUI Suite to Standalone Executable...
call "%~dp0build_exe.bat"

echo.
echo [2/2] Checking C++ Native Build Environment...
if exist "%~dp0native_cpp\build.bat" (
    echo [*] To compile native C++ binaries, run: native_cpp\build.bat
)

echo.
echo =====================================================================
echo [✓] All C2 components unified and ready in this single directory!
echo =====================================================================
pause
