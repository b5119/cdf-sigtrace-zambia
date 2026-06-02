# 03 · API Endpoints

Base path `/api/v1`. All responses JSON. **Auth** column: `public` = no auth; otherwise the required
permission/role. Two-tier scoping is applied automatically to every response (see `05_RBAC_SECURITY.md`).
Build endpoints in the increment that owns them (see `08_INCREMENT_PLAN.md`).

Conventions: list endpoints support `?page&size&sort&filter`; errors use
`{ "error": {code, message, details} }`; mutations require `Idempotency-Key` where noted.

## Auth  (INC-001)
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/auth/login` | public | email+password → MFA challenge token |
| POST | `/auth/mfa/verify` | public | TOTP code → access + refresh tokens |
| POST | `/auth/refresh` | refresh token | rotate tokens |
| POST | `/auth/logout` | bearer | revoke refresh (jti) |
| POST | `/auth/password/forgot` | public | start reset |
| POST | `/auth/password/reset` | reset token | set new password |
| GET | `/auth/me` | bearer | current principal (role, institution, permissions) |

## Public — transparency  (INC-007, INC-008, INC-014)
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/public/overview` | public | national KPIs (allocation, projects, verified, flags) |
| GET | `/public/constituencies` | public | list + summary risk/verification status |
| GET | `/public/constituencies/{id}` | public | constituency detail + projects (de-identified) |
| GET | `/public/projects` | public | list public projects (filter by constituency/status) |
| GET | `/public/projects/{id}` | public | project detail: disbursement, evidence, verified location, status |
| GET | `/public/map` | public | GeoJSON + per-constituency aggregates for the choropleth/map |
| GET | `/public/risk/aggregate` | public | de-identified procurement risk by entity/sector |
| POST | `/public/verify-contract` | public | upload a PDF → server hashes → compare to anchor → match/mismatch + anchor meta |
| GET | `/public/anchors/{ocid}` | public | public anchor record (hash, tx, timestamp) — no document |
| GET | `/public/opendata/{dataset}` | public | downloadable aggregated datasets (CSV/JSON) |

## Contracts & analysis — SigTrace  (INC-002…005, INC-009)
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/contracts` | read_named | risk list (named, scored, filterable) |
| GET | `/contracts/{ocid}` | read_named | full contract record |
| GET | `/contracts/{ocid}/checks` | read_named | all 8 check results + evidence |
| GET | `/contracts/{ocid}/risk` | read_named | score + weighted breakdown |
| GET | `/suppliers/{id}` | read_named | supplier profile |
| GET | `/suppliers/network` | read_named | related-party graph for a tender/supplier |
| POST | `/analysis/run` | system_admin | (re)run the engine over a set/date range (async) |
| GET | `/ingestion/runs` | system_admin | ingestion run history |
| POST | `/ingestion/runs` | system_admin | trigger an ingestion run (async) |
| GET | `/ingestion/runs/{id}` | system_admin | run status + errors |

## Anchoring & verification  (INC-006, INC-007)
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/anchors` | oversight_officer | anchor a contract's SHA-256 hash to Fabric (Idempotency-Key) |
| GET | `/anchors/{ocid}` | read_named | anchor record (named context) |
| POST | `/verify` | read_named | verify an uploaded document vs its anchor (restricted variant of public verify) |

## CDF Pulse — field evidence  (INC-010…014)
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/pulse/assignments` | community_monitor | my assigned constituency/projects |
| POST | `/pulse/submissions` | community_monitor | create submission (multipart: photo + lat/lng/ts/meta); Idempotency-Key for offline de-dup |
| POST | `/pulse/sync` | community_monitor | batch upload queued offline submissions |
| GET | `/pulse/submissions` | community_monitor / officer | list (own for monitor; scoped for officer) |
| GET | `/pulse/submissions/{id}` | community_monitor / officer | submission detail incl. IPFS CID + status |
| POST | `/pulse/submissions/{id}/confirm` | inst_confirmer / officer | record a multi-party confirmation (→ Polygon) |
| POST | `/pulse/submissions/{id}/reject` | inst_confirmer / officer | reject with reason |
| GET | `/pulse/projects/{id}/evidence` | public(de-id)/officer | evidence list for a project |

## Integrated monitor  (INC-015)
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/monitor/ghost-projects` | read_named | disbursements with no verified completion (queue) |
| GET | `/monitor/mismatches` | read_named | full mismatch list (contract/delivery) |
| GET | `/monitor/disbursements` | read_named | disbursements + match status |
| POST | `/monitor/run` | system_admin | run a monitor sweep (async) |
| POST | `/monitor/ghost-projects/{id}/clear` | oversight_officer | clear a signal with justification |

## Cases & notifications  (INC-016)
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/cases` | case_mgmt | list cases (scoped) |
| POST | `/cases` | case_mgmt | open a case (subject = contract or ghost-project) |
| GET | `/cases/{id}` | case_mgmt | case detail + notes |
| PATCH | `/cases/{id}` | case_mgmt | update status/assignee/priority |
| POST | `/cases/{id}/notes` | case_mgmt | add a note |
| POST | `/cases/{id}/escalate` | oversight_officer | escalate (e.g. to ACC) |
| GET | `/notifications` | bearer | my notifications |
| POST | `/notifications/{id}/read` | bearer | mark read |

## Admin  (INC-017, INC-018)
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET/POST | `/admin/users` | system_admin | list / create users |
| GET/PATCH/DELETE | `/admin/users/{id}` | system_admin | manage a user (role, institution, active) |
| GET | `/admin/roles` | system_admin | roles + permissions |
| GET/PUT | `/admin/config/weights` | system_admin | the 8 check weights (calibrate with OAG) |
| GET/PUT | `/admin/config/thresholds` | system_admin | standstill days, amendment cap, ghost window, high-risk threshold |
| GET | `/admin/institutions` | system_admin | institutions + data-sharing agreements |
| GET | `/admin/ledger/nodes` | system_admin | Fabric peers / Polygon contract status |
| GET | `/admin/audit` | audit_read | audit log (filter by actor/action/target) |
| GET | `/admin/health` | system_admin | component health (DB, Redis, Fabric, Polygon, IPFS, pipeline) |

## System
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/healthz` | public | liveness |
| GET | `/readyz` | public | readiness |
| GET | `/openapi.json`, `/docs` | public(dev) | OpenAPI / Swagger (lock down in prod) |
