# Backend

The Phase 2 backend foundation is a small FastAPI service with environment-based settings, versioned routing, CORS configuration, OpenAPI documentation, and a liveness endpoint.

## Run locally

```powershell
cd backend
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Then open `http://localhost:8000/docs` or check `http://localhost:8000/api/v1/health`.

Database, Redis, authentication, document processing, and AI integrations are intentionally deferred to later reviewed phases.
