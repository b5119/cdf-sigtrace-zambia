# INC-009 · Oversight Console (Risk)

- **Status:** DONE
- **Started:** 2026-06-04  ·  **Completed:** 2026-06-04
- **Owner / session:** Claude Code
- **Weight:** 8%

## Goal
Build the restricted oversight console (React SPA) — the officer-facing app where OAG/ACC/ZPPA
staff log in with MFA, review named contract risk data, open the 8-check anomaly detail, and act.
Screens: O1 (login), O2 (dashboard), O3 (contract list), O4 (contract detail), O5 (supplier network),
O11 (analytics), O12 (reports), O13 (notifications) + audit log + admin stub.

## Deliverables

### Frontend — `src/frontend-oversight-app/`
- [x] Vite + React 18 + TypeScript + Tailwind (design tokens from Stitch handover)
- [x] TanStack Query + Axios API client with JWT interceptor (`lib/api.ts`)
- [x] Zustand auth store with persisted tokens (`store/auth.ts`)
- [x] Route table (`lib/routes.ts`)
- [x] **O1 Login** — email/password → MFA challenge flow
- [x] **MFA Challenge** — 6-digit TOTP entry → access + refresh tokens
- [x] **O2 Risk Dashboard** — KPI cards (total, high-risk, scored, cases), recent high-risk contract table
- [x] **O3 Contract Risk List** — sortable/filterable table (risk score colour), pagination, min-score filter
- [x] **O4 Contract Detail** — 8-check breakdown with evidence, risk gauge, ledger seal, action buttons
- [x] **O5 Supplier Network** — related-party SVG graph (shared attributes flagged copper)
- [x] **O11 Analytics** — risk distribution bars, summary stats
- [x] **O12 Reports** — report generation cards (PDF/CSV)
- [x] **O13 Notifications** — alert feed
- [x] **Audit Log** — append-only privileged action record
- [x] **Admin** — component health + recent ingestion runs (full console at INC-017)
- [x] `Sidebar.tsx` (nav + sign-out), `ConsoleLayout.tsx` (auth guard), `RiskScore.tsx`, `CheckRow.tsx`

### Auth flow (wired to INC-001 backend)
1. `POST /auth/login` → MFA challenge token (or direct tokens if MFA off)
2. `POST /auth/mfa/verify` → access + refresh tokens stored in Zustand + localStorage
3. JWT auto-attached to all requests via Axios interceptor
4. `ConsoleLayout` redirects to /login when no token present
5. Sign-out calls `POST /auth/logout` (revokes refresh jti) and clears store

### Backend
No new endpoints — the console consumes existing INC-005 restricted endpoints:
- `GET /contracts` (named, scored, filterable)
- `GET /contracts/{ocid}` (full record)
- `GET /contracts/{ocid}/checks` (8 check results + evidence)
- `GET /contracts/{ocid}/risk` (score + breakdown)
- `GET /ingestion/runs` (admin)
All require `read_named` / `system_admin` permission — RBAC enforced server-side (tested in INC-005).

## Two-tier separation
- Oversight console is a **separate app** (`console.*` domain) from the public portal (`portal.*`).
- It shows **named** contract data (procuring entity, supplier name) — only accessible with a valid
  officer JWT carrying `read_named` permission.
- Public portal (INC-008) has zero auth and zero named data; the two never blend.

## Build
```
✓ built in 993ms
dist/assets/index.css   12.9 kB
dist/assets/index.js    344 kB (108 kB gzip)
```

## Tests — 261/261 backend tests green (0 new — console consumes tested INC-005 endpoints; Playwright E2E at INC-019)

## Design fidelity
- Sidebar matches O2_dashboard.html nav exactly (Risk Dashboard, Contract List, Supplier Network, etc.)
- Risk score chips colour-coded (high red / mid amber / low green) matching design tokens
- 8-check list mirrors O4_contract_detail.html (FLAG/OK/SKIP styling)
- Ledger seal with coat-of-arms motif on contract detail
- Integrity Green / Eagle Copper / dark sidebar throughout

## Follow-ups
- O6 Ghost Queue + O7 Mismatch Explorer → INC-015 (integrated monitor)
- O8 Verification Review → INC-013 (confirmation workflow)
- O10 Cases → INC-016
- Full admin console (S1–S9) → INC-017
- Reports actually generate files → INC-012/016
- Playwright E2E for the login → dashboard → contract detail journey → INC-019

## Progress update
- INC-009 = **DONE** — Overall: **54%** (3+5+6+6+6+4+6+4+6+8).
