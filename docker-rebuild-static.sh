#!/bin/bash
set -e

echo "🔄 Starting Docker rebuild with static files fix..."

# Stop any existing containers
echo "🛑 Stopping containers..."
docker-compose down

# Clean up volumes specifically for static files
echo "🧹 Cleaning up static volumes..."
docker volume rm $(docker volume ls -q | grep "diploma-project-2025_static_volume") 2>/dev/null || true

# Make sure scripts are executable
echo "🔧 Setting proper permissions on scripts..."
chmod +x entrypoint.sh
chmod +x fix-static.sh
chmod +x healthcheck.sh

# Build containers with a clean build
echo "🏗️ Rebuilding containers..."
docker-compose build --no-cache

# Start containers
echo "🚀 Starting containers..."
docker-compose up -d

# Give containers time to start and become healthy
echo "⏳ Waiting for containers to become healthy..."
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
  docker-compose logs web
  exit 1
fi

echo "✅ Web container is healthy!"

# Fix static files case sensitivity
echo "🔧 Running static files fix..."
./fix-static.sh

echo ""
echo "✅ Rebuild with static files fix completed successfully!"
echo "🌐 Your application is now running at:"
echo "   - Main site: http://localhost:80"
echo "   - Direct to Django: http://localhost:8000"
echo ""
echo "💻 To see container logs, run:"
echo "   docker-compose logs -f"
echo ""