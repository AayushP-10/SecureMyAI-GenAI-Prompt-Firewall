#!/bin/bash

# SecureMyAI Docker Management Script

echo "🛡️ SecureMyAI Docker Management"
echo "================================"

case "$1" in
    "build")
        echo "🔨 Building SecureMyAI Docker image..."
        docker-compose build
        ;;
    "up")
        echo "🚀 Starting SecureMyAI..."
        docker-compose up -d
        echo "✅ SecureMyAI is running at http://localhost:8501"
        ;;
    "down")
        echo "🛑 Stopping SecureMyAI..."
        docker-compose down
        ;;
    "restart")
        echo "🔄 Restarting SecureMyAI..."
        docker-compose restart
        ;;
    "logs")
        echo "📋 Showing logs..."
        docker-compose logs -f
        ;;
    "shell")
        echo "🐚 Opening shell in container..."
        docker-compose exec securemyai /bin/bash
        ;;
    "clean")
        echo "🧹 Cleaning up Docker resources..."
        docker-compose down -v
        docker system prune -f
        ;;
    "status")
        echo "📊 Container status:"
        docker-compose ps
        ;;
    *)
        echo "Usage: $0 {build|up|down|restart|logs|shell|clean|status}"
        echo ""
        echo "Commands:"
        echo "  build   - Build the Docker image"
        echo "  up      - Start the application"
        echo "  down    - Stop the application"
        echo "  restart - Restart the application"
        echo "  logs    - Show application logs"
        echo "  shell   - Open shell in container"
        echo "  clean   - Clean up Docker resources"
        echo "  status  - Show container status"
        exit 1
        ;;
esac 