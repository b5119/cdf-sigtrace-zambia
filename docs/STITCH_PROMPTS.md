# Stitch AI Prompts — every screen

> **How to use:** paste the **DESIGN SYSTEM PRIMER** (below) first, then append one screen prompt.
> Generate one screen at a time. After generating, export and hand-finish the signature elements
> (Verification Seal, map, risk gauge, motion). Screen IDs match `04_SCREENS.md`. ★ = build first
> (INC-008–010).

---

## DESIGN SYSTEM PRIMER  (paste before every screen)
Design a government-grade civic-transparency app for Zambia called "SigTrace / CDF Pulse" that lets
citizens verify how Constituency Development Fund money is spent. Visual style: serious, institutional,
trustworthy — like a national court-of-record, not a generic SaaS dashboard. Palette: primary Integrity
Green #0E5C46, accent Eagle Copper #B8762A, near-black ink #0B1F1A, light background #F6F8F6, white
cards, risk scale green #138636 → amber #B45309 → red #B91C1C. Typography: Space Grotesk for headings,
Inter for body, JetBrains Mono for hashes/IDs/coordinates. Rounded 12px cards, soft shadows, generous
white space, WCAG AA contrast, lucide icons, no emoji, no purple gradients. A recurring signature
element is an official circular "Verification Seal" featuring the Zambian coat of arms, the words
"VERIFIED ON LEDGER", a monospace SHA-256 hash and a ledger transaction id.

---

# A. PUBLIC PORTAL  (anonymous)

**P1 — Landing / Home** ★
Top nav with a small coat-of-arms mark, links (Map, Verify, Constituencies, Open Data, About) and a
primary "Verify a contract" button. Hero: a bold headline "See how Zambia's CDF money is really spent",
a subline about independent, tamper-evident verification, the figure "K6.245 billion a year across 156
constituencies", and two buttons "Verify a contract" and "Explore the map". Below: three feature cards
(Verify contracts · Track delivery · Flag ghost projects) and a strip of live statistics. Calm,
institutional, lots of white space.

**P2 — National Dashboard** ★
A public national dashboard. Hero is a large interactive map of Zambia's 156 constituencies as a
choropleth coloured by project verification status (green verified, amber pending, red mismatch). Above
it, four KPI cards: CDF Allocated K6.245bn, Projects Tracked, Verified Complete, Ghost-Project Flags.
Right column: a live feed of recently verified projects and flags. Top nav with a small coat-of-arms
mark and a prominent "Verify a contract" button.

**P3 — Project Map** ★
A full-screen interactive map of Zambia showing all 156 constituencies as a choropleth coloured by
verification status (green verified, amber pending, red mismatch). Left panel: filters (province,
sector, status, year) and a legend. Clicking a constituency opens a side drawer with its projects,
allocation and aggregate risk. Top: a search box and national totals.

**P4 — Constituency Detail**
A constituency detail page. Header with constituency name, province, CDF allocation and an aggregate
verification status. A grid of project cards (photo, title, sector, cost in monospace, status badge,
verified-seal indicator). A small locator map. Breadcrumb back to the national map.

**P5 — Project Detail (public)**
A public project detail page. Header: project title, constituency, sector, total cost (monospace),
status. Main: a gallery of photographic evidence from IPFS, a verified-location mini-map with a pin, a
timeline of disbursement and confirmations, and the official circular Verification Seal showing the
anchor hash and ledger transaction. Sidebar: project facts and a "report a concern" link.

**P6 — Contract Verification Portal** ★
A contract verification page. Centre: a drag-and-drop zone to upload a contract PDF, with helper text
"we hash it locally and compare to the ledger". Below, two result states side by side: a VERIFIED state
showing the green/copper circular Verification Seal with the coat of arms, a monospace SHA-256 hash,
ledger tx and timestamp; and a MISMATCH state with a red broken seal reading "NOT VERIFIED — altered or
unregistered".

**P7 — Procurement Risk Overview**
A public, de-identified procurement risk overview. Column charts of anomaly rates by sector and by
procuring entity (aggregated only, no names), a trend line over time, and KPI cards (contracts analysed,
flagged rate, average risk). A clear note that figures are aggregated risk signals, not determinations
of wrongdoing.

**P8 — Open Data**
An open-data downloads page. A table of datasets (name, description, format CSV/JSON, last updated,
size) each with a Download button, plus a card linking to the public API documentation. Clean and
minimal.

**P9 — About / Methodology / FAQ**
An about/methodology page explaining in plain language how the platform works: the eight integrity
checks, how contract hashes are anchored to the ledger, how community photo evidence is verified, and a
prominent disclaimer that outputs are risk signals requiring review, never determinations of wrongdoing.
Include a short FAQ accordion and a data-protection notice.

