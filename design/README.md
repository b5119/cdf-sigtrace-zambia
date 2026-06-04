# CDF / SigTrace — Frontend Design Handover

This folder is the **visual + interaction spec** for the build. It's a fully clickable, self-contained
HTML prototype of every screen, plus the design system and an automated routing audit. The next build
increment (**INC-008 — Public CDF dashboard + map**) implements the public screens here in React.

**Design phase status: COMPLETE and audited** (baseline date 2026-06-03).

---

## Start here
1. Open **`screens/index.html`** in a browser — the **Screen Map**: every screen as a clickable node, grouped
   by app, with the primary user flows drawn as arrows. This is the map of the whole product.
2. Open **`screens/landing_enhanced.html`** — the locked public landing (P1).
3. Read **`../docs/14_SCREEN_FLOWS.md`** — sitemap, all user journeys, the two front doors, and the audit
   results. (Companion docs: `11_FRONTEND_DESIGN.md` = design system; `13_NAVIGATION_IA.md` = navigation IA.)

## What's in here
| Path | What it is |
|------|------------|
| `screens/index.html` | The flow map / screen index (visual sitemap) |
| `screens/landing_enhanced.html` | **P1** public landing — locked, hand-built (morphing Zambia map, bento, seal) |
| `screens/*.html` | 41 generated screens (P2, P7–P10, O1–O13, S1–S9, M1–M8, X1–X6) |
| `stitch_export/*/code.html` | 5 hi-fi Stitch screens: **P3** national map, **P4** constituency, **P5** project, **P6** verify portal (+ legacy landing) |
| `screens/generate.py` | The generator: **route table `R`**, shared components (nav, sidebar, cards, charts, `zambia_map()`), and every generated screen. Edit here, then `python generate.py`. |
| `audit.py` | Re-runnable routing/semantic/tier/date test harness. `cd design && python audit.py` |
| `assets/coat_of_arms.png` | Real Zambian coat of arms (used everywhere a seal appears) |
| `assets/zambia_path.txt` | Real Zambia outline SVG path (60-vertex, from GeoJSON) — used by all maps |

## How to regenerate / verify
```bash
cd design/screens && python generate.py    # rebuilds all 41 generated screens + index.html
cd design && python audit.py               # runs the full audit (must be all-green)
```
The Stitch screens (`stitch_export/`) are hand-finished HTML, not generated — edit them directly.

---

## Design system (authoritative tokens — see `docs/11_FRONTEND_DESIGN.md`)
- **Colour:** Integrity Green `#0E5C46`, Eagle Copper `#B8762A`, Ink `#0B1F1A`, surface `#F6F8F6`,
  surface-2 `#EEF3EF`. Risk scale: low `#138636` / mid `#B45309` / high `#B91C1C`.
- **Type:** Space Grotesk (display), Inter (body), JetBrains Mono (hashes/IDs/amounts).
- **Radius:** 12px components, circular Verification Seal. Flat, 1px borders, no heavy shadows.
- **Voice:** "court-of-record / digital monument", zero decoration. Outputs are *risk signals requiring
  review*, never determinations.
- The Tailwind config that encodes these tokens is inline at the top of `generate.py` (`TW_CONFIG`) and in
  each Stitch file — copy it into the React app's `tailwind.config.js`.

## Architecture the design assumes (see `docs/11_FRONTEND_DESIGN.md`)
- **Three separate apps / domains, never blended:**
  - **Public portal** (P*) — anonymous, `portal.*`. React + Vite + Tailwind (Next.js also fine).
  - **Oversight + Admin console** (O*, S*) — restricted, `console.*`. React + Vite SPA.
  - **CDF Pulse** (M*) — field PWA, `pulse.*`. PWA now → Expo React Native later.
- **Two front doors only:** public landing **P1** (citizens) and officials portal **O1** (OAG/ACC/ZPPA,
  MFA). They cross only at "🔒 For officials" → O1 and "← Back to public portal" → P1. **Pulse** has its own
  **web login M1** (the PWA install/login page), linked from the public footer and the officials portal.
- **State/data:** TanStack Query against the FastAPI backend. Mirror the prototype's **route table `R`**
  (in `generate.py`) as your React Router path constants — every nav link already resolves through it.

## Screen → increment map (which screens each INC builds)
| INC | Screens |
|-----|---------|
| **INC-008 Public dashboard + map** | **P1, P2, P3, P4, P7, P8, P9** (+ P10 public ledger) |
| INC-009 Oversight (risk) | O2, O3, O4, O5, O11, O12, O13, O1 |
| INC-010 Pulse capture + offline | M1–M6, M8 |
| INC-013 Confirmation | M7, O8 |
| INC-014 Public project (evidence) | P5 |
| INC-015 Monitor + ghost queue | O6, O7 |
| INC-016 Cases & notifications | O10, O13 |
| INC-017 Admin | S1–S9 |
| INC-019 Hardening | X5, X6 |

---

## For INC-008 specifically (the next build)
**Goal (from `docs/08_INCREMENT_PLAN.md`):** Public CDF dashboard + map render **real aggregates**; **no named
data anywhere in the public app**. Endpoints: `/public/*` (already built — `/public/overview`, `/public/map`,
`/public/constituencies/{id}`, `/public/projects/{id}`, `/public/risk/aggregate`, `/public/opendata/{dataset}`).

Build these screens to match the prototype:
- **P1 Landing** → `landing_enhanced.html` (locked). KPIs, live-ledger bento, verify CTA. `/public/overview`.
- **P2 National Dashboard** → `P2_dashboard.html`. 4 KPI cards + **constituency risk heat-map** + recently
  verified feed. `/public/overview`, `/public/map`.
- **P3 National Map** → `stitch_export/national_project_map/code.html`. Choropleth of constituencies.
  `/public/map` → click marker → P4.
- **P4 Constituency** → `stitch_export/constituency_detail/code.html`. Allocation, project list, locator
  map. `/public/constituencies/{id}`.
- **P7 Procurement Risk** → `P7_procurement_risk.html`. **De-identified** bars only. `/public/risk/aggregate`.
- **P8 Open Data**, **P9 About/Methodology**, **P10 Public Audit Trail** (live ledger feed).

**The map / choropleth:** the prototype already renders the **real Zambia outline** (`assets/zambia_path.txt`)
with risk-coloured, point-in-polygon-verified markers — see `zambia_map()` in `generate.py` for the exact
SVG + marker logic and `CITIES` for sample coordinates. For the React build use **MapLibre GL + the
constituency GeoJSON** for a true choropleth (the SVG version is the design reference). Risk colours and the
legend (Low/Med/High) are defined in `zambia_map()`.

**Two-tier rule:** public screens must show **aggregates only, no supplier/entity names** (P7 entities are
"Entity A…E"). The audit enforces public↔officials isolation; keep it.

---

## Verification (re-run anytime with `python audit.py`)
All green at handover: 0 broken links · 0 dead `#` links · 0 semantic mismatches · 0 unreachable · 0
orphans/dead-ends · 0 tier leaks · 0 can't-go-back · 0 title mismatches · 0 external image URLs · only
non-2026 year is the "Procurement Act No. 8 of 2020" citation.

## Open (non-blocking) decisions
- The Stitch ribbons keep their original labels (Registry / Audit Trail / Allocations) which route correctly
  but aren't yet unified with the public IA (Explore / Data / About). Optional cleanup, not required for the build.
