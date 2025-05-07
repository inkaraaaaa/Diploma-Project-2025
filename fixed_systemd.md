# Fixing systemd Service for Docker Compose

The error `Job for intern-go.service failed because the control process exited with error code` indicates an issue with the systemd service configuration. Here's how to fix it:

## 1. Update the systemd service file

```bash
sudo nano /etc/systemd/system/intern-go.service
```

Replace the content with this more explicit configuration:

```ini
[Unit]
Description=InternGo Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/beimbet_m04/apps/Diploma-Project-2025
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Key changes:
- Using the full path to your project directory (not a variable)
- Using `/usr/bin/docker-compose` instead of `/usr/local/bin/docker-compose`

## 2. Reload systemd and start the service

```bash
sudo systemctl daemon-reload
sudo systemctl start intern-go.service
sudo systemctl status intern-go.service
```

## 3. If still encountering issues:

Check if docker-compose is actually in `/usr/bin`:

```bash
which docker-compose
```

If it shows a different path, update the service file with the correct path.

Also, try adding the full path to docker-compose in the ExecStart and ExecStop commands:

```ini
ExecStart=/usr/bin/docker-compose -f /home/beimbet_m04/apps/Diploma-Project-2025/docker-compose.yml up -d
ExecStop=/usr/bin/docker-compose -f /home/beimbet_m04/apps/Diploma-Project-2025/docker-compose.yml down
```

## 4. Make sure the WARN messages aren't causing issues

The warnings about variables not being set (`aip_04w286vi` and `ffkim`) might be related to your DJANGO_SECRET_KEY in docker-compose.yml. You can fix this by updating the docker-compose.yml file:

```bash
sudo nano /home/beimbet_m04/apps/Diploma-Project-2025/docker-compose.yml
```

Replace:
```yaml
- DJANGO_SECRET_KEY=5=pi3$)$aip_04w286vi$=1b#$ffkim*b^3@lastlln8zp5d34
```

With:
```yaml
- "DJANGO_SECRET_KEY=5=pi3$)$aip_04w286vi$=1b#$ffkim*b^3@lastlln8zp5d34"
```

(Quotes around the entire value)

Then try restarting the service.

