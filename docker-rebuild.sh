#!/bin/bash
set -e

echo "🔄 Starting Docker rebuild process..."

# Stop any existing containers
echo "🛑 Stopping containers..."
docker-compose down

# Clean up volumes (optional - remove this if you want to preserve data)
echo "🧹 Cleaning up volumes..."
docker volume rm $(docker volume ls -q | grep "diploma-project-2025_static_volume\|diploma-project-2025_media_volume") 2>/dev/null || true

# Make sure script is executable
echo "🔧 Setting proper permissions..."
chmod +x entrypoint.sh
chmod +x fix-static.sh
chmod +x healthcheck.sh

# Build containers with a clean build
echo "🏗️ Rebuilding containers..."
docker-compose build --no-cache

# Start containers
echo "🚀 Starting containers..."
docker-compose up -d

# Wait for containers to be healthy
echo "⏳ Waiting for containers to be ready..."
attempt=1
max_attempts=20
until [ $(docker inspect --format='{{.State.Health.Status}}' diploma-project-2025-web-1 2>/dev/null) = "healthy" ] || [ $attempt -gt $max_attempts ]; do
  echo "⏱️ Waiting for web container to be healthy (attempt $attempt/$max_attempts)..."
  sleep 5
  attempt=$((attempt+1))
done

if [ $attempt -gt $max_attempts ]; then
  echo "❌ Web container failed to become healthy within the timeout period"
  echo "📋 Showing container logs for debugging..."
  docker-compose logs
  exit 1
fi

echo "✅ Web container is healthy!"

echo "🔎 Checking if nginx container is running..."
if [ $(docker inspect --format='{{.State.Running}}' diploma-project-2025-nginx-1 2>/dev/null) = "true" ]; then
  echo "✅ Nginx is running"
else
  echo "❌ Nginx container failed to start properly"
  echo "📋 Showing container logs for debugging..."
  docker-compose logs nginx
  exit 1
fi

# Show how to access
echo ""
echo "✅ Rebuild completed successfully!"
echo "🌐 Your application is now running at:"
echo "   - Main site: http://localhost:80"
echo "   - Direct to Django: http://localhost:8000"
echo ""
echo "💻 To see container logs, run:"
echo "   docker-compose logs -f"
echo ""