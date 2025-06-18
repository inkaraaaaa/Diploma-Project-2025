# Intern Go Project - Google Cloud Platform Deployment Guide

This guide will walk you through deploying the Intern Go Project on Google Cloud Platform using a VM instance with Ubuntu 22.04.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Creating the VM Instance](#creating-vm-instance)
3. [Setting up the VM](#setting-up-vm)
4. [Deploying the Application](#deploying-application)
5. [SSL Configuration](#ssl-configuration)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

- Google Cloud Platform account with billing enabled
- Basic knowledge of Linux command line
- Domain name (optional, for SSL certificates)

## Creating VM Instance

### Step 1: Create a New VM Instance

1. **Go to Google Cloud Console**
   - Visit [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select an existing one

2. **Navigate to Compute Engine**
   - Go to `Compute Engine` > `VM instances`
   - Click `Create Instance`

3. **Configure the VM Instance**
   ```
   Name: intern-go-production
   Region: us-central1 (or your preferred region)
   Zone: us-central1-a (or auto)
   
   Machine Configuration:
   - Machine family: General-purpose
   - Series: E2
   - Machine type: e2-standard-2 (2 vCPU, 8 GB memory)
   
   Boot disk:
   - Operating System: Ubuntu
   - Version: Ubuntu 22.04 LTS
   - Boot disk type: Standard persistent disk
   - Size: 20 GB (minimum recommended)
   
   Firewall:
   ☑ Allow HTTP traffic
   ☑ Allow HTTPS traffic
   ```

4. **Click Create** to create the VM instance

### Step 2: Configure Firewall Rules

1. **Go to VPC Network > Firewall**
2. **Create firewall rules** for the application:

   ```bash
   # Allow HTTP traffic on port 80
   gcloud compute firewall-rules create allow-http-80 \
     --allow tcp:80 \
     --source-ranges 0.0.0.0/0 \
     --description "Allow HTTP traffic on port 80"

   # Allow HTTPS traffic on port 443
   gcloud compute firewall-rules create allow-https-443 \
     --allow tcp:443 \
     --source-ranges 0.0.0.0/0 \
     --description "Allow HTTPS traffic on port 443"

   # Allow development HTTP on port 8080 (optional)
   gcloud compute firewall-rules create allow-http-8080 \
     --allow tcp:8080 \
     --source-ranges 0.0.0.0/0 \
     --description "Allow HTTP traffic on port 8080"
   ```

## Setting up VM

### Step 1: Connect to Your VM

1. **SSH into your VM instance**
   - Click the SSH button next to your instance in the Google Cloud Console
   - Or use gcloud command:
   ```bash
   gcloud compute ssh intern-go-production
   ```

### Step 2: Initial System Setup

1. **Update the system**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install required packages**
   ```bash
   sudo apt install -y \
     apt-transport-https \
     ca-certificates \
     curl \
     gnupg \
     lsb-release \
     git \
     unzip \
     htop \
     ufw \
     fail2ban
   ```

3. **Configure firewall (UFW)**
   ```bash
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow ssh
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 8080/tcp
   sudo ufw --force enable
   ```

4. **Configure fail2ban (intrusion prevention)**
   ```bash
   sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

### Step 3: Install Docker and Docker Compose

1. **Install Docker**
   ```bash
   # Add Docker's official GPG key
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

   # Add Docker repository
   echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

   # Install Docker
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io

   # Add current user to docker group
   sudo usermod -aG docker $USER
   
   # Log out and log back in for group changes to take effect
   exit
   ```

2. **Re-connect to VM and install Docker Compose**
   ```bash
   # Download Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

   # Make it executable
   sudo chmod +x /usr/local/bin/docker-compose

   # Verify installation
   docker --version
   docker-compose --version
   ```

### Step 4: Setup Application Directory

1. **Create application directory**
   ```bash
   mkdir -p ~/intern-go
   cd ~/intern-go
   ```

2. **Clone the repository** (replace with your actual repository URL)
   ```bash
   git clone https://github.com/your-username/Diploma-Project-2025.git .
   ```

   Or upload files manually:
   ```bash
   # If you're uploading files manually, create the directory structure
   # and upload all project files to ~/intern-go/
   ```

## Deploying the Application

### Step 1: Configure Environment

1. **Create environment file**
   ```bash
   cd ~/intern-go
   cp env.production.template .env
   ```

2. **Edit the environment file**
   ```bash
   nano .env
   ```

   Update the following values:
   ```bash
   # Database Configuration
   POSTGRES_DB=intern_go
   POSTGRES_USER=admin
   POSTGRES_PASSWORD=YourSecurePasswordHere123!

   # Django Configuration
   DJANGO_SECRET_KEY=your-very-long-secret-key-here-make-it-random-and-secure
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=your-vm-external-ip,your-domain.com,localhost

   # Redis Configuration
   REDIS_PASSWORD=YourRedisPasswordHere123!

   # Email Configuration (update with your SMTP settings)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

   **To get your VM's external IP:**
   ```bash
   curl ifconfig.me
   ```

3. **Generate a strong Django secret key** (optional but recommended)
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

### Step 2: Deploy the Application

1. **Make the deployment script executable**
   ```bash
   chmod +x deploy.sh
   ```

2. **Run the deployment script**
   ```bash
   ./deploy.sh
   ```

   This script will:
   - Validate your environment configuration
   - Create SSL certificates (self-signed)
   - Build and start all Docker containers
   - Wait for services to be healthy
   - Test the deployment

3. **Verify the deployment**
   ```bash
   # Check container status
   docker-compose -f docker-compose.production.yml ps

   # Check logs
   docker-compose -f docker-compose.production.yml logs -f web
   ```

### Step 3: Access Your Application

1. **Get your VM's external IP**
   ```bash
   gcloud compute instances describe intern-go-production --zone=your-zone --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
   ```

2. **Access the application**
   - HTTP: `http://YOUR_EXTERNAL_IP:8080`
   - HTTPS: `https://YOUR_EXTERNAL_IP` (with self-signed certificate warning)

3. **Default login credentials**
   - Username: `admin`
   - Password: `IntGo12345`

## SSL Configuration

### Option 1: Self-Signed Certificates (Default)

The deployment script automatically creates self-signed certificates. This is suitable for testing but not recommended for production.

### Option 2: Let's Encrypt (Recommended for Production)

1. **Install Certbot**
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   ```

2. **Get SSL certificate** (replace with your domain)
   ```bash
   sudo certbot certonly --standalone -d your-domain.com
   ```

3. **Copy certificates to nginx directory**
   ```bash
   sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ~/intern-go/nginx/ssl/cert.pem
   sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ~/intern-go/nginx/ssl/key.pem
   sudo chown $USER:$USER ~/intern-go/nginx/ssl/*
   ```

4. **Update nginx configuration**
   ```bash
   nano ~/intern-go/nginx/nginx.production.conf
   ```
   
   Replace `server_name _;` with `server_name your-domain.com;`

5. **Restart nginx**
   ```bash
   docker-compose -f docker-compose.production.yml restart nginx
   ```

6. **Setup auto-renewal**
   ```bash
   echo "0 12 * * * /usr/bin/certbot renew --quiet && cd ~/intern-go && docker-compose -f docker-compose.production.yml restart nginx" | sudo crontab -
   ```

## Monitoring and Maintenance

### Daily Operations

1. **View application logs**
   ```bash
   cd ~/intern-go
   docker-compose -f docker-compose.production.yml logs -f web
   ```

2. **Monitor system resources**
   ```bash
   htop
   df -h
   docker stats
   ```

3. **Backup database**
   ```bash
   # Create backup directory
   mkdir -p ~/backups

   # Backup database
   docker-compose -f docker-compose.production.yml exec db pg_dump -U admin intern_go > ~/backups/backup_$(date +%Y%m%d_%H%M%S).sql
   ```

### Update Application

1. **Pull latest code**
   ```bash
   cd ~/intern-go
   git pull origin main
   ```

2. **Rebuild and restart**
   ```bash
   ./deploy.sh
   ```

### System Maintenance

1. **Update system packages**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Clean up Docker**
   ```bash
   docker system prune -f
   docker volume prune -f
   ```

3. **Monitor disk space**
   ```bash
   df -h
   # If running low on space, clean up old backups and Docker images
   ```

## Troubleshooting

### Common Issues

1. **Application not accessible**
   ```bash
   # Check if containers are running
   docker-compose -f docker-compose.production.yml ps

   # Check firewall rules
   sudo ufw status

   # Check nginx logs
   docker-compose -f docker-compose.production.yml logs nginx
   ```

2. **Database connection issues**
   ```bash
   # Check database container
   docker-compose -f docker-compose.production.yml logs db

   # Connect to database manually
   docker-compose -f docker-compose.production.yml exec db psql -U admin -d intern_go
   ```

3. **SSL certificate issues**
   ```bash
   # Check certificate files
   ls -la nginx/ssl/

   # Verify certificate
   openssl x509 -in nginx/ssl/cert.pem -text -noout
   ```

4. **Performance issues**
   ```bash
   # Check system resources
   htop
   free -h
   df -h

   # Check Docker stats
   docker stats

   # Restart services
   docker-compose -f docker-compose.production.yml restart
   ```

### Log Locations

- Application logs: `docker-compose logs web`
- Nginx logs: `docker-compose logs nginx`
- Database logs: `docker-compose logs db`
- System logs: `/var/log/syslog`

### Useful Commands

```bash
# Restart all services
docker-compose -f docker-compose.production.yml restart

# Stop all services
docker-compose -f docker-compose.production.yml down

# Start all services
docker-compose -f docker-compose.production.yml up -d

# View real-time logs
docker-compose -f docker-compose.production.yml logs -f

# Execute commands in containers
docker-compose -f docker-compose.production.yml exec web python manage.py shell
docker-compose -f docker-compose.production.yml exec db psql -U admin -d intern_go

# Scale web service (if needed)
docker-compose -f docker-compose.production.yml up -d --scale web=2
```

## Security Considerations

1. **Change default passwords** in the `.env` file
2. **Keep system updated** with security patches
3. **Monitor access logs** regularly
4. **Use strong SSL certificates** for production
5. **Configure proper backup strategy**
6. **Monitor resource usage** to prevent abuse

## Support

If you encounter issues:

1. Check the logs using the commands above
2. Ensure all environment variables are properly set
3. Verify firewall rules and port accessibility
4. Check Docker and system resources

For persistent issues, check the application's health endpoint at `/health/` and review container logs for specific error messages.

## Estimated Costs

**Google Cloud VM (e2-standard-2):**
- ~$50-70/month (varies by region and usage)
- Additional costs for network egress and storage

**To reduce costs:**
- Use `e2-micro` or `e2-small` for development/testing
- Set up automatic shutdown during non-business hours
- Use preemptible instances for development (not recommended for production)

---

**Deployment complete!** Your Intern Go application should now be running on Google Cloud Platform. 