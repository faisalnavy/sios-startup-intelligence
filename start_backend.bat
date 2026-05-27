@echo off
title SIOS Backend
echo.
echo  SIOS Backend starting on http://localhost:8000
echo  Press Ctrl+C to stop
echo.

powershell -NoProfile -Command "Start-Process python.exe -ArgumentList 'main.py' -WorkingDirectory '%~dp0backend' -NoNewWindow -Wait"
pause
