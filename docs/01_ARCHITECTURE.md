# 01 · Architecture

See also: `schematics/deployment_architecture.png`, `schematics/erd.png`.

## 1. High-level
Two systems + an integrated monitor, over shared cryptographic infrastructure, behind one API gateway.

```
            Public portal      Oversight console     CDF Pulse PWA     Admin console
                  \                  |                    |                /
                   \                 |                    |               /
                 ┌───────────────────────────────────────────────────────────┐
                 │  API GATEWAY  — TLS 1.3 · JWT/MFA · RBAC · rate-limit ·     │
                 │                 two-tier data scoping · audit               │
                 └───────────────────────────────────────────────────────────┘
   Auth/RBAC · Ingestion · Anomaly engine · Anchoring & verify · Pulse API · Integrated monitor · Cases
                 |                |                 |                |
        PostgreSQL · Redis · Object store    Hyperledger Fabric · Polygon PoS · IPFS
```

## 2. Components (what lives in `src/`)
| Component | Folder | Responsibility |
|-----------|--------|----------------|
| API / gateway | `backend/api` | Routing, authN/Z, scoping, validation, OpenAPI |
| Auth & RBAC | `backend/core` | JWT, MFA, roles, permission checks, institution scoping |
| Ingestion | `ingestion/` | Fetch OCDS, normalise, load to DB; scheduled runs |
| Anomaly engine | `anomaly-engine/` | The 8 checks + weighted risk score (library + CLI + service) |
| Anchoring & verify | `backend/services/anchor` | SHA-256 hash → Fabric; document-vs-hash verification |
| Pulse API | `backend/services/pulse` | Submissions, IPFS pinning, confirmation orchestration |
| Smart contract | `contracts/` | Polygon multi-sig confirmation contract |
| Integrated monitor | `backend/services/monitor` | Disbursement ↔ contract ↔ completion matching; ghost-project signals |
| Cases & notifications | `backend/services/cases` | Case management, alerts |
| Public portal | `frontend-public/` | Transparency dashboard, map, verification portal |
| Oversight console | `frontend-oversight/` | Risk list, contract detail, network, queue, cases |
| Pulse PWA | `pulse-pwa/` | Offline capture + sync |
| Admin console | part of `frontend-oversight` (admin routes) | Users, weights, thresholds, ingestion, health |

## 3. Architecture layers (the "ecosystem stack")
1. **Data source** — ZPPA e-GP / OCDS published data (and the separate CPMS module).
2. **Open data** — OCDS records + the 21 analytics reports.
3. **Researcher systems** — SigTrace and CDF Pulse.
4. **Shared cryptographic infrastructure** — SHA-256, Fabric, Polygon, IPFS.
5. **Action layer** — OAG, ACC, Parliament, citizens.

## 4. Data-flow routes (each is independently testable)
**Route A — Procurement ingestion & analysis**
OCDS records → ingestion → DB → 8-check engine → per-contract flags → weighted 0–100 score → two-tier output.

**Route B — Contract anchoring**
Signed-contract PDF → SHA-256 hash → tx to Hyperledger Fabric → immutable timestamped hash record
(the document itself never goes on-chain).

**Route C — Public verification**
User uploads a contract → portal re-computes SHA-256 → compares to the anchored hash → match / mismatch.

**Route D — Field evidence capture**
Monitor captures photo offline (GPS+timestamp embedded) → local cache → on reconnect: photo → IPFS
(returns CID) → hash+metadata+location → Polygon multi-sig contract → confirmations → public dashboard.

**Route E — Integrated mismatch detection**
Monitor job matches each disbursement against (i) a clean-integrity contract and (ii) a verified
completion; no verified completion within the window → ghost-project signal → OAG queue.

## 5. Runtime / processing model
- **Synchronous** (request/response): auth, reads, verification, submission accept.
- **Asynchronous** (Celery + Redis): ingestion runs, batch anomaly analysis, anchoring tx, IPFS
  pinning, integrated-monitor sweeps, notifications.
- **Idempotency**: ingestion and anchoring use OCID + content-hash keys so re-runs don't duplicate.

## 6. Two-tier data scoping (enforced centrally)
A scoping middleware reads the caller's role and:
- **Public/anonymous** → only aggregated, de-identified projections (no party names, no contract-level PII).
- **Restricted (officer/analyst/admin)** → named, contract-level data, filtered by institution where applicable.
This is enforced once, at the gateway/service boundary, not per-screen.

## 7. Key non-functional requirements
- Anonymity/confidentiality of any personal data (off-chain, encrypted at rest).
- Integrity (anchored hashes; append-only audit log).
- Availability of the public read path; resilience of the Pulse offline path.
- Explainability/auditability of every flag.
- Accessibility (WCAG 2.1 AA target for public + Pulse).
