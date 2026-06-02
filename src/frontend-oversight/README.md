# frontend-oversight — Oversight + Admin console (React + Vite + TS)

Restricted tier (JWT + MFA). Screens O1–O13 (oversight) and S1–S9 (admin) — see
`../../docs/04_SCREENS.md`. Institution-scoped, named data. Built mainly in **INC-009** (risk list,
contract/anomaly detail, supplier network), **INC-015** (ghost-project queue), **INC-016** (cases),
**INC-017** (admin: users, weights, thresholds, ingestion, ledger, health), **INC-018** (audit viewer).

Key pieces: data-dense tables with risk colouring, contract detail showing all 8 checks + evidence +
anchor status, supplier-network graph, ghost-project queue, case management, admin config with the
check-weight sliders. Tailwind UI, TanStack Query, charting + graph libs.
