# INC-018 · Audit Logging (Anchored)

- **Status:** DONE
- **Started:** 2026-06-05  ·  **Completed:** 2026-06-05
- **Owner / session:** Claude Code
- **Weight:** 3%

## Goal
An append-only audit log of every privileged action, with a periodic batch hash anchored to
Hyperledger Fabric — making the audit trail tamper-evident. Screen S8 (Audit Log Viewer).

## Deliverables

### Backend
- [x] `app/models/audit.py` — AuditLog (append-only) + migration `012_inc018_audit`
- [x] `app/services/audit_service.py` — log_action, compute_batch_hash, anchor_batch, get_audit
- [x] `log_action` wired into privileged actions:
  - `case_service` — case_opened, case_escalated
  - `admin_service` — weights_updated, thresholds_updated
  - `monitor_service` — ghost_signal_cleared
  - `anchor_service` — contract_anchored
- [x] `app/api/admin.py` — `GET /admin/audit` (read_audit), `POST /admin/audit/anchor` (system_admin)
- [x] `tests/test_audit.py` — 9 tests

### Frontend — oversight console
- [x] **S8 Audit Log Viewer** (Admin → Audit tab) — filterable entry table, per-entry anchored status, "Anchor batch to Fabric" button showing the resulting batch hash

## Tamper-evidence design
- Each entry is **append-only** — never updated or deleted (no mutation endpoints).
- `anchor_batch` collects all unanchored entries, computes a SHA-256 over their canonical
  JSON serialisation (sorted keys), and anchors that batch hash to Fabric via the existing
  mock/real Fabric client. Every entry in the batch is stamped with the batch hash + tx.
- Altering any past entry would change the recomputed batch hash and break the on-chain anchor —
  the trail is cryptographically tamper-evident.

## Acceptance criteria — results
| Criterion | Test | Result |
|-----------|------|:------:|
| **Every privileged action is logged** | `test_opening_case_is_audited`, `test_weight_change_is_audited` | ✅ |
| log_action appends append-only entry | `test_log_action_appends` | ✅ |
| **Audit batch hash is anchored** | `test_anchor_batch_stamps_entries` (entries get hash + tx) | ✅ |
| Batch hash deterministic | `test_batch_hash_deterministic` (64-char SHA-256) | ✅ |
| Anchoring idempotent | `test_anchor_batch_idempotent` (already-anchored skipped) | ✅ |
| read_audit required to view | `test_audit_requires_read_audit` → 403; `test_officer_can_read_audit` → 200 | ✅ |
| Anchor endpoint works | `test_audit_anchor_endpoint` | ✅ |

## Tests — 367/367 backend green (9 new). Console type-checks clean (tsc exit 0).

## Follow-ups
- Blanket middleware to auto-log ALL mutating requests (currently key services log explicitly) → INC-019
- Scheduled (Celery beat) periodic audit anchoring → INC-020
- Verify-audit-integrity endpoint (recompute batch hash, compare to on-chain) → INC-019

## Progress update
- INC-018 = **DONE** — Overall: **94%**.
