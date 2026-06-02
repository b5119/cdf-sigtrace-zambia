# INC-000 · Project scaffold & handover

- **Status:** DONE
- **Started:** project kickoff  ·  **Completed:** same session
- **Owner / session:** initial planning session
- **Weight:** 3%

## Goal
Stand up the project folder so any later session can pick up and build the system increment by
increment, with design schematics, full specifications, and a progress/validation system.

## Deliverables
- [x] `START_HERE.md` handover entry point + working rhythm
- [x] `README.md`
- [x] `docs/00_PROJECT_OVERVIEW.md`
- [x] `docs/01_ARCHITECTURE.md` (components, layers, data-flow routes, runtime, two-tier scoping)
- [x] `docs/02_DATA_MODEL.md` (entities + relationships; ERD)
- [x] `docs/03_API_ENDPOINTS.md` (every endpoint)
- [x] `docs/04_SCREENS.md` (~45 screens by role)
- [x] `docs/05_RBAC_SECURITY.md` (roles, permission matrix, security architecture, STRIDE)
- [x] `docs/06_TECH_STACK.md`
- [x] `docs/07_SETUP.md`
- [x] `docs/08_INCREMENT_PLAN.md` (21 increments, weighted to 100)
- [x] `docs/09_PROGRESS.md` (live % tracker)
- [x] `docs/10_TESTING.md` (strategy + definition of done)
- [x] `docs/templates/INCREMENT_TEMPLATE.md`, `VALIDATION_TEMPLATE.md`
- [x] `schematics/` — 10 design schematics (wireframes for every dashboard, ERD, RBAC matrix, deployment)
- [x] `src/` skeleton (backend, frontends, pulse-pwa, contracts, anomaly-engine, ingestion) + READMEs
- [x] `.gitignore`

## What was built
The complete handover/specification set and design schematics. No application code yet — INC-000 is the
scaffold and plan only.

```
cdf_sigtrace_project/
  START_HERE.md, README.md, .gitignore
  docs/ (11 specs + 2 templates)
  schematics/ (10 PNG + generator)
  increments/INC-000_scaffold.md
  src/ (7 skeleton modules with READMEs)
```

## Acceptance criteria — results
| Criterion | How verified | Result |
|-----------|--------------|:------:|
| A new session can understand and continue the build from this folder | Read-through of START_HERE → PROGRESS → INC-001 | ✅ |
| Every dashboard has a design schematic | `schematics/` rendered (10 PNGs) | ✅ |
| Every endpoint and screen documented | `03_API_ENDPOINTS.md`, `04_SCREENS.md` | ✅ |
| RBAC roles + access security architecture documented | `05_RBAC_SECURITY.md` + `rbac_matrix.png` | ✅ |
| Progress tracking with % and per-increment validation convention exists | `09_PROGRESS.md` + templates | ✅ |

## Tests
- N/A (documentation/scaffold increment). Schematic generator runs clean: `python schematics/generate_schematics.py`.

## Decisions / deviations
- Tech stack fixed per `06_TECH_STACK.md` (FastAPI + Postgres + Fabric + Polygon + IPFS + React).
  Changeable later with a recorded reason.

## Follow-ups / known gaps
- [ ] No runnable code yet — begins at INC-001.
- [ ] `docker-compose` and CI land at INC-001 / INC-020.

## Progress update
- INC-000 = **DONE** in `09_PROGRESS.md`.
- Overall completion: **3%**.
