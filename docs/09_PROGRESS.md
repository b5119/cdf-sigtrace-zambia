# 09 · Progress — LIVE

> **This is the single source of truth for completion.** Update it whenever an increment changes
> state. Overall % = Σ(weight × completion%). Do not mark an increment `DONE` without a matching
> `increments/INC-XXX_*.md` validation record.

## Overall completion: **69%**

```
[██████████████████████████████████░░░░░░░░░░░░░░░]  69 / 100
```

Last updated: INC-012 complete (2026-06-04).

## Status table
Status ∈ `TODO` · `IN PROGRESS` · `BLOCKED` · `DONE`.

| ID | Title | Weight | Status | % | Validation record |
|----|-------|:-----:|--------|:--:|-------------------|
| INC-000 | Project scaffold & handover | 3 | **DONE** | 100 | `increments/INC-000_scaffold.md` |
| INC-001 | Auth, RBAC & user/role model | 5 | **DONE** | 100 | `increments/INC-001_auth_rbac.md` |
| INC-002 | OCDS ingestion pipeline | 6 | **DONE** | 100 | `increments/INC-002_ocds_ingestion.md` |
| INC-003 | Anomaly engine — checks 1–3 | 6 | **DONE** | 100 | `increments/INC-003_anomaly_checks_1_3.md` |
| INC-004 | Anomaly engine — checks 4–8 | 6 | **DONE** | 100 | `increments/INC-004_anomaly_checks_4_8.md` |
| INC-005 | Risk scoring + two-tier output | 4 | **DONE** | 100 | `increments/INC-005_risk_scoring.md` |
| INC-006 | Fabric anchoring service | 6 | **DONE** | 100 | `increments/INC-006_fabric_anchoring.md` |
| INC-007 | Public verification portal | 4 | **DONE** | 100 | `increments/INC-007_public_verification_portal.md` |
| INC-008 | Public CDF dashboard + map | 6 | **DONE** | 100 | `increments/INC-008_public_dashboard.md` |
| INC-009 | Oversight console (risk) | 8 | **DONE** | 100 | `increments/INC-009_oversight_console.md` |
| INC-010 | CDF Pulse PWA — capture + offline | 6 | **DONE** | 100 | `increments/INC-010_pulse_pwa.md` |
| INC-011 | IPFS evidence storage | 3 | **DONE** | 100 | `increments/INC-011_ipfs_evidence.md` |
| INC-012 | Polygon confirmation contract | 6 | **DONE** | 100 | `increments/INC-012_polygon_confirmation.md` |
| INC-013 | Confirmation workflow | 4 | TODO | 0 | — |
| INC-014 | Public project dashboard (evidence) | 4 | TODO | 0 | — |
| INC-015 | Integrated monitor + ghost queue | 6 | TODO | 0 | — |
| INC-016 | Cases & notifications | 3 | TODO | 0 | — |
| INC-017 | Admin console | 5 | TODO | 0 | — |
| INC-018 | Audit logging (anchored) | 3 | TODO | 0 | — |
| INC-019 | Testing, security & accessibility | 4 | TODO | 0 | — |
| INC-020 | Deployment, CI/CD & docs | 2 | TODO | 0 | — |

## How to update
1. Set the increment's `Status` and `%` (use 0/50/100, or finer if helpful).
2. Recompute **Overall** = Σ(weight × %/100), rounded.
3. Redraw the bar (each block ≈ 2%).
4. Update "Last updated".

## Milestones
- **M1 — SigTrace MVP (~40%):** INC-001…009 → ingest, score, anchor, verify, public + oversight views.
- **M2 — CDF Pulse MVP (~70%):** INC-010…015 → capture, IPFS, Polygon, confirmations, ghost queue.
- **M3 — Platform complete (100%):** INC-016…020 → cases, admin, audit, hardening, deployment.
