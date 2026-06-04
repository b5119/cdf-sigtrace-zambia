# INC-016 · Cases & Notifications

- **Status:** DONE
- **Started:** 2026-06-04  ·  **Completed:** 2026-06-04
- **Owner / session:** Claude Code
- **Weight:** 3%

## Goal
Case management opened from a contract or ghost-project signal, with notes, status changes,
escalation, and notifications (alerts). Screens O10 (Cases), O13 (Notifications).

## Deliverables

### Backend
- [x] `app/models/case.py` — Case, CaseNote, Notification
- [x] `alembic/versions/010_inc016_cases.py` — migration
- [x] `app/services/case_service.py` — open_case, list/get/update, add_note, escalate_case, notifications
- [x] `app/schemas/case.py` + `app/api/cases.py`:
  - `GET/POST /cases`, `GET/PATCH /cases/{id}` (case_mgmt)
  - `POST /cases/{id}/notes`, `POST /cases/{id}/escalate`
  - `GET /notifications`, `POST /notifications/{id}/read` (any bearer, own-scoped)
- [x] `tests/test_cases.py` — 15 tests

### Frontend — oversight console
- [x] **O10 Cases** (`pages/Cases.tsx`) — list + detail with notes, status select, escalate-to-ACC
- [x] **O13 Notifications** (`pages/Notifications.tsx`) — live feed, mark-read, type-styled
- [x] Sidebar "Cases" link + route

## Alerts (notifications fire)
- Opening a case → `case_opened` notification to the assignee.
- Assigning a case → `case_assigned`.
- Escalating a case → `case_escalated` (with target, e.g. ACC).
Notifications are strictly own-scoped: a user only sees notifications addressed to them.

## Acceptance criteria — results
| Criterion | Test | Result |
|-----------|------|:------:|
| Case opens from a contract | `test_open_case_from_contract` | ✅ |
| Case opens from a ghost signal | `test_open_case_from_ghost_project` | ✅ |
| Notes work | `test_add_note_to_case` (note appears in detail) | ✅ |
| Status changes work | `test_update_case_status`, `test_close_case_sets_closed_at` | ✅ |
| Escalation works | `test_escalate_case` (status → escalated) | ✅ |
| **Alerts fire on open** | `test_opening_case_fires_notification` | ✅ |
| **Alerts fire on escalate** | `test_escalation_fires_notification` | ✅ |
| Mark notification read | `test_mark_notification_read` | ✅ |
| Notifications own-scoped | `test_notifications_scoped_to_user` | ✅ |
| case_mgmt permission required | `test_case_requires_case_mgmt_permission` → 403 | ✅ |
| Auth required | `test_list_cases_requires_auth`, `test_notifications_require_auth` → 401 | ✅ |

## Tests — 343/343 backend green (15 new). Oversight console type-checks clean (tsc exit 0).

## Follow-ups
- Auto-open a case directly from the ghost queue (O6 → O10) and contract detail (O4 → O10) → polish
- Auto-notify on new high-risk contract / new ghost signal (monitor sweep fires `ghost_signal`) → INC-020
- Email/SMS delivery of notifications → INC-020

## Progress update
- INC-016 = **DONE** — Overall: **86%**.
