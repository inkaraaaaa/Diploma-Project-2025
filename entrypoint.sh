#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
if [ "$DATABASE" = "postgres" ]; then
  echo "Waiting for PostgreSQL..."
  
  # Use a more reliable way to check if PostgreSQL is ready
  until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
  done
  
  echo "PostgreSQL started"
fi

# Create required directories
echo "Creating required directories..."
mkdir -p /app/staticfiles /app/static /app/media

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if not exists
echo "Setting up admin user..."
python manage.py shell -c "
from users.models import UserProfile;
if not UserProfile.objects.filter(username='admin').exists():
    UserProfile.objects.create_superuser('admin', 'admin@example.com', 'admin');
    print('Admin user created');
else:
    print('Admin user already exists');
"

# Run user creation script
echo "Creating additional users..."
python manage.py shell < /app/add_users.py || echo "Warning: Error in add_users.py, but continuing"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Apply proper permissions to static files
echo "Setting proper permissions for static files..."
chmod -R 755 /app/staticfiles
chmod -R 755 /app/static
chmod -R 755 /app/media

# Initialize SSL fix for email on container start
echo "Applying SSL fix for email..."
python -c "exec(open('/app/ssl_fix.py').read())"

# Start Gunicorn server
echo "Starting Gunicorn server..."
exec gunicorn testt.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120