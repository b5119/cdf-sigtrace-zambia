# START HERE — CDF / SigTrace + CDF Pulse build

> **Read this first.** This file is the handover entry point. Any new session (human or AI) should
> read this, then `docs/09_PROGRESS.md`, then the next open increment in `docs/08_INCREMENT_PLAN.md`,
> and begin building. Everything needed to continue is in this folder.

---

## What we are building

A **blockchain-anchored accountability framework** for Zambia's Constituency Development Fund (CDF)
and government procurement, made of two prototype systems plus an integrated monitor:

| System | Job |
|--------|-----|
| **SigTrace Zambia** | Reads public OCDS procurement data, runs an 8-check anomaly engine over the contract-execution stage, anchors a SHA-256 hash of each signed contract to a permissioned Hyperledger Fabric ledger, and exposes a public document-vs-hash verification portal. |
| **CDF Pulse** | Offline-capable PWA that captures GPS-tagged photos of CDF projects, stores them on IPFS, records multi-party confirmations on a Polygon smart contract, and shows everything on a public constituency dashboard. |
| **Integrated Monitor** | Matches each disbursement against a clean-integrity contract AND a verified completion; a disbursement with no verified completion is raised as a **ghost-project signal**. |

The full rationale, design, legal posture and Q&A are in the proposal and the
**Architecture & Defence Brief** (`../CDF_SigTrace_Architecture_and_Defence_Brief.docx`).

---

## How this folder is organised

```
cdf_sigtrace_project/
├── START_HERE.md                ← you are here
├── README.md
├── docs/
│   ├── 00_PROJECT_OVERVIEW.md    purpose, scope, glossary
│   ├── 01_ARCHITECTURE.md        components, layers, runtime, data-flow routes
│   ├── 02_DATA_MODEL.md          entities, fields, relationships
│   ├── 03_API_ENDPOINTS.md       every endpoint (method, auth, req/resp)
│   ├── 04_SCREENS.md             every screen by role, in detail
│   ├── 05_RBAC_SECURITY.md       roles, permission matrix, security architecture
│   ├── 06_TECH_STACK.md          chosen stack + justification + versions
│   ├── 07_SETUP.md               how to run the repo locally
│   ├── 08_INCREMENT_PLAN.md      the ordered build increments (the work-list)
│   ├── 09_PROGRESS.md            live % completion + status table  ← UPDATE THIS
│   ├── 10_TESTING.md             testing strategy + definition of done
│   └── templates/
│       ├── INCREMENT_TEMPLATE.md  copy this when an increment is finished
│       └── VALIDATION_TEMPLATE.md test/validation evidence template
├── schematics/                  design schematics (wireframes, ERD, RBAC, deployment)
├── increments/                  one MD per COMPLETED increment (validation record)
└── src/                         the codebase (skeleton; fill it in)
    ├── backend/                 FastAPI services
    ├── frontend-public/         public transparency portal (React)
    ├── frontend-oversight/      oversight console (React)
    ├── pulse-pwa/               CDF Pulse field app (React PWA)
    ├── contracts/               Polygon smart contracts (Solidity)
    ├── anomaly-engine/          the 8-check engine (Python)
    └── ingestion/               OCDS ingestion pipeline (Python)
```

---

## The working rhythm (read carefully — this is the process)

We build **one increment at a time**, in the order in `docs/08_INCREMENT_PLAN.md`. For each increment:

1. **Pick** the next increment whose status in `docs/09_PROGRESS.md` is `TODO`. Set it to `IN PROGRESS`.
2. **Build** the deliverables listed for that increment in the plan, into `src/`.
3. **Test** against the increment's acceptance criteria (see `docs/10_TESTING.md`).
4. **Record** completion: copy `docs/templates/INCREMENT_TEMPLATE.md` to
   `increments/INC-XXX_<slug>.md`, fill in what was built, the tests run, the results, and any
   follow-ups. This file is the proof the increment is genuinely done.
5. **Update** `docs/09_PROGRESS.md`: set the increment to `DONE`, tick its checklist, and recompute
   the overall completion percentage.
6. **Commit** (`feat(INC-XXX): …`) and move to the next increment.

> **Rule:** never mark an increment `DONE` in PROGRESS.md without a matching `increments/INC-XXX_*.md`
> validation record showing the tests actually passed. "Done" means built **and** verified.

---

## Current status

- **Overall completion: 14%** (see `docs/09_PROGRESS.md` for the live figure).
- **Done:** INC-000 (scaffold), INC-001 (Auth/RBAC/JWT/MFA, 101 tests), INC-002 (OCDS ingestion pipeline, 116 tests).
- **Next up:** **INC-003 — Anomaly engine checks 1–3 (signing, standstill, time-gap).**

Open `docs/09_PROGRESS.md` to see the full table, then `docs/08_INCREMENT_PLAN.md` → INC-002 to begin.
