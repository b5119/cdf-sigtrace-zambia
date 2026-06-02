# backend — FastAPI services

Central API: auth/RBAC, two-tier scoping, contracts, anchoring/verify, pulse, integrated monitor,
cases, admin. See `../../docs/03_API_ENDPOINTS.md` and `../../docs/01_ARCHITECTURE.md`.

Intended structure (created at INC-001):
```
app/
  main.py            FastAPI app + router mounting
  core/              config, security (JWT/MFA), rbac (permissions + decorator), scoping middleware
  models/            SQLAlchemy models (see docs/02_DATA_MODEL.md)
  schemas/           Pydantic request/response (public vs restricted projections)
  api/               routers per domain (auth, public, contracts, anchors, pulse, monitor, cases, admin)
  services/          anchor/, pulse/, monitor/, cases/  (business logic)
  tasks/             Celery tasks (ingestion, anchoring, monitor sweeps, notifications)
  db/                session, alembic migrations
tests/               pytest (unit + integration)
requirements.txt
```
First built in **INC-001** (auth/RBAC/scoping), then extended by later increments.
