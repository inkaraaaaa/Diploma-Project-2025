#!/bin/bash
set -e

echo "🔧 Starting static files fix script..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
  echo "❌ Docker is not running. Please start Docker and try again."
  exit 1
fi

echo "🔍 Checking if containers are running..."
if ! docker-compose ps | grep -q "diploma-project-2025-web-1.*Up"; then
  echo "❌ Web container is not running. Please start containers first with docker-compose up -d"
  exit 1
fi

if ! docker-compose ps | grep -q "diploma-project-2025-nginx-1.*Up"; then
  echo "❌ Nginx container is not running. Please start containers first with docker-compose up -d"
  exit 1
fi

echo "🔄 Fixing static file case sensitivity issues..."

# Fix 'frame.png' -> 'Frame.png' case sensitivity issue
docker exec diploma-project-2025-web-1 bash -c 'sed -i "s/frame.png/Frame.png/g" /app/templates/*.html /app/templates/**/*.html 2>/dev/null || true'

# Fix static file path in Django settings
echo "📝 Updating SSL fix file..."
docker exec diploma-project-2025-web-1 bash -c 'cat > /app/ssl_fix.py << EOF
import ssl
from django.core.mail.backends.smtp import EmailBackend
EmailBackend.ssl_context = ssl._create_unverified_context()
EOF'

# Fix Docker internal permissions for static files
echo "🔒 Fixing permissions inside containers..."
docker exec diploma-project-2025-web-1 bash -c "mkdir -p /app/staticfiles /app/static /app/media && chmod -R 755 /app/staticfiles /app/static /app/media"
docker exec diploma-project-2025-nginx-1 bash -c "mkdir -p /app/staticfiles /app/static /app/media && chmod -R 755 /app/static /app/staticfiles /app/media"

# Collect static files again
echo "📦 Collecting static files again..."
docker exec diploma-project-2025-web-1 bash -c "python manage.py collectstatic --noinput --clear"

# Restart containers
echo "🔄 Restarting containers..."
docker-compose restart web nginx

echo "⏳ Waiting for containers to be ready again..."
sleep 5

echo "✅ Static files fix complete! Please refresh your browser."
echo "🌐 Your application should now be accessible at: http://localhost:80"