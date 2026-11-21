# Infrastructure

`docker-compose.yml` provides the free local development services used by the backend: PostgreSQL with pgvector and Redis. Persistent data is stored in named Docker volumes.

## Production-like deployment

1. Copy `backend/.env.example` to `backend/.env`.
2. Set a strong `JWT_SECRET` in `backend/.env` and export `POSTGRES_PASSWORD`
   for Compose (Compose interpolates the database password before loading the
   backend environment file).
3. Start the stack:

```powershell
$env:POSTGRES_PASSWORD = "replace-with-a-long-random-password"
docker compose -f infra/docker-compose.prod.yml up -d --build
docker compose -f infra/docker-compose.prod.yml exec backend alembic upgrade head
```

The API is available at `http://localhost:8000`, the dashboard at
`http://localhost:8080`, liveness at `/api/v1/health`, and readiness at
`/api/v1/health/ready`. Do not expose Postgres or Redis directly to the public
internet. Use managed secrets, TLS termination, backups, and centralized logs
for a real production deployment.
