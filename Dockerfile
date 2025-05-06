FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Fix SSL certificate issue for email and create directory structure for static files
RUN echo "import ssl" > /app/ssl_fix.py \
    && echo "from django.core.mail.backends.smtp import EmailBackend" >> /app/ssl_fix.py \
    && echo "EmailBackend.ssl_context = ssl._create_unverified_context()" >> /app/ssl_fix.py \
    && mkdir -p /app/staticfiles /app/static

# Run entrypoint script
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]