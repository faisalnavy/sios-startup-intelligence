@echo off
title SIOS Frontend
pushd "%~dp0frontend"

if not exist "node_modules" (
    echo Installing npm packages, please wait...
    npm install
)

echo.
echo  SIOS Frontend starting...
echo  App: http://localhost:3000
echo  Press Ctrl+C to stop
echo.

node node_modules/next/dist/bin/next dev
popd
pause
