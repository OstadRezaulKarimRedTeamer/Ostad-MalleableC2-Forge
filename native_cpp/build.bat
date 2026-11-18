@echo off
title Build Ostad Malleable C2 (C++ Native)
cd /d "%~dp0"
echo =====================================================================
echo 🦅 BUILDING OSTAD MALLEABLE C2 FORGE (NATIVE C++ EDITION)
echo Ostad Red Team Forge • Elite Offensive Security Edition
echo =====================================================================
echo.

:: Check for cl.exe (MSVC)
where cl.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [*] Compiling with Microsoft Visual C++ (MSVC)...
    cl.exe /std:c++17 /O2 /Iinclude src\main.cpp /Fe:OstadMalleableC2.exe
    goto DONE
)

:: Check for g++ (MinGW)
where g++.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [*] Compiling with MinGW GCC (g++)...
    g++.exe -std=c++17 -O3 -Iinclude src\main.cpp -o OstadMalleableC2.exe
    goto DONE
)

:: Check for clang++
where clang++.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [*] Compiling with Clang++...
    clang++.exe -std=c++17 -O3 -Iinclude src\main.cpp -o OstadMalleableC2.exe
    goto DONE
)

echo [!] No C++ compiler (cl.exe, g++.exe, or clang++.exe) was found in PATH.
echo [*] Tip: Run from Developer Command Prompt for VS 2022, or install MinGW.
pause
exit /b 1

:DONE
if exist OstadMalleableC2.exe (
    echo.
    echo [✓] Build successful: OstadMalleableC2.exe
) else (
    echo.
    echo [!] Build failed.
)
pause
