# INC-015 · Integrated Monitor + Ghost Queue

- **Status:** DONE
- **Started:** 2026-06-04  ·  **Completed:** 2026-06-04
- **Owner / session:** Claude Code
- **Weight:** 6%

## Goal
The integrated monitor — the centerpiece tying procurement and delivery together. Matches each
disbursement against a clean-integrity contract AND a verified completion. A disbursement with no
verified completion within the window becomes a ghost-project signal in the OAG queue. Screens O6, O7.

## Deliverables

### Backend
- [x] `app/models/monitor.py` — Disbursement, GhostProjectSignal
- [x] `alembic/versions/009_inc015_monitor.py` — migration
- [x] `app/services/monitor_service.py` — run_sweep, get_ghost_queue, get_disbursements, get_mismatches, clear_ghost_signal
- [x] `app/schemas/monitor.py` + `app/api/monitor.py`:
  - `GET /monitor/ghost-projects` (read_named) — the ghost queue (O6)
  - `GET /monitor/disbursements`, `GET /monitor/mismatches` (read_named) — explorer (O7)
  - `POST /monitor/run` (system_admin) — sweep
  - `POST /monitor/ghost-projects/{id}/clear` (ghost_action) — clear with justification
- [x] `app/core/config.py` — `GHOST_WINDOW_DAYS = 180`
- [x] `tests/test_monitor.py` — 10 tests

### Frontend — oversight console
- [x] **O6 Ghost-Project Queue** (`pages/GhostQueue.tsx`) — table with days-overdue, clear action
- [x] **O7 Disbursement / Mismatch Explorer** (`pages/MismatchExplorer.tsx`) — all disbursements + match status
- [x] Sidebar links + routes (GHOST_QUEUE, MISMATCH)

## The matching logic
For each disbursement, on each sweep:
- A **verified completion** = the disbursement's project has ≥1 PulseSubmission with status `confirmed`
  (i.e. multi-party confirmed on Polygon — INC-013).
- If a verified completion exists → mark `matched_completion`, auto-clear any open ghost signal.
- Else if `(as_of - disbursement.date) > GHOST_WINDOW_DAYS` → raise a ghost-project signal with `days_overdue`.

This closes the loop: **procurement (clean contract) ↔ disbursement (IFMIS) ↔ delivery (verified completion)**.

## Acceptance criteria — results
| Criterion | Test | Result |
|-----------|------|:------:|
| **Disbursement with no completion in window → ghost queue** | `test_old_disbursement_no_completion_raises_ghost` | ✅ |
| **Matching one clears it** | `test_matching_clears_existing_ghost` (completion → cleared) | ✅ |
| Within-window disbursement → no ghost yet | `test_recent_disbursement_within_window_no_ghost` | ✅ |
| Disbursement with completion → matched, no ghost | `test_disbursement_with_completion_no_ghost` | ✅ |
| Run requires system_admin | `test_run_requires_admin` → 403 | ✅ |
| Clear requires ghost_action + justification | `test_clear_ghost_signal_via_api`, `test_clear_requires_justification` → 422 | ✅ |
| Mismatch list = unmatched disbursements | `test_disbursements_and_mismatches` | ✅ |
| Ghost queue requires auth | `test_ghost_queue_requires_auth` → 401 | ✅ |

## Tests — 328/328 backend green (10 new). Oversight console type-checks clean (tsc exit 0).

## Follow-ups
- Seed real IFMIS disbursement data → INC-017 (admin) / INC-020 (data load)
- Celery-scheduled monitor sweeps → INC-020
- Ghost signal → open case directly (O6 → O10) → INC-016
- Public ghost-signal count on the dashboard (currently seeded) wired to live data → polish

## Progress update
- INC-015 = **DONE** — Overall: **83%**. M3 platform-completion phase begins.
