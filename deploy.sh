#!/bin/bash

# Deployment script for Intern Go Project
# This script automates the deployment process on Google Cloud Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    error "Do not run this script as root!"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    warn ".env file not found. Creating from template..."
    cp env.production.template .env
    warn "Please edit .env file with your configuration before running again!"
    exit 1
fi

# Load environment variables
source .env

log "Starting deployment process..."

# Validate required environment variables
required_vars=("POSTGRES_PASSWORD" "DJANGO_SECRET_KEY" "DJANGO_ALLOWED_HOSTS")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "change_this_secure_password" ] || [ "${!var}" = "change_this_very_long_secret_key_for_production" ]; then
        error "Please set $var in .env file"
    fi
done

# Create SSL directory and self-signed certificates if not exists
log "Setting up SSL certificates..."
mkdir -p nginx/ssl

if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    warn "SSL certificates not found. Creating self-signed certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    log "Self-signed certificates created. Consider using Let's Encrypt for production."
fi

# Stop existing containers if running
log "Stopping existing containers..."
docker-compose -f docker-compose.production.yml down --remove-orphans || true

# Remove old images to free up space
log "Cleaning up old Docker images..."
docker system prune -f || true

# Build and start new containers
log "Building and starting containers..."
docker-compose -f docker-compose.production.yml up -d --build

# Wait for services to be healthy
log "Waiting for services to be healthy..."
max_attempts=60
attempt=1

while [ $attempt -le $max_attempts ]; do
    if docker-compose -f docker-compose.production.yml ps | grep -q "healthy"; then
        log "Services are healthy!"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        error "Services failed to become healthy after $max_attempts attempts"
    fi
    
    log "Attempt $attempt/$max_attempts - waiting for services..."
    sleep 10
    attempt=$((attempt + 1))
done

# Show container status
log "Container status:"
docker-compose -f docker-compose.production.yml ps

# Show logs
log "Recent logs:"
docker-compose -f docker-compose.production.yml logs --tail=20

# Test the deployment
log "Testing deployment..."
sleep 5

if curl -f http://localhost:8080/health/ >/dev/null 2>&1; then
    log "✅ Deployment successful! Application is running on:"
    log "   HTTP: http://localhost:8080"
    if [ -f "nginx/ssl/cert.pem" ]; then
        log "   HTTPS: https://localhost (with self-signed certificate)"
    fi
    log ""
    log "Default admin credentials:"
    log "   Username: admin"
    log "   Password: IntGo12345"
    log ""
    log "To view logs: docker-compose -f docker-compose.production.yml logs -f"
    log "To stop: docker-compose -f docker-compose.production.yml down"
else
    error "❌ Deployment failed! Check logs: docker-compose -f docker-compose.production.yml logs"
fi 