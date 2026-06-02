# CDF / SigTrace + CDF Pulse

A blockchain-anchored accountability framework for Zambia's Constituency Development Fund and
government procurement. Two prototype systems — **SigTrace Zambia** (procurement contract integrity)
and **CDF Pulse** (field delivery verification) — joined by an **integrated monitor** that flags
ghost projects.

> New here? Open **[START_HERE.md](START_HERE.md)**.

## Status
- Overall completion: **3%** — see [docs/09_PROGRESS.md](docs/09_PROGRESS.md).
- Build proceeds increment by increment — see [docs/08_INCREMENT_PLAN.md](docs/08_INCREMENT_PLAN.md).

## Documentation map
| Doc | Contents |
|-----|----------|
| [00_PROJECT_OVERVIEW](docs/00_PROJECT_OVERVIEW.md) | Purpose, scope, glossary |
| [01_ARCHITECTURE](docs/01_ARCHITECTURE.md) | Components, runtime, data-flow routes |
| [02_DATA_MODEL](docs/02_DATA_MODEL.md) | Entities and relationships |
| [03_API_ENDPOINTS](docs/03_API_ENDPOINTS.md) | Every REST endpoint |
| [04_SCREENS](docs/04_SCREENS.md) | Every screen, by role |
| [05_RBAC_SECURITY](docs/05_RBAC_SECURITY.md) | Roles, permissions, security architecture |
| [06_TECH_STACK](docs/06_TECH_STACK.md) | Stack + justification |
| [07_SETUP](docs/07_SETUP.md) | Local setup |
| [08_INCREMENT_PLAN](docs/08_INCREMENT_PLAN.md) | The build work-list |
| [09_PROGRESS](docs/09_PROGRESS.md) | Live progress & % |
| [10_TESTING](docs/10_TESTING.md) | Testing & definition of done |

## Design schematics
See `schematics/`: public dashboard, verification portal, oversight console, contract/anomaly detail,
ghost-project queue, CDF Pulse mobile app, admin console, ERD, RBAC matrix, deployment architecture.

## Ethics & scope (important)
This is a civic-transparency / anti-corruption prototype. All analytical outputs are **risk signals
requiring review, never determinations of wrongdoing**. Personal data is kept **off-chain**; only
hashes and non-personal metadata are written to any ledger. A two-tier output model keeps the public
tier aggregated and de-identified, with named findings restricted to authorised oversight bodies.

## Licence
TBD (recommend a permissive licence for the academic prototype; confirm with ZCAS).
