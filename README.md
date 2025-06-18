# Intern Go Project

A Django-based web application for internship and job management.

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start with Docker

1. Clone the repository:
   ```
   git clone <repository-url>
   cd Diploma-Project-2025
   ```

2. Build and start the containers:
   ```
   docker-compose up -d --build
   ```

3. The application will be available at:
   - Web UI: http://localhost:80
   - Admin panel: http://localhost:80/admin

4. Default users:
   - Admin: 
     - Username: `admin`
     - Password: `IntGo12345`
   - Staff users:
     - Username: `Ayana`, `Assem`, `Altush`
     - Password: `IntGo12345` (same for all users)

## Development

### Project Structure

```
├── admin_panel/         # Admin panel app
├── home_after/          # Home page app for logged-in users
├── internship/          # Internship management app
├── media/               # User-uploaded files
├── nginx/               # Nginx configuration
├── sendreview/          # Review and comment functionality
├── static/              # Static assets
├── templates/           # HTML templates
├── testt/               # Main project settings
├── unboarding_form/     # User onboarding app
├── userprofile/         # User profile app
├── users/               # User authentication and account app
└── vacancies/           # Job listings app
```

### Docker Commands

- Start containers: `docker-compose up -d`
- Stop containers: `docker-compose down`
- View logs: `docker-compose logs -f`
- Rebuild and start: `./docker-rebuild.sh`
- Rebuild static files: `./docker-rebuild-static.sh`

### Direct Development (without Docker)

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Create initial users:
   ```
   python manage.py shell < add_users.py
   ```

5. Run development server:
   ```
   python manage.py runserver
   ```

## Health Check

The application includes health check endpoints for Docker:
- Main app health: http://localhost:8000/health/
- Database is checked automatically

## Data Management

- Admin panel is accessible at /admin
- Initial users are created automatically on container start

## Troubleshooting

If you encounter issues:

1. Check the logs:
   ```
   docker-compose logs -f web
   ```

2. Run the health check script:
   ```
   ./healthcheck.sh
   ```

3. Restart the containers:
   ```
   docker-compose down
   docker-compose up -d
   ```