#!/usr/bin/env bash
# ==============================================================================
# FacultyIQ Development Environment Lifecycle Manager (Bash)
# ==============================================================================

set -e

ACTION=${1:-start}
DOCKER_COMPOSE_FILE="docker/docker-compose.yml"

echo "=========================================================="
echo "                FacultyIQ Dev Lifecycle Manager           "
echo "=========================================================="

case "$ACTION" in
    start)
        echo "[+] Starting infrastructure containers..."
        docker-compose -f $DOCKER_COMPOSE_FILE up -d
        echo "[+] Containers operational."
        ;;
    stop)
        echo "[-] Stopping infrastructure containers..."
        docker-compose -f $DOCKER_COMPOSE_FILE down
        echo "[-] Containers stopped."
        ;;
    restart)
        echo "[*] Restarting containers..."
        docker-compose -f $DOCKER_COMPOSE_FILE restart
        ;;
    build)
        echo "[+] Building ASP.NET Core 9 Backend..."
        dotnet build backend/FacultyIQ.sln --configuration Release
        echo "[+] Building Next.js Frontend..."
        (cd frontend && npm run build)
        echo "[+] Monorepo build completed successfully."
        ;;
    clean)
        echo "[!] Cleaning build artifacts..."
        find backend -type d \( -name bin -o -name obj \) -exec rm -rf {} +
        rm -rf frontend/.next
        echo "[!] Clean completed."
        ;;
    migrate)
        echo "[+] Applying Database Migrations..."
        dotnet ef database update --project backend/src/FacultyIQ.Persistence --startup-project backend/src/FacultyIQ.Api
        ;;
    health)
        echo "[*] Checking container health statuses..."
        docker-compose -f $DOCKER_COMPOSE_FILE ps
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|build|clean|migrate|health}"
        exit 1
        ;;
esac
