# Property Management System

A vacation-rental property management platform built with **Django**, **GeoDjango / PostGIS**, and **pgvector**. It combines a traditional location-based property search with **AI semantic search** powered by Sentence Transformers, all running in Docker.

The project lets you browse rental properties, search by destination, view property details with images and amenities, see each property's distance from its city center, and search destinations by *meaning* (e.g. "beach vacation" or "mountain getaway") rather than exact names.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Features](#features)
- [Screenshots](#screenshots)
- [Requirements](#requirements)
- [Setup](#setup)
- [API Endpoints](#api-endpoints)
- [Trying the Semantic Features](#trying-the-semantic-features)
- [Managing Data Manually](#managing-data-manually)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Useful Docker Commands](#useful-docker-commands)
- [Limitations & Future Improvements](#limitations--future-improvements)
- [Troubleshooting](#troubleshooting)
- [Author](#author)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django, Django REST Framework |
| Spatial | GeoDjango + PostGIS |
| Vector / AI | pgvector + Sentence Transformers (`all-MiniLM-L6-v2`) |
| Database | PostgreSQL 16 (PostGIS 3.5, pgvector 0.8) |
| Data import | pandas |
| Containerization | Docker + Docker Compose |

---

## Features

- **Location-based search** — find properties by destination with pagination.
- **Property detail pages** — image gallery, amenities, price, and **distance from the city center** (computed with PostGIS).
- **Semantic location search** — rank destinations by meaning using vector embeddings.
- **Semantic autocomplete API** — a DRF endpoint that suggests locations by semantic similarity.
- **Combined search** — filter by location and rank the results semantically.
- **Django admin** — manage data with filters and image previews.
- **HNSW vector indexing** — fast approximate nearest-neighbor search in pgvector.

### Technical Highlights

- **Spatial data with GeoDjango** — `Location` and `Property` use PostGIS `geography` point fields (SRID 4326), plus a `MultiPolygonField` boundary, enabling true metric distance calculations rather than naive coordinate math.
- **Auto-syncing coordinates** — a reusable `PointSyncMixin` keeps each model's spatial `point` in sync with its latitude/longitude on save, so data entry stays simple while spatial queries stay accurate.
- **PostgreSQL array amenities** — property amenities are stored in a native `ArrayField`, not a separate table, keeping the schema lean.
- **One-command, self-seeding setup** — the Docker entrypoint waits for the database, migrates, imports sample data, and generates embeddings automatically, with guards so restarts never duplicate data or re-run the slow model load.
- **Lean, reproducible image** — PyTorch is pinned to the CPU-only build and dependencies are version-locked, avoiding gigabytes of unused GPU libraries.
- **Resilient startup** — embedding generation is non-fatal, so the app still launches even if the model can't be downloaded.

---

## Screenshots

### Homepage with Search
![Homepage](docs/home.png)

### Location Search Results
![Search results](docs/search.png)

### Property Detail (images, amenities, and distance from city)
![Property detail](docs/detail.png)

### Semantic Location Search
![Semantic location search](docs/semantic_location.png)

### Property Semantic Search
![Property semantic search](docs/property_semantic.png)

### Combined Location + Semantic Search
![Combined search](docs/combined.png)

---

## Requirements

- Docker Desktop
- Docker Compose
- A few GB of free disk space (the image includes PyTorch for embeddings)
- Internet access on first run (to download the embedding model, ~90 MB)

---

## Setup

### 1. Create a `.env` file

Copy the provided example and adjust if needed:

```bash
cp .env.example .env
```

The `.env` file should contain:

```env
SECRET_KEY=replace-this-with-a-long-random-secret-key
DEBUG=True

DB_NAME=vacation_rental
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

Keep `DB_HOST=db` — `db` is the PostgreSQL service name in `docker-compose.yml`.

To generate a fresh secret key:

```bash
docker compose run --rm web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Build and start

From the project root:

```bash
docker compose up --build -d
```

On the **first** startup the container automatically:

1. Waits for PostgreSQL to be ready
2. Applies database migrations
3. Imports the sample properties from `data/vacation_rentals.csv`
4. Generates semantic embeddings for properties and locations

> **First launch takes about a minute** because it downloads the embedding model and generates vectors. This happens only once — later restarts are fast and skip these steps. If embedding generation fails (for example, no internet), the app still starts, but semantic search will be empty until embeddings are generated.

### 3. Create an admin user

```bash
docker compose exec web python manage.py createsuperuser
```

### 4. Open the app

| Page | URL |
|------|-----|
| Homepage | http://127.0.0.1:8000/ |
| Property search | http://127.0.0.1:8000/search/ |
| Property detail | http://127.0.0.1:8000/property/&lt;slug&gt;/ |
| Semantic location search | http://127.0.0.1:8000/locations/semantic/ |
| Combined search | http://127.0.0.1:8000/combine/ |
| Autocomplete API (semantic) | http://127.0.0.1:8000/api/locations/?q=beach |
| Django admin | http://127.0.0.1:8000/admin/ |

---

## API Endpoints

The project exposes a REST API endpoint built with **Django REST Framework**.

### Location Autocomplete (Semantic)

Returns up to 10 locations ranked by **semantic similarity** to the query, using vector embeddings and cosine distance.

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/locations/` |
| **Query param** | `q` — the search text (e.g. `beach`, `mountain`) |

**Example request:**

```
GET /api/locations/?q=beach
```

**Example response:**

```json
{
  "results": [
    { "label": "Miami, Florida", "slug": "miami-florida" },
    { "label": "Destin, Florida", "slug": "destin-florida" }
  ]
}
```

An empty or missing `q` returns `{"results": []}`.

---

## Trying the Semantic Features

The semantic search works on *meaning*, so try descriptive queries rather than exact names:

- On the **homepage search box**, type `beach` or `mountain` — the autocomplete suggests matching destinations.
- On **semantic location search** (`/locations/semantic/`), try `warm beach vacation`, `mountain ski getaway`, or `wine country`.
- On **combined search** (`/combine/`), enter a location (e.g. `Aspen`) and a description (e.g. `luxury lodge with sauna`) to filter by place and rank by meaning.

---

## Managing Data Manually

These steps run automatically on first startup, but you can also run them by hand.

Import properties from CSV:

```bash
docker compose exec web python manage.py import_properties data/vacation_rentals.csv
```

Generate embeddings (only fills in missing ones, safe to re-run):

```bash
docker compose exec web python manage.py generate_embeddings
docker compose exec web python manage.py generate_location_embeddings
```

> The importer adds new properties without duplicating existing ones, and the embedding commands only process records that don't yet have an embedding.

---

## Running Tests

The project includes an automated test suite covering the spatial point-sync logic, location-based property search, and the semantic autocomplete ranking (with the embedding model mocked for fast, deterministic runs).

Run the tests inside the container:

```bash
docker compose exec web python manage.py test
```

The tests verify, among other things, that:

- saving a model auto-populates its PostGIS `point` from latitude/longitude,
- slug search returns only the chosen location while text search spans all matches,
- the autocomplete API ranks results by cosine distance and handles empty queries.

---

## Project Structure

```
.
├── config/                  # Django project settings, URLs
├── property_app/            # Main app
│   ├── models.py            # Location, Property, PropertyImage
│   ├── views.py             # Search, detail, semantic, combined views
│   ├── serializers.py       # DRF serializer for autocomplete API
│   ├── embeddings.py        # Shared Sentence Transformers helpers
│   ├── admin.py             # Admin with filters and image previews
│   ├── management/commands/ # import_properties, generate_embeddings, ...
│   ├── migrations/
│   └── tests.py             # Point-sync, search, and autocomplete tests
├── templates/property_app/  # HTML templates
├── static/                  # CSS and JS (autocomplete)
├── data/                    # Sample CSV and property images
├── docker/                  # Postgres image + entrypoint script
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Useful Docker Commands

```bash
docker compose ps                 # list running containers
docker compose logs -f web        # follow Django logs
docker compose logs -f db         # follow database logs
docker compose restart web        # restart the Django container
docker compose down               # stop containers (keeps data)
docker compose down -v            # stop containers and DELETE the database
```

Use `docker compose down -v` only when you want to wipe the database and start fresh (it will re-seed and re-generate embeddings on the next startup).

---

## Limitations & Future Improvements

- **Image similarity search** — the schema and stack support image embeddings; a future version could add visual "find similar properties" search.
- **Advanced spatial queries** — the PostGIS foundation enables radius search, polygon containment, and geofencing, which could power map-based browsing.

---

## Troubleshooting

**Page shows `ERR_EMPTY_RESPONSE`** — the web container may have started before PostgreSQL finished initializing. Restart it:

```bash
docker compose restart web
```

**Semantic search returns no results** — embeddings may not have been generated (e.g. the first-run download failed). Generate them manually:

```bash
docker compose exec web python manage.py generate_embeddings
docker compose exec web python manage.py generate_location_embeddings
```

**Build fails during `apt-get` / `dpkg`** — ensure Docker Desktop is running and your drive has enough free space.

**Duplicate properties appear** — the import was run multiple times on an already-seeded database. Clear and re-import:

```bash
docker compose exec web python manage.py shell -c "from property_app.models import Property, PropertyImage, Location; PropertyImage.objects.all().delete(); Property.objects.all().delete(); Location.objects.all().delete()"
docker compose exec web python manage.py import_properties data/vacation_rentals.csv
docker compose exec web python manage.py generate_embeddings
docker compose exec web python manage.py generate_location_embeddings
```

---

## Author

**[Naimur Rahman Lam](https://github.com/NaimurRahmannn)**