# 08 · Increment Plan (the build work-list)

Build in this order. Each increment is a vertical slice that ends in something testable. `Weight` is
its share of overall completion (sums to 100). When finished, record it in `increments/INC-XXX_*.md`
and update `09_PROGRESS.md`.

> **Definition of Done** for every increment: deliverables built · acceptance criteria pass · tests
> written and green · `increments/INC-XXX_*.md` validation record created · `09_PROGRESS.md` updated.

| ID | Title | Weight | Delivers (screens/endpoints/code) |
|----|-------|:-----:|-----------------------------------|
| INC-000 | Project scaffold & handover | 3 | This folder: docs, schematics, increment/progress system, src skeleton |
| INC-001 | Auth, RBAC & user/role model | 5 | `/auth/*`; roles, permissions, MFA; X1–X4, O1, M1; scoping middleware |
| INC-002 | OCDS ingestion pipeline | 6 | `ingestion/`; `/ingestion/runs`; Contract/Supplier load; S5 (read) |
| INC-003 | Anomaly engine — checks 1–3 | 6 | signing, standstill, time-gap; per-contract flags |
| INC-004 | Anomaly engine — checks 4–8 | 6 | forensics, supplier-network, score-variance, amendment, debarment |
| INC-005 | Risk scoring + two-tier output | 4 | weighted 0–100 score; public vs restricted projections |
| INC-006 | Fabric anchoring service | 6 | `/anchors`; SHA-256 → Hyperledger Fabric; anchor records |
| INC-007 | Public verification portal | 4 | `POST /public/verify-contract`; screen P6; `/verify` |
| INC-008 | Public CDF dashboard + map | 6 | P1–P4, P7–P9; `/public/*`; constituency choropleth |
| INC-009 | Oversight console (risk) | 8 | O2–O5, O11–O13; `/contracts/*`, `/suppliers/network` |
| INC-010 | CDF Pulse PWA — capture + offline | 6 | M2–M6, M8; `/pulse/assignments`, `/pulse/submissions`, `/pulse/sync` |
| INC-011 | IPFS evidence storage | 3 | pin photos, store CID, retrieve evidence |
| INC-012 | Polygon confirmation contract | 6 | `contracts/`; Solidity multi-sig; deploy to Amoy testnet |
| INC-013 | Confirmation workflow | 4 | M7, O8; `/pulse/.../confirm`,`/reject`; on-chain record |
| INC-014 | Public project dashboard (evidence) | 4 | P5; `/pulse/projects/{id}/evidence` |
| INC-015 | Integrated monitor + ghost queue | 6 | O6, O7; `/monitor/*`; disbursement↔contract↔completion matching |
| INC-016 | Cases & notifications | 3 | O10, O13; `/cases/*`, `/notifications/*` |
| INC-017 | Admin console | 5 | S1–S9; `/admin/*`; weights/thresholds/users/health |
| INC-018 | Audit logging (anchored) | 3 | append-only AuditLog; periodic hash anchor; S8 |
| INC-019 | Testing, security & accessibility hardening | 4 | coverage, pen-test checklist, WCAG pass, X5/X6 |
| INC-020 | Deployment, CI/CD & docs finalisation | 2 | docker-compose, GitHub Actions, runbook |

**Total = 100.**

## Acceptance criteria (per increment, summary — expand in the validation record)
- **INC-001:** A restricted user can log in with MFA; a public caller gets only de-identified data;
  permission checks reject unauthorised calls (tested). Tokens rotate; logout revokes.
- **INC-002:** A real OCDS sample loads into Contract/Supplier idempotently; re-running doesn't
  duplicate; run history + error log visible.
- **INC-003/004:** Each check produces correct flags on crafted fixtures (positive + negative cases),
  including the false-positive safeguards (framework call-offs, lawful emergency).
- **INC-005:** Score = weighted sum normalised to 0–100; weights come from config; public projection
  contains no names/contract-level PII.
- **INC-006:** Anchoring a contract writes a hash to Fabric and stores the tx; re-anchoring is
  idempotent; the document is never sent on-chain.
- **INC-007:** Uploading the original document returns MATCH; a modified byte returns MISMATCH.
- **INC-008:** Public dashboard + map render real aggregates; no named data anywhere in the public app.
- **INC-009:** Officer can list/sort/filter contracts, open a contract, see all 8 checks + evidence,
  and take an action; supplier network renders.
- **INC-010:** Capture works fully offline; submissions queue and sync on reconnect with no loss;
  GPS+timestamp embedded.
- **INC-011:** Photo pins to IPFS; altering the file changes the CID (tamper-evidence demonstrated).
- **INC-012/013:** Contract requires N distinct confirmations before "complete"; confirmations recorded
  on Polygon; a single party cannot complete alone.
- **INC-014:** Public project page shows evidence, verified location and confirmation status.
- **INC-015:** A disbursement with no verified completion within the window appears in the ghost queue;
  matching one clears it.
- **INC-016:** Cases open from a contract or ghost signal; notes/status/escalation work; alerts fire.
- **INC-017:** Admin can change a weight and see the score recompute; thresholds editable; users
  manageable; health reflects real component status.
- **INC-018:** Every privileged action is logged; the audit batch hash is anchored.
- **INC-019:** Coverage targets met; security checklist passed; WCAG AA on public + Pulse.
- **INC-020:** `docker-compose up` brings the whole stack up; CI runs lint+test on PR.

## Dependencies
INC-001 precedes all restricted work. INC-002 precedes 003–005, 009, 015. INC-006 precedes 007.
INC-010 precedes 011, 013. INC-012 precedes 013. INC-002+010 precede 015. 017 depends on 005 (weights).
