# Property Management System

Django property management project using PostgreSQL/PostGIS and Docker Compose.

## Requirements

- Docker Desktop
- Docker Compose
- At least a few GB of free disk space for Docker images and database data

## Environment Setup

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-this-with-a-long-random-secret-key
DEBUG=True

DB_NAME=vacation_rental
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

For Docker, keep `DB_HOST=db` because `db` is the PostgreSQL service name in `docker-compose.yml`.

## Run With Docker

From the project root:

```powershell
docker compose up --build -d
```

Run database migrations:

```powershell
docker compose exec web python manage.py migrate
```

Create an admin user:

```powershell
docker compose exec web python manage.py createsuperuser
```

Open the app:

```text
http://127.0.0.1:8000/
```

Django admin:

```text
http://127.0.0.1:8000/admin/
```

## Useful Docker Commands

View running containers:

```powershell
docker compose ps
```

View web logs:

```powershell
docker compose logs -f web
```

View database logs:

```powershell
docker compose logs -f db
```

Restart the Django container:

```powershell
docker compose restart web
```

Stop containers:

```powershell
docker compose down
```

Stop containers and remove the database volume:

```powershell
docker compose down -v
```

Use `docker compose down -v` only when you want to delete the local database data.

## Troubleshooting

If `http://127.0.0.1:8000/` shows `ERR_EMPTY_RESPONSE`, the web container may have started before PostgreSQL finished initializing. Restart the web container:

```powershell
docker compose restart web
```

Then check the logs:

```powershell
docker compose logs -f web
```

If Docker build fails during `apt-get` or `dpkg`, make sure Docker Desktop is running and your system drive has enough free space.
