# Enterprise AI Knowledge Assistant

A modular enterprise knowledge assistant built around secure document ingestion, hybrid retrieval, and source grounded answers.

## Repository layout

- `backend/` — FastAPI application, domain models, services, migrations, and backend tests.
- `frontend/` — React and TypeScript application, organized by shared UI and product features.
- `infra/` — local and deployment infrastructure, container definitions, and operational scripts.
- `docs/` — architecture notes and technical decisions.
- `evaluation/` — retrieval and answer quality datasets and evaluation reports.
- `scripts/` — developer utilities and repeatable project tasks.

## Phases

Phase 1 established the repository structure. Phase 2 added the runnable FastAPI foundation. Phase 3 adds local PostgreSQL/pgvector and Redis services, SQLAlchemy models, and Alembic migrations. Authentication, document processing, and external AI credentials will be introduced in later reviewed phases.

## Planned technology

Python 3.11+, FastAPI, SQLAlchemy, Alembic, PostgreSQL with pgvector, Redis, LangChain/LangGraph, React, TypeScript, and Tailwind CSS.
