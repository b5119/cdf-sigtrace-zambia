# INC-017 · Admin Console

- **Status:** DONE
- **Started:** 2026-06-04  ·  **Completed:** 2026-06-04
- **Owner / session:** Claude Code
- **Weight:** 5%

## Goal
The admin console (S1–S9): system health, user management, check weights, thresholds, ledger
governance. Key acceptance: **admin can change a weight and see the score recompute.**

## Deliverables

### Backend
- [x] `app/models/config.py` — Config (versioned key-value) + migration `011_inc017_config`
- [x] `app/services/admin_service.py` — weights, thresholds, users CRUD, roles, institutions, health, ledger status
- [x] `app/services/anomaly_service.py` — `_load_config` now also loads admin-tuned thresholds from the Config table
- [x] `app/schemas/admin.py` + `app/api/admin.py`:
  - `GET /admin/health` (S1) · `GET /admin/ledger/nodes` (S6)
  - `GET/POST /admin/users`, `PATCH /admin/users/{id}`, `GET /admin/roles`, `GET /admin/institutions` (S2)
  - `GET/PUT /admin/config/weights` (S3) · `GET/PUT /admin/config/thresholds` (S4)
- [x] `tests/test_admin.py` — 15 tests

### Frontend — oversight console
- [x] **Admin Console** (`pages/Admin.tsx`) — tabbed: Health (S1), Users (S2), Weights (S3), Thresholds (S4), Ledger (S6)
  - Health: live component status dots (DB/Redis/Fabric/Polygon/IPFS/engine)
  - Users: list, enable/disable
  - Weights: 8 sliders + live total/100, save → recompute
  - Thresholds: editable numeric fields
  - Ledger: Fabric/Polygon/IPFS mode + counts

## The key acceptance — change a weight, score recomputes
- `PUT /admin/config/weights` updates `CheckDefinition.weight`.
- The scoring service's `_load_config` reads weights from `check_definitions` on every analysis.
- `test_changing_weight_recomputes_score`: scores a contract (signing flag, weight 15), raises the
  signing weight to 40 via the admin API, re-scores → **score strictly increases**. Verified.
- Thresholds are loaded from the Config table into the engine config too, so editing
  `standstill_days` etc. changes how checks fire on the next run.

## Acceptance criteria — results
| Criterion | Test | Result |
|-----------|------|:------:|
| **Change a weight → score recomputes** | `test_changing_weight_recomputes_score` | ✅ |
| Weight update persists | `test_update_weight_persists` | ✅ |
| Thresholds editable | `test_update_thresholds` | ✅ |
| Users manageable (create/disable) | `test_create_user`, `test_deactivate_user` | ✅ |
| Duplicate email rejected | `test_create_user_duplicate_email` → 400 | ✅ |
| Health reflects component status | `test_health_reports_components` (DB ok, ledger modes) | ✅ |
| Ledger status | `test_ledger_status` | ✅ |
| RBAC — configure_weights / manage_users | `test_weights_require_configure_permission`, `test_users_require_manage_permission` → 403 | ✅ |

## Tests — 358/358 backend green (15 new). Console type-checks clean (tsc exit 0).

## Follow-ups
- S5 Ingestion Management UI (endpoints already exist from INC-002) → wire into Admin tab → polish
- S7 Institutions & Agreements UI (endpoint exists) → polish
- S8 Audit Log Viewer → INC-018 (anchored audit log)
- S9 Notification templates/config → polish
- Live Redis/Fabric/IPFS health probes (currently mode-based) → INC-020

## Progress update
- INC-017 = **DONE** — Overall: **91%**.
