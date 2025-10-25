#!/bin/bash

# Redis Memory Magic - Quick Start Script
echo "🚀 Starting Redis Memory Magic Chat Application..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your OpenAI API key if needed."
        echo ""
    else
        echo "⚠️  .env.example not found. You may need to configure environment variables manually."
    fi
fi

# Start docker-compose
echo "📦 Starting Docker containers..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

echo ""
echo "═══════════════════════════════════════════════════════"
echo "✨ Redis Memory Magic is ready!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "📱 Frontend UI:  http://localhost:3000"
echo "🔧 Backend API:  http://localhost:9090"
echo "📖 API Docs:     http://localhost:9090/docs"
echo ""
echo "═══════════════════════════════════════════════════════"
echo ""
echo "💡 Tips:"
echo "  • View logs:        docker-compose logs -f"
echo "  • Stop app:         docker-compose down"
echo "  • Remove all data:  docker-compose down -v"
echo ""
echo "⚠️  Note: For vLLM provider, ensure your AWS vLLM server is running"
echo "   and configured in the .env file"
echo ""
echo "🎉 Happy chatting!"
