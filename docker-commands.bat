@echo off
REM SecureMyAI Docker Management Script for Windows

echo 🛡️ SecureMyAI Docker Management
echo ================================

if "%1"=="build" (
    echo 🔨 Building SecureMyAI Docker image...
    docker-compose build
) else if "%1"=="up" (
    echo 🚀 Starting SecureMyAI...
    docker-compose up -d
    echo ✅ SecureMyAI is running at http://localhost:8501
) else if "%1"=="down" (
    echo 🛑 Stopping SecureMyAI...
    docker-compose down
) else if "%1"=="restart" (
    echo 🔄 Restarting SecureMyAI...
    docker-compose restart
) else if "%1"=="logs" (
    echo 📋 Showing logs...
    docker-compose logs -f
) else if "%1"=="shell" (
    echo 🐚 Opening shell in container...
    docker-compose exec securemyai /bin/bash
) else if "%1"=="clean" (
    echo 🧹 Cleaning up Docker resources...
    docker-compose down -v
    docker system prune -f
) else if "%1"=="status" (
    echo 📊 Container status:
    docker-compose ps
) else (
    echo Usage: %0 {build^|up^|down^|restart^|logs^|shell^|clean^|status}
    echo.
    echo Commands:
    echo   build   - Build the Docker image
    echo   up      - Start the application
    echo   down    - Stop the application
    echo   restart - Restart the application
    echo   logs    - Show application logs
    echo   shell   - Open shell in container
    echo   clean   - Clean up Docker resources
    echo   status  - Show container status
) 