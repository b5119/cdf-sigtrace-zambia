# 11 · Front-End Design System & Build Guide

> **Read before building any UI (INC-008 onward).** This is the design language for all three apps.
> Goal: a public-institution-grade product that signals trust and feels purpose-built — not a generic
> dashboard template. Pair this with `04_SCREENS.md` (what each screen is) and `05_RBAC_SECURITY.md`
> (who sees what). Project stack baseline: React + TypeScript + Tailwind + TanStack Query.

---

## 0. Where we are
Backend, anomaly engine, anchoring and the public verification API are built (INC-001–007, 40%).
**INC-008 (Public CDF dashboard + map) is the first real UI.** Everything below applies from here on.

---

## 1. Design philosophy — what makes it *not* generic

Three audiences, one product, one feeling: **"this is official, trustworthy, and built for Zambia."**
We get there with five signature moves — these are the things that make it feel game-changing rather
than a Bootstrap admin theme:

1. **The Verification Seal (hero element).** When a contract or project verifies against the ledger, we
   render an official-looking circular **seal** — Zambian coat of arms at the centre, the words
   *"VERIFIED ON LEDGER"*, the SHA-256 hash, the ledger tx and timestamp around the ring. A mismatch
   shows a **broken/red seal**. This single element ties national identity to cryptographic trust and
   becomes the brand's signature. (See §3 and §6.1.)
2. **Cryptographic data is first-class.** Hashes, OCIDs and tx IDs are shown in a **monospace** type
   with copy buttons and truncation (`0xa1b2…9f`). Treating crypto data as a designed object — not raw
   text — instantly reads as "serious infrastructure."
3. **The risk score is alive.** A contract's 0–100 score is an animated **gauge**, and the eight checks
   render as a **checklist that fills in** (pass green / flag amber / fail red) — not a flat table.
4. **The map is the centrepiece, not a widget.** The public dashboard leads with an interactive
   **Zambia constituency choropleth** (156 constituencies) coloured by verification/risk — the first
   thing a citizen sees.
