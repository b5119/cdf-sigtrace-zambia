# INC-003 · Anomaly Engine — Checks 1–3

- **Status:** DONE
- **Started:** 2026-06-02  ·  **Completed:** 2026-06-02
- **Owner / session:** Claude Code
- **Weight:** 6%

## Goal
Build the first three anomaly checks of the 8-check engine (signing, standstill, time-gap),
the check runner, the CheckDefinition/AnomalyFlag DB models, and the anomaly service that
persists flags against contracts.

## Deliverables

- [x] `src/anomaly-engine/engine/__init__.py`, `config.py` — default weights and thresholds
- [x] `src/anomaly-engine/engine/models.py` — `CheckResult`, `CheckOutput`, `EngineOutput`
- [x] `src/anomaly-engine/engine/base.py` — abstract `CheckBase`
- [x] `src/anomaly-engine/engine/checks/check_01_signing.py` — signing check
- [x] `src/anomaly-engine/engine/checks/check_02_standstill.py` — standstill check
- [x] `src/anomaly-engine/engine/checks/check_03_time_gap.py` — time-gap check
- [x] `src/anomaly-engine/engine/runner.py` — `run_checks()`, `build_config()`
- [x] `src/anomaly-engine/engine/cli.py` — CLI: `python -m engine.cli --ocid <ocid> --sample`
- [x] `src/backend/app/models/anomaly.py` — `CheckDefinition`, `AnomalyFlag`
- [x] `src/backend/alembic/versions/003_inc003_anomaly_checks.py` — migration + seeds all 8 check definitions
- [x] `src/backend/app/services/anomaly_service.py` — `analyse_contract()`, `analyse_all_contracts()`
- [x] `src/backend/tests/test_anomaly_checks.py` — 27 tests

## What was built

### Engine structure
```
src/anomaly-engine/engine/
  config.py       DEFAULT_WEIGHTS, DEFAULT_THRESHOLDS
  models.py       CheckResult (FLAG/OK/SKIP), CheckOutput, EngineOutput
  base.py         abstract CheckBase
  checks/
    check_01_signing.py    — missing signing date
    check_02_standstill.py — award→signing gap < 14 days
    check_03_time_gap.py   — identical stage dates / zero-day evaluation
  runner.py       run_checks(contract, config) → EngineOutput
  cli.py          python -m engine.cli --ocid <ocid> --sample [--json]
```

### Check logic

| # | Check | FLAG condition | SKIP (false-positive safeguard) |
|---|-------|---------------|--------------------------------|
| 1 | Signing | `signing_date` is null on a non-cancelled contract | Status = cancelled |
| 2 | Standstill | `(signing_date - award_date) < 14 days` | Framework call-off (framework_parent set); either date absent |
| 3 | Time-gap | All key stage dates identical **or** evaluation period < 1 day | Framework call-off; direct/limited procurement; no tender period dates |

Check 3 evaluates sub-check B (identical dates) before sub-check A (gap < min) — identical dates is a stronger fabrication signal.

### Database additions
- `check_definitions` — id (1-8), key, name, basis, severity, weight, enabled
- `anomaly_flags` — id, contract_ocid FK, check_id FK, result, weight_applied, evidence_note, created_at
- Seeded all 8 check definitions (checks 4-8 disabled, enabled=False, until INC-004)

### Config system
`build_config(weight_overrides, threshold_overrides, enabled_check_ids)` merges runtime
overrides onto defaults — same pattern that INC-017 (admin console) will use to push DB config.

### Anomaly service
`analyse_contract(db, ocid)` — loads contract, runs engine, replaces AnomalyFlag rows, updates
`contract.risk_score` (raw score, normalised in INC-005). Returns per-check JSON.
`analyse_all_contracts(db)` — bulk run over all contracts.

## Acceptance criteria — results

| Criterion | How verified | Result |
|-----------|--------------|:------:|
| Check 1 flags missing signing date | `test_flag_when_signing_date_absent` | ✅ |
| Check 1 OK when date present | `test_ok_when_signing_date_present` | ✅ |
| Check 1 SKIP for cancelled contract | `test_skip_cancelled_contract` | ✅ |
| Check 2 flags standstill violation | `test_flag_when_signed_before_standstill` (1-day gap) | ✅ |
| Check 2 OK when standstill observed | `test_ok_when_standstill_observed` (18 days) | ✅ |
| Check 2 SKIP for framework call-off | `test_skip_framework_calloff` | ✅ |
| Check 3 flags identical stage dates | `test_flag_identical_key_stage_dates` | ✅ |
| Check 3 flags zero-day evaluation | `test_flag_zero_day_evaluation_period` | ✅ |
| Check 3 SKIP for direct procurement | `test_skip_direct_procurement` | ✅ |
| Sample 002 missing signing date flagged | `test_sample_002_missing_signing_flagged` | ✅ |
| Sample 003 standstill violation flagged | `test_sample_003_standstill_violation_flagged` | ✅ |
| Sample 004 framework call-off NOT flagged | `test_sample_004_framework_calloff_standstill_skipped` | ✅ |
| Weight overrides respected | `test_weight_override_respected` | ✅ |
| Custom threshold respected | `test_custom_standstill_threshold` | ✅ |

## Tests

```
143 passed, 2 warnings in 1.89s

New in INC-003:
  test_anomaly_checks.py  27 tests
    — Check 1 (4), Check 2 (7), Check 3 (8), Runner (5), Sample integration (4)
```

## Decisions / deviations
- Sub-check B (identical dates) evaluated before sub-check A (evaluation gap) in Check 3 —
  identical timestamps is the stronger fabrication signal and takes priority in the evidence note.
- `AnomalyFlag.id` uses `String(36)` (UUID string) for SQLite compatibility in tests.
- Checks 4-8 are seeded in `check_definitions` but `enabled=False` until INC-004.
- `contract.risk_score` is set to `int(raw_score)` — normalised 0-100 scoring comes in INC-005.

## Follow-ups / known gaps
- [ ] INC-004: implement checks 4-8 (forensics, supplier-network, score-variance, amendment, debarment)
- [ ] INC-005: normalise raw_score → weighted 0-100 risk score
- [ ] INC-009: expose `/contracts/{ocid}/checks` API endpoint for the oversight console

## Progress update
- INC-003 = **DONE** in `09_PROGRESS.md`.
- Overall completion: **20%** (3 + 5 + 6 + 6).
