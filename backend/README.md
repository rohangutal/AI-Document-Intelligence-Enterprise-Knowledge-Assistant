# Backend

The backend contains the FastAPI service, SQLAlchemy persistence layer, and Alembic migrations.

## Run locally

```powershell
cd backend
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Then open `http://localhost:8000/docs` or check `http://localhost:8000/api/v1/health`.

## Local persistence services

From the repository root, start PostgreSQL with pgvector and Redis:

```powershell
docker compose -f infra/docker-compose.yml up -d
cd backend
alembic upgrade head
```

Authentication, document processing, and AI integrations are intentionally deferred to later reviewed phases.
