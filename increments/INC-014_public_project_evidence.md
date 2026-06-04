# INC-014 · Public Project Dashboard (Evidence)

- **Status:** DONE
- **Started:** 2026-06-04  ·  **Completed:** 2026-06-04
- **Owner / session:** Claude Code
- **Weight:** 4%

## Goal
The public project page (P5): photographic evidence (from IPFS), verified location, and
confirmation status — all **de-identified** (no monitor or confirmer identity). Endpoint
`/pulse/projects/{id}/evidence` gets a public, de-identified counterpart.

## Deliverables

### Backend
- [x] `app/schemas/public.py` — PublicEvidenceItem, PublicProjectDetail, PublicEvidenceListResponse
- [x] `app/api/public.py`:
  - `GET /public/projects/{id}` — disbursement, evidence count, verified status, location centroid
  - `GET /public/projects/{id}/evidence` — de-identified evidence list (NO monitor_id)
  - `GET /public/evidence/{cid}` — serve evidence photo by IPFS CID (content-addressed, public)
- [x] `tests/test_public_evidence.py` — 9 tests

### Frontend — `src/frontend-public-app/`
- [x] **P5 ProjectDetail** (`pages/ProjectDetail.tsx`) — disbursement summary, evidence photo gallery (IPFS), verified-location panel, per-evidence confirmation status + on-chain badge
- [x] `lib/api.ts` — projectApi (detail, evidence, photoUrl)
- [x] Route `PROJECT = /projects/:id`
- [x] ConstituencyDetail project rows now link to P5 (ids aligned to backend `proj-001…004`)

## De-identification (the two-tier rule)
The public evidence list deliberately **omits `monitor_id`** and any confirmer identity.
Each item carries only: submission_id, ipfs_cid, lat/lng, category, captured_at, status,
confirmation_count, onchain_tx. Verified by `test_evidence_has_no_monitor_identity`, which
asserts neither the string "monitor_id" nor the actual monitor UUID appears in the response.

## Acceptance criteria — results
| Criterion | Test | Result |
|-----------|------|:------:|
| Public project page shows evidence | `test_project_detail_no_auth`, `test_evidence_list_no_auth` | ✅ |
| Shows verified location | `test_project_detail_verified_location` (centroid) | ✅ |
| Shows confirmation status | `test_evidence_shows_confirmation_status` (status + count + tx) | ✅ |
| Verified after 2 confirmations | `test_project_verified_after_confirmation` | ✅ |
| **De-identified — no monitor identity** | `test_evidence_has_no_monitor_identity` | ✅ |
| Evidence photo by CID, no auth | `test_evidence_photo_by_cid_no_auth` (bytes match) | ✅ |
| Unknown CID → 404 | `test_evidence_photo_unknown_cid_404` | ✅ |
| Unknown project → empty list | `test_evidence_empty_for_unknown_project` | ✅ |

## Tests — 318/318 backend green (9 new). Public app type-checks clean (tsc exit 0).

## Design fidelity (P5)
Matches `stitch_export/project_transparency_detail`: disbursement summary, photographic evidence
grid (IPFS-served), verified-location panel, confirmation status badges. Photos load from
`/public/evidence/{cid}` (content-addressed). Footer note explains IPFS + Polygon provenance.

## Follow-ups
- Real MapLibre mini-map for verified location (currently a location pin panel) → polish
- Evidence photo lightbox/zoom → polish
- Wire P5 into the dashboard "recently verified" feed → INC-015 ties delivery to monitor

## Progress update
- INC-014 = **DONE** — Overall: **77%**. M2 milestone (CDF Pulse MVP) nearly complete.
