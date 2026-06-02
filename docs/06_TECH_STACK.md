# 06 · Technology Stack

These are **decisions of record** for the prototype. Change them only with a note in the increment
record explaining why. Versions are indicative; pin exact versions in each `src/*` package manifest.

## Backend
| Concern | Choice | Why |
|---------|--------|-----|
| Language | **Python 3.12** | Same language as the anomaly engine and ingestion; rich data libraries |
| API framework | **FastAPI** | Async, typed, auto OpenAPI docs, fast to build |
| ORM | **SQLAlchemy 2.x** + **Alembic** | Mature ORM + migrations |
| Validation | **Pydantic v2** | Request/response schemas, settings |
| Auth | **JWT** (access+refresh) via `python-jose`; **TOTP MFA** via `pyotp` | Stateless, MFA for restricted tier |
| Task queue | **Celery** + **Redis** | Ingestion runs, anchoring, monitor jobs |
| Tests | **pytest** + **httpx** | Unit + API tests |

## Data
| Concern | Choice | Why |
|---------|--------|-----|
| Primary DB | **PostgreSQL 16** | Relational domain data, JSONB for OCDS payloads |
| Cache / queue broker | **Redis 7** | Celery broker + caching + offline-sync de-dup |
| Object storage | **S3-compatible (MinIO in dev)** | Contract PDFs (off-chain) |
| Graph (optional) | computed in Python (NetworkX) | Supplier-network check |

## Ledgers & crypto
| Concern | Choice | Why |
|---------|--------|-----|
| Permissioned ledger | **Hyperledger Fabric 2.5** | Controlled institutional membership for contract anchoring |
| Public ledger | **Polygon PoS (Amoy testnet in dev)** | Low-cost, public, citizen-verifiable confirmations |
| Smart contracts | **Solidity 0.8.x** + **Hardhat** | Polygon multi-sig confirmation contract |
| Off-chain media | **IPFS** (Kubo node / web3.storage in dev) | Content-addressed, tamper-evident evidence |
| Hashing | **SHA-256** (hashlib) | Standard, collision-resistant anchoring primitive |

## Frontend
| App | Choice | Why |
|-----|--------|-----|
| Public portal | **React 18 + Vite + TypeScript** | Fast, typed SPA |
| Oversight console | **React 18 + Vite + TS** + table/chart libs | Data-dense admin UI |
| CDF Pulse PWA | **React 18 + Vite + TS + service worker (Workbox)** | Offline-first, installable |
| Maps | **MapLibre GL** + Zambia GeoJSON | Constituency choropleth + project map |
| UI kit | **Tailwind CSS** + headless components | Consistent, accessible, quick |
| State/data | **TanStack Query** | Server-state caching, offline mutations queue (Pulse) |

## Platform / ops
| Concern | Choice |
|---------|--------|
| Containers | **Docker** + **docker-compose** (dev) |
| CI | **GitHub Actions** (lint, test, build) |
| Config | `.env` per service + Pydantic settings; secrets via env/vault (never committed) |
| Observability | structured logging (JSON), health endpoints, request IDs |

## Repository layout (monorepo)
```
src/backend/          FastAPI app: api/, services/, models/, schemas/, core/(auth,rbac,config)
src/ingestion/        OCDS fetch → normalise → load
src/anomaly-engine/   the 8 checks + risk scoring (importable library + CLI)
src/contracts/        Solidity + Hardhat (Polygon confirmation contract)
src/frontend-public/  React app
src/frontend-oversight/ React app
src/pulse-pwa/        React PWA
```

## Why this mix (one line)
Permissioned chain for sensitive institutional contract data; public chain for citizen-facing
confirmations; IPFS for large media off-chain; transparent Python checks so every flag is auditable.
