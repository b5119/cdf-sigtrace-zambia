# 14 · Screen Map & User Flows

How every screen connects. This is the navigation graph behind the clickable prototype in
`design/screens/`. The interactive version is **`design/screens/index.html`** (the "Screen Map" — open
it and click any node). Every node below maps to a real route in the generator's route table `R`.

> Legend: **PUB** public portal · **OVS** oversight console · **ADM** admin (within OVS) ·
> **PWA** CDF Pulse field app · **X** shared/auth. `→` = primary path, `⇄` = drill-in/return.

---

## 1. Sitemap (every screen + its file)

### Public portal (PUB) — top nav: Explore ▾ · Data ▾ · About ▾ · [Verify a contract] · 🔒 For officials
| ID | Screen | File |
|----|--------|------|
| P1 | Landing (locked) | `landing_enhanced.html` |
| P2 | National Dashboard | `P2_dashboard.html` |
| P3 | National Map | `../stitch_export/national_project_map/code.html` |
| P4 | Constituency Detail | `../stitch_export/constituency_detail/code.html` |
| P5 | Project Detail | `../stitch_export/project_transparency_detail/code.html` |
| P6 | Verification Portal | `../stitch_export/verification_portal/code.html` |
| P7 | Procurement Risk | `P7_procurement_risk.html` |
| P8 | Open Data / API | `P8_open_data.html` |
| P9 | About / Methodology / FAQ | `P9_about.html` |
| P10 | Public Audit Trail / Live Ledger | `P10_audit_trail.html` |

### Oversight console (OVS) — left sidebar
| ID | Screen | File |
|----|--------|------|
| O1 | Login (MFA) | `O1_login.html` |
| O2 | Risk Dashboard (home) | `O2_dashboard.html` |
| O3 | Contract Risk List | `O3_contract_list.html` |
| O4 | Contract Detail / Anomaly Review | `O4_contract_detail.html` |
| O5 | Supplier Network | `O5_supplier_network.html` |
| O6 | Ghost-Project Queue | `O6_ghost_queue.html` |
| O7 | Disbursement / Mismatch Explorer | `O7_mismatch.html` |
| O8 | Verification Review (confirm field evidence) | `O8_verify_review.html` |
| O9 | Document Verification Console | `O9_doc_verify.html` |
| O10 | Cases | `O10_cases.html` |
| O11 | Analytics | `O11_analytics.html` |
| O12 | Reports & Exports | `O12_reports.html` |
| O13 | Notifications | `O13_notifications.html` |

### Admin console (ADM) — left sidebar (own brand)
| ID | Screen | File |
|----|--------|------|
| S1 | Admin Home | `S1_admin_home.html` |
| S2 | Users & Roles | `S2_users.html` |
| S3 | Check Weights | `S3_weights.html` |
| S4 | Thresholds | `S4_thresholds.html` |
| S5 | Ingestion | `S5_ingestion.html` |
| S6 | Ledger & Nodes | `S6_ledger.html` |
| S7 | Institutions | `S7_institutions.html` |
| S8 | Audit Log | `S8_audit.html` |
| S9 | Notification Config | `S9_notif_config.html` |

### CDF Pulse (PWA) — bottom nav: Home · Capture · Submissions · Confirm · Profile
| ID | Screen | File |
|----|--------|------|
| M1 | Login / device registration | `M1_login.html` |
| M2 | Home / assignments | `M2_home.html` |
| M3 | Capture submission | `M3_capture.html` |
| M4 | Review & submit | `M4_review.html` |
| M5 | My submissions / sync queue | `M5_sync.html` |
| M6 | Submission detail | `M6_detail.html` |
| M7 | Confirmation inbox *(confirmer)* | `M7_confirm.html` |
| M8 | Profile / settings | `M8_profile.html` |

### Shared (X)
| ID | Screen | File |
|----|--------|------|
| X1 | Generic login | `X1_login.html` |
| X2 | MFA | `X2_mfa.html` |
| X3 | Reset password | `X3_reset.html` |
| X4 | Account & sessions | `X4_account.html` |
| X5 | Status states (403/404/error/offline) | `X5_errors.html` |
| X6 | Data-protection notice | `X6_consent.html` |

---

## 1a. Two front doors (public vs officials — separate, tailored)
The system has **two distinct entry surfaces on two surfaces/domains**, never blended:

