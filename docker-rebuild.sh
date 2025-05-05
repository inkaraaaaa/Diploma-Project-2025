#!/bin/bash

# Stop any existing containers
echo "Stopping containers..."
docker-compose down -v

# Remove existing volumes for static files
echo "Removing static volumes..."
docker volume rm $(docker volume ls -q | grep static_volume) 2>/dev/null || true

# Build and start containers with a clean build
echo "Rebuilding and starting containers..."
docker-compose up -d --build --force-recreate

# Show container logs
echo "Showing container logs..."
docker-compose logs -f