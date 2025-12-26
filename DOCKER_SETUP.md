# Docker Setup Instructions

This project is now dockerized to solve PostgreSQL connection issues. Follow these steps to run the project:

## Prerequisites

- Docker installed on your system
- Docker Compose installed

## Setup Steps

### 1. Create .env file (if you don't have one)

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here

# Database Configuration (for local development - Docker uses its own)
DB_NAME=evara
DB_USER=nihal
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Social Authentication
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-google-oauth-key
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-google-oauth-secret
```

**Note:** When using Docker, the database credentials are automatically set by docker-compose.yml, so you don't need to worry about the DB_* variables for Docker.

### 2. Build and Run with Docker Compose

```bash
# Build and start containers
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 3. Run Migrations

In a new terminal, run:

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser (optional)
docker-compose exec web python manage.py createsuperuser
```

### 4. Access the Application

- Django app: http://localhost:8000
- PostgreSQL: localhost:5432 (from host machine)

## Docker Services

- **web**: Django application (port 8000)
- **db**: PostgreSQL database (port 5432)

## Useful Commands

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v

# View logs
docker-compose logs -f

# Execute commands in web container
docker-compose exec web python manage.py <command>

# Access database shell
docker-compose exec db psql -U evara_user -d evara
```

## Database Credentials (Docker)

- Database: `evara`
- User: `evara_user`
- Password: `evara_password`
- Host: `db` (from within Docker network) or `localhost` (from host)

## Benefits of Dockerization

1. **No local PostgreSQL setup required** - Database runs in a container
2. **Consistent environment** - Same setup across all machines
3. **Easy cleanup** - Remove containers and volumes when done
4. **Isolated dependencies** - No conflicts with system packages

