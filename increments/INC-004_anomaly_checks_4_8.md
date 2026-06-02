# INC-004 · Anomaly Engine — Checks 4–8

- **Status:** DONE
- **Started:** 2026-06-02  ·  **Completed:** 2026-06-02
- **Owner / session:** Claude Code
- **Weight:** 6%

## Goal
Complete the 8-check anomaly engine with checks 4–8: forensics, supplier network,
score variance, amendment cap, and debarment. All 8 checks are now active.

## Deliverables

- [x] `engine/checks/check_04_forensics.py` — round-number bias + predetermined pricing
- [x] `engine/checks/check_05_supplier_network.py` — shared address/phone/TPIN among tenderers
- [x] `engine/checks/check_06_score_variance.py` — award value exceeds tender estimate by >15%
- [x] `engine/checks/check_07_amendment.py` — cumulative amendment value exceeds cap
- [x] `engine/checks/check_08_debarment.py` — debarred supplier awarded contract
- [x] `engine/runner.py` — updated to include all 8 checks
- [x] `alembic/versions/003_*` — checks 4-8 enabled in DB seed (updated)
- [x] `src/ingestion/sample/ocds_sample.json` — added record 006 (amendment violation: 33% increase)
- [x] `tests/test_anomaly_checks_4_8.py` — 37 tests
- [x] 180/180 total tests green

## Check logic

| # | Check | FLAG condition | SKIP safeguards |
|---|-------|---------------|-----------------|
| 4 | Forensics | Round-number value (multiple of 1M) OR award == estimate exactly | Framework call-off; no value |
| 5 | Supplier network | ≥2 suppliers share address, phone, or TPIN | Framework call-off; direct procurement; <2 suppliers |
| 6 | Score variance | Award > estimate by more than cap% (default 15%) | Framework call-off; no estimate; no value |
| 7 | Amendment | Cumulative amendment deltas > cap% of original value (default 15%) | No original value |
| 8 | Debarment | Supplier debarred at time of award (inclusive) | Debarment info absent (no false positive); unparseable date |

## Sample fixture update
Added `ocds-zm-zppa-006` — Ministry of Housing construction contract with a 33% amendment
increase (ZMW 18M → ZMW 24M), triggering Check 7.

## Tests (37 new)
- Check 4: 6 tests (2 FLAG, 2 OK, 2 SKIP)
- Check 5: 8 tests (3 FLAG, 1 OK, 4 SKIP)
- Check 6: 7 tests (1 FLAG, 3 OK, 3 SKIP)
- Check 7: 6 tests (2 FLAG, 2 OK, 1 SKIP, 1 sample integration)
- Check 8: 6 tests (3 FLAG, 1 OK, 2 SKIP)
- Runner: 4 tests (8 outputs, IDs 1-8, score accumulation, multi-flag stress)

## Progress update
- INC-004 = **DONE** in `09_PROGRESS.md`.
- Overall completion: **26%** (3+5+6+6+6).
