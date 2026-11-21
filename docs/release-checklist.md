# Release checklist

Use this checklist before promoting a build beyond local development.

## Configuration and secrets

- [ ] `ENVIRONMENT=production` is set.
- [ ] `JWT_SECRET` is random, private, and at least 32 characters.
- [ ] `POSTGRES_PASSWORD` is stored in a secret manager.
- [ ] `CORS_ORIGINS` contains only approved HTTPS origins.
- [ ] No credentials are committed to the repository.

## Verification

- [ ] CI passes backend tests and Ruff checks.
- [ ] CI passes the frontend TypeScript/Vite build.
- [ ] Database migrations run successfully with `alembic upgrade head`.
- [ ] `/api/v1/health` returns `200`.
- [ ] `/api/v1/health/ready` returns `200` only when PostgreSQL and Redis are reachable.
- [ ] Registration, login, authorization, document permissions, and audit behavior are smoke-tested.
- [ ] Evaluation report is regenerated and reviewed.

## Operations and security

- [ ] PostgreSQL backups and restore testing are configured.
- [ ] Logs and error monitoring are routed to the operational system.
- [ ] Postgres and Redis are private network services.
- [ ] TLS is terminated at the ingress or platform edge.
- [ ] Uploaded legal documents have retention and deletion policies.
- [ ] Human review is required for material legal decisions.

## Rollback

- [ ] Previous application image is retained.
- [ ] Database migration rollback or forward-fix procedure is documented.
- [ ] Recovery owner and escalation contact are known.
