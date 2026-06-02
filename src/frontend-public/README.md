# frontend-public — Transparency portal (React + Vite + TS)

Public, unauthenticated. Screens P1–P9 (see `../../docs/04_SCREENS.md`). Consumes only `/public/*`
endpoints — receives **no named/PII data** by design. Built in **INC-007** (verify portal) and
**INC-008** (dashboard, map, constituency/project, risk, open data); P5 evidence at **INC-014**.

Key pieces: national dashboard + KPI cards, MapLibre constituency choropleth, contract verification
portal (client computes SHA-256, server confirms vs anchor), open-data downloads. Tailwind UI,
TanStack Query, WCAG 2.1 AA.
