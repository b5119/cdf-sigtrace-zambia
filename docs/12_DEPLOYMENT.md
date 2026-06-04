# 12 · Deployment & Runbook

> How to run CDF Integrity locally and host it **completely free**. The whole stack runs on
> SQLite + mock ledgers with **zero external services**, so it works on any laptop and on any
> free hosting tier.

---

## 0. The key idea — it runs with no dependencies

The backend defaults to **SQLite** and **mock mode** for all three ledgers
(`FABRIC_MOCK_MODE`, `POLYGON_MOCK_MODE`, `IPFS_MOCK_MODE` = true). The mocks compute *real-format*
hashes/CIDs/tx, so the system behaves identically to production — there's just no Postgres, Redis,
Hyperledger Fabric, Polygon node, or IPFS daemon to install. Rate-limiting and caching degrade
gracefully without Redis; Celery isn't needed (the demo endpoints run synchronously).

This makes the entire platform **free to run and host**.

---

## 1. Run locally (one command)

```bash
./run-local.sh
```
This seeds a SQLite demo DB, starts the backend on `:8000`, and the public portal on `:5173`.

**Demo logins:**
| Email | Password | Role |
|-------|----------|------|
| `admin@cdf.zm` | `AdminPass123!` | system_admin |
| `officer@oag.gov.zm` | `Officer123!` | oversight_officer |
| `monitor@cdf.zm` | `Monitor123!` | community_monitor |

Run the other two apps in separate terminals:
```bash
cd src/frontend-oversight-app && VITE_API_BASE_URL=http://localhost:8000/api/v1 npx vite --port 5174
cd src/pulse-pwa-app          && VITE_API_BASE_URL=http://localhost:8000/api/v1 npx vite --port 5175
```

### Or with Docker
```bash
docker compose up        # backend :8000, public :5173, oversight :5174, pulse :5175
```

---

## 2. Host it completely free

Three pieces: **frontends** (static), **backend** (one small web service), **database** (optional).

### Recommended free stack

| Piece | Free host | Notes |
|-------|-----------|-------|
| 3 frontends | **Cloudflare Pages** or **Vercel** or **Netlify** | Static SPAs — free forever, global CDN |
| Backend | **Render** (free web service) or **Fly.io** | `render.yaml` blueprint included |
| Database | **SQLite** (on the box) or **Neon** / **Supabase** free Postgres | SQLite is simplest; Neon adds persistence |
| Redis | *not needed* (graceful degradation) — or **Upstash** free | only for production rate-limit/cache |
| Ledgers | **mock mode** (free) — or **Polygon Amoy** testnet (free test MATIC) | mocks are production-faithful |

### A. One-click backend on Render (free)
1. Push to GitHub (done).
2. On Render → **New → Blueprint** → point at the repo. It reads `render.yaml` and provisions the
   backend (free web service) + the public & oversight static sites.
3. `JWT_SECRET` is auto-generated. Done.
> Render's free web service sleeps after 15 min idle and cold-starts in ~30 s — fine for a pilot/demo.

### B. Frontends on Cloudflare Pages / Vercel (free)
For each app (`frontend-public-app`, `frontend-oversight-app`, `pulse-pwa-app`):
- **Build command:** `npm run build` · **Output dir:** `dist`
- **Env var:** `VITE_API_BASE_URL = https://<your-backend>.onrender.com/api/v1`
- SPA routing: `vercel.json` (included) or Cloudflare Pages "single-page app" mode.

### C. Backend on Fly.io (free allowance, doesn't sleep)
```bash
cd src/backend
fly launch --dockerfile Dockerfile   # accept defaults; pick a free region
fly deploy
```

### Persistence note
On free tiers with ephemeral disk, SQLite resets on redeploy. For a stable pilot use **Neon** (free
Postgres that doesn't expire): set `DATABASE_URL=postgresql+asyncpg://...` and
`DATABASE_SYNC_URL=postgresql://...`, then run Alembic migrations (`alembic upgrade head`).

---

## 3. Going to real ledgers (still mostly free)

| Layer | Free path |
|-------|-----------|
| **Polygon** | Deploy `CDFConfirmation.sol` to **Amoy testnet** — free test MATIC from a faucet. `cd src/contracts && npx hardhat run scripts/deploy.js --network amoy`. Set `POLYGON_MOCK_MODE=false`, `POLYGON_CONTRACT_ADDRESS=…`. |
| **IPFS** | A free **web3.storage** token, or run a **Kubo** node (compose service included). Set `IPFS_MOCK_MODE=false`. |
| **Fabric** | Heaviest — needs a permissioned network with institutional MSPs (OAG/ACC/ZPPA). For a pilot, a single-org Fabric test network; keep `FABRIC_MOCK_MODE=true` until then. |

---

## 4. CI/CD

`.github/workflows/ci.yml` runs **free on GitHub** for every push/PR:
- **backend** — `pytest` (390 tests)
- **contracts** — `hardhat test` (14 Solidity tests)
- **frontends** — `npm run build` for all three apps (matrix)

---

## 5. Production hardening checklist (when leaving free tier)
- Set a strong `JWT_SECRET`; set `MFA_ENFORCE=true`; restrict `CORS_ORIGINS` to real domains.
- Real Postgres + `alembic upgrade head`; Redis for rate-limit/cache; Celery worker for async jobs.
- TLS at the edge (Render/Fly/Cloudflare provide it free); the app already sends HSTS/CSP/X-Frame headers.
- Swap ledgers off mock as above; run a real IPFS pinning service.
- Add `gitleaks`, `pip-audit`, `npm audit` to CI; run axe/Lighthouse against the deployed public app.