---

# B. OVERSIGHT CONSOLE  (restricted, MFA)

**O1 — Login (MFA)** ★
A restricted oversight console login. Centred card on a dark Integrity-ink background with a subtle map
texture: small coat-of-arms mark, "SigTrace Oversight Console", email and password fields, a primary
green button, then a second step for a 6-digit TOTP code. Understated, secure, government-grade.

**O2 — Risk Dashboard (home)** ★
An oversight home dashboard with a dark green-black sidebar (Risk dashboard, Contract risk list,
Ghost-project queue, Supplier network, Cases, Verify, Reports, Settings) and light content. Four KPI
cards (open flags, high-risk contracts, ghost-project signals, open cases). A line chart of anomaly rate
over time, a bar chart of risk by procuring entity, and an alert feed of the newest high-risk contracts
and ghost-project signals on the right.

**O3 — Contract Risk List** ★
The same dark sidebar and light content. Main: a dense, sortable contract risk table with columns OCID,
Procuring Entity, Risk (a 0–100 score as a coloured badge green/amber/red), Flags (dots), Anchor (✓),
Action (review). Four KPI cards above: open flags, high-risk contracts, ghost-project signals, cases
open. Filter bar with entity, risk range, flag type, date.

**O4 — Contract Detail / Anomaly Review** ★
A contract detail page. Left: a checklist of eight integrity checks, each green-pass / amber-flag /
red-fail with a short reason. Right: an animated circular risk gauge showing 88/100 in red, an evidence
panel, the Verification Seal showing anchor status, and an actions card (add to case, escalate to ACC,
mark reviewed). Header shows OCID and value in monospace.

**O5 — Supplier Network Graph**
A supplier network analysis page. A force-directed graph where supplier nodes connect when they share a
registration attribute (address, phone, shareholder); suspicious clusters highlighted in copper. Side
panel lists the tender, the linked suppliers and the shared attributes. Controls to filter by attribute
and zoom.

**O6 — Ghost-Project Queue**
A ghost-project queue with a purple-accent header. A table of disbursements with no matched verified
completion: constituency, project, amount, disbursement date, days overdue (red if over 30), evidence
status, and an "open case" action. KPI strip: total signals, overdue, escalated.

**O7 — Disbursement / Mismatch Explorer**
A disbursement and mismatch explorer. A table of all disbursements with match status (clean contract ✓,
verified completion ✓, or mismatch ✗), filters by constituency and status, and a drill-down drawer
linking a disbursement to its contract (SigTrace) and its delivery evidence (CDF Pulse).

**O8 — Project Verification Review**
A review queue for field submissions awaiting institutional confirmation. Rows each showing the photo
thumbnail, constituency/project, captured GPS and time, submitter, and Confirm / Reject buttons (reject
asks for a reason). A map preview and the IPFS CID in monospace.

**O9 — Document Verification Console**
A restricted document verification console. Upload a contract to re-hash and compare against the anchored
record, showing the named contract context and the Verification Seal result; plus a list of recent
anchor records (OCID, hash, tx, timestamp) in a monospace table.

**O10 — Cases**
A case management view. Left: a list of cases (subject, assignee, status, priority). Right: the selected
case detail with a timeline of notes, status and assignee controls, the linked contract or ghost-project,
and an "Escalate to ACC" button. An add-note composer at the bottom.

**O11 — Analytics**
An analyst workspace. Configurable charts of anomaly rates and trends, comparisons across procuring
entities and sectors, and saved views. A filter bar across the top and export buttons. Data-dense but
calm.

**O12 — Reports & Exports**
A reports and exports page. A form to generate a restricted report (scope, date range, format PDF/CSV),
a preview, and a history table of previously generated reports with download links. A note that exports
are audit-logged.

**O13 — Notifications**
A notifications centre. A list of alerts (new high-risk contract, new ghost-project signal, confirmation
requested, case assigned) with read/unread states, filters by type, and mark-all-read. Each item links
to the relevant record.

---

# C. ADMIN CONSOLE  (system admin)

**S1 — Admin Home**
An admin home with system health: status tiles for the ingestion pipeline, Hyperledger Fabric peers
(3/3), Polygon RPC, IPFS gateway, API latency and database, each green/amber/red. Quick links to user
management and configuration. A dark slate accent.

**S2 — Users & Roles**
An admin users-and-roles screen. A table of users (name, email, role, institution, status, MFA) with
create and edit, plus a role-and-permissions reference panel showing the six roles and what each can do.
Activate/deactivate and force-MFA-reset actions.

