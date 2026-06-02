# Generates low-fidelity design schematics (wireframes + diagrams) for the whole system.
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle

HERE = os.path.dirname(__file__)
plt.rcParams["font.family"] = "DejaVu Sans"

NAVY = "#1F4E79"; GREEN = "#1E6F43"; AMBER = "#9C6500"; PURPLE = "#5A2D82"
GREY = "#9AA5AE"; LGREY = "#E8ECEF"; DGREY = "#37474F"; INK = "#10202B"; RED = "#B03A3A"


def canvas(w=12, h=7.2):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100); ax.set_ylim(0, 60); ax.axis("off")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    return fig, ax


def rbox(ax, x, y, w, h, fc="white", ec=GREY, lw=1.4, rad=0.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.1,rounding_size={rad}",
                 linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2))


def box(ax, x, y, w, h, fc="white", ec=GREY, lw=1.4):
    ax.add_patch(Rectangle((x, y), w, h, linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2))


def txt(ax, x, y, s, fs=9, color=INK, bold=False, ha="left", va="center", it=False):
    ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va,
            fontweight=("bold" if bold else "normal"), style=("italic" if it else "normal"), zorder=5)


def lines(ax, x, y, w, n=3, gap=2.0, color=GREY):
    for i in range(n):
        ax.add_line(plt.Line2D([x, x + w], [y - i * gap, y - i * gap], lw=2, color=color, zorder=3))


def chrome(ax, title, role, accent=NAVY):
    box(ax, 2, 2, 96, 56, fc="white", ec=DGREY, lw=1.6)          # window
    box(ax, 2, 52, 96, 6, fc=accent, ec=accent)                  # top bar
    txt(ax, 5, 55, title, fs=12, color="white", bold=True)
    txt(ax, 95, 55, role, fs=9, color="white", ha="right")


def save(fig, name):
    p = os.path.join(HERE, name)
    fig.savefig(p, dpi=150, facecolor="white", bbox_inches="tight"); plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------------- PUBLIC DASHBOARD
def public_dashboard():
    fig, ax = canvas()
    chrome(ax, "CDF Transparency Portal — National Overview", "PUBLIC (no login)", NAVY)
    for i, t in enumerate(["Home", "Map", "Constituencies", "Verify Contract", "Procurement Risk", "Open Data"]):
        txt(ax, 6 + i * 15.5, 49, t, fs=8.5, color=NAVY, bold=(i == 0))
    box(ax, 4, 46, 92, 1.4, fc=LGREY, ec=LGREY)
    # KPI cards
    for i, (k, v) in enumerate([("CDF Allocated", "K6.245 bn"), ("Projects Tracked", "—"),
                                ("Verified Complete", "—"), ("Ghost-Project Flags", "—")]):
        rbox(ax, 5 + i * 23, 38, 21, 6, fc="#F4F8FB", ec=GREY)
        txt(ax, 7 + i * 23, 42.5, k, fs=8, color=GREY)
        txt(ax, 7 + i * 23, 39.6, v, fs=12, color=NAVY, bold=True)
    # map + list
    rbox(ax, 5, 8, 50, 27, fc="#EEF3F2", ec=GREY)
    txt(ax, 30, 33, "Constituency risk heat-map (156 constituencies)", fs=9, color=GREEN, bold=True, ha="center")
    txt(ax, 30, 20, "[ Zambia choropleth: green=verified, amber=pending, red=mismatch ]", fs=8, color=GREY, ha="center")
    rbox(ax, 58, 8, 38, 27, fc="white", ec=GREY)
    txt(ax, 60, 33, "Recent verified projects / flags", fs=9, color=NAVY, bold=True)
    for i in range(5):
        box(ax, 60, 28 - i * 3.6, 34, 2.8, fc="#FAFBFC", ec=LGREY)
        lines(ax, 61, 30 - i * 3.6, 22, n=1)
        txt(ax, 92, 29.3 - i * 3.6, "view", fs=7.5, color=NAVY, ha="right")
    save(fig, "wf_public_dashboard.png")


