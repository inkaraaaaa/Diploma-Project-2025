#!/bin/bash

# Stop any existing containers
echo "Stopping any running containers..."
docker-compose down

# Build and start containers
echo "Building and starting containers..."
docker-compose up -d --build

# Show container logs
echo "Showing container logs..."
docker-compose logs -f