**S3 — Check Weights**
An admin screen to tune the eight anomaly-check weights with labelled sliders (signing completeness,
standstill, time-gap, document forensics, supplier network, score variance, amendment value, debarment),
each showing its current weight and a running total, a "calibrate with OAG" note, version history, and
a Save button.

**S4 — Thresholds**
An admin thresholds screen with labelled numeric inputs: standstill minimum days (14), amendment cap
percent (15), time-gap minimum, high-risk escalation score (70), ghost-project window days (90). Each
with a short explanation and Save; show the active version.

**S5 — Ingestion Management**
An admin ingestion-management screen for the OCDS pipeline: a "Run ingestion" button, a schedule control,
and a table of past runs (started, finished, records in/loaded, errors, status) with an expandable error
log.

**S6 — Ledger & Node Governance**
An admin ledger governance screen showing Hyperledger Fabric peer/MSP status per institution, the
Polygon contract address and signer status, and the anchoring backlog. Health indicators and last-block
info in monospace.

**S7 — Institutions & Agreements**
An admin screen listing institutions (OAG, ACC, ZPPA, …) with their type and data-sharing agreement
reference and status, and controls to add or edit an institution and its restricted-tier access.

**S8 — Audit Log Viewer**
An admin audit-log viewer: an immutable, filterable table (actor, action, target, timestamp) with
filters by actor/action/date, and an indicator showing the latest audit batch hash anchored to the
ledger (monospace).

**S9 — Notification Templates / Config**
An admin screen to manage alert rules and notification templates: a list of rules (trigger, audience,
channel) and a template editor with variables, plus enable/disable toggles.

---

# D. CDF PULSE  (mobile — monitors & confirmers)

**M1 — Login / device registration** ★
A mobile field-app login/registration screen. App logo, "CDF Pulse", a phone-number or assigned-
credential field, an OTP step, and a device-registration confirmation. Large touch targets, high
contrast, works one-handed; an "offline grace" note.

**M2 — Home / assignments** ★
A mobile home screen for a community monitor. Header with assigned constituency and a sync-status
indicator. A list of assigned project cards (title, sector, status, chevron). A large primary "+ New
capture" button fixed at the bottom.

**M3 — Capture submission** ★
A mobile field-app capture screen, camera-first: a full-bleed camera viewfinder, an animated "GPS
locked" chip showing coordinates, an automatic timestamp, a category dropdown and a note field, a clear
"Offline — will sync" banner, and a large primary "Submit" button. Big touch targets, high contrast,
works one-handed.

**M4 — Review & submit**
A mobile review screen before submitting: the captured photo, the locked GPS coordinates and timestamp,
the chosen category and note (editable), and a large "Submit" button with an "Offline — will sync" note
if there is no connection.

**M5 — My submissions / sync queue** ★
A mobile "my submissions" list with a sync queue: each item shows a photo thumbnail, project, captured
time and a sync state (synced ✓ green, pending ⟳ amber). A manual "Sync now" button and a count of
pending items.

**M6 — Submission detail**
A mobile submission detail screen: the photo, project and constituency, a GPS map pin, timestamp, the
IPFS CID in monospace, and the confirmation status (awaiting / confirmed by N parties). A tamper-evident
note.

**M7 — Confirmation inbox (confirmer)**
A mobile confirmation inbox for an institutional confirmer: a list of field submissions awaiting
confirmation, each with photo, location, submitter and Confirm / Reject buttons (reject requires a
reason). Big touch targets.

**M8 — Profile / settings**
A mobile profile and settings screen: account info, assigned constituency, storage and sync settings, a
high-contrast toggle, language, and sign-out. Simple and clean.

---

# E. SHARED / SYSTEM

**X1 — Login**
A clean login screen (email and password) with the app wordmark and a "forgot password" link; matches
the platform palette.

**X2 — MFA Challenge**
A 6-digit TOTP code entry screen with a segmented OTP input, a resend timer, and a Verify button.

**X3 — Forgot / Reset Password**
A two-step forgot-password flow: request reset by email, then set a new password with strength feedback.

**X4 — Account / Session Settings**
An account settings screen: profile, change password, manage MFA device, and a list of active sessions
with "sign out everywhere".

**X5 — Error / 403 / 404 / Offline**
A set of friendly status screens (403 forbidden, 404 not found, a generic error, and a PWA offline
screen) each with the platform mark, a short message and a primary action to go back or retry.

**X6 — Consent / Data-Protection Notice**
A plain-language data-protection and consent screen shown at onboarding: what data is collected, that
personal data stays off-chain, the right to erasure, and an "I understand" acknowledgement.

---

*45 screens. The 6 starred groups (P1, P2, P3, P6, O1–O4, M1–M3, M5) cover INC-008 to INC-010.*