| | Public surface | Officials surface |
|--|----------------|-------------------|
| **Front door** | **P1 Landing** (`landing_enhanced.html`) — citizen-tailored: hero, live ledger, verify CTA | **O1 Officials Portal** (`O1_login.html`) — institution-tailored: "restricted · authorised institutions only" (OAG / ACC / ZPPA), MFA, audit-logged |
| **Audience** | Anonymous citizens, press, watchdogs | OAG / ACC / ZPPA officers, analysts, admins |
| **Home hub** | P1 / P2 dashboard | O2 Risk Dashboard |
| **Bridge in** | "🔒 For officials" → O1 | — |
| **Bridge back** | — | O1 / X1 "← Back to public portal" → P1 |

These are the **only** two crossing points. The audit confirms **0 public→officials leaks** (other than the
intended For-officials → O1) and **0 officials→public leaks** (other than the explicit back link). In the
build these become two separate deployments/domains (see `11_FRONTEND_DESIGN.md` app segregation):
`portal.*` (public) and `console.*` (officials).

## 2. How the apps connect to each other
- The **public portal** is the only public surface. Its single bridge to the restricted tier is the
  quiet **🔒 For officials** link → **O1 login**. Citizens never see oversight chrome.
- **O1 login** → **O2 dashboard** is the gate into the oversight console. "← Back to public portal"
  returns to P1.
- **Admin (S*)** is reached from inside oversight via the sidebar's **Admin** item (O2 → S1). Same auth
  tier, separate brand.
- **CDF Pulse (M*)** is a separate installable app. Field evidence it captures (M3→M5) surfaces to
  oversight at **O8 Verification Review** and on the public **P5 Project Detail** (evidence section).
- The **Screen Map** (`index.html`) is the developer/review entry to all of the above.

---

## 3. Key user flows (the journeys we wired)

### A. Public — verify a contract  *(the headline flow)*
```
P1 Landing ──[Verify a contract]──► P6 Verification Portal
   │                                    │ drop PDF → local SHA-256 → match/mismatch
   │                                    ▼
   │                                 Verification Seal (verified ⇄ not verified)
   └──[Explore the map]──► P3 National Map ─► P4 Constituency ─► P5 Project Detail (evidence)
```
Entry: landing CTA, nav "Verify a contract", or P9 "Verify a contract now". No login required.

### B. Public — explore the spending
```
P1 ─► P2 National Dashboard ─► P3 Map ─► P4 Constituency ─► P5 Project
                 └─ KPI cards drill: allocation→P4, verified→P5, flagged→P7 Procurement Risk
P7 ─► P9 Methodology   ·   P8 Open Data ─► P8 API docs
```

### C. Oversight — risk flag → case  *(core analyst loop)*
```
O1 Login ─► O2 Risk Dashboard
              │ KPI "high-risk"  ─► O3 Contract Risk List ─► O4 Contract Detail
              │ alert feed       ─► O4 / O6 / O8 / O10
              ▼
            O4 Contract Detail ──[Add to case / Escalate]──► O10 Cases
              ├─[View supplier network]─► O5 ⇄ O4
              └─[Open document verify]─► O9
```

### D. Oversight — ghost-project pursuit
```
O2 ─► O6 Ghost-Project Queue ──[Open case]──► O10 Cases
         └─ O7 Disbursement Explorer (contract ⇄ O4, completion ⇄ O6) — mismatch → case
```

### E. Oversight — confirm field evidence  *(meets Pulse)*
```
PWA: M3 Capture ─► M5 Sync ─► (server)
                                  ▼
OVS: O2 ─► O8 Verification Review ──[Confirm/Reject]──► (verifies M-submission)
            └─ O9 Document Verification (anchor check) ⇄ O4
```

### F. CDF Pulse — capture → sync → confirm  *(field loop)*
> **M1 is the web login for the Pulse PWA** (responsive web page, "install the app" QR), reachable from the
> public footer ("CDF Pulse (field app)") and the officials portal ("Institutional confirmer?"). The
> in-app screens (M2–M8) render in the phone frame. So Pulse now has a real web interface entry.
```
M1 Web login ─► M2 Home/assignments ──[+ New capture]──► M3 Capture (GPS+timestamp, offline)
   ─► M4 Review ─► M5 Sync queue ─► M6 Submission detail
Bottom nav everywhere: Home(M2) · Capture(M3) · Submissions(M5) · Confirm(M7) · Profile(M8)
Confirmer path: M7 Confirmation inbox ──[Confirm/Reject]──► (mirrors O8)
```

### G. Admin — configuration & governance
```
O2 ─[sidebar: Admin]─► S1 Admin Home
       ├─ S2 Users · S3 Weights · S4 Thresholds
       ├─ S5 Ingestion · S6 Ledger & Nodes · S7 Institutions
       └─ S8 Audit Log · S9 Notification Config
```

