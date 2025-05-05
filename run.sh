#!/bin/bash

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install django psycopg2-binary Pillow

# Fix Python SSL certificate verification for MacOS
if [[ "$OSTYPE" == "darwin"* ]]; then
  # On macOS, create a new file to bypass SSL verification
  cat > $(pwd)/users/ssl_bypass.py << EOF
import ssl
import os

# Create unverified SSL context for email
def get_unverified_ssl_context():
    ssl_context = ssl._create_unverified_context()
    return ssl_context

# Apply the patch to the email backend
os.environ['PYTHONHTTPSVERIFY'] = '0'
EOF

  # Update the send_verification_code function to import and use the unverified SSL context
  sed -i.bak "s/from django.conf import settings/from django.conf import settings\nimport ssl\nfrom django.core.mail.backends.smtp import EmailBackend\nEmailBackend.ssl_context = ssl._create_unverified_context()/g" users/views.py
fi

# Use SQLite database by default
# The settings.py file has been modified already to use SQLite

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Start the development server
echo "Starting development server..."
python manage.py runserver 0.0.0.0:8000

echo "Server running at http://127.0.0.1:8000/"