# ---------------------------------------------------------------- VERIFICATION PORTAL
def verify_portal():
    fig, ax = canvas()
    chrome(ax, "Contract Verification Portal", "PUBLIC", NAVY)
    txt(ax, 50, 44, "Verify a contract document against its registered hash", fs=11, color=INK, bold=True, ha="center")
    rbox(ax, 20, 24, 60, 14, fc="#F4F8FB", ec=GREY)
    txt(ax, 50, 33, "⤓  Drop a contract PDF here, or browse", fs=11, color=GREY, ha="center")
    txt(ax, 50, 28, "We hash it locally (SHA-256) and compare to the ledger record", fs=8.5, color=GREY, ha="center", it=True)
    rbox(ax, 36, 16, 28, 5, fc=NAVY, ec=NAVY)
    txt(ax, 50, 18.5, "Verify", fs=11, color="white", bold=True, ha="center")
    # result states
    rbox(ax, 12, 5, 36, 8, fc="#E7F3EC", ec=GREEN)
    txt(ax, 30, 10.5, "✓  MATCH — authentic & unaltered", fs=9, color=GREEN, bold=True, ha="center")
    txt(ax, 30, 7.5, "Anchored 2026-… · tx 0x… · block …", fs=7.5, color=GREY, ha="center")
    rbox(ax, 52, 5, 36, 8, fc="#F7E4E4", ec=RED)
    txt(ax, 70, 10.5, "✗  MISMATCH — altered or unregistered", fs=9, color=RED, bold=True, ha="center")
    txt(ax, 70, 7.5, "Document hash not found / differs", fs=7.5, color=GREY, ha="center")
    save(fig, "wf_verification_portal.png")


# ---------------------------------------------------------------- OAG DASHBOARD (risk list)
def oag_dashboard():
    fig, ax = canvas()
    chrome(ax, "SigTrace — Oversight Console", "OVERSIGHT OFFICER · OAG  🔒", NAVY)
    # sidebar
    box(ax, 2, 2, 16, 50, fc="#10324F", ec="#10324F")
    for i, t in enumerate(["▣ Risk dashboard", "▤ Contract risk list", "◈ Ghost-project queue",
                           "◫ Supplier network", "✎ Cases", "⤒ Verify document", "⎙ Reports", "⚙ Settings"]):
        txt(ax, 4, 48 - i * 5, t, fs=8, color=("white" if i == 1 else "#9FB8CC"), bold=(i == 1))
    # KPI row
    for i, (k, v) in enumerate([("Open flags", "—"), ("High-risk contracts", "—"),
                                ("Ghost-project signals", "—"), ("Cases open", "—")]):
        rbox(ax, 21 + i * 19, 44, 17, 6, fc="#F4F8FB", ec=GREY)
        txt(ax, 23 + i * 19, 48, k, fs=7.5, color=GREY)
        txt(ax, 23 + i * 19, 45.4, v, fs=12, color=NAVY, bold=True)
    # table
    rbox(ax, 21, 6, 75, 35, fc="white", ec=GREY)
    txt(ax, 23, 39, "Contract risk list", fs=9.5, color=NAVY, bold=True)
    hdr = ["Contract / OCID", "Procuring entity", "Risk", "Flags", "Anchor", "Action"]
    xs = [23, 44, 63, 71, 81, 90]
    for x, h in zip(xs, hdr):
        txt(ax, x, 35.5, h, fs=7.5, color=GREY, bold=True)
    box(ax, 22, 34.4, 73, 0.3, fc=GREY, ec=GREY)
    for r in range(7):
        y = 32 - r * 3.8
        box(ax, 22, y - 1.4, 73, 3.2, fc=("#FAFBFC" if r % 2 else "white"), ec=LGREY)
        lines(ax, 23, y + 0.2, 18, n=1)
        lines(ax, 44, y + 0.2, 16, n=1)
        sc = [88, 74, 61, 40, 22, 15][r % 6]
        col = RED if sc >= 70 else (AMBER if sc >= 40 else GREEN)
        rbox(ax, 63, y - 0.9, 6, 2.2, fc=col, ec=col, rad=0.3)
        txt(ax, 66, y + 0.2, str(sc), fs=8, color="white", bold=True, ha="center")
        txt(ax, 73, y + 0.2, "● ● ●", fs=7, color=AMBER)
        txt(ax, 82, y + 0.2, "✓" if r % 3 else "—", fs=9, color=(GREEN if r % 3 else GREY))
        txt(ax, 90, y + 0.2, "review", fs=7.5, color=NAVY, bold=True)
    save(fig, "wf_oag_dashboard.png")


