# BuildBoard Backend

## Local Development Setup

This guide explains how to set up the database and application locally. 

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.11+

### 2. Local Database (Docker)
We use a `docker-compose.yml` file strictly for **local development**. It spins up a PostgreSQL database so you don't have to install one manually.

**Start the database:**
```bash
docker compose up -d
```

This starts a Postgres container on port `5432` with the following credentials:
- **User**: `user`
- **Password**: `password`
- **Database**: `buildboard`

### 3. Environment Configuration
You need a `.env` file to tell the application how to connect to this local database.

1. Copy the example configuration:
   ```bash
   cp .env.example .env
   ```

2. **Verify your `.env` file**. For local development, it **MUST** contain this exact connection string:
   ```properties
   DATABASE_URL=postgresql://user:password@127.0.0.1:5432/buildboard
   ```

   *If you are running the app inside Docker as well (not just the DB), you might need to use `host.docker.internal` instead of `localhost`.*

### 4. Running the App
Install dependencies:
```bash
pip install -r requirements.txt
```

Start the server (with hot-reload):
```bash
uvicorn app.main:app --reload
```

The app will automatically migrate the database schema upon startup.

---

## Production vs. Local
There is a strict separation between local dev and production:

- **Local**: Uses `docker-compose.yml` to run a throwaway Postgres container. You control the variables via `.env`.
- **Production (Coolify)**: 
    - Uses the `Dockerfile` to build the application image.
    - The Database is managed by Coolify (or an external provider).
    - Environment variables (like `DATABASE_URL`) are injected by Coolify's dashboard, NOT from the `.env` file.
    - **Do NOT** use the `docker-compose.yml` for production deployment.
