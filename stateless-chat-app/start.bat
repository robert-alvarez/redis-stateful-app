@echo off
REM Redis Memory Magic - Quick Start Script for Windows

echo.
echo Starting Redis Memory Magic Chat Application...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo No .env file found. Creating from .env.example...
    if exist .env.example (
        copy .env.example .env >nul
        echo Created .env file. Please edit it with your OpenAI API key if needed.
        echo.
    ) else (
        echo .env.example not found. You may need to configure environment variables manually.
    )
)

REM Start docker-compose
echo Starting Docker containers...
docker-compose up -d

REM Wait for services to start
echo.
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

echo.
echo ===============================================================
echo   Redis Memory Magic is ready!
echo ===============================================================
echo.
echo   Frontend UI:  http://localhost:3000
echo   Backend API:  http://localhost:9090
echo   API Docs:     http://localhost:9090/docs
echo.
echo ===============================================================
echo.
echo Tips:
echo   - View logs:        docker-compose logs -f
echo   - Stop app:         docker-compose down
echo   - Remove all data:  docker-compose down -v
echo.
echo Note: For vLLM provider, ensure your AWS vLLM server is running
echo       and configured in the .env file
echo.
echo Happy chatting!
echo.
pause