# ---------------------------------------------------------------- CONTRACT DETAIL (anomaly review)
def contract_detail():
    fig, ax = canvas()
    chrome(ax, "Contract Detail — Anomaly Review", "OVERSIGHT OFFICER  🔒", NAVY)
    rbox(ax, 4, 44, 58, 6, fc="#F4F8FB", ec=GREY)
    txt(ax, 6, 48, "OCID: ocds-…-000123   ·   Procuring Entity: …   ·   Value: K…", fs=8.5, color=INK)
    txt(ax, 6, 45.4, "Award → Signing: 9 days   ·   Status: active", fs=8, color=GREY)
    rbox(ax, 64, 44, 32, 6, fc=RED, ec=RED)
    txt(ax, 80, 48, "RISK 88 / 100", fs=12, color="white", bold=True, ha="center")
    txt(ax, 80, 45.4, "HIGH — review required", fs=8, color="white", ha="center")
    # eight checks panel
    rbox(ax, 4, 6, 56, 36, fc="white", ec=GREY)
    txt(ax, 6, 40, "The eight integrity checks", fs=9.5, color=NAVY, bold=True)
    checks = [("1 Signing completeness", "FLAG", RED), ("2 Standstill (<14d)", "FLAG", RED),
              ("3 Stage time-gap", "FLAG", AMBER), ("4 Document forensics", "ok", GREEN),
              ("5 Supplier network", "FLAG", AMBER), ("6 Score variance", "ok", GREEN),
              ("7 Amendment value", "ok", GREEN), ("8 Debarment cross-ref", "ok", GREEN)]
    for i, (c, s, col) in enumerate(checks):
        y = 36 - i * 3.7
        box(ax, 6, y - 1.4, 52, 3.0, fc="#FAFBFC", ec=LGREY)
        txt(ax, 8, y + 0.1, c, fs=8, color=INK)
        rbox(ax, 49, y - 0.8, 7, 2.0, fc=col, ec=col, rad=0.3)
        txt(ax, 52.5, y + 0.1, s, fs=7, color="white", bold=True, ha="center")
    # right: evidence + actions
    rbox(ax, 63, 22, 33, 20, fc="white", ec=GREY)
    txt(ax, 65, 40, "Evidence & hash status", fs=9, color=NAVY, bold=True)
    lines(ax, 65, 36, 28, n=4, gap=2.4)
    txt(ax, 65, 24.5, "Anchor: ✓ registered · tx 0x…", fs=7.5, color=GREEN)
    rbox(ax, 63, 6, 33, 14, fc="#F4F8FB", ec=GREY)
    txt(ax, 65, 18, "Actions", fs=9, color=NAVY, bold=True)
    for i, a in enumerate(["Add to case", "Escalate to ACC", "Mark reviewed (false positive)"]):
        rbox(ax, 65, 13.5 - i * 3.2, 29, 2.4, fc="white", ec=NAVY)
        txt(ax, 79.5, 14.7 - i * 3.2, a, fs=7.5, color=NAVY, ha="center")
    save(fig, "wf_contract_detail.png")


