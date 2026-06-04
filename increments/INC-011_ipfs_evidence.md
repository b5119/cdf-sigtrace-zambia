# INC-011 · IPFS Evidence Storage

- **Status:** DONE
- **Started:** 2026-06-04  ·  **Completed:** 2026-06-04
- **Owner / session:** Claude Code
- **Weight:** 3%

## Goal
Pin field-evidence photos to IPFS, store the content-addressed CID on the submission,
and retrieve evidence. Demonstrate tamper-evidence: altering the photo changes the CID.

## Deliverables

### Backend
- [x] `app/services/ipfs_client.py` — `compute_cid()` (real CIDv1: raw codec, sha2-256, base32 → `bafkrei…`); MockIPFSClient (in-memory, content-addressed) + KuboIPFSClient (real Kubo HTTP API); `IPFS_MOCK_MODE` flag
- [x] `app/services/ipfs_service.py` — `pin_submission_photo()`, `retrieve_photo()`, `verify_cid()`, `get_project_evidence()`
- [x] `app/core/config.py` — IPFS_API_URL, IPFS_GATEWAY_URL, IPFS_MOCK_MODE, IPFS_MAX_PHOTO_MB
- [x] `app/api/pulse.py` — `POST /pulse/submissions/{id}/photo`, `GET /pulse/submissions/{id}/photo`, `GET /pulse/projects/{id}/evidence`
- [x] `tests/test_ipfs.py` — 15 tests
- No migration needed — `pulse_submissions.ipfs_cid` column already exists (INC-010)

### Frontend — `src/pulse-pwa-app/`
- [x] `lib/api.ts` — `evidenceApi.uploadPhoto()`
- [x] `lib/sync.ts` — after metadata sync, pins each captured photo to IPFS (content-addressed = idempotent)
- [x] `pages/SubmissionDetail.tsx` — shows evidence-photo pin status

## The tamper-evidence property (core acceptance criterion)
IPFS is **content-addressed**: `CID = base32( CIDv1 + raw-codec + sha2-256(photo_bytes) )`.
The CID is a cryptographic commitment to the exact photo bytes.
- `compute_cid()` produces genuine CIDv1 format (`bafkrei…`, 59 chars) identical to real IPFS output.
- A single-byte change to the photo → completely different CID.
- `verify_cid(cid, bytes)` returns False for any altered bytes.

This means a stored CID cannot be satisfied by a doctored photo — the evidence is tamper-evident.

## Acceptance criteria — results
| Criterion | Test | Result |
|-----------|------|:------:|
| Photo pins to IPFS, CID stored | `test_upload_photo_pins_and_stores_cid` | ✅ |
| **Altering the file changes the CID** | `test_altering_one_byte_changes_cid` | ✅ |
| CID is deterministic | `test_cid_is_deterministic` | ✅ |
| CID is real CIDv1 raw format (`bafkrei…`) | `test_cid_format_is_cidv1_raw` | ✅ |
| verify_cid rejects altered bytes | `test_verify_cid_rejects_altered` | ✅ |
| Retrieve photo round-trip | `test_retrieve_photo_round_trip` (bytes match + X-IPFS-CID header) | ✅ |
| Same bytes → same CID (idempotent) | `test_mock_add_same_bytes_same_cid` | ✅ |
| Non-image rejected (415) | `test_upload_photo_rejects_non_image` | ✅ |
| Cross-monitor upload forbidden (403) | `test_upload_photo_forbidden_for_other_monitor` | ✅ |
| Project evidence lists pinned only | `test_project_evidence_lists_pinned_only` | ✅ |

## Tests — 288/288 backend green (15 new)

## Design notes
- Mirrors the Fabric anchoring pattern (INC-006): mock + real client behind a `*_MOCK_MODE` flag.
- The mock computes a **real-format** CID so it behaves exactly like production IPFS — the
  tamper-evidence test is meaningful, not a stub.
- PWA pins photos during sync (after metadata), so capture stays fully offline; pinning happens
  when connectivity returns. Content-addressing makes re-pinning idempotent automatically.

## Follow-ups
- Public project evidence page (P5) with photo gallery → INC-014
- Polygon on-chain record of the submission/CID → INC-012
- Real Kubo node in docker-compose → INC-020

## Progress update
- INC-011 = **DONE** — Overall: **63%**.
