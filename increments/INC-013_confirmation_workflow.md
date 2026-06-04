# INC-013 · Confirmation Workflow

- **Status:** DONE
- **Started:** 2026-06-04  ·  **Completed:** 2026-06-04
- **Owner / session:** Claude Code
- **Weight:** 4%

## Goal
Wire field-evidence confirmation to the Polygon contract: a submission needs N distinct
institutional confirmations before it is marked complete. Build the confirm/reject endpoints
(recording on-chain) and the M7 confirmation inbox (Pulse PWA) + O8 verification review (console).

## Deliverables

### Backend
- [x] `app/models/confirmation.py` — Confirmation model (submission, confirmer, decision, signature, onchain_tx)
- [x] `alembic/versions/008_inc013_confirmation.py` — migration
- [x] `app/services/confirmation_service.py` — confirm_submission (records on-chain via polygon_client), reject_submission, get_confirmations
- [x] `app/schemas/pulse.py` — ConfirmRequest, RejectRequest, ConfirmationResult, ConfirmationOut
- [x] `app/api/pulse.py` — `POST /pulse/submissions/{id}/confirm`, `/reject`, `GET /…/confirmations`
- [x] `app/core/config.py` — `CONFIRMATIONS_REQUIRED = 2`
- [x] `tests/test_confirmation.py` — 10 tests

### Frontend
- [x] **M7 Confirmation Inbox** (`pulse-pwa-app/src/pages/Confirm.tsx`) — pending submissions, confirm/reject, live count
- [x] Bottom-nav "Confirm" tab added
- [x] **O8 Verification Review** (`frontend-oversight-app/src/pages/VerificationReview.tsx`) — table with confirm/reject actions, on-chain status
- [x] Sidebar "Verification Review" link added

## On-chain flow
1. A submission is recorded on Polygon lazily, on first confirmation (`_ensure_on_chain`).
2. Each `confirm` calls the Polygon mock's `confirm(key, confirmer_id)` which enforces:
   - distinctness (a confirmer cannot confirm twice → 409)
   - monitor cannot self-confirm (→ 400)
   - completion only on the Nth distinct confirmation
3. On completion the submission `status` → `confirmed` and the completion tx is stored.
4. Each confirmation is mirrored off-chain in the `confirmations` table with its `onchain_tx`.

## Acceptance criteria — results (shared with INC-012)
| Criterion | Test | Result |
|-----------|------|:------:|
| N-1 confirmations ≠ complete | `test_first_confirmation_does_not_complete` | ✅ |
| Nth distinct confirmation completes | `test_second_distinct_confirmation_completes` (status → confirmed) | ✅ |
| Single party cannot complete alone | `test_single_party_cannot_complete_alone` (dup → 409, stays pending) | ✅ |
| Confirmations recorded on Polygon | every confirm returns `onchain_tx`; `test_list_confirmations` | ✅ |
| Monitor cannot self-confirm | `test_monitor_cannot_self_confirm` → 400 | ✅ |
| Reject sets status rejected | `test_reject_submission` | ✅ |
| Cannot confirm after reject | `test_cannot_confirm_after_reject` → 400 | ✅ |
| Confirm requires permission | `test_confirm_requires_permission` → 403 | ✅ |
| Reject requires reason | `test_reject_requires_reason` → 422 | ✅ |

## Design note — separation of duties
No canonical role holds BOTH `create_submission` and `confirm_submission` — monitors capture,
confirmers confirm. This is the anti-fraud separation. The self-confirm guard is an additional
defence (the on-chain `confirmer != monitor` check), tested by constructing a submission whose
monitor IS a confirmer and asserting the guard rejects it.

## Tests — 309/309 backend green (10 new). Both frontends type-check clean (tsc exit 0).

## Follow-ups
- Real Amoy on-chain confirmation via Web3PolygonClient → INC-020
- O8/M7 show full confirmation history timeline → polish
- Confirmed submissions feed the integrated monitor (clears ghost signals) → INC-015

## Progress update
- INC-013 = **DONE** — Overall: **73%**.