5. **Motion with meaning.** The same step-by-step *build* reveals used in the defence deck are reused in
   the product (data flows in as it's explained). Calm, purposeful micro-interactions — never decorative.

**Anti-patterns to avoid:** stock admin templates, purple gradient SaaS hero, emoji icons, dense grey
tables with no hierarchy, "AI dashboard" clichés, decorative 3D blobs. Government-grade = restrained,
legible, confident.

---

## 2. Brand & national identity

We adopt the **idea** from ZedLedger (Zambian coat of arms as a national-identity mark) but deliberately
**do not mimic** its look:

| | ZedLedger | **CDF / SigTrace (ours)** |
|---|---|---|
| Primary colour | Flag green `#198A00` | **Integrity Green `#0E5C46`** (deeper, "ledger/audit") |
| Signature accent | — | **Eagle Copper `#B8762A`** (from the eagle on the arms) — our differentiator |
| Coat of arms role | Small nav icon | **A functional verification seal** tied to cryptographic proof |
| Feel | Bright, service-portal | Serious, institutional, "court-of-record" |

So we look unmistakably Zambian and official, but distinct from ZedLedger, and the copper seal is *our*
mark.

### 2.1 Logo / wordmark
- **Wordmark:** `SigTrace` (procurement) and `CDF Pulse` (delivery) as sibling wordmarks under one
  parent mark **"CDF Integrity"** (or the chosen umbrella name). Strong, slightly condensed sans.
- **App mark:** a custom geometric glyph (a shield/ledger motif) in Integrity Green — **not** the coat
  of arms. The coat of arms is reserved for the official seal and official document/export contexts only
  (it is a national emblem; use it as a mark of *record authenticity*, not as the company logo).

---

## 3. The Verification Seal (the signature component)

This is the one component to get perfect.

```
            ╭───────────────────────────╮
            │   ✶  VERIFIED ON LEDGER ✶  │      ← copper ring text, around the circle
            │     [ coat of arms ]        │      ← Zambian arms, embossed, centre
            │   Hyperledger Fabric        │
            │   sha256 0xa1b2…9f  ⧉        │      ← monospace, copy button
            │   tx 0x…   ·  2026-06-01    │
            ╰───────────────────────────╯
```
- **Verified state:** Integrity-Green ring, copper inner ring, arms embossed, subtle gold sheen on
  reveal; check-mark stamp animation (~500 ms).
- **Mismatch state:** red ring, the arms desaturated, a visible "break" in the ring, "NOT VERIFIED —
  altered or unregistered."
- **Pending/unanchored:** neutral grey, "Not yet anchored."
- Appears on: the public verification result (INC-007/008), contract detail (INC-009), project detail
  (INC-014), and on **PDF/print exports** (where it reads as an official seal of authenticity).
- Reference patterns: blockchain "proof-of-authenticity" seals (OriginStamp SealPact, CB Blockchain
  Seal, Truth Verifier) — see §12.

---

## 4. Design tokens

Implement as CSS variables + a shared Tailwind preset (`packages/ui` — see §10). Light-mode first;
dark mode optional for the oversight console.

```css
:root {
  /* Brand */
  --c-primary:        #0E5C46;  /* Integrity Green */
  --c-primary-hover:  #0A4533;
  --c-primary-tint:   #E3EFEA;
  --c-accent:         #B8762A;  /* Eagle Copper (seal, highlights, key CTAs) */
  --c-accent-hover:   #9C6322;
  --c-ink:            #0B1F1A;  /* near-black text + dark sidebar */

  /* Surfaces */
  --c-bg:             #F6F8F6;
  --c-surface:        #FFFFFF;
  --c-surface-2:      #EEF3EF;
  --c-border:         #D7E0DA;

  /* Text */
  --c-text:           #0B1F1A;
  --c-text-muted:     #586B63;

  /* Risk scale (0–100) — reuse across gauges, tables, map */
  --c-risk-low:       #138636;  /* 0–39  green  */
  --c-risk-mid:       #B45309;  /* 40–69 amber  */
  --c-risk-high:      #B91C1C;  /* 70–100 red   */

  /* Semantic */
  --c-success:#138636; --c-warning:#B45309; --c-danger:#B91C1C; --c-info:#1D4ED8;

  /* Radius / shadow / motion */
  --radius: 12px;  --radius-sm: 8px;
  --shadow-card: 0 1px 2px rgba(11,31,26,.06), 0 8px 24px rgba(11,31,26,.06);
  --ease: cubic-bezier(.2,.8,.2,1);
}
[data-contrast="high"] { --c-text:#000; --c-border:#000; --c-primary:#0A4533; } /* a11y mode */
```

### 4.1 Typography
- **Display/headings:** `Space Grotesk` (or `Inter Tight`) — modern, civic, a little editorial.
- **Body/UI:** `Inter`.
- **Cryptographic data (hashes, OCID, tx, coordinates):** `JetBrains Mono` / `IBM Plex Mono` — always
  monospace, with a copy affordance. This is a deliberate signature.
- Scale: 12 / 14 / 16 (body) / 20 / 24 / 32 / 44 (display). Generous line-height (1.5 body).

### 4.2 Iconography
`lucide-react` (matches ZedLedger), 1.5px stroke, consistent 20/24px. No emoji in product UI.

---

## 5. Component library (build once in `packages/ui`)
Buttons (primary copper/green, secondary, ghost, danger) · Cards · Stat/KPI cards · Data table (sortable,
filterable, sticky header, risk-coloured cells) · **RiskGauge** · **RiskScore badge** · **CheckList** (the
8 checks) · **VerificationSeal** · **HashChip** (mono + copy + truncate) · **ConstituencyMap** · Tabs ·
Drawer/Sheet · Modal · Toast · Badge/Pill (status) · Empty/Loading/Error states · Skeletons ·
Form controls (react-hook-form + zod) · App shell (top bar + dark sidebar) · Seal/PDF export layout.

All components: keyboard-navigable, focus-visible rings, ARIA-labelled, ≥4.5:1 contrast.

---

## 6. Per-app design direction

### 6.1 Public Portal (anonymous) — *the showcase*
The public face; this is where "game-changing" must land. Screens P1–P9 (`04_SCREENS.md`).
- **Landing/Home:** a confident hero — one line ("Verify how Zambia's CDF money is spent"), the
  K6.245 bn figure, a primary action *Verify a contract* and *Explore the map*. Optional subtle WebGL/
  canvas motion (ZedLedger uses `ogl`) — keep it tasteful, performance-budgeted.
- **National Dashboard (INC-008):** lead with the **constituency choropleth map**; KPI cards
  (allocated, projects, verified, ghost-project flags); a live feed of recently verified projects/flags.
- **Verification Portal (INC-007/008):** drag-drop a contract PDF → client hashes (SHA-256) → the
  **Verification Seal** animates the result. This is the money shot — make it feel official.
- **Project detail:** photo evidence (from IPFS), verified location mini-map, confirmation status, seal.
- Tone: open, civic, trustworthy; lots of white space; map and seal do the talking.

### 6.2 Oversight Console + Admin (restricted, MFA) — *dense but calm*
Screens O1–O13, S1–S9. Internal, data-heavy, auth-gated.
- App shell: **dark Integrity-ink sidebar** + light content (ZedLedger pattern).
- **Risk list:** the data table with risk-coloured score badges, flag dots, anchor status.
- **Contract / anomaly review:** the **CheckList** of 8 checks filling in, the **RiskGauge**, evidence
  panel, the seal, and actions (add to case, escalate, mark reviewed).
- **Supplier network graph**, **ghost-project queue**, **cases**, **admin** (weight sliders, thresholds,
  users, health). Calm, efficient, no decoration.

### 6.3 CDF Pulse (community monitors / confirmers) — *camera-first, offline-first*
Screens M1–M8. Mobile. Big touch targets, one primary action per screen, works with no signal.
- **Capture:** full-bleed camera viewfinder; an animated **GPS-lock** indicator; auto timestamp;
  category + note; an explicit **"offline — will sync"** state.
- **Sync queue** with optimistic UI (synced ✓ / pending ⟳). Confirmer inbox for multi-party sign-off.
- Low-bandwidth: tiny assets, system fonts acceptable, degrade gracefully.

---

## 7. Motion & micro-interactions
- Page/section content **builds in** (staggered fade/slide ~250 ms) — same language as the defence deck.
- Seal reveal (~500 ms stamp), risk gauge sweep, checklist tick cascade, map hover/zoom.
- Honour `prefers-reduced-motion`. Motion is feedback, never filler.

## 8. Accessibility (non-negotiable — civic product)
- WCAG 2.1 **AA** across public + Pulse; target AAA contrast on the public portal.
- A **High-Legibility mode** toggle (like ZedLedger's `data-a11y-contrast`).
- Full keyboard nav, visible focus, semantic landmarks, alt text, form labels, screen-reader names.
- Don't encode meaning in colour alone — risk also shows a number + label; flags show an icon + text.
- Localisation-ready (English first; structure for major Zambian languages later).

---

## 9. App segregation & framework decision (answering "how do we split the apps + mobile")

**Three separate apps by audience and trust tier** (already the `src/` layout) — this is the right
segregation, because it gives a clean security boundary (the public app physically cannot receive
restricted data), independent deploys, and audience-tailored UX:

| App | Audience / tier | Recommended framework | Folder |
|-----|-----------------|----------------------|--------|
| **Public Portal** | Anonymous, public tier | **Next.js (App Router)** — recommended upgrade* | `src/frontend-public` |
| **Oversight + Admin** | OAG/ACC/ZPPA + admin, restricted | **React + Vite SPA** (as planned) | `src/frontend-oversight` |
| **CDF Pulse** | Monitors + confirmers | **PWA now → Expo (React Native) later** | `src/pulse-pwa` |

\* **Why Next.js for the public portal (optional but recommended):** it's the SEO-critical, marketing-
grade, public-facing site — server rendering gives a fast first paint, Open-Graph cards make a shared
verification result look official, and image optimisation suits the map/evidence. The other two are
auth-gated internal apps with no SEO need, so **Vite SPA** is the faster, simpler choice there. If you
prefer one toolchain, staying on **Vite for all three is acceptable** — the design system is framework-
agnostic. Either way, do **not** put public and restricted UIs in the same app.

**Keep them one product** with a shared design-system package (§10), so all three look identical.

### 9.1 Mobile: yes — and the stack
**Yes, CDF Pulse is the mobile app.** Recommendation in two stages:
- **Now (prototype / INC-010):** build it as a **PWA** — Vite + React + Workbox service worker +
  IndexedDB offline queue. Camera (`getUserMedia`), GPS (`geolocation`), installable, offline-first, no
  app-store friction, fastest to ship, and it matches the proposal's "offline-first PWA." This is enough
  to demonstrate and defend.
- **Production / native upgrade:** **React Native via Expo.** Chosen over Flutter because the whole
  project is **React/TypeScript** (skill + component reuse), and Expo gives first-class camera, precise
  GPS, **background sync**, secure storage, push, OTA updates and Play-Store presence. (ZedLedger used
  Flutter for its citizen app and native Android for field workers — both valid, but Expo keeps us in
  one language across web + mobile.)
- **Don't** build a separate native app for the prototype — the PWA covers the academic deliverable;
  Expo is the post-prototype path. Document the choice in the increment record either way.

---

## 10. Implementation: one design system, three apps
Create a shared package so the apps can't drift:
```
packages/ui/
  tokens.css         the CSS variables in §4
  tailwind-preset.js  colours/radius/shadow/fonts mapped to Tailwind theme
  components/         Button, Card, DataTable, RiskGauge, CheckList, VerificationSeal, HashChip, Map…
  icons/
```
Each app imports the preset + components. Acceptance for any UI increment: uses the tokens (no ad-hoc
hex), uses shared components, passes axe/Lighthouse AA, and matches the relevant screen in `04_SCREENS.md`.

**Coat of arms asset:** the Zambian coat of arms (public emblem). A clean PNG/SVG already exists at
`ZedLedger/assets/Coat_of_arms_of_Zambia.svg.png` — copy into `packages/ui` (or each app's `/public`)
as `coat_of_arms.png`. Use it **only** inside the Verification Seal and official/export contexts.

---

## 11. Using Stitch AI to generate the UI (recommended workflow)

[Google **Stitch**](https://stitch.withgoogle.com) turns prompts into UI designs + front-end code. To
get on-brand (not generic) output:

1. **Prime it with the design system first** (paste the "DESIGN SYSTEM" prompt below) — this is what
   stops it producing a generic dashboard.
2. **Generate one screen at a time**, re-pasting the design-system block each time.
3. Export to Figma/code, then **hand-finish** the signature elements (the Seal, the map, motion) — Stitch
   gets you 70% there; the last 30% (the seal animation, the choropleth, micro-interactions) is hand-built.
4. Keep the real component library (`packages/ui`) as the source of truth; treat Stitch output as a
   visual starting point, not the final code.

### 11.1 DESIGN SYSTEM prompt (paste before every screen)
> Design a government-grade civic-transparency web app for Zambia called "SigTrace / CDF Pulse" that lets
> citizens verify how Constituency Development Fund money is spent. Visual style: serious, institutional,
> trustworthy — like a national court-of-record, not a generic SaaS dashboard. Palette: primary Integrity
> Green #0E5C46, accent Eagle Copper #B8762A, near-black ink #0B1F1A, light background #F6F8F6, white
> cards, risk scale green #138636 → amber #B45309 → red #B91C1C. Typography: Space Grotesk for headings,
> Inter for body, JetBrains Mono for hashes/IDs/coordinates. Rounded 12px cards, soft shadows, generous
> white space, WCAG AA contrast, lucide icons, no emoji, no purple gradients. A recurring signature
> element is an official circular "Verification Seal" featuring the Zambian coat of arms, the words
> "VERIFIED ON LEDGER", a monospace SHA-256 hash and a ledger transaction id.

### 11.2 Per-screen prompts (append to the design-system prompt)
- **Public dashboard (INC-008):** "A public national dashboard. Hero is a large interactive map of
  Zambia's 156 constituencies as a choropleth coloured by project verification status (green verified,
  amber pending, red mismatch). Above it, four KPI cards: CDF Allocated K6.245bn, Projects Tracked,
  Verified Complete, Ghost-Project Flags. Right column: a live feed of recently verified projects and
  flags. Top nav with a small coat-of-arms mark and a prominent 'Verify a contract' button."
- **Verification portal + Seal:** "A contract verification page. Centre: a drag-and-drop zone to upload a
  contract PDF, with helper text 'we hash it locally and compare to the ledger'. Below, two result
  states side by side: a VERIFIED state showing the green/copper circular Verification Seal with the
  coat of arms, a monospace SHA-256 hash, ledger tx and timestamp; and a MISMATCH state with a red
  broken seal reading 'NOT VERIFIED — altered or unregistered'."
- **Oversight risk list (INC-009):** "A restricted oversight console with a dark green-black left
  sidebar (Risk dashboard, Contract risk list, Ghost-project queue, Supplier network, Cases, Verify,
  Reports, Settings) and a light content area. Main: a dense, sortable contract risk table with columns
  OCID, Procuring Entity, Risk (a 0–100 score as a coloured badge green/amber/red), Flags (dots), Anchor
  (✓), Action (review). Four KPI cards above: open flags, high-risk contracts, ghost-project signals,
  cases open."
- **Contract / anomaly detail (INC-009):** "A contract detail page. Left: a checklist of eight integrity
  checks, each green-pass / amber-flag / red-fail with a short reason. Right: an animated circular risk
  gauge showing 88/100 in red, an evidence panel, the Verification Seal showing anchor status, and an
  actions card (add to case, escalate to ACC, mark reviewed). Header shows OCID and value in monospace."
- **CDF Pulse capture (INC-010, mobile):** "A mobile field-app capture screen, camera-first: a full-bleed
  camera viewfinder, an animated 'GPS locked' chip showing coordinates, an automatic timestamp, a
  category dropdown and a note field, a clear 'Offline — will sync' banner, and a large primary 'Submit'
  button. Big touch targets, high contrast, works one-handed."

---

## 12. Design references to incorporate (researched)
- **Accessibility & gov baseline:** GOV.UK Design System and the U.S. Web Design System — the gold
  standard for accessible, no-nonsense government UI. Adopt their rigour, then add our signature polish.
- **Procurement transparency patterns:** Open Contracting Partnership and Ukraine's **ProZorro** — how to
  present tenders, awards and red flags to the public.
- **Verification-seal UI pattern:** OriginStamp **SealPact**, Connecting Software **CB Blockchain Seal**,
  **Truth Verifier** — public "upload-a-file → see authenticity + timestamp" flows. Direct inspiration
  for our Verification Seal. (https://originstamp.com/en/clients/sealpact ·
  https://www.connecting-software.com/cb-blockchain-seal/)
- **Civic-tech trust UX:** research shows civic platforms live or die on usability and perceived trust —
  prioritise clarity and accessibility over flourish (IJRSI, "UI/UX Design on User Trust… in Civic Tech").
- **National identity:** ZedLedger (internal reference) — for the coat-of-arms-as-mark idea, which we
  evolve into the functional Verification Seal.

---

## 13. Definition of done for UI increments
Built with `packages/ui` tokens + components · matches `04_SCREENS.md` · WCAG AA (axe/Lighthouse) ·
keyboard + screen-reader pass · public app exposes **no** restricted data · the Verification Seal and
risk visuals used where relevant · increment record written per `10_TESTING.md`.
