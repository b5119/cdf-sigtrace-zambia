# INC-005 · Risk Scoring + Two-Tier Output

- **Status:** DONE
- **Started:** 2026-06-02  ·  **Completed:** 2026-06-02
- **Owner / session:** Claude Code
- **Weight:** 4%

## Goal
Normalise engine output into a 0-100 risk score with a per-check breakdown,
persist it in the DB, expose it via restricted API endpoints, and enforce the
public-vs-restricted two-tier projection at the contract list and detail level.

## Deliverables
- [x] `app/models/risk.py` — RiskScore model (score, normalised_score, breakdown, weights_version)
- [x] `alembic/versions/004_inc005_risk_score.py` — migration
- [x] `app/services/scoring_service.py` — compute_score(), risk_tier(), score_contract(), score_all_contracts()
- [x] `app/schemas/contract.py` — ContractPublic / ContractRestricted / RiskScoreOut / AnalysisRunResponse
- [x] `app/api/contracts.py` — GET /contracts (two-tier), GET /contracts/{ocid}, GET /contracts/{ocid}/risk, GET /contracts/{ocid}/checks
- [x] `app/api/analysis.py` — POST /analysis/run (system_admin)
- [x] `tests/test_scoring.py` — 26 tests

## Scoring formula
- **absolute_score** = Σ weight_applied for FLAG checks (0–100; weights sum to 100)
- **applicable_max** = Σ weight for non-SKIP checks
- **normalised_score** = round(absolute / applicable_max × 100), capped at 100
- **tier** = high (≥60) | medium (≥30) | low (<30)
- **weights_version** = SHA-256[:8] of weight dict — detects config drift

## Two-tier enforcement
Public callers → ContractPublic (no procuring_entity, no supplier name, score only).
Restricted callers → ContractRestricted (full named data).
Enforced via explicit Pydantic response schemas + scoping middleware (defence-in-depth).

## Tests — 206/206 green (26 new)
- Scoring unit: 8 (zero flags, single flag, all flags, normalised for skips, breakdown, cap, weights version)
- Tier labelling: 4
- Two-tier projection: 5 (public strips names, restricted gets them, all roles correct)
- API: 9 (list public/restricted, get contract auth, get risk score, analysis run auth/response)

## Progress update
- INC-005 = **DONE** — Overall: **30%** (3+5+6+6+6+4).
