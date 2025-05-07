# Debugging systemd Service for Docker Compose

Check these commands to debug the issue:

```bash
# 1. Check the service status for detailed errors
sudo systemctl status intern-go.service

# 2. Check systemd journal logs for more details
sudo journalctl -xe | grep intern-go

# 3. Find the exact location of docker-compose
which docker-compose

# 4. Check if docker-compose can run from the systemd service directory
cd /home/beimbet_m04/apps/Diploma-Project-2025
sudo docker-compose config

# 5. Run the command manually to see if it works
cd /home/beimbet_m04/apps/Diploma-Project-2025
sudo docker-compose up -d
```

## Alternative Service Configuration

Try this alternative service file format that uses multiple ExecStart commands:

```bash
sudo nano /etc/systemd/system/intern-go.service
```

```ini
[Unit]
Description=InternGo Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/home/beimbet_m04/apps/Diploma-Project-2025
ExecStartPre=/bin/sleep 10
ExecStart=/usr/bin/docker-compose up
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then reload and try again:

```bash
sudo systemctl daemon-reload
sudo systemctl start intern-go.service
```

## Another Alternative: Use a Shell Script

If the direct systemd approach isn't working, create a shell script:

```bash
sudo nano /home/beimbet_m04/apps/Diploma-Project-2025/start-service.sh
```

```bash
#!/bin/bash
cd /home/beimbet_m04/apps/Diploma-Project-2025
/usr/bin/docker-compose up -d
```

```bash
sudo chmod +x /home/beimbet_m04/apps/Diploma-Project-2025/start-service.sh
```

Then update the service file:

```bash
sudo nano /etc/systemd/system/intern-go.service
```

```ini
[Unit]
Description=InternGo Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/home/beimbet_m04/apps/Diploma-Project-2025/start-service.sh
ExecStop=/usr/bin/docker-compose -f /home/beimbet_m04/apps/Diploma-Project-2025/docker-compose.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Then reload and try again:

```bash
sudo systemctl daemon-reload
sudo systemctl start intern-go.service
```