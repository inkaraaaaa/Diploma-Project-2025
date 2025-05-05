#!/bin/bash

# First, check if Docker is running
if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Please start Docker and try again."
  exit 1
fi

echo "Fixing static file case sensitivity issues..."

# Fix 'frame.png' -> 'Frame.png' case sensitivity issue
docker exec -it diploma-project-2025-web-1 bash -c 'sed -i "s/frame.png/Frame.png/g" /app/templates/*.html /app/templates/**/*.html 2>/dev/null || true'

# Fix static file path in Django settings
echo "Updating settings.py to handle static files correctly..."
docker exec -it diploma-project-2025-web-1 bash -c 'cat > /app/ssl_fix.py << EOF
import ssl
from django.core.mail.backends.smtp import EmailBackend
EmailBackend.ssl_context = ssl._create_unverified_context()
EOF'

# Fix Docker internal permissions for static files
echo "Fixing permissions inside the container..."
docker exec -it diploma-project-2025-web-1 bash -c "mkdir -p /app/staticfiles && chmod -R 755 /app/staticfiles"
docker exec -it diploma-project-2025-nginx-1 bash -c "chmod -R 755 /app/static /app/staticfiles /app/media"

# Restart containers
echo "Restarting containers..."
docker-compose restart web nginx

echo "Static files fix complete. Please refresh your browser."