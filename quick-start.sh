#!/bin/bash

# Quick Start Script for Task Management API
# This script automates the initial setup process

set -e

echo "🚀 Task Management API - Quick Start"
echo "===================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please review and update if needed."
fi

# Stop existing containers
echo ""
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start services
echo ""
echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

# Wait for MySQL to be ready
echo ""
echo "⏳ Waiting for MySQL to be ready..."
sleep 10

# Run migrations
echo ""
echo "🔄 Running database migrations..."
docker-compose exec -T api python manage.py migrate

# Create superuser
echo ""
echo "👤 Creating superuser account..."
echo "   You'll be prompted for credentials..."
docker-compose exec api python manage.py createsuperuser

# Collect static files
echo ""
echo "📦 Collecting static files..."
docker-compose exec -T api python manage.py collectstatic --noinput

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Your API is now running:"
echo "   API: http://localhost:8000/api/v1/"
echo "   Admin: http://localhost:8000/admin/"
echo "   Swagger Docs: http://localhost:8000/api/docs/"
echo "   Health Check: http://localhost:8000/api/health/"
echo ""
echo "📚 Quick Commands:"
echo "   View logs: docker-compose logs -f api"
echo "   Run tests: docker-compose exec api pytest"
echo "   Stop services: docker-compose down"
echo "   Restart: docker-compose restart api"
echo ""
echo "🎉 Happy coding!"