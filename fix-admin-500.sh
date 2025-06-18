#!/bin/bash
set -e

echo "🔧 Fixing Django Admin 500 Error..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Copying fixed files to server...${NC}"

# Copy the fixed admin.py files and URLs to the server
scp -i ~/.ssh/google_cloud_key admin_panel/admin.py marbik@34.118.56.95:~/Diploma-Project-2025/admin_panel/
scp -i ~/.ssh/google_cloud_key company/admin.py marbik@34.118.56.95:~/Diploma-Project-2025/company/
scp -i ~/.ssh/google_cloud_key testt/urls.py marbik@34.118.56.95:~/Diploma-Project-2025/testt/
scp -i ~/.ssh/google_cloud_key testt/settings.py marbik@34.118.56.95:~/Diploma-Project-2025/testt/

echo -e "${YELLOW}Step 2: Restarting Django containers...${NC}"

# Restart the web container to apply changes
ssh -i ~/.ssh/google_cloud_key marbik@34.118.56.95 "cd ~/Diploma-Project-2025 && sudo docker-compose restart web"

echo -e "${YELLOW}Step 3: Waiting for containers to be ready...${NC}"
sleep 10

echo -e "${YELLOW}Step 4: Checking container status...${NC}"
ssh -i ~/.ssh/google_cloud_key marbik@34.118.56.95 "cd ~/Diploma-Project-2025 && sudo docker-compose ps"

echo -e "${GREEN}✅ Django Admin fix deployed successfully!${NC}"
echo -e "${GREEN}🌐 Try accessing the admin at: http://34.118.56.95/admin${NC}"
echo ""
echo -e "${YELLOW}If you still get errors, check logs with:${NC}"
echo "ssh -i ~/.ssh/google_cloud_key marbik@34.118.56.95 'sudo docker-compose logs web --tail=50'" 