### H. Auth / edge (shared)
```
X1 ─► X2 MFA ─► O2   ·   X1 ─► X3 Reset ─► X1   ·   X6 Data notice ─► P1
X5 Status states (403 → back, 404 → home, error → retry, offline → dismiss) → P1
```

---

## 3a. Stitch hi-fi screens — coat of arms & ribbon
The five Stitch-designed screens (P3, P4, P5, P6, and the legacy landing) shipped with **Google-hosted
placeholder seals** and **`href="#"` ribbon links**. Both are fixed:
- **Coat of arms:** every placeholder seal now uses the real `assets/coat_of_arms.png` (filters stripped
  so it shows in full colour). 0 placeholders remain.
- **Ribbon:** each label is wired to a real page —
  `Home→P1 · Map→P3 · Constituencies→P4 · Verify (a Contract)→P6 · Open Data / Public Reports→P8 ·
  Registry / Allocations→P2 · Audit Trail→P10 · About→P9`, and `Portal Login→O1`.
- The new **P10 Public Audit Trail** was created to back the "Audit Trail" label and the landing's
  "Live Ledger" bento (which now points to P10, the public ledger — *not* the oversight dashboard).

**Maps & visuals (real, not placeholders):** the national map (P3), the P2/O2 risk heat-maps, and the
P4/P5 locator maps all render the **real Zambia outline** (from `assets/zambia_path.txt`) with risk-coloured,
point-in-polygon-verified markers. The procurement-risk (P7), analytics (O11) and supplier-network (O5)
placeholders are now real bar/line charts and a node graph. All external Stitch images were replaced with
local assets / on-brand placeholders, so the prototype is fully self-contained (0 external image URLs).

> Note: the Stitch ribbons keep their original labels (Registry / Audit Trail / Allocations …), which
> differ from the canonical public ribbon (Explore / Data / About). They route correctly, but the wording
> isn't unified yet — a later pass can converge them onto the IA in `13_NAVIGATION_IA.md`.

## 3b. Routing verification (automated audit)
A re-runnable harness — **`design/audit.py`** (`cd design && python audit.py`) — traces every screen and
every link. Baseline date **2026-06-03**. Latest run, all green:

| # | Test | Result |
|---|------|--------|
| A | Screens discovered / mapped to a route ID | 48 / 47 (48th = legacy Stitch landing) |
| B | Dead `href="#"` links (ribbons, sidebars, footers) | **0** |
| C | Broken links (target file missing) | **0** of 600+ |
| D | **Semantic** mismatches (label → wrong screen, e.g. "Constituencies" must open P4) | **0** |
| E | Unreachable screens (BFS from P1 / O1 / M1 entries) | **0** |
| F | Orphans (no inbound) · dead-ends (no outbound) | **0 · 0** |
| G | Tier isolation: public→officials leaks · officials→public leaks | **0 · 0** |
| H | Non-2026 years in visible text | **1** — only "Procurement Act No. 8 of **2020**" (a real citation, kept) |
| I | Missing local image `src` | **0** |
| J | Screens that cannot navigate **back** to their home hub | **0** |
| K | Title ↔ purpose mismatches (does the page say what it is) | **0** |

What this proves: every nav item, sidebar link, button and table row goes where its label promises;
you can always get forward to any screen and back to a hub; and the public and officials surfaces stay
isolated. Stitch placeholder dates were corrected to 2026; the placeholder coat-of-arms seals were
replaced with the real `assets/coat_of_arms.png` (verified 0 placeholders remain).

## 4. Connection rules (so the build stays consistent)
1. **One route table.** Filenames live in `R` in `design/screens/generate.py`; every nav link, sidebar
   item, button and table row resolves through it. In React this becomes the router's path constants.
2. **No dead ends.** Every screen offers a way forward and a way back (breadcrumb, sidebar, or bottom
   nav). Validated: all 633 internal links in the prototype resolve, 0 broken.
3. **Tier isolation.** Public ↔ restricted only ever cross at the two explicit bridges (For officials →
   O1; O-sidebar → public). Never blend public and oversight chrome on one screen.
4. **Actions are buttons, navigation is links.** Dropdowns/sidebars/bottom-nav navigate; primary
   actions (Verify, Confirm, Escalate, Save) are buttons that may then navigate.
5. **Pulse meets oversight at evidence.** A Pulse submission's only cross-app destinations are O8
   (confirm) and P5 (public display). Keep that contract when wiring the API.
```
