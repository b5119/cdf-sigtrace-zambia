# INC-002 · OCDS Ingestion Pipeline

- **Status:** DONE
- **Started:** 2026-06-02  ·  **Completed:** 2026-06-02
- **Owner / session:** Claude Code (automated build session)
- **Weight:** 6%

## Goal
Build the OCDS data ingestion pipeline that fetches procurement records, normalises them to domain
models, and loads them idempotently into the database. Expose ingestion run management via the API.

## Deliverables

- [x] `src/backend/app/models/contract.py` — `Contract`, `Supplier`, `IngestionRun` ORM models
- [x] `src/backend/alembic/versions/002_inc002_ocds_ingestion.py` — migration (suppliers, contracts, ingestion_runs tables)
- [x] `src/ingestion/__init__.py`, `config.py` — pipeline config
- [x] `src/ingestion/fetch.py` — fetch from OCDS API (paginated) or local sample file
- [x] `src/ingestion/normalise.py` — OCDS record → (contract_dict, supplier_dict); SHA-256 content hash
- [x] `src/ingestion/load.py` — idempotent upsert (OCID + content hash); IngestionRun tracking
- [x] `src/ingestion/run.py` — CLI: `python -m ingestion.run [--sample] [--since DATE]`
- [x] `src/ingestion/sample/ocds_sample.json` — 5-contract OCDS record-package fixture covering: clean contract, missing signing date, standstill violation, framework call-off, completed contract
- [x] `src/backend/app/schemas/ingestion.py` — Pydantic schemas
- [x] `src/backend/app/api/ingestion.py` — `GET/POST /ingestion/runs`, `GET /ingestion/runs/{id}`
- [x] `src/backend/tests/test_ingestion.py` — 15 tests

## What was built

### Ingestion pipeline
```
src/ingestion/
  config.py          OCDS_API_URL, OCDS_API_KEY, OCDS_BATCH_SIZE, SAMPLE_FILE
  fetch.py           load_sample() / fetch_from_api(since, max_pages) — paginated httpx
  normalise.py       normalise_record() → (contract_dict, supplier_dict | None)
                     _content_hash() — SHA-256 of canonical JSON
                     _framework_parent() — detects call-off via relatedProcesses
  load.py            upsert_contract() → 'created'|'updated'|'skipped'
                     _upsert_supplier() — find by TPIN → name → create
                     run_load() — bulk load with IngestionRun tracking
  run.py             CLI entry (--sample / --since / --url)
  sample/
    ocds_sample.json 5 OCDS records (Ministry of Health, Education, Road Development,
                     Agriculture call-off, Local Government)
```

### Database schema additions
- `suppliers` — id, name, tpin (indexed), address, phone, shareholders, debarred_until
- `contracts` — ocid (PK), procuring_entity, supplier_id (FK), value, currency, award_date,
  signing_date, framework_parent, status, risk_score (null until INC-003), content_hash (indexed), raw_ocds
- `ingestion_runs` — id, started_at, finished_at, source, records_in/loaded/updated/skipped, errors, status

### Idempotency
- Each contract is keyed by `ocid` (primary key).
- A `content_hash` (SHA-256 of canonical JSON) is stored. On re-run: if hash matches → `skipped`;
  if hash differs → `updated`; if new → `created`.
- Suppliers are matched by TPIN first, then name.

### API
- `GET /api/v1/ingestion/runs` — paginated list, `system_admin` only
- `POST /api/v1/ingestion/runs` → 202 Accepted, returns run record (async dispatch placeholder for Celery)
- `GET /api/v1/ingestion/runs/{id}` — run detail

### OCDS sample fixture (5 contracts)
| OCID | Entity | Anomaly hint |
|------|--------|--------------|
| ocds-zm-zppa-001 | Ministry of Health | Clean — Medical Equipment |
| ocds-zm-zppa-002 | Ministry of Education | Missing signing date |
| ocds-zm-zppa-003 | Ministry of Road Development | Standstill violation (1 day) |
| ocds-zm-zppa-004 | Ministry of Agriculture | Framework call-off — must NOT flag single-source |
| ocds-zm-zppa-005 | Ministry of Local Government | Clean — complete status |

## Acceptance criteria — results

| Criterion | How verified | Result |
|-----------|--------------|:------:|
| OCDS sample loads into Contract/Supplier idempotently | `test_load_sample_creates_contracts` — 5 contracts, 5 suppliers | ✅ |
| Re-running doesn't duplicate | `test_load_idempotent_no_duplicates` — 5 contracts after 2 runs | ✅ |
| Changed content triggers update, not duplicate | `test_load_update_on_changed_content` | ✅ |
| Suppliers not duplicated | `test_supplier_upserted_not_duplicated` — 5 suppliers after 2 runs | ✅ |
| Framework call-off maps framework_parent | `test_normalise_framework_calloff` | ✅ |
| Missing signing_date preserved as None | `test_normalise_missing_signing_date` | ✅ |
| Run history + errors visible via API | `test_ingestion_runs_list_returns_data`, `test_get_run_returns_detail` | ✅ |
| API requires system_admin | `test_ingestion_runs_list_requires_auth` → 401 | ✅ |

## Tests

```
116 passed, 2 warnings in 1.82s

New in INC-002:
  test_ingestion.py  15 tests — normalise unit (6), load integration (4), API (5)
```

## Security / privacy spot-checks
- [x] Ingestion endpoints require `system_admin` permission — `test_ingestion_runs_list_requires_auth` → 401
- [x] `raw_ocds` (contains named data) stored in restricted DB, not exposed on public endpoints
- [x] No ledger writes at this increment — raw data stays in Postgres only

## Decisions / deviations
- Celery async dispatch is stubbed (TODO comment in `POST /ingestion/runs`) — the run record is created
  synchronously and returned; actual pipeline execution will be wired via Celery at INC-020.
  For the prototype and tests, `run_load()` is called directly.
- `pytest.ini pythonpath = ..` — adds `src/` to the Python path so `ingestion.*` imports resolve
  in the backend test suite without a separate install step.

## Follow-ups / known gaps
- [ ] Celery task `ingestion_tasks.run_ingestion` — dispatch from `POST /ingestion/runs` (INC-020)
- [ ] Scheduled ingestion via Celery beat (INC-020)
- [ ] `IngestionRun.since` filter not yet used in API trigger (straightforward addition)
- [ ] `risk_score` column is NULL until INC-003/004 (anomaly engine) populates it

## Progress update
- INC-002 = **DONE** in `09_PROGRESS.md`.
- Overall completion: **14%** (INC-000 3% + INC-001 5% + INC-002 6%).
