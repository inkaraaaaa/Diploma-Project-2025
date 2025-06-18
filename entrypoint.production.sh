#!/bin/bash
set -e

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Wait for PostgreSQL to be ready
if [ "$DATABASE" = "postgres" ]; then
    log "Waiting for PostgreSQL..."
    
    max_attempts=30
    attempt=1
    
    until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
        log "PostgreSQL is unavailable - attempt $attempt/$max_attempts"
        if [ $attempt -eq $max_attempts ]; then
            log "ERROR: PostgreSQL connection failed after $max_attempts attempts"
            exit 1
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    log "PostgreSQL connection established"
fi

# Apply database migrations
log "Applying database migrations..."
python manage.py migrate --noinput

# Create superuser if not exists
log "Setting up admin user..."
python manage.py shell -c "
from users.models import UserProfile;
from django.db import transaction;
try:
    with transaction.atomic():
        if not UserProfile.objects.filter(username='admin').exists():
            admin = UserProfile.objects.create_superuser('admin', 'admin@intern-go.com', 'IntGo12345');
            admin.first_name = 'System';
            admin.last_name = 'Administrator';
            admin.save();
            print('Admin user created successfully');
        else:
            admin = UserProfile.objects.get(username='admin');
            admin.set_password('IntGo12345');
            admin.save();
            print('Admin user password updated');
except Exception as e:
    print(f'Error setting up admin user: {e}');
"

# Run user creation script
log "Creating additional users..."
if [ -f "/app/add_users.py" ]; then
    python manage.py shell < /app/add_users.py || log "Warning: Error in add_users.py, but continuing"
else
    log "Warning: add_users.py not found, skipping additional user creation"
fi

# Collect static files
log "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Validate deployment
log "Validating Django deployment..."
python manage.py check --deploy

log "Starting Gunicorn server..."
exec gunicorn testt.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class sync \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --log-level info 