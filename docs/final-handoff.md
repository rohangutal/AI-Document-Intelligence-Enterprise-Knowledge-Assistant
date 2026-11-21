# Final handoff status

## Acceptance checks

- Evaluation suite: passed, 3 cases and 5/5 automated checks.
- Frontend TypeScript compilation: passed.
- Frontend production bundle: passed when emitted to a writable temporary output directory.
- Launch smoke-test script syntax: passed.
- Python syntax checks: passed for the Phase 12–14 modules.
- Backend pytest suite: not run because `pytest` is not installed in the current environment.
- Live deployment smoke test: pending until Docker, PostgreSQL, Redis, and the API are running.

## Security acceptance notes

- Uploads require authentication and are scoped to the authenticated user.
- Supported extensions are restricted to PDF, DOCX, and TXT.
- Upload size is bounded by `MAX_UPLOAD_BYTES`.
- Stored filenames use generated document IDs rather than user-controlled paths.
- Contract, risk, obligation, and analysis reads enforce contract ownership.
- Security headers are enabled by the API middleware.
- Production secrets must be supplied through the environment or a secret manager.

## Handoff commands

```powershell
docker compose -f infra\docker-compose.prod.yml up -d --build
docker compose -f infra\docker-compose.prod.yml exec backend alembic upgrade head
powershell -ExecutionPolicy Bypass -File .\scripts\smoke-test.ps1
```

Before production promotion, install backend development dependencies and run
`pytest -q` and `ruff check app tests` from `backend/`. Attach those results and
the live smoke-test output to the release record.
