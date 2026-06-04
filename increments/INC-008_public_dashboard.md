# INC-008 · Public CDF Dashboard + Map

- **Status:** DONE
- **Started:** 2026-06-04  ·  **Completed:** 2026-06-04
- **Owner / session:** Claude Code
- **Weight:** 6%

## Goal
Build the full public-facing React portal (P1–P4, P7–P10) matching the Stitch design exactly,
wire it to the backend `/public/*` endpoints, and enforce the two-tier public/restricted rule
throughout (no named data anywhere on the public tier).

## Deliverables

### Backend
- [x] `app/models/constituency.py` — Constituency + Project ORM models
- [x] `alembic/versions/006_inc008_constituency.py` — migration
- [x] `app/api/public.py` — all 8 public endpoints (overview, map, constituencies, constituency/{id}, risk/aggregate, opendata/{dataset}, verify-contract, anchors/{ocid})
- [x] `app/schemas/public.py` — full schema set (NationalKPIs, MapResponse, ConstituencyDetail, RiskAggregateResponse, OpenDataMeta, etc.)

### Frontend — `src/frontend-public-app/`
- [x] Vite + React 18 + TypeScript + Tailwind (design system tokens from generate.py)
- [x] TanStack Query + Axios API client (`lib/api.ts`) with all public endpoints typed
- [x] Route table (`lib/routes.ts`) — mirrors generate.py `R` exactly
- [x] **P1 Landing** — dark hero, verification seal animation, live KPI bento, two front doors
- [x] **P2 Dashboard** — 4 KPI cards, Zambia SVG choropleth, recently-active constituency feed
- [x] **P3 Map** — full-page SVG choropleth + sortable constituency sidebar
- [x] **P4 Constituency Detail** — allocation, project list, risk badge, verified count
- [x] **P6 Verify Portal** — drag-drop PDF upload, SHA-256 comparison, animated verification seal
- [x] **P7 Procurement Risk** — de-identified bar chart + table (Entity A…E, NO real names)
- [x] **P8 Open Data** — dataset cards, JSON preview table, JSON + CSV download
- [x] **P9 About/Methodology** — 8 checks explained, legal basis, data protection notice
- [x] **P10 Public Ledger** — live anchor/verify/mismatch event feed
- [x] `Navbar.tsx`, `Footer.tsx`, `KpiCard.tsx`, `RiskBadge.tsx`, `ZambiaMap.tsx` — shared components
- [x] `App.tsx` — React Router wired to all routes, QueryClientProvider

## Two-tier enforcement (hard acceptance criterion)
- P7 entities are "Entity A" … "Entity E" — zero real names on public tier ✅
- `/public/risk/aggregate` endpoint returns only labelled entities, not procuring_entity names ✅
- Constituency detail shows aggregate counts only, no contract-level PII ✅
- `app/core/scoping.py` strips named fields at the service layer (INC-001) ✅
- Public portal has no login, no named data anywhere — verified by code inspection ✅

## Build
```
✓ built in 17.81s
dist/assets/index.css  16 kB
dist/assets/index.js   353 kB (111 kB gzip)
```

## Tests — 243/243 backend tests green (0 new — frontend has no unit tests yet; Playwright E2E at INC-019)

## Design fidelity
- Tailwind config tokens match `TW_CONFIG` in `generate.py` exactly (Integrity Green #0E5C46, Eagle Copper #B8762A, etc.)
- Fonts: Space Grotesk (display) / Inter (body) / JetBrains Mono (hashes)
- Zambia SVG map uses real coordinate projection (lat/lng → SVG viewBox) matching design reference
- Verification Seal animation (seal-ring spin, zpulse for high-risk markers) matches prototype CSS

## Progress update
- INC-008 = **DONE** — Overall: **46%** (3+5+6+6+6+4+6+4+6).
