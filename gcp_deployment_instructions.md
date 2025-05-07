# Deployment Guide: InternGo on Google Cloud Platform

This guide provides detailed instructions for deploying the InternGo application on a new Google Cloud Platform (GCP) VM instance using Ubuntu 20.04, with only an external IP address.

## Prerequisites

- Google Cloud Platform account
- Git access to https://github.com/inkaraaaaa/Diploma-Project-2025

## Step 1: Create a New VM Instance

1. Sign in to Google Cloud Console at https://console.cloud.google.com/
2. Navigate to "Compute Engine" > "VM instances"
3. Click "Create Instance"
4. Configure the VM:
   - Name: `intern-go-vm`
   - Region/Zone: Choose a region close to your users
   - Machine Type: e2-medium (2 vCPU, 4GB memory)
   - Boot disk: Ubuntu 20.04 LTS
   - Boot disk size: 20GB or more
   - Firewall: Check "Allow HTTP traffic" and "Allow HTTPS traffic"
5. Click "Create"
6. Note your VM's external IP address - we'll use this throughout the guide

## Step 2: Connect to Your VM

1. In the Google Cloud Console, click on the "SSH" button next to your VM
2. A new browser window will open with a terminal session

## Step 3: Set Up Environment Variables

```bash
# Set your external IP as an environment variable
export VM_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")
echo "External IP: $VM_IP"

# Add to .bashrc for persistence
echo "export VM_IP=$VM_IP" >> ~/.bashrc
```

## Step 4: Install Required Packages

```bash
# Update package repositories
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common git

# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.6/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
/usr/local/bin/docker-compose --version
```

## Step 5: Log Out and Log Back In

For the group changes to take effect, log out and log back in:

```bash
exit
```

Click the SSH button again to reconnect.

## Step 6: Clone and Configure the Application

```bash
# Create application directory
mkdir -p ~/apps
cd ~/apps

# Clone the repository
git clone https://github.com/inkaraaaaa/Diploma-Project-2025.git
cd Diploma-Project-2025

# Retrieve external IP address again after reconnecting
export VM_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")
echo "External IP: $VM_IP"
```

## Step 7: Update Application Configuration Files

### 1. Update Docker Compose Configuration

```bash
# Edit docker-compose.yml
sudo nano docker-compose.yml
```

Find the DJANGO_ALLOWED_HOSTS line and update it to include your external IP:
```yaml
- DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,${VM_IP}
```

Wrap the Django secret key in quotes to prevent shell variable interpretation:
```yaml
- "DJANGO_SECRET_KEY=5=pi3$)$aip_04w286vi$=1b#$ffkim*b^3@lastlln8zp5d34"
```

Save and exit: Ctrl+O, Enter, Ctrl+X

### 2. Update Nginx Configuration

```bash
# Edit Nginx configuration
sudo nano nginx/nginx.conf
```

Find the server_name line and update it to include your external IP:
```nginx
server_name localhost ${VM_IP};
```

Save and exit: Ctrl+O, Enter, Ctrl+X

## Step 8: Deploy the Application

```bash
# Start the application in detached mode
sudo /usr/local/bin/docker-compose up -d --build
```

Check if all containers are running:
```bash
sudo /usr/local/bin/docker-compose ps
```

You should see three containers (web, db, nginx) all with "Up" status.

## Step 9: Set Up Automated Startup

### 1. Create Docker Compose Startup Script

```bash
# Create startup script
sudo nano ~/apps/Diploma-Project-2025/start-service.sh
```

Add the following content:
```bash
#!/bin/bash
cd /home/$(whoami)/apps/Diploma-Project-2025
/usr/local/bin/docker-compose up -d
```

Make the script executable:
```bash
sudo chmod +x ~/apps/Diploma-Project-2025/start-service.sh
```

### 2. Create Systemd Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/intern-go.service
```

Add the following content:
```ini
[Unit]
Description=InternGo Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/home/$(whoami)/apps/Diploma-Project-2025/start-service.sh
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Replace `$(whoami)` with your actual username (output of the `whoami` command) if the service fails to start.

### 3. Enable and Start the Service

```bash
# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable intern-go.service
sudo systemctl start intern-go.service

# Check service status
sudo systemctl status intern-go.service
```

## Step 10: Set Up Automated Monitoring and Backup

### 1. Create Monitoring Script

```bash
# Create monitoring script
sudo nano ~/monitor.sh
```

