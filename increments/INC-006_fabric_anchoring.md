# INC-006 · Fabric Anchoring Service

- **Status:** DONE
- **Started:** 2026-06-02  ·  **Completed:** 2026-06-02
- **Owner / session:** Claude Code
- **Weight:** 6%

## Goal
SHA-256 hash of each signed contract → Hyperledger Fabric ledger. Document bytes
never go on-chain. Full verify pipeline (original → MATCH, modified → MISMATCH,
unknown → NOT_REGISTERED). Idempotent anchoring.

## Deliverables
- [x] `app/models/anchor.py` — AnchorRecord model (sha256, ledger_tx, block_ref, is_mock)
- [x] `alembic/versions/005_inc006_anchor.py` — migration
- [x] `app/services/fabric_client.py` — MockFabricClient (in-memory, deterministic) + FabricGatewayClient (real SDK stub); `FABRIC_MOCK_MODE=True` selects mock in dev/test
- [x] `app/services/anchor_service.py` — `anchor_contract()`, `verify_document()`, `get_anchor_history()`
- [x] `app/schemas/anchor.py` — AnchorRecordOut, VerifyResponse, PublicAnchorOut
- [x] `app/api/anchors.py` — POST /anchors, GET /anchors/{ocid}, GET /public/anchors/{ocid}, POST /verify
- [x] `tests/test_anchoring.py` — 26 tests

## Key design decisions
- **Document never on-chain.** Only the SHA-256 hex digest is submitted to Fabric. The upload bytes are discarded after hashing in the API handler.
- **Idempotency.** `anchor_contract()` checks for an existing AnchorRecord with the same (ocid, sha256). If found, returns it without a second Fabric transaction.
- **Re-anchoring allowed.** A different hash (re-signed/corrected document) creates a new record; full history is preserved via `get_anchor_history()`.
- **Mock mode.** `MockFabricClient` uses a module-level dict (`_mock_store`) for test isolation. Tests reset it via `client.clear()` in an `autouse` fixture. `FABRIC_MOCK_MODE=True` is the default — switch off by setting `FABRIC_GATEWAY_ENDPOINT` in production.

## Endpoints
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/api/v1/anchors` | action_anomaly | Hash upload + anchor to Fabric |
| GET | `/api/v1/anchors/{ocid}` | read_named | Full anchor history (named) |
| GET | `/api/v1/public/anchors/{ocid}` | public | Latest hash + tx (no named data) |
| POST | `/api/v1/verify` | read_named | Hash uploaded doc, compare to anchor |

## Acceptance criteria — results
| Criterion | How verified | Result |
|-----------|--------------|:------:|
| Anchoring writes hash + stores record | `test_anchor_creates_record` | ✅ |
| Re-anchoring same doc is idempotent | `test_anchor_idempotent_same_document` — same id returned | ✅ |
| Modified doc → new record | `test_anchor_new_record_for_modified_document` | ✅ |
| Original → MATCH | `test_verify_original_match` | ✅ |
| Modified → MISMATCH | `test_verify_modified_mismatch` | ✅ |
| Unknown OCID → NOT_REGISTERED | `test_verify_not_registered` | ✅ |
| Single byte change → MISMATCH | `test_verify_single_byte_change_mismatch` | ✅ |
| Public endpoint strips named data | `test_public_anchor_endpoint` — anchored_by absent | ✅ |
| `action_anomaly` required for POST /anchors | `test_post_anchor_wrong_role_forbidden` → 403 | ✅ |

## Tests — 232/232 green (26 new)
SHA-256 unit (3), MockFabricClient (4), anchor service integration (4),
verify service (4), API endpoints (11 — auth, RBAC, idempotency, match/mismatch/not_registered)

## Progress update
- INC-006 = **DONE** — Overall: **36%** (3+5+6+6+6+4+6).