# ---------------------------------------------------------------- GHOST-PROJECT QUEUE
def ghost_queue():
    fig, ax = canvas()
    chrome(ax, "Integrated Monitor — Ghost-Project Queue", "OVERSIGHT OFFICER  🔒", PURPLE)
    txt(ax, 5, 48, "Disbursements with NO matched verified completion within the review window", fs=9, color=INK)
    hdr = ["Constituency", "Project", "Disbursed", "Date", "Days overdue", "Evidence", "Action"]
    xs = [6, 26, 46, 58, 68, 80, 90]
    rbox(ax, 4, 6, 92, 38, fc="white", ec=GREY)
    for x, h in zip(xs, hdr):
        txt(ax, x, 41, h, fs=7.5, color=GREY, bold=True)
    box(ax, 4, 39.8, 92, 0.3, fc=GREY, ec=GREY)
    for r in range(8):
        y = 37 - r * 4.0
        box(ax, 4, y - 1.6, 92, 3.4, fc=("#FBF7FC" if r % 2 else "white"), ec=LGREY)
        lines(ax, 6, y + 0.2, 17, n=1); lines(ax, 26, y + 0.2, 17, n=1)
        txt(ax, 46, y + 0.2, "K…", fs=8, color=INK); txt(ax, 58, y + 0.2, "2026-…", fs=7.5, color=GREY)
        od = [12, 30, 45, 7, 60, 21, 90, 5][r]
        txt(ax, 69, y + 0.2, f"{od}d", fs=8, color=(RED if od > 30 else AMBER), bold=True, ha="center")
        txt(ax, 82, y + 0.2, "none" if od > 30 else "partial", fs=7.5, color=GREY, ha="center")
        txt(ax, 90, y + 0.2, "open case", fs=7.5, color=PURPLE, bold=True)
    save(fig, "wf_ghost_project_queue.png")


# ---------------------------------------------------------------- CDF PULSE MOBILE (PWA)
def pulse_mobile():
    fig, ax = canvas(13, 6.6)
    ax.set_xlim(0, 130)
    titles = ["1 · Home / assigned", "2 · Capture submission", "3 · My submissions / sync"]
    for s in range(3):
        ox = 6 + s * 41
        rbox(ax, ox, 6, 34, 48, fc="white", ec=DGREY, lw=2, rad=2)         # phone
        box(ax, ox, 49, 34, 5, fc=GREEN, ec=GREEN)
        txt(ax, ox + 17, 51.5, "CDF Pulse", fs=9, color="white", bold=True, ha="center")
        txt(ax, ox + 17, 2.5, titles[s], fs=8.5, color=GREEN, bold=True, ha="center")
        if s == 0:
            txt(ax, ox + 3, 45, "Constituency: …", fs=7.5, color=INK)
            for i in range(4):
                box(ax, ox + 3, 40 - i * 6, 28, 4.6, fc="#FAFBFC", ec=LGREY)
                txt(ax, ox + 5, 42.2 - i * 6, f"Project #{i+1}", fs=7.5, color=INK)
                txt(ax, ox + 29, 42.2 - i * 6, "›", fs=11, color=GREY, ha="right")
            rbox(ax, ox + 3, 8, 28, 4.5, fc=GREEN, ec=GREEN); txt(ax, ox + 17, 10.2, "+ New capture", fs=8, color="white", bold=True, ha="center")
        elif s == 1:
            box(ax, ox + 3, 30, 28, 18, fc="#EEF3F2", ec=GREY)
            txt(ax, ox + 17, 39, "[ camera viewfinder ]", fs=7.5, color=GREY, ha="center")
            txt(ax, ox + 3, 27, "📍 GPS: -15.4,28.3 (locked)", fs=7, color=GREEN)
            txt(ax, ox + 3, 24, "🕑 timestamp auto", fs=7, color=GREY)
            for i, t in enumerate(["Category ▾", "Notes …", "Offline — will sync"]):
                box(ax, ox + 3, 19 - i * 4.2, 28, 3.2, fc="white", ec=LGREY); txt(ax, ox + 5, 20.6 - i * 4.2, t, fs=7, color=INK)
            rbox(ax, ox + 3, 8, 28, 4.5, fc=GREEN, ec=GREEN); txt(ax, ox + 17, 10.2, "Submit", fs=8, color="white", bold=True, ha="center")
        else:
            txt(ax, ox + 3, 45, "Sync queue", fs=8, color=NAVY, bold=True)
            for i, st in enumerate(["✓ synced", "✓ synced", "⟳ pending (offline)", "⟳ pending"]):
                box(ax, ox + 3, 40 - i * 6, 28, 4.6, fc="#FAFBFC", ec=LGREY)
                txt(ax, ox + 5, 42.2 - i * 6, f"Submission #{i+1}", fs=7, color=INK)
                txt(ax, ox + 29, 42.2 - i * 6, st, fs=6.5, color=(GREEN if "✓" in st else AMBER), ha="right")
    save(fig, "wf_pulse_mobile.png")


