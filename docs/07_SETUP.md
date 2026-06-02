# 07 · Local Setup

> The repo is a skeleton at INC-000. INC-001 and INC-020 flesh out the runnable stack and
> `docker-compose`. This file is the intended setup; update it as components land.

## Prerequisites
- Docker + docker-compose
- Python 3.12, Node 20+, pnpm (or npm)
- (For ledger work) a local Hyperledger Fabric test network; a Polygon Amoy testnet key; an IPFS node
  (Kubo) or a web3.storage token.

## Intended dev workflow
```bash
# 1. infra (Postgres, Redis, MinIO, IPFS) — added in INC-001/011
docker compose up -d db redis minio ipfs

# 2. backend
cd src/backend
python -m venv .venv && . .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload         # http://localhost:8000/docs

# 3. anomaly engine / ingestion (run as CLI or via backend tasks)
cd ../ingestion && python -m ingestion.run --sample
cd ../anomaly-engine && python -m engine.cli --ocid <ocid>

# 4. frontends
cd ../frontend-public && pnpm i && pnpm dev        # http://localhost:5173
cd ../frontend-oversight && pnpm i && pnpm dev     # http://localhost:5174
cd ../pulse-pwa && pnpm i && pnpm dev              # http://localhost:5175

# 5. smart contracts
cd ../contracts && pnpm i && npx hardhat test
```

## Environment
Each service has its own `.env` (never commit). Minimum keys:
- backend: `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `OBJECT_STORE_*`, `FABRIC_*`, `POLYGON_RPC`,
  `POLYGON_SIGNER_KEY`, `IPFS_API`.
- frontends: `VITE_API_BASE_URL`, map tile/style URL.

## First task for the next session
Open `docs/09_PROGRESS.md` → start **INC-001**. Stand up the backend app, the user/role model, JWT+MFA
auth, the RBAC permission decorator, and the two-tier scoping middleware, then write the RBAC
table-driven test from `10_TESTING.md`.
