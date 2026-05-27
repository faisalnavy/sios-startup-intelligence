@echo off
title SIOS Launcher
echo.
echo  Starting SIOS - Startup Intelligence Operating System
echo.

start "SIOS Backend"  cmd /k ""%~dp0start_backend.bat""
timeout /t 3 /nobreak >nul
start "SIOS Frontend" cmd /k ""%~dp0start_frontend.bat""

echo  Backend  ^>  http://localhost:8000
echo  Frontend ^>  http://localhost:3000
echo.
timeout /t 5 /nobreak >nul
start http://localhost:3000