# ---------------------------------------------------------------- ADMIN CONSOLE
def admin_console():
    fig, ax = canvas()
    chrome(ax, "Administration Console", "SYSTEM ADMIN  🔒", DGREY)
    box(ax, 2, 2, 18, 50, fc="#263238", ec="#263238")
    for i, t in enumerate(["Users & roles", "Check weights", "Thresholds", "Ingestion runs",
                           "Ledger nodes", "Institutions", "Audit log", "System health"]):
        txt(ax, 4, 48 - i * 5, t, fs=8, color=("white" if i == 1 else "#B0BEC5"), bold=(i == 1))
    rbox(ax, 23, 30, 73, 22, fc="white", ec=GREY)
    txt(ax, 25, 49, "Anomaly check weights (calibrate with OAG)", fs=9.5, color=NAVY, bold=True)
    rows = [("1 Signing completeness", "25"), ("2 Standstill compliance", "20"), ("3 Stage time-gap", "12"),
            ("4 Document forensics", "12"), ("5 Supplier network", "12"), ("6 Score variance", "8"),
            ("7 Amendment value", "8"), ("8 Debarment cross-ref", "18")]
    for i, (c, w) in enumerate(rows):
        y = 45 - i * 1.9
        txt(ax, 25, y, c, fs=7.5, color=INK)
        box(ax, 62, y - 0.7, 20, 1.4, fc=LGREY, ec=LGREY)
        box(ax, 62, y - 0.7, int(int(w) * 0.7), 1.4, fc=NAVY, ec=NAVY)
        txt(ax, 84, y, w, fs=7.5, color=NAVY, bold=True)
    rbox(ax, 23, 6, 35, 22, fc="white", ec=GREY)
    txt(ax, 25, 25, "Thresholds", fs=9, color=NAVY, bold=True)
    for i, t in enumerate(["Standstill min: 14 days", "Amendment cap: 15%", "Time-gap min: configurable",
                           "High-risk escalation: ≥70", "Ghost-project window: 90 days"]):
        txt(ax, 25, 21 - i * 3, "• " + t, fs=7.5, color=INK)
    rbox(ax, 61, 6, 35, 22, fc="#F4F8FB", ec=GREY)
    txt(ax, 63, 25, "System health", fs=9, color=NAVY, bold=True)
    for i, t in enumerate([("Ingestion pipeline", GREEN), ("Fabric peers (3/3)", GREEN),
                           ("Polygon RPC", GREEN), ("IPFS gateway", AMBER), ("API latency", GREEN)]):
        txt(ax, 63, 21 - i * 3, "● " + t[0], fs=7.5, color=t[1])
    save(fig, "wf_admin_console.png")


