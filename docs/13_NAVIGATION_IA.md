# 13 · Navigation & Information Architecture

How the apps are navigated and how the top "ribbon" should be structured. Grounded in how real
public-spending / procurement-transparency portals do it.

## Sources analysed
- **USASpending.gov** (US federal spending — the reference standard): leads with **Search**, then a
  **Spending Explorer** (Budget function / Agency / Object class), **Award Search**, **Download** (custom
  award/account data), **Profiles**, and **About**. The primary action is search/explore; everything else
  is grouped into a few sections.
- **ProZorro** (Ukraine procurement): search tenders → analytics dashboards → about.
- **Open Contracting Partnership / OCDS**: the data standard + "how to use the data".
- **ZPPA** (Zambia, our actual source): e-GP, OCDS reports, supplier registration, bidding guidance.
- **Milenge Town Council** (local CDF): "CDF Corner", "CDF Tracking", e-GP, Complaints, Publications.
- **GOV.UK Design System**: lean, topic-based, plain-language; minimal top-level items, no jargon.

**Pattern that emerges:** one prominent primary action, 3–4 grouped nav sections (Explore / Data /
About), dropdowns to the specific screens, and a content-rich footer for secondary links.

## The problem with the current ribbon
Today: `Home · Map · Verify · Constituencies · Open Data · About` **+ a "Verify a Contract" button**.
- **"Verify" appears twice** (nav link *and* the CTA button) — redundant and confusing.
- Six flat links with no grouping; "Map / Constituencies" are really the same thing ("explore"), and
  "Open Data" sits alone.
- No dropdowns, so there's nowhere to surface Projects, Procurement Risk, API, Methodology, etc.

## Recommended public-portal ribbon
```
[⬢ coat of arms · REP. OF ZAMBIA | LEDGER]   Explore ▾  Data ▾  About ▾    🔒 For officials   [ 🛡 Verify a contract ]
```
- **Home** = the logo (click to return) — no separate "Home" link needed.
- **Verify** lives only as the **primary CTA button** (right) — the one unique, high-value action. Remove
  the redundant "Verify" nav link.
- **For officials** = a quiet text link (lock icon) to the Oversight/Admin login (restricted tier). Kept
  visually subordinate to the citizen-facing "Verify a contract" CTA — present but not competing. Mirrors
  USASpending's restrained "Sign in" / agency-login treatment. Hidden on small screens (lives in the mobile menu).
- Three grouped **dropdowns** that drop to real screens:

| Nav group | Drops down to (screen) |
|-----------|------------------------|
| **Explore ▾** | National Dashboard (P2) · National Map (P3) · Constituencies (P4) · Projects (P5) · Procurement Risk (P7) |
| **Data ▾** | Open Data / Datasets (P8) · Public API · Methodology |
| **About ▾** | How it works (P9) · FAQ · Data Protection (X6) · Contact |
| **Verify a contract** (button) | Verification Portal (P6) |

This mirrors USASpending's "Explore / Download / About + prominent action", in plain language, and every
item maps to a screen we've already designed.

## Footer (public) — secondary links
Privacy Protocol · Open Data Policy · API Documentation · Methodology · Contact · (and the seal).
Footer carries the "long tail" so the ribbon stays lean.

## Mobile (public)
Hamburger → the same three groups as collapsible accordions, with "Verify a contract" pinned at the top
as the primary action.

## Oversight console — left sidebar (unchanged, already designed)
Risk dashboard · Contract risk list · Ghost-project queue · Supplier network · Cases · Verify document ·
Reports · Notifications · Settings. (Admin gets its own sidebar: Users · Weights · Thresholds · Ingestion
· Ledger · Institutions · Audit log · Notifications.) Restricted tier — never mixed with the public nav.

## CDF Pulse — mobile bottom nav (4 items max)
Home (assignments) · Capture (primary, centre) · Submissions (sync queue) · Profile. Confirmers get a
"Confirm" inbox tab. Big touch targets; one primary action per screen.

## Rule of thumb
- Public ribbon: **max 3 dropdown groups + 1 primary action.** Anything else goes in the footer.
- Every nav item must land on a real screen in `04_SCREENS.md`. No dead links.
- Dropdowns are for *navigation to screens*, not for actions (actions are buttons).