Add the following content:
```bash
#!/bin/bash

# Set variables
VM_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")
LOG_FILE=/home/$(whoami)/monitor.log
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check if containers are running
CONTAINER_COUNT=$(sudo docker ps -q | wc -l)
if [ $CONTAINER_COUNT -lt 3 ]; then
  echo "$DATE - Some containers are down. Restarting..." >> $LOG_FILE
  cd /home/$(whoami)/apps/Diploma-Project-2025
  sudo /usr/local/bin/docker-compose down
  sudo /usr/local/bin/docker-compose up -d
else
  echo "$DATE - All containers running ($CONTAINER_COUNT)" >> $LOG_FILE
fi
```

Make the script executable:
```bash
sudo chmod +x ~/monitor.sh
```

### 2. Create Database Backup Script

```bash
# Create backup script
sudo nano ~/backup-db.sh
```

Add the following content:
```bash
#!/bin/bash

# Set variables
BACKUP_DIR="/home/$(whoami)/backups"
DATE=$(date +%Y-%m-%d)
LOG_FILE=/home/$(whoami)/backup.log

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Log start of backup
echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting database backup" >> $LOG_FILE

# Backup the PostgreSQL database
cd /home/$(whoami)/apps/Diploma-Project-2025
sudo /usr/local/bin/docker-compose exec -T db pg_dump -U admin intern_go > $BACKUP_DIR/db_backup_$DATE.sql

# Check if backup was successful
if [ $? -eq 0 ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') - Backup successful: $BACKUP_DIR/db_backup_$DATE.sql" >> $LOG_FILE
else
  echo "$(date '+%Y-%m-%d %H:%M:%S') - Backup failed" >> $LOG_FILE
fi

# Keep only the last 7 days of backups
find $BACKUP_DIR -name "db_backup_*.sql" -type f -mtime +7 -delete
```

Make the script executable:
```bash
sudo chmod +x ~/backup-db.sh
```

### 3. Set Up Cron Jobs

```bash
# Edit crontab
crontab -e
```

Select an editor (nano is a good choice for beginners) and add the following lines:
```
# Run monitoring every 5 minutes
*/5 * * * * /home/$(whoami)/monitor.sh

# Run backup daily at 2 AM
0 2 * * * /home/$(whoami)/backup-db.sh
```

Save and exit.

## Step 11: Configure Firewall

```bash
# Install UFW (Uncomplicated Firewall)
sudo apt install -y ufw

# Set up basic firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Enable the firewall
sudo ufw enable

# Check status
sudo ufw status
```

## Step 12: Access Your Application

1. Open a web browser and navigate to:
   ```
   http://<YOUR-VM-IP>
   ```
   Replace `<YOUR-VM-IP>` with your VM's external IP address (echo $VM_IP)

2. Access the admin panel:
   ```
   http://<YOUR-VM-IP>/admin
   ```
   Login credentials:
   - Username: `admin`
   - Password: `IntGo12345`

## Step 13: Additional Security Measures

### 1. Set Up Automatic Security Updates

```bash
# Install unattended upgrades
sudo apt install -y unattended-upgrades

# Configure unattended upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 2. Change Default Passwords

After deployment, log in to the admin panel and change the default admin password.

## Troubleshooting

### Docker Compose Errors

If you see errors when running docker-compose commands:
```bash
# View Docker Compose logs
sudo /usr/local/bin/docker-compose logs

# Restart containers
sudo /usr/local/bin/docker-compose down
sudo /usr/local/bin/docker-compose up -d
```

### Database Connection Issues

If the application can't connect to the database:
```bash
# Check database logs
sudo /usr/local/bin/docker-compose logs db

# Test database connection
sudo /usr/local/bin/docker-compose exec web python manage.py shell -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('SELECT 1'); print('Database connection successful')"
```

### Nginx Issues

If the web server isn't responding:
```bash
# Check Nginx logs
sudo /usr/local/bin/docker-compose logs nginx

# Test Nginx configuration
sudo /usr/local/bin/docker-compose exec nginx nginx -t
```

### Systemd Service Issues

If the systemd service fails to start:
```bash
# Check service logs
sudo journalctl -u intern-go.service

# Update service file with absolute path
sudo nano /etc/systemd/system/intern-go.service
```

Update ExecStart with your actual username instead of $(whoami):
```ini
ExecStart=/home/your_actual_username/apps/Diploma-Project-2025/start-service.sh
```

## Maintenance

### Updating the Application

To update the application:
```bash
cd ~/apps/Diploma-Project-2025
git pull
sudo /usr/local/bin/docker-compose down
sudo /usr/local/bin/docker-compose up -d --build
```

### Checking Logs

```bash
# View all container logs
sudo /usr/local/bin/docker-compose logs

# View specific container logs
sudo /usr/local/bin/docker-compose logs web
sudo /usr/local/bin/docker-compose logs db
sudo /usr/local/bin/docker-compose logs nginx
```

### Viewing Monitoring Results

```bash
# View monitoring log
cat ~/monitor.log

# View backup log
cat ~/backup.log
```