# ---------------------------------------------------------------- ERD
def erd():
    fig, ax = canvas(13, 7.6)
    ax.set_ylim(0, 64)
    ents = {
        "Contract": (8, 50, ["ocid PK", "procuring_entity", "value", "award_date",
                              "signing_date", "signing_doc", "framework_parent", "status", "risk_score"]),
        "AnomalyFlag": (38, 52, ["id PK", "contract_ocid FK", "check_id", "result", "weight", "note"]),
        "AnchorRecord": (38, 36, ["id PK", "contract_ocid FK", "sha256", "ledger_tx", "anchored_at"]),
        "Supplier": (68, 52, ["id PK", "name", "tpin", "address", "phone", "debarred_until"]),
        "SupplierLink": (68, 40, ["id PK", "supplier_a FK", "supplier_b FK", "shared_attr"]),
        "Disbursement": (8, 30, ["id PK", "constituency", "project_id FK", "amount", "date", "matched"]),
        "Project": (8, 14, ["id PK", "constituency", "title", "status", "verified"]),
        "PulseSubmission": (38, 16, ["id PK", "project_id FK", "ipfs_cid", "lat", "lng", "ts", "status"]),
        "Confirmation": (68, 18, ["id PK", "submission_id FK", "confirmer", "signature", "ts"]),
        "GhostProjectSignal": (38, 2, ["id PK", "disbursement_id FK", "days_overdue", "state"]),
        "Case": (88, 34, ["id PK", "subject_ref", "assignee", "status"]),
        "User": (88, 52, ["id PK", "role", "institution", "mfa"]),
        "AuditLog": (88, 16, ["id PK", "actor", "action", "target", "ts(anchored)"]),
    }
    pos = {}
    for name, (x, y, fields) in ents.items():
        nm = "GhostProjectSignal" if name.startswith("Ghost") else name
        h = 2.2 + len(fields) * 1.7
        rbox(ax, x, y, 22, h, fc="white", ec=NAVY)
        box(ax, x, y + h - 2.0, 22, 2.0, fc=NAVY, ec=NAVY)
        txt(ax, x + 1, y + h - 1.0, nm, fs=8, color="white", bold=True)
        for i, f in enumerate(fields):
            txt(ax, x + 1, y + h - 3.2 - i * 1.7, f, fs=6.5, color=INK)
        pos[nm] = (x, y, 22, h)

    def link(a, b):
        ax_, ay, aw, ah = pos[a]; bx, by, bw, bh = pos[b]
        ax.add_patch(FancyArrowPatch((ax_ + aw / 2, ay), (bx + bw / 2, by + bh),
                     arrowstyle="-", linewidth=1.2, color=GREY, zorder=1,
                     connectionstyle="arc3,rad=0.05"))
    for a, b in [("AnomalyFlag", "Contract"), ("AnchorRecord", "Contract"), ("SupplierLink", "Supplier"),
                 ("Disbursement", "Project"), ("PulseSubmission", "Project"), ("Confirmation", "PulseSubmission"),
                 ("GhostProjectSignal", "Disbursement")]:
        try: link(a, b)
        except Exception: pass
    txt(ax, 50, 62, "Entity-Relationship Overview (core domain)", fs=12, color=NAVY, bold=True, ha="center")
    save(fig, "erd.png")


# ---------------------------------------------------------------- RBAC MATRIX
def rbac_matrix():
    fig, ax = canvas(13, 7)
    ax.set_xlim(0, 120); ax.set_ylim(0, 60)
    roles = ["Anonymous", "Community\nMonitor", "Inst.\nConfirmer", "Oversight\nOfficer", "Analyst", "System\nAdmin"]
    perms = ["Public aggregates (read)", "Verify document", "Named contract data (read)",
             "Review / action anomalies", "Create field submission", "Confirm submission",
             "Ghost-project actions", "Case management", "Manage users & roles",
             "Configure weights/thresholds", "Ledger / node governance", "Read audit log"]
    grid = [
        [1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1],
        [0, 0, 0, 1, 0, 1],
        [0, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 1],
        [0, 0, 1, 1, 0, 1],
        [0, 0, 0, 1, 0, 1],
        [0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 1],
        [0, 0, 0, 1, 1, 1],
    ]
    x0, y0, cw, ch = 42, 6, 12, 3.4
    for j, r in enumerate(roles):
        txt(ax, x0 + cw * j + cw / 2, 52, r, fs=7.5, color=NAVY, bold=True, ha="center")
    for i, p in enumerate(perms):
        y = 49 - i * ch
        txt(ax, 40, y - ch / 2, p, fs=7.3, color=INK, ha="right")
        for j in range(len(roles)):
            x = x0 + cw * j
            allowed = grid[i][j]
            box(ax, x, y - ch, cw - 0.6, ch - 0.4, fc=("#D6EBDD" if allowed else "#F3F4F5"),
                ec="white", lw=1.5)
            if allowed:
                txt(ax, x + cw / 2 - 0.3, y - ch / 2, "✓", fs=9, color=GREEN, bold=True, ha="center")
    txt(ax, 60, 57, "Role-Based Access Control — permission matrix", fs=12, color=NAVY, bold=True, ha="center")
    save(fig, "rbac_matrix.png")


# ---------------------------------------------------------------- DEPLOYMENT
def deployment():
    fig, ax = canvas(13, 7)
    ax.set_xlim(0, 120)
    txt(ax, 60, 57, "Deployment / Runtime Architecture", fs=12, color=NAVY, bold=True, ha="center")
    # clients
    for i, (t, c) in enumerate([("Public web\n(React)", NAVY), ("Oversight console\n(React)", NAVY),
                                ("CDF Pulse PWA\n(React + SW)", GREEN)]):
        rbox(ax, 6 + i * 22, 46, 18, 7, fc="#F4F8FB", ec=c); txt(ax, 15 + i * 22, 49.5, t, fs=8, color=c, bold=True, ha="center")
    rbox(ax, 78, 46, 34, 7, fc="#FBF3E6", ec=AMBER)
    txt(ax, 95, 49.5, "Admin console (React)", fs=8, color=AMBER, bold=True, ha="center")
    # gateway
    rbox(ax, 30, 37, 60, 5, fc=DGREY, ec=DGREY)
    txt(ax, 60, 39.5, "API Gateway — TLS 1.3 · JWT/MFA · RBAC · rate-limit · two-tier data scoping", fs=8, color="white", bold=True, ha="center")
    # services
    svcs = ["Auth & RBAC", "Ingestion\n(OCDS)", "Anomaly engine\n(8 checks)", "Anchoring\n& verify",
            "Pulse API", "Integrated\nmonitor", "Cases &\nnotifications"]
    for i, s in enumerate(svcs):
        rbox(ax, 4 + i * 16.5, 26, 14, 7, fc="white", ec=NAVY); txt(ax, 11 + i * 16.5, 29.5, s, fs=7, color=NAVY, bold=True, ha="center")
    # data + infra
    for i, (t, c) in enumerate([("PostgreSQL\n(domain data)", NAVY), ("Object store\n(PDFs)", NAVY),
                                ("Redis\n(queue/cache)", NAVY)]):
        rbox(ax, 6 + i * 19, 15, 16, 6, fc="#EEF3F8", ec=c); txt(ax, 14 + i * 19, 18, t, fs=7, color=c, bold=True, ha="center")
    for i, (t, c) in enumerate([("Hyperledger\nFabric (perm.)", PURPLE), ("Polygon PoS\n(public)", PURPLE),
                                ("IPFS\n(evidence)", GREEN)]):
        rbox(ax, 70 + i * 16, 15, 14, 6, fc="#F3ECF7", ec=c); txt(ax, 77 + i * 16, 18, t, fs=7, color=c, bold=True, ha="center")
    # arrows
    for x in [15, 37, 59]:
        ax.add_patch(FancyArrowPatch((x, 46), (x if x < 60 else 60, 42.2), arrowstyle="-|>", mutation_scale=12, color=GREY))
    ax.add_patch(FancyArrowPatch((60, 37), (60, 33.2), arrowstyle="-|>", mutation_scale=14, color=DGREY))
    txt(ax, 60, 9, "All inter-service calls authenticated · personal data off-chain · only hashes on ledgers",
        fs=8, color=GREY, ha="center", it=True)
    save(fig, "deployment_architecture.png")


if __name__ == "__main__":
    public_dashboard(); verify_portal(); oag_dashboard(); contract_detail()
    ghost_queue(); pulse_mobile(); admin_console(); erd(); rbac_matrix(); deployment()
    print("done")
