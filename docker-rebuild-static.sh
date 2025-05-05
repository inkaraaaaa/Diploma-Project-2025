#!/bin/bash

# Stop any existing containers
echo "Stopping containers..."
docker-compose down

# Build and restart with case sensitivity fix
echo "Rebuilding containers..."
docker-compose build --no-cache

# Start containers
echo "Starting containers..."
docker-compose up -d

# Give containers time to start
echo "Waiting for containers to start..."
sleep 10

# Fix static files case sensitivity
echo "Running static files fix..."
./fix-static.sh

echo "Done! Your application should now have working static files."
echo "Access your site at http://localhost:80"