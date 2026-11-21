# Phase 11 — Launch validation

Phase 11 validates the deployed system as one flow: browser → API → database
and Redis. It does not replace the security and legal-review requirements in
the release checklist.

## Run the smoke test

After starting the production-like stack:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke-test.ps1
```

For another host:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke-test.ps1 `
  -ApiUrl https://api.example.com `
  -FrontendUrl https://app.example.com
```

The test checks API liveness, API documentation availability, frontend
availability, and dependency readiness. A failed readiness check is expected
when PostgreSQL or Redis is unavailable and should block release promotion.

## Acceptance gate

- [ ] CI is green on the release commit.
- [ ] Database migrations complete successfully.
- [ ] Smoke test passes from the deployed network boundary.
- [ ] A user can register, log in, and access only their own contracts.
- [ ] Contract analysis returns source references.
- [ ] A PDF, DOCX, and TXT upload each creates a contract and source chunks.
- [ ] Oversized and unsupported uploads are rejected.
- [ ] Risk and obligation review updates persist after refresh.
- [ ] Logs contain no passwords, JWTs, or document contents beyond approved retention.
- [ ] Evaluation and security results are attached to the release record.
