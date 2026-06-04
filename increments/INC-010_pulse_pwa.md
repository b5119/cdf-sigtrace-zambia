# INC-010 · CDF Pulse PWA — Capture + Offline

- **Status:** DONE
- **Started:** 2026-06-04  ·  **Completed:** 2026-06-04
- **Owner / session:** Claude Code
- **Weight:** 6%

## Goal
Build the CDF Pulse field app — an offline-first PWA for community monitors to capture
GPS-tagged photographic evidence of project completion. Capture works fully offline; submissions
queue in IndexedDB and sync exactly-once on reconnect. Screens M1–M6, M8.

## Deliverables

### Backend
- [x] `app/models/pulse.py` — PulseSubmission model (client_uuid idempotency key, GPS, timestamp, status)
- [x] `alembic/versions/007_inc010_pulse.py` — migration
- [x] `app/schemas/pulse.py` — SubmissionCreate, SyncBatch, SyncResult, etc.
- [x] `app/services/pulse_service.py` — create_submission (idempotent), sync_batch, list/get with scoping
- [x] `app/api/pulse.py` — GET /assignments, POST /submissions, POST /sync, GET /submissions, GET /submissions/{id}
- [x] `tests/test_pulse.py` — 12 tests

### Frontend — `src/pulse-pwa-app/`
- [x] React 18 + Vite + Tailwind + vite-plugin-pwa (Workbox service worker)
- [x] **IndexedDB offline queue** (`lib/db.ts`) — every capture lands here first, works fully offline
- [x] **Sync engine** (`lib/sync.ts`) — pushes pending submissions, exactly-once via client_uuid
- [x] **M1 Login** + MFA — device-bound credential, token in localStorage
- [x] **M2 Home** — assigned constituency + project list
- [x] **M3/M4 Capture** — camera (file capture), auto GPS lock (watchPosition), timestamp, category, note, offline indicator
- [x] **M5 Submissions** — sync queue with status badges, manual + auto sync on reconnect
- [x] **M6 Submission Detail** — photo, GPS, client/server IDs, IPFS placeholder
- [x] **M8 Profile** — account, connection status, sign-out
- [x] PhoneShell + BottomNav + online/offline indicator
- [x] PWA manifest (installable, standalone, portrait) + service worker (app-shell precache)

## The exactly-once invariant (core acceptance criterion)
Every submission carries a **client-generated `client_uuid`** (`cu-<randomUUID>`).
- Capture → write to IndexedDB immediately (offline-safe).
- Sync → POST batch to `/pulse/sync`.
- Backend de-dupes on `client_uuid` (unique constraint) — re-syncing the same submission
  returns `duplicates++` without creating a row.
- Tested: submit-then-sync, double-sync, offline-retry all produce zero duplicates.

## Acceptance criteria — results
| Criterion | Test | Result |
|-----------|------|:------:|
| Capture works (GPS + timestamp embedded) | `test_create_submission`, `test_gps_and_timestamp_persisted` | ✅ |
| Offline queue → sync exactly-once | `test_sync_idempotent_no_duplicates` (double-sync → 0 dups) | ✅ |
| Submit online then in sync batch = no dup | `test_single_submit_then_sync_no_duplicate` | ✅ |
| Batch sync creates all new | `test_sync_batch_creates_submissions` | ✅ |
| Monitor sees only own submissions | `test_monitor_sees_only_own_submissions` | ✅ |
| Cross-monitor detail forbidden | `test_submission_detail_forbidden_for_other_monitor` | ✅ |
| create_submission permission required | `test_create_submission_forbidden_without_permission` → 403 | ✅ |

## Build
```
✓ built in 5.53s — PWA v1.3.0, generateSW, precache 8 entries (349 KiB)
dist/sw.js + workbox generated · dist/manifest.webmanifest
dist/assets/index.js 331 kB (106 kB gzip)
```

## Tests — 273/273 backend green (12 new pulse tests)

## Follow-ups
- IPFS pinning of photos (ipfs_cid currently null) → INC-011
- Polygon on-chain submission record (onchain_tx null) → INC-012
- M7 Confirmation inbox (inst_confirmer) → INC-013
- Background Sync API registration (currently sync-on-reconnect via online event) → INC-019 hardening
- Playwright offline E2E (airplane mode → capture → reconnect → sync) → INC-019

## Progress update
- INC-010 = **DONE** — Overall: **60%**. M2 milestone (CDF Pulse MVP) begun.
