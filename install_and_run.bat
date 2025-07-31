@echo off
echo ============================================================
echo 🏛️  AnwaltsAI - Installing Dependencies and Starting App
echo ============================================================

REM Set Python path
set PYTHON_PATH=C:\Program Files\Python312\python.exe

REM Check if Python exists
if not exist "%PYTHON_PATH%" (
    echo ❌ Python not found at %PYTHON_PATH%
    echo Please install Python 3.12 first
    pause
    exit /b 1
)

echo ✅ Python found, installing dependencies...
"%PYTHON_PATH%" -m pip install --user flask flask-cors requests pyjwt

echo.
echo 🚀 Starting AnwaltsAI Backend Server...
cd /d "%~dp0law-firm-ai"
start "AnwaltsAI Backend" "%PYTHON_PATH%" enhanced_api_server.py

echo.
echo 🌐 Starting Frontend Web Server...
cd /d "%~dp0Client"
start "AnwaltsAI Frontend" "%PYTHON_PATH%" -m http.server 8080

echo.
echo ⏳ Waiting for servers to start...
timeout /t 5 /nobreak >nul

echo.
echo 🎉 AnwaltsAI is now running!
echo.
echo 📋 Access Information:
echo 🔧 Backend API:      http://localhost:5001
echo 🌐 Frontend App:     http://localhost:8080/anwalts-ai-app.html  
echo 📊 Health Check:     http://localhost:5001/health
echo.
echo 🔑 Default Login:
echo 📧 Email:           admin@anwalts-ai.de
echo 🔐 Password:        admin123
echo.
echo 🚀 Opening application in browser...
timeout /t 2 /nobreak >nul
start "" "http://localhost:8080/anwalts-ai-app.html"

echo.
echo ✨ AnwaltsAI is ready! Press any key to stop all services...
pause >nul

echo.
echo 🛑 Stopping services...
taskkill /f /im python.exe >nul 2>&1
echo ✅ All services stopped.
pause