@echo off
title Build Ostad Malleable C2 Client Agent (C++)
cd /d "%~dp0"
echo =====================================================================
echo 🦅 BUILDING OSTAD MALLEABLE C2 CLIENT (NATIVE C++)
echo Ostad Red Team Forge • Elite Offensive Security Edition
echo =====================================================================
echo.

:: MSVC
where cl.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [*] Compiling with MSVC (cl.exe)...
    cl.exe /std:c++17 /O2 /Iinclude client\main_client.cpp ws2_32.lib /Fe:OstadC2_Client.exe
    goto DONE
)

:: MinGW
where g++.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [*] Compiling with MinGW GCC (g++)...
    g++.exe -std=c++17 -O3 -Iinclude client\main_client.cpp -lws2_32 -o OstadC2_Client.exe
    goto DONE
)

:: Clang++
where clang++.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [*] Compiling with Clang++...
    clang++.exe -std=c++17 -O3 -Iinclude client\main_client.cpp -lws2_32 -o OstadC2_Client.exe
    goto DONE
)

echo [!] No C++ compiler found in PATH.
pause
exit /b 1

:DONE
if exist OstadC2_Client.exe (
    echo [✓] Client build successful: OstadC2_Client.exe
) else (
    echo [!] Client build failed.
)
pause
