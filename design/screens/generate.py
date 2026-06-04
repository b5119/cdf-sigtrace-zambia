# Generates the remaining screen prototypes as on-brand HTML, matching the Stitch design system
# (extracted tailwind.config from design/stitch_export). Output: design/screens/*.html + index.html.
# Screens are CONNECTED: nav, sidebar, buttons and table rows carry real hrefs (route table R).
import os
HERE = os.path.dirname(__file__)

# ----------------------------------------------------------------- route table
# Canonical filename for every screen ID. Stitch screens live in ../stitch_export.
R = {
  "P1":"landing_enhanced.html", "P2":"P2_dashboard.html",
  "P3":"../stitch_export/national_project_map/code.html",
  "P4":"../stitch_export/constituency_detail/code.html",
  "P5":"../stitch_export/project_transparency_detail/code.html",
  "P6":"../stitch_export/verification_portal/code.html",
  "P7":"P7_procurement_risk.html", "P8":"P8_open_data.html", "P9":"P9_about.html", "P10":"P10_audit_trail.html",
  "O1":"O1_login.html", "O2":"O2_dashboard.html", "O3":"O3_contract_list.html",
  "O4":"O4_contract_detail.html", "O5":"O5_supplier_network.html", "O6":"O6_ghost_queue.html",
  "O7":"O7_mismatch.html", "O8":"O8_verify_review.html", "O9":"O9_doc_verify.html",
  "O10":"O10_cases.html", "O11":"O11_analytics.html", "O12":"O12_reports.html", "O13":"O13_notifications.html",
  "S1":"S1_admin_home.html", "S2":"S2_users.html", "S3":"S3_weights.html", "S4":"S4_thresholds.html",
  "S5":"S5_ingestion.html", "S6":"S6_ledger.html", "S7":"S7_institutions.html", "S8":"S8_audit.html", "S9":"S9_notif_config.html",
  "M1":"M1_login.html", "M2":"M2_home.html", "M3":"M3_capture.html", "M4":"M4_review.html",
  "M5":"M5_sync.html", "M6":"M6_detail.html", "M7":"M7_confirm.html", "M8":"M8_profile.html",
  "X1":"X1_login.html", "X2":"X2_mfa.html", "X3":"X3_reset.html", "X4":"X4_account.html",
  "X5":"X5_errors.html", "X6":"X6_consent.html", "MAP":"index.html",
}

TW_CONFIG = """
tailwind.config = { darkMode: "class", theme: { extend: {
  colors: {
    primary:"#0E5C46", "primary-h":"#0A4533", "primary-container":"#0e5c46",
    accent:"#B8762A", "accent-h":"#9C6322", ink:"#0B1F1A",
    surface:"#F6F8F6", "surface-2":"#EEF3EF", card:"#FFFFFF",
    "on-surface":"#191c1b", "on-surface-variant":"#3f4944",
    outline:"#6f7974", "outline-variant":"#D7E0DA",
    "risk-low":"#138636", "risk-mid":"#B45309", "risk-high":"#B91C1C",
    success:"#138636", warning:"#B45309", danger:"#B91C1C", info:"#1D4ED8",
    "sidebar":"#0B1F1A", "sidebar-2":"#13302A", "sidebar-text":"#E7EFEA", "sidebar-muted":"#8FA89C"
  },
  fontFamily:{ display:["Space Grotesk"], body:["Inter"], mono:["JetBrains Mono"] },
  borderRadius:{ DEFAULT:"0.5rem", lg:"0.5rem", xl:"0.75rem", "2xl":"1rem", full:"9999px" }
}}}
"""

HEAD = """<!DOCTYPE html><html class="light" lang="en"><head>
<meta charset="utf-8"/><meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{title} — CDF Integrity</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap" rel="stylesheet"/>
<script>{tw}</script>
<style>
 body{{font-family:Inter}} h1,h2,h3,.disp{{font-family:'Space Grotesk'}} .mono{{font-family:'JetBrains Mono'}}
 .material-symbols-outlined{{font-variation-settings:'FILL' 0,'wght' 400,'GRAD' 0,'opsz' 24;vertical-align:middle}}
 .seal-ring{{animation:spin 26s linear infinite}} @keyframes spin{{to{{transform:rotate(360deg)}}}}
 .zpulse{{transform-box:fill-box;transform-origin:center;animation:zp 2.2s ease-out infinite}}
 @keyframes zp{{0%{{transform:scale(.7);opacity:.5}}70%{{transform:scale(1.9);opacity:0}}100%{{opacity:0}}}}
 svg a{{cursor:pointer}} svg a:hover circle{{fill-opacity:1}}
</style></head>
<body class="bg-surface text-on-surface">{body}</body></html>"""

def ico(n, cls=""): return f'<span class="material-symbols-outlined {cls}">{n}</span>'
def page(title, body): return HEAD.format(title=title, tw=TW_CONFIG, body=body)
def linkwrap(href, html): return f'<a href="{href}" class="block">{html}</a>'

# ---- real Zambia choropleth (shared) ----
ZPATH = open(os.path.join(HERE,"..","assets","zambia_path.txt"),encoding="utf-8").read().strip()
# (name, x, y, risk0-100) — positions inside the 1000x800 viewBox of the real outline
CITIES = [("Lusaka",560,592,82),("Kafue",548,632,71),("Ndola",560,402,38),("Kitwe",520,390,33),
          ("Solwezi",360,382,46),("Mansa",590,300,29),("Chinsali",690,332,57),("Chipata",792,470,34),
          ("Mongu",225,520,26),("Livingstone",448,735,21),("Milenge",612,320,88),("Kabwe",520,470,40)]
def riskcol(s): return "#B91C1C" if s>=70 else ("#B45309" if s>=40 else "#138636")
def zambia_map(markers=CITIES, link="#", controls=False, h="h-72"):
    dots=""
    for name,x,y,s in markers:
        c=riskcol(s); r=7+s/10.0
        pulse=' class="zpulse"' if s>=70 else ''
        dots += (f'<a href="{link}">'
                 f'<circle cx="{x}" cy="{y}" r="{r+6}" fill="{c}" fill-opacity="0.16"{pulse}/>'
                 f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" fill-opacity="0.92" stroke="#fff" stroke-width="2.5">'
                 f'<title>{name} — risk {s}/100</title></circle></a>')
    ctrl=("" if not controls else
        '<div class="absolute bottom-4 right-4 flex flex-col gap-2">'
        + ''.join(f'<button class="bg-card border border-outline-variant w-9 h-9 rounded-lg flex items-center justify-center shadow-sm hover:bg-surface-2">{ico(i)}</button>' for i in ["add","remove","my_location"])
        + '</div>')
    legend=('<div class="absolute top-4 left-4 bg-card/90 backdrop-blur border border-outline-variant rounded-lg px-3 py-2 flex items-center gap-3 text-[11px] font-semibold">'
        '<span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full" style="background:#138636"></span>Low</span>'
        '<span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full" style="background:#B45309"></span>Medium</span>'
        '<span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full" style="background:#B91C1C"></span>High</span></div>')
    return (f'<div class="relative {h} rounded-lg bg-surface-2 overflow-hidden border border-outline-variant">'
        f'<svg viewBox="0 0 1000 800" class="w-full h-full" preserveAspectRatio="xMidYMid meet">'
        f'<path d="{ZPATH}" fill="#0E5C46" fill-opacity="0.07" stroke="#0E5C46" stroke-opacity="0.45" stroke-width="2.5"/>'
        f'{dots}</svg>{legend}{ctrl}</div>')

def barchart(rows, unit="%"):  # rows = [(label, value, color)]
    out=""
    for label,val,c in rows:
        out+=(f'<div class="flex items-center gap-3 py-1.5"><span class="text-xs w-32 shrink-0 text-on-surface-variant">{label}</span>'
              f'<div class="flex-1 h-3 rounded-full bg-surface-2"><div class="h-3 rounded-full" style="width:{val}%;background:{c}"></div></div>'
              f'<span class="mono text-xs w-12 text-right">{val}{unit}</span></div>')
    return f'<div class="py-2">{out}</div>'

def supplier_graph():
    edges=[(300,210,160,110,"#B8762A"),(300,210,150,300,"#B8762A"),(300,210,470,120,"#6f7974"),
           (300,210,460,310,"#6f7974"),(160,110,150,300,"#B8762A"),(160,110,90,210,"#B8762A"),(150,300,90,210,"#B8762A")]
    nodes=[(300,210,26,"#0E5C46","#fff","Tender"),(160,110,20,"#B91C1C","#fff","Supplier A"),
           (150,300,20,"#B91C1C","#fff","Supplier B"),(470,120,18,"#138636","#fff","Supplier C"),
           (460,310,18,"#138636","#fff","Supplier D"),(90,210,16,"#B8762A","#fff","Shared director")]
    e="".join(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" stroke="{col}" stroke-width="{3 if col!="#6f7974" else 1.5}" stroke-opacity="0.7"/>' for a,b,c,d,col in edges)
    nn=""
    for x,y,r,fill,tc,label in nodes:
        nn+=(f'<g><circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="#fff" stroke-width="2"><title>{label}</title></circle>'
             f'<text x="{x}" y="{y+r+13}" text-anchor="middle" font-family="Inter" font-size="12" font-weight="600" fill="#0B1F1A">{label}</text></g>')
    return (f'<div class="relative h-[420px] rounded-lg bg-surface-2 overflow-hidden border border-outline-variant">'
            f'<svg viewBox="0 0 600 420" class="w-full h-full">{e}{nn}</svg>'
            f'<div class="absolute top-3 left-3 bg-card/90 backdrop-blur border border-outline-variant rounded-lg px-3 py-1.5 text-[11px] font-semibold flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full" style="background:#B8762A"></span>copper = shared attribute (flagged)</div></div>')

def linechart(vals, color="#0E5C46", px=210):
    n=len(vals); pts=" ".join(f"{i*(300/(n-1)):.0f},{100-v:.0f}" for i,v in enumerate(vals))
    area="0,100 "+pts+" 300,100"
    dotsv="".join(f'<circle cx="{i*(300/(n-1)):.0f}" cy="{100-v:.0f}" r="2.5" fill="{color}"/>' for i,v in enumerate(vals))
    return (f'<svg viewBox="0 0 300 100" preserveAspectRatio="none" class="w-full" style="height:{px}px">'
            f'<polygon points="{area}" fill="{color}" fill-opacity="0.08"/>'
            f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5" vector-effect="non-scaling-stroke"/>{dotsv}</svg>')

# ---------------- shared chrome ----------------
def public_nav(active=""):
    def dd(label, items):
        rows="".join(f'<a href="{R[k]}" class="block px-3 py-2 rounded-lg text-sm text-on-surface hover:bg-surface-2">{t}</a>' for t,k in items)
        return (f'<div class="relative group">'
                f'<button class="flex items-center gap-1 text-sm text-on-surface-variant hover:text-ink">{label}'
                f'<span class="material-symbols-outlined" style="font-size:16px">expand_more</span></button>'
                f'<div class="absolute left-0 top-full pt-2 hidden group-hover:block z-50">'
                f'<div class="w-56 bg-card border border-outline-variant rounded-xl shadow-lg p-2">{rows}</div></div></div>')
    nav = (dd("Explore",[("National dashboard","P2"),("National map","P3"),("Constituencies","P4"),("Projects","P5"),("Procurement risk","P7")])
           + dd("Data",[("Open data &amp; datasets","P8"),("Public API","P8"),("Public ledger (audit trail)","P10"),("Methodology","P9")])
           + dd("About",[("How it works","P9"),("FAQ","P9"),("Data protection","X6"),("Contact","P9")]))
    return f"""<header class="sticky top-0 z-50 flex justify-between items-center px-12 h-16 bg-card border-b border-outline-variant">
      <a href="{R['P1']}" class="flex items-center gap-2.5"><img src="../assets/coat_of_arms.png" alt="Republic of Zambia" class="h-8 w-8 object-contain"/>
        <span class="disp font-bold tracking-tight">REP. OF ZAMBIA <span class="text-outline font-normal">|</span> LEDGER</span></a>
      <nav class="flex items-center gap-7">{nav}</nav>
      <div class="flex items-center gap-5">
        <a href="{R['O1']}" class="hidden md:flex items-center gap-1.5 text-sm text-on-surface-variant hover:text-ink">{ico('lock')}For officials<span class="material-symbols-outlined" style="font-size:16px">chevron_right</span></a>
        <a href="{R['P6']}" class="bg-primary text-white text-sm font-semibold px-4 py-2 rounded-lg flex items-center gap-2">{ico('shield')}Verify a contract</a>
      </div>
    </header>"""

def sidebar(items, active, brand="SigTrace Oversight"):
    home = "S1" if brand=="System Administration" else "O2"
    foot_key, foot_label, foot_icon = ("S8","View Audit Log","history") if brand=="System Administration" else ("O12","Generate Report","summarize")
    rows=""
    for label,icon,key in items:
        on = label==active
        rows+=f'<a href="{R[key]}" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm {"bg-sidebar-2 text-white font-semibold" if on else "text-sidebar-muted hover:text-white hover:bg-sidebar-2/60"}">{ico(icon)}<span>{label}</span></a>'
    return f"""<aside class="w-[260px] shrink-0 bg-sidebar min-h-screen p-4 flex flex-col gap-1">
      <a href="{R[home]}" class="flex items-center gap-2 px-2 py-3 mb-2"><img src="../assets/coat_of_arms.png" class="h-6 w-6 object-contain"/>
        <span class="text-white disp font-semibold text-sm">{brand}</span></a>
      {rows}
      <div class="mt-auto"><a href="{R[foot_key]}" class="w-full bg-accent text-white text-sm font-semibold px-3 py-2.5 rounded-lg flex items-center justify-center gap-2">{ico(foot_icon)}{foot_label}</a></div>
    </aside>"""

OVS=[("Risk Dashboard","monitoring","O2"),("Contract Risk List","table_rows","O3"),("Ghost-Project Queue","report","O6"),
     ("Supplier Network","hub","O5"),("Disbursement Explorer","compare_arrows","O7"),("Cases","folder_open","O10"),
     ("Verify Document","fact_check","O9"),("Verification Review","how_to_reg","O8"),("Analytics","insights","O11"),
     ("Reports","summarize","O12"),("Notifications","notifications","O13"),("Admin","settings","S1")]
ADM=[("Admin Home","dashboard","S1"),("Users & Roles","group","S2"),("Check Weights","tune","S3"),("Thresholds","speed","S4"),
     ("Ingestion","cloud_sync","S5"),("Ledger & Nodes","lan","S6"),("Institutions","account_balance","S7"),
     ("Audit Log","history","S8"),("Notifications","notifications","S9"),("← Oversight Console","arrow_back","O2")]

def topbar(title, sub, right=""):
    return f"""<div class="flex items-end justify-between mb-6"><div>
      <h1 class="disp text-2xl font-bold text-ink">{title}</h1>
      <p class="text-sm text-on-surface-variant mt-1">{sub}</p></div><div class="flex gap-2">{right}</div></div>"""

def kpi(label,val,sub="",accent="ink"):
    return f"""<div class="bg-card border border-outline-variant rounded-xl p-4 h-full hover:border-primary transition-colors">
      <p class="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">{label}</p>
      <p class="disp text-2xl font-bold text-{accent} mt-1">{val}</p>
      <p class="text-xs text-on-surface-variant mt-0.5">{sub}</p></div>"""

def card(title, inner, extra=""):
    head=f'<div class="flex items-center justify-between mb-4"><h3 class="disp font-semibold text-ink">{title}</h3>{extra}</div>' if title else ""
    return f'<div class="bg-card border border-outline-variant rounded-xl p-5">{head}{inner}</div>'

def riskbadge(s):
    c="risk-high" if s>=70 else ("risk-mid" if s>=40 else "risk-low")
    return f'<span class="mono text-white text-xs font-semibold px-2 py-0.5 rounded bg-{c}">{s}</span>'

def btn(t, kind="primary", icon="", href=None):
    base="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2"
    sty={"primary":"bg-primary text-white","accent":"bg-accent text-white",
         "secondary":"border border-accent text-accent","ghost":"text-ink hover:bg-surface-2",
         "danger":"bg-danger text-white"}[kind]
    inner=f'{ico(icon) if icon else ""}{t}'
    if href: return f'<a href="{href}" class="{base} {sty}">{inner}</a>'
    return f'<button class="{base} {sty}">{inner}</button>'

def field(label, ph="", val="", type_="text"):
    return f"""<label class="block mb-3"><span class="block text-xs font-semibold text-on-surface-variant mb-1">{label}</span>
      <input type="{type_}" placeholder="{ph}" value="{val}" class="w-full rounded-lg border border-outline-variant bg-card px-3 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary"/></label>"""

def table(cols, rows):
    th="".join(f'<th class="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-2 px-3">{c}</th>' for c in cols)
    body=""
    for i,r in enumerate(rows):
        tds="".join(f'<td class="py-2.5 px-3 text-sm">{c}</td>' for c in r)
        body+=f'<tr class="{"bg-surface-2/40" if i%2 else ""} border-b border-outline-variant/60 hover:bg-surface-2/70">{tds}</tr>'
    return f'<div class="overflow-x-auto"><table class="w-full"><thead><tr class="border-b border-outline">{th}</tr></thead><tbody>{body}</tbody></table></div>'

def seal(ok=True):
    col="primary" if ok else "danger"
    label="VERIFIED ON LEDGER" if ok else "NOT VERIFIED"
    inner = ('<img src="../assets/coat_of_arms.png" class="h-16 w-16 object-contain"/>' if ok
             else '<span class="material-symbols-outlined text-danger" style="font-size:46px">gpp_bad</span>')
    return f"""<div class="flex flex-col items-center text-center gap-2">
      <div class="relative w-32 h-32 rounded-full border-4 border-{('accent' if ok else 'danger')} flex items-center justify-center bg-{('primary' if ok else 'danger')}/5">
        {inner}</div>
      <p class="text-[11px] font-bold tracking-widest text-{col}">{label} &middot; REPUBLIC OF ZAMBIA</p>
      <p class="mono text-xs text-on-surface-variant">sha256 0x{'a1b2…9f' if ok else 'd4e5…0c'}</p>
      <p class="mono text-[11px] text-on-surface-variant">tx 0x7f2a… · 2026-06-01</p></div>"""

def shell(title, sub, items, active, body, brand="SigTrace Oversight", topright=""):
    return page(title, f'<div class="flex">{sidebar(items,active,brand)}<main class="flex-1 p-10 bg-surface min-h-screen">{topbar(title,sub,topright)}{body}</main></div>')

def pub(title, body):  # public page wrapper
    return page(title, public_nav("")+f'<main class="max-w-[1200px] mx-auto px-12 py-10">{body}</main>')

def bottomnav(active):
    items=[("Home","home","M2"),("Capture","add_a_photo","M3"),("Submissions","sync","M5"),("Confirm","fact_check","M7"),("Profile","person","M8")]
    cells=""
    for label,icon,key in items:
        on = key==active
        cells+=f'<a href="{R[key]}" class="flex-1 flex flex-col items-center gap-0.5 py-2 text-[10px] {"text-primary font-semibold" if on else "text-on-surface-variant"}">{ico(icon)}<span>{label}</span></a>'
    return f'<div class="border-t border-outline-variant flex bg-card">{cells}</div>'

def phone(title, inner, footer="", tab=None):  # mobile frame; tab => bottom nav
    nav = bottomnav(tab) if tab else ""
    return page(title, f"""<div class="min-h-screen bg-surface-2 flex items-center justify-center py-8">
      <div class="w-[380px] h-[760px] bg-card rounded-[2rem] border-4 border-ink overflow-hidden flex flex-col shadow-xl">
        <div class="bg-primary text-white px-4 py-3 flex items-center gap-2"><span class="material-symbols-outlined">eco</span><span class="disp font-semibold">CDF Pulse</span><span class="ml-auto text-xs">{title}</span></div>
        <div class="flex-1 overflow-y-auto p-4">{inner}</div>{footer}{nav}</div></div>""")

# =================================================================== SCREENS
S = {}

# ---- PUBLIC ----
S["P2_dashboard"] = pub("National Dashboard", topbar("National CDF Dashboard","Top-line oversight across all 156 constituencies. Public, aggregated, tamper-evident.",
    right=btn("Open the map","secondary","map",href=R["P3"]))+
  f'<div class="grid grid-cols-4 gap-4 mb-6">'
    + linkwrap(R["P4"],kpi("Total allocation","K 1.6 bn","FY2026"))
    + linkwrap(R["P5"],kpi("Projects tracked","8,742","across 156 constituencies","ink"))
    + linkwrap(R["P5"],kpi("Verified on ledger","61%","5,332 projects","risk-low"))
    + linkwrap(R["P7"],kpi("Flagged for review","8.2%","risk signals only","accent")) + '</div>'+
  f'<div class="grid grid-cols-3 gap-6"><div class="col-span-2">'
    + card("Constituency risk heat-map", zambia_map(link=R["P4"]), extra=btn("Open full map","ghost","open_in_full",href=R["P3"]))
    + '</div><div>'
    + card("Recently verified","".join(f'<a href=\"'+R["P5"]+f'\" class=\"flex items-center gap-2 py-2 border-b border-outline-variant/60 last:border-0\"><span class=\"material-symbols-outlined text-risk-low\" style=\"font-size:18px\">verified</span><div><p class=\"text-sm font-semibold\">Project #{i}</p><p class=\"text-xs text-on-surface-variant\">Constituency {i} &middot; verified</p></div></a>' for i in range(1,5)))
    + '</div></div>')

S["P7_procurement_risk"] = pub("Procurement Risk", topbar("Procurement Risk Overview","Aggregated, de-identified integrity signals — not determinations of wrongdoing.")+
  f'<div class="grid grid-cols-3 gap-4 mb-6">{kpi("Contracts analysed","12,480")}{kpi("Flagged rate","8.2%","","accent")}{kpi("Average risk","31 / 100","","risk-low")}</div>'+
  f'<div class="grid grid-cols-2 gap-6">{card("Anomaly rate by sector", barchart([("Works",62,"#B91C1C"),("Consultancy",41,"#B45309"),("Goods",24,"#138636"),("Services",18,"#138636")]))}{card("Risk by procuring entity",barchart([("Entity A",78,"#B8762A"),("Entity B",64,"#B8762A"),("Entity C",47,"#B8762A"),("Entity D",33,"#B8762A"),("Entity E",21,"#B8762A")],unit=""))}</div>'+
  f'<div class="mt-6">{card("Methodology", "<p class=\'text-sm text-on-surface-variant\'>How these signals are computed is explained in the public methodology.</p>"+btn("Read the methodology","secondary","menu_book",href=R["P9"]))}</div>')

S["P8_open_data"] = pub("Open Data", topbar("Open Data","Download the underlying aggregated datasets, or use the public API.")+
  card("", table(["Dataset","Description","Format","Updated","Download"],[
    ["Constituency summaries","Allocation, projects, verification status","CSV · JSON","2026-06-01",btn("Download","secondary","download")],
    ["Procurement risk (aggregate)","De-identified risk by entity & sector","CSV","2026-06-01",btn("Download","secondary","download")],
    ["Verified projects","Public project + evidence index","JSON","2026-05-30",btn("Download","secondary","download")]]))+
  f'<div class="mt-6">{card("Public API","<p class=\'text-sm text-on-surface-variant mb-3\'>Programmatic access to the public tier. See the API documentation.</p>"+btn("API documentation","secondary","api",href=R["P9"]))}</div>')

S["P9_about"] = pub("About & Methodology", topbar("How it works","Plain-language methodology, the eight checks, and our commitments.")+
  f'<div class="grid grid-cols-2 gap-6">{card("The eight integrity checks","<ol class=\'text-sm text-on-surface-variant space-y-1 list-decimal pl-4\'><li>Signing completeness</li><li>Standstill compliance</li><li>Stage time-gap</li><li>Document forensics</li><li>Supplier network</li><li>Score variance</li><li>Amendment value</li><li>Debarment cross-reference</li></ol>")}{card("Our commitment","<p class=\'text-sm text-on-surface-variant\'>Every output is a <b>risk signal requiring review</b>, never a determination of wrongdoing. Personal data stays off-chain; only hashes are anchored.</p>")}</div>'+
  f'<div class="mt-6">{card("FAQ","<div class=\'text-sm text-on-surface-variant space-y-2\'><p>▸ Why two blockchains?</p><p>▸ Is this legally admissible?</p><p>▸ How is my data protected?</p></div>"+"<div class=\'mt-3\'>"+btn("Verify a contract now","primary","shield",href=R["P6"])+"</div>")}</div>')

def ledger_event(icon, col, title, meta):
    return (f'<div class="flex items-start gap-3 py-3 border-b border-outline-variant/60 last:border-0">'
            f'<span class="material-symbols-outlined text-{col}" style="font-size:20px">{icon}</span>'
            f'<div class="flex-1"><p class="text-sm font-semibold">{title}</p>'
            f'<p class="mono text-[11px] text-on-surface-variant">{meta}</p></div>'
            f'<span class="mono text-[11px] text-on-surface-variant">just now</span></div>')

S["P10_audit_trail"] = pub("Public Audit Trail", topbar("Public Audit Trail · Live Ledger",
    "Every anchor, verification and flag, in the order it happened. Tamper-evident and public.",
    right=btn("Verify a contract","secondary","shield",href=R["P6"]))+
  f'<div class="grid grid-cols-3 gap-4 mb-6">{kpi("Events today","1,284","anchors + verifications")}{kpi("Last block","#48,210","Hyperledger Fabric","ink")}{kpi("Anchor backlog","0","fully synced","risk-low")}</div>'+
  f'<div class="grid grid-cols-3 gap-6"><div class="col-span-2">'+
    card("Live ledger feed",
      ledger_event("anchor","primary","Contract anchored","0xa1b2…9f · ocds-zm-000123 · Hyperledger Fabric")
      + ledger_event("verified","risk-low","Project verified · Milenge","3 confirmations · IPFS Qm…f1")
      + ledger_event("gpp_maybe","risk-high","Ghost-project flag · Kafue","disbursed, unverified — routed to review")
      + ledger_event("fact_check","accent","Field evidence submitted","-15.41,28.30 · borehole · CDF Pulse")
      + ledger_event("anchor","primary","Audit batch anchored","0x91c4… · 142 actions · Polygon"),
      extra='<span class="flex items-center gap-1.5 text-[11px] font-bold text-risk-low"><span class="w-1.5 h-1.5 rounded-full bg-risk-low"></span>LIVE</span>')
    + '</div><div>'+
    card("What is this?","<p class='text-sm text-on-surface-variant mb-3'>The ledger records a hash of every contract and confirmation. Records cannot be altered retroactively without a public, detectable trail.</p>"+btn("How it works","secondary","menu_book",href=R["P9"]))
    + '</div></div>')

# ---- OVERSIGHT ----
S["O1_login"] = page("Officials Portal — SigTrace Oversight", f"""<div class="min-h-screen grid grid-cols-1 lg:grid-cols-2">
  <!-- LEFT: officials-tailored hero (separate from the public landing) -->
  <div class="bg-ink text-white p-12 flex flex-col justify-between min-h-screen">
    <div class="flex items-center gap-2.5"><img src="../assets/coat_of_arms.png" class="h-8 w-8 object-contain"/>
      <span class="disp font-bold tracking-tight">SigTrace <span class="text-white/40 font-normal">|</span> Oversight &amp; Audit Console</span></div>
    <div class="max-w-md">
      <span class="inline-flex items-center gap-1.5 text-[11px] font-bold tracking-widest text-accent bg-accent/15 px-3 py-1 rounded-full"><span class="material-symbols-outlined" style="font-size:14px">lock</span>RESTRICTED · AUTHORISED INSTITUTIONS ONLY</span>
      <h1 class="disp text-4xl font-bold leading-tight mt-5">The officials' portal for<br>contract &amp; CDF oversight</h1>
      <p class="text-white/70 mt-4">Investigate procurement risk signals, confirm field evidence, manage cases and anchor audit actions to the ledger. Access is institutional, MFA-protected and fully audit-logged.</p>
      <div class="flex flex-wrap gap-2 mt-6">
        {''.join(f'<span class="text-xs font-semibold bg-white/10 border border-white/15 px-3 py-1.5 rounded-lg">{i}</span>' for i in ["Office of the Auditor General","Anti-Corruption Commission","ZPPA"])}
      </div>
    </div>
    <div class="text-xs text-white/50 space-y-1">
      <p>This is a separate, restricted system from the public portal.</p>
      <a href="{R['M1']}" class="text-white/80 hover:text-white font-semibold inline-flex items-center gap-1">Institutional confirmer? Open the CDF Pulse field app<span class="material-symbols-outlined" style="font-size:16px">arrow_forward</span></a>
      <a href="{R['P1']}" class="block text-white/80 hover:text-white font-semibold">Looking for public information? Go to the public portal →</a>
    </div>
  </div>
  <!-- RIGHT: sign-in -->
  <div class="bg-surface flex items-center justify-center p-8 min-h-screen">
    <div class="w-[380px] bg-card rounded-2xl p-7 border border-outline-variant">
      <h2 class="disp font-bold text-ink mb-1">Sign in</h2>
      <p class="text-xs text-on-surface-variant mb-5">Use your institutional credentials.</p>
      {field("Institutional email","officer@oag.gov.zm")}{field("Password","••••••••","","password")}
      <div class="mt-1">{btn("Continue","primary",href=R["O2"])}</div>
      <div class="mt-5 pt-4 border-t border-outline-variant"><p class="text-xs text-on-surface-variant mb-2">Two-factor authentication</p>
        <div class="flex gap-2 justify-between mono">{''.join('<input class="w-10 h-12 text-center rounded-lg border border-outline-variant" maxlength="1"/>' for _ in range(6))}</div>
        <div class="mt-3">{btn("Verify &amp; sign in","accent",href=R["O2"])}</div></div>
      <p class="text-[11px] text-on-surface-variant mt-4 flex items-center gap-1.5"><span class="material-symbols-outlined text-risk-low" style="font-size:15px">verified_user</span>Every sign-in and action is recorded in the immutable audit log.</p>
      <p class="text-xs text-center text-on-surface-variant mt-3"><a href="{R['P1']}" class="hover:text-ink">← Back to public portal</a></p>
    </div>
  </div></div>""")

S["O2_dashboard"] = shell("Risk Dashboard","System-wide integrity signals across all sources",OVS,"Risk Dashboard",
  f'<div class="grid grid-cols-4 gap-4 mb-6">'
    + linkwrap(R["O3"],kpi("Open flags","37","needs review","accent"))
    + linkwrap(R["O3"],kpi("High-risk contracts","12","≥ 70 score","risk-high"))
    + linkwrap(R["O6"],kpi("Ghost signals","5","overdue delivery","accent"))
    + linkwrap(R["O10"],kpi("Open cases","8","2 escalated","ink")) + '</div>'+
  f'<div class="grid grid-cols-3 gap-6 mb-6"><div class="col-span-2">'
    + card("Constituency risk heat-map", zambia_map(link=R["O4"], controls=True), extra='<span class="text-xs text-on-surface-variant">click a marker → contract</span>')
    + '</div><div>'
    + card("Alert feed","".join(f'<a href=\"{href}\" class=\"flex items-center gap-2 py-2.5 border-b border-outline-variant/60 last:border-0\"><span class=\"material-symbols-outlined text-{c}\" style=\"font-size:18px\">{ic}</span><p class=\"text-sm flex-1\">{t}</p></a>' for t,ic,c,href in [("High-risk contract flagged (88)","priority_high","risk-high",R["O4"]),("Ghost signal — Milenge","report","accent",R["O6"]),("Confirmation requested #214","fact_check","info",R["O8"]),("Case #001 assigned","folder","primary",R["O10"])]))
    + '</div></div>'+
  card("Recent high-risk contracts", table(["OCID","Entity","Risk","Flags","Anchor",""],
    [[f'<a href="{R["O4"]}" class="mono text-primary hover:underline">ocds-zm-0001{n}</a>',e,riskbadge(s),f,'<span class="text-risk-low">✓</span>',btn("Open","ghost","chevron_right",href=R["O4"])]
     for n,e,s,f in [(23,"Lusaka CC",88,"2 flags"),(24,"Kafue DC",74,"1 flag"),(25,"Ndola CC",69,"1 flag"),(26,"Kitwe CC",41,"—")]]),
    extra=btn("View all contracts","secondary","table_rows",href=R["O3"])),
  topright=btn("Export","secondary","download",href=R["O12"])+btn("Run monitor","accent","play_arrow",href=R["O6"]))

S["O3_contract_list"] = shell("Contract Risk List","All analysed contracts, sortable by risk",OVS,"Contract Risk List",
  card("", table(["OCID","Procuring entity","Sector","Value","Risk","Flags","Anchor","Action"],
    [[f'<a href="{R["O4"]}" class="mono text-primary hover:underline">ocds-zm-0001{n}</a>',e,sec,f'<span class="mono">K {v}</span>',riskbadge(s),fl,'<span class="text-risk-low">✓</span>',btn("Review","ghost","chevron_right",href=R["O4"])]
     for n,e,sec,v,s,fl in [(23,"Lusaka CC","Works","1.2m",88,"2"),(24,"Kafue DC","Goods","430k",74,"1"),(25,"Ndola CC","Works","980k",69,"1"),(26,"Kitwe CC","Services","210k",41,"—"),(27,"Chipata MC","Works","760k",33,"—"),(28,"Solwezi MC","Goods","145k",22,"—")]]),
    extra='<div class="flex gap-2"><input placeholder="Search OCID / entity" class="rounded-lg border border-outline-variant px-3 py-1.5 text-sm"/>'+btn("Filter","secondary","filter_list")+'</div>'))

S["O4_contract_detail"] = shell("Contract Detail","Anomaly review · OCID ocds-zm-000123",OVS,"Contract Risk List",
  f"""<div class="mb-4 text-sm text-on-surface-variant"><a href="{R['O3']}" class="hover:text-ink">← Contract risk list</a></div>
  <div class="grid grid-cols-3 gap-6">
    <div class="col-span-2 space-y-4">
      <div class="bg-card border border-outline-variant rounded-xl p-4 flex items-center justify-between">
        <div><p class="mono text-sm">ocds-zm-000123</p><p class="text-xs text-on-surface-variant">Lusaka CC · Works · <span class="mono">K 1,204,987.89</span> · Award→Signing 9 days</p></div>
        <div class="text-right"><p class="disp text-3xl font-bold text-risk-high">88</p><p class="text-[11px] text-risk-high font-semibold">HIGH — review</p></div></div>
      {card("Eight integrity checks", ''.join(f'<div class="flex items-center justify-between py-2 border-b border-outline-variant/60 last:border-0"><span class="text-sm">{n}</span><span class="text-xs font-semibold text-{c}">{ {"risk-high":"FLAG","risk-mid":"FLAG","risk-low":"OK"}[c] }</span></div>' for n,c in [("1 Signing completeness","risk-high"),("2 Standstill (<14d)","risk-high"),("3 Stage time-gap","risk-mid"),("4 Document forensics","risk-low"),("5 Supplier network","risk-mid"),("6 Score variance","risk-low"),("7 Amendment value","risk-low"),("8 Debarment cross-ref","risk-low")]))}
      <div class="flex gap-2">{btn("View supplier network","secondary","hub",href=R["O5"])}{btn("Open document verify","secondary","fact_check",href=R["O9"])}</div>
    </div>
    <div class="space-y-4">{card("Ledger status",seal(True))}{card("Actions", btn("Add to case","secondary","folder",href=R["O10"])+'<div class="h-2"></div>'+btn("Escalate to ACC","accent","priority_high",href=R["O10"])+'<div class="h-2"></div>'+btn("Mark reviewed","ghost","done",href=R["O3"]))}</div>
  </div>""")

S["O5_supplier_network"] = shell("Supplier Network","Related-party analysis for a tender",OVS,"Supplier Network",
  f'<div class="grid grid-cols-3 gap-6"><div class="col-span-2">{card("Network graph",supplier_graph())}</div><div>{card("Linked parties","<p class=\'text-sm text-on-surface-variant mb-3\'>Suppliers A &amp; B share a director and phone number (copper links). Flagged for review.</p>"+btn("Back to contract","secondary","arrow_back",href=R["O4"]))}</div></div>')

S["O6_ghost_queue"] = shell("Ghost-Project Queue","Disbursements with no verified completion",OVS,"Ghost-Project Queue",
  card("", table(["Constituency","Project","Disbursed","Date","Overdue","Evidence","Action"],
    [[c,p,f'<span class="mono">K {a}</span>',"2026-…",f'<span class="text-{("risk-high" if o>30 else "risk-mid")} font-semibold">{o}d</span>',e,btn("Open case","ghost","folder",href=R["O10"])]
     for c,p,a,o,e in [("Milenge","Borehole","420,000",45,"none"),("Lusaka C.","Clinic annex","1.2m",12,"partial"),("Kafue","Classroom","730,094",90,"none")]])),
  topright=btn("Run monitor","accent","play_arrow"))

S["O7_mismatch"] = shell("Disbursement Explorer","Match disbursement ↔ contract ↔ completion",OVS,"Disbursement Explorer",
  card("", table(["Constituency","Project","Amount","Clean contract","Verified completion","Status"],
    [["Milenge","Borehole",'<span class="mono">K 420,000</span>',f'<a href="{R["O4"]}" class="text-risk-low">✓</a>',f'<a href="{R["O6"]}" class="text-risk-high">✗</a>','<span class="text-risk-high font-semibold">Mismatch</span>'],
     ["Lusaka C.","Clinic",'<span class="mono">K 1.2m</span>','<span class="text-risk-low">✓</span>','<span class="text-risk-low">✓</span>','<span class="text-risk-low font-semibold">Accountable</span>']])))

S["O8_verify_review"] = shell("Verification Review","Field submissions awaiting confirmation",OVS,"Verification Review",
  f'<div class="grid grid-cols-2 gap-4">'+''.join(card("", f'<div class="flex gap-3"><div class="w-24 h-24 rounded-lg bg-surface-2 shrink-0"></div><div class="flex-1"><p class="text-sm font-semibold">Project #{i}</p><p class="mono text-xs text-on-surface-variant">-15.41, 28.30 · 2026-05-3{i}</p><div class="flex gap-2 mt-3">{btn("Confirm","primary","check")}{btn("Reject","ghost","close")}</div></div></div>') for i in range(1,5))+'</div>')

S["O9_doc_verify"] = shell("Document Verification","Verify any contract against its anchor",OVS,"Verify Document",
  f'<div class="grid grid-cols-2 gap-6"><div>{card("Verify a document","<div class=\'h-40 rounded-lg border-2 border-dashed border-outline-variant flex items-center justify-center text-on-surface-variant text-sm\'>Drop a contract PDF</div>")}</div><div>{card("Result",seal(True))}</div></div>'+
  f'<div class="mt-6">{card("Recent anchors", table(["OCID","Hash","Tx","Anchored"],[[f"<a href=\""+R["O4"]+"\" class=\"mono text-primary hover:underline\">ocds-…00"+str(i)+"</a>","<span class=\"mono\">0xa1…9f</span>","<span class=\"mono\">0x7f…</span>","2026-06-0"+str(i)] for i in range(1,5)]))}</div>')

S["O10_cases"] = shell("Cases","Investigations & escalations",OVS,"Cases",
  f"""<div class="grid grid-cols-3 gap-6"><div class="col-span-1 space-y-2">{''.join(f'<div class="bg-card border border-outline-variant rounded-xl p-3 {"ring-2 ring-primary" if i==1 else ""}"><p class="text-sm font-semibold">Case #{i:03d}</p><p class="text-xs text-on-surface-variant">Contract ocds-…00{i} · Open</p></div>' for i in range(1,5))}</div>
    <div class="col-span-2">{card("Case #001 — Signing gap, Lusaka CC", '<div class="space-y-3 text-sm"><div class="flex gap-2">'+btn("Open contract","secondary","description",href=R["O4"])+btn("Escalate to ACC","accent","priority_high")+'</div><div class="border-l-2 border-outline-variant pl-3 space-y-2 text-on-surface-variant"><p>2026-06-01 · Opened from contract risk list.</p><p>2026-06-02 · Note added by officer.</p></div><textarea class="w-full rounded-lg border border-outline-variant p-2" placeholder="Add a note…"></textarea>'+btn("Save note","primary","save")+'</div>')}</div></div>""")

S["O11_analytics"] = shell("Analytics","Trends & comparisons",OVS,"Analytics",
  f'<div class="grid grid-cols-2 gap-6">{card("Anomaly rate over time (12 mo)",linechart([22,28,25,31,34,30,38,41,37,44,40,46]))}{card("Entity comparison",barchart([("Lusaka CC",72,"#B8762A"),("Kafue DC",58,"#B8762A"),("Ndola CC",46,"#B8762A"),("Kitwe CC",34,"#B8762A"),("Chipata MC",27,"#B8762A")],unit=""))}</div>')

S["O12_reports"] = shell("Reports & Exports","Generate restricted reports (audit-logged)",OVS,"Reports",
  f'<div class="grid grid-cols-2 gap-6"><div>{card("New report", field("Scope","High-risk contracts")+field("Date range","2026-01-01 → 2026-06-01")+field("Format","PDF")+btn("Generate","primary","summarize"))}</div><div>{card("History", table(["Report","Date","Format",""],[["High-risk Q2","2026-06-01","PDF",btn("Download","ghost","download")]]))}</div></div>')

S["O13_notifications"] = shell("Notifications","Alerts across the system",OVS,"Notifications",
  card("", ''.join(f'<a href="{href}" class="flex items-center gap-3 py-3 border-b border-outline-variant/60 hover:bg-surface-2/60"><span class="material-symbols-outlined text-{c}">{ic}</span><div class="flex-1"><p class="text-sm font-semibold">{t}</p><p class="text-xs text-on-surface-variant">2 hours ago</p></div><span class="text-xs text-primary">view →</span></a>'
    for t,ic,c,href in [("New high-risk contract flagged (88/100)","priority_high","risk-high",R["O4"]),("Ghost-project signal raised — Milenge","report","accent",R["O6"]),("Confirmation requested on submission #214","fact_check","info",R["O8"]),("Case #001 assigned to you","folder","primary",R["O10"])])))

# ---- ADMIN ----
S["S1_admin_home"] = shell("Admin Home","System health & operations",ADM,"Admin Home",
  f'<div class="grid grid-cols-3 gap-4 mb-6">'+''.join(kpi(n,v,"",c) for n,v,c in [("Ingestion pipeline","Healthy","risk-low"),("Fabric peers","3 / 3","risk-low"),("Polygon RPC","Online","risk-low"),("IPFS gateway","Degraded","risk-mid"),("API latency","82 ms","risk-low"),("Database","Online","risk-low")])+'</div>'+
  f'<div class="grid grid-cols-2 gap-6">{card("Quick links","<div class=\'flex gap-2 flex-wrap\'>"+btn("Users","secondary","group",href=R["S2"])+btn("Weights","secondary","tune",href=R["S3"])+btn("Ingestion","secondary","cloud_sync",href=R["S5"])+btn("Ledger","secondary","lan",href=R["S6"])+"</div>")}{card("Recent admin activity","<p class=\'text-sm text-on-surface-variant\'>Weights v4 saved · user added · ingestion run #58 ok</p>"+"<div class=\'mt-3\'>"+btn("Open audit log","ghost","history",href=R["S8"])+"</div>")}</div>',
  brand="System Administration")

S["S2_users"] = shell("Users & Roles","Manage accounts and access",ADM,"Users & Roles",
  card("", table(["Name","Email","Role","Institution","MFA","Status"],
    [["A. Banda","a@oag.gov.zm","Oversight Officer","OAG","✓","Active"],["C. Phiri","c@acc.gov.zm","Analyst","ACC","✓","Active"],["Admin","admin@…","System Admin","—","✓","Active"]]),
    extra=btn("Add user","primary","person_add")), brand="System Administration")

S["S3_weights"] = shell("Check Weights","Calibrate the eight checks (with OAG)",ADM,"Check Weights",
  card("Anomaly check weights", ''.join(f"""<div class="flex items-center gap-4 py-2"><span class="text-sm w-56">{n}</span>
    <div class="flex-1 h-2 rounded-full bg-surface-2"><div class="h-2 rounded-full bg-primary" style="width:{w*3}%"></div></div>
    <span class="mono text-sm w-10 text-right">{w}</span></div>""" for n,w in [("1 Signing completeness",25),("2 Standstill",20),("3 Stage time-gap",12),("4 Document forensics",12),("5 Supplier network",12),("6 Score variance",8),("7 Amendment value",8),("8 Debarment",18)])+f'<div class="mt-4 flex items-center justify-between"><span class="text-xs text-on-surface-variant">Calibrated with the Office of the Auditor General · v4</span>{btn("Save weights","primary","save")}</div>'), brand="System Administration")

S["S4_thresholds"] = shell("Thresholds","Statutory & risk thresholds",ADM,"Thresholds",
  f'<div class="grid grid-cols-2 gap-6"><div>{card("Thresholds", field("Standstill minimum (days)","","14")+field("Amendment cap (%)","","15")+field("High-risk escalation score","","70")+field("Ghost-project window (days)","","90")+btn("Save","primary","save"))}</div><div>{card("Notes","<p class=\'text-sm text-on-surface-variant\'>Standstill and amendment cap derive from the Public Procurement Act No. 8 of 2020. Escalation and window are calibrated with the OAG.</p>")}</div></div>', brand="System Administration")

S["S5_ingestion"] = shell("Ingestion","OCDS pipeline runs",ADM,"Ingestion",
  card("", table(["Run","Started","Records in","Loaded","Errors","Status"],
    [[f"#{n}",f"2026-06-0{n%9}","4,210","4,210","0",'<span class="text-risk-low">OK</span>'] for n in range(58,54,-1)]),
    extra=btn("Run ingestion","accent","play_arrow")), brand="System Administration")

S["S6_ledger"] = shell("Ledger & Node Governance","Fabric & Polygon status",ADM,"Ledger & Nodes",
  f'<div class="grid grid-cols-2 gap-6">{card("Hyperledger Fabric","<div class=\'text-sm space-y-1\'><p>Peer OAG · <span class=\'text-risk-low\'>online</span></p><p>Peer ZPPA · <span class=\'text-risk-low\'>online</span></p><p>Peer ACC · <span class=\'text-risk-low\'>online</span></p><p class=\'mono text-xs text-on-surface-variant\'>last block #48,210</p></div>")}{card("Polygon","<div class=\'text-sm space-y-1\'><p>Contract <span class=\'mono text-xs\'>0x8fa3…</span></p><p>Signer · <span class=\'text-risk-low\'>ready</span></p><p>Anchor backlog · 0</p></div>")}</div>', brand="System Administration")

S["S7_institutions"] = shell("Institutions","Data-sharing agreements",ADM,"Institutions",
  card("", table(["Institution","Type","Agreement","Status"],
    [["Office of the Auditor General","Oversight","DSA-2026-01","Active"],["Anti-Corruption Commission","Enforcement","DSA-2026-02","Active"],["ZPPA","Regulator","DSA-2026-03","Active"]]),
    extra=btn("Add institution","primary","add")), brand="System Administration")

S["S8_audit"] = shell("Audit Log","Immutable, anchored action log",ADM,"Audit Log",
  f'<div class="mb-4 text-xs text-on-surface-variant">Latest batch anchored: <span class="mono">0x91c4…</span> · 2026-06-02</div>'+
  card("", table(["Actor","Action","Target","When"],
    [["a@oag.gov.zm","viewed contract","ocds-…123","12:04"],["admin","saved weights v4","config","11:50"],["c@acc.gov.zm","exported report","Q2","11:20"]])), brand="System Administration")

S["S9_notif_config"] = shell("Notification Config","Alert rules & templates",ADM,"Notifications",
  f'<div class="grid grid-cols-2 gap-6">{card("Rules","<div class=\'text-sm space-y-2\'><p>High-risk ≥70 → officers · email + in-app</p><p>Ghost-project signal → OAG queue</p><p>Confirmation requested → confirmer</p></div>")}{card("Template editor","<textarea class=\'w-full h-40 rounded-lg border border-outline-variant p-2 text-sm\'>A new high-risk contract {{ocid}} scored {{score}}.</textarea>")}</div>', brand="System Administration")

# ---- PULSE (mobile) — flow: M1→M2→M3→M4→M5→M6 ; M7 confirm inbox ; M8 profile ----
def pcard(inner, href=None):
    block=f'<div class="bg-card border border-outline-variant rounded-xl p-3 mb-3">{inner}</div>'
    return f'<a href="{href}" class="block">{block}</a>' if href else block

# M1 is the WEB interface login for the CDF Pulse PWA (installable web app), responsive — not a phone mock.
_qr = ('<div class="w-24 h-24 rounded-lg bg-white border border-white/20 grid grid-cols-5 grid-rows-5 gap-0.5 p-1.5 shrink-0">'
       + ''.join(f'<span class="rounded-[1px] {"bg-ink" if (i*7+3)%5 and i%3 else "bg-transparent"}"></span>' for i in range(25)) + '</div>')
S["M1_login"] = page("CDF Pulse — Sign in", f"""<div class="min-h-screen grid grid-cols-1 lg:grid-cols-2">
  <!-- LEFT: Pulse field-app hero -->
  <div class="bg-primary text-white p-12 flex flex-col justify-between min-h-screen">
    <div class="flex items-center gap-2.5"><img src="../assets/coat_of_arms.png" class="h-8 w-8 object-contain"/>
      <span class="disp font-bold tracking-tight">CDF Pulse <span class="text-white/50 font-normal">|</span> Field Verification</span></div>
    <div class="max-w-md">
      <span class="inline-flex items-center gap-1.5 text-[11px] font-bold tracking-widest text-white bg-white/15 px-3 py-1 rounded-full">{ico('eco')}COMMUNITY MONITORING · OFFLINE-FIRST</span>
      <h1 class="disp text-4xl font-bold leading-tight mt-5">Capture proof that<br>projects are real</h1>
      <p class="text-white/80 mt-4">Community monitors and institutional confirmers record geo-tagged, timestamped, tamper-evident evidence from the field. Works offline and syncs to the ledger when you're back online.</p>
      <div class="flex items-center gap-4 mt-6 bg-white/10 border border-white/15 rounded-xl p-4">
        {_qr}
        <div><p class="text-sm font-semibold">Install the app</p><p class="text-xs text-white/70">Scan to install CDF Pulse on your phone, or use it right here in your browser.</p></div>
      </div>
    </div>
    <a href="{R['P1']}" class="text-xs text-white/80 hover:text-white inline-flex items-center gap-1">{ico('arrow_back')}Back to public portal</a>
  </div>
  <!-- RIGHT: sign-in -->
  <div class="bg-surface flex items-center justify-center p-8 min-h-screen">
    <div class="w-[380px] bg-card rounded-2xl p-7 border border-outline-variant">
      <h2 class="disp font-bold text-ink mb-1">Sign in</h2>
      <p class="text-xs text-on-surface-variant mb-5">Field monitor or institutional confirmer.</p>
      {field("Phone or credential","+260 …")}
      <div class="my-2">{btn("Send code","primary","sms")}</div>
      <p class="text-xs text-on-surface-variant mb-2">Enter the 6-digit code</p>
      <div class="flex gap-2 justify-between mono mb-3">{''.join('<input class="w-11 h-12 text-center rounded-lg border border-outline-variant" maxlength="1"/>' for _ in range(6))}</div>
      {btn("Verify &amp; continue","accent",href=R["M2"])}
      <p class="text-[11px] text-on-surface-variant mt-4 flex items-center gap-1.5">{ico('smartphone')}This device is bound to your account. Offline grace: 7 days.</p>
    </div>
  </div></div>""")

S["M2_home"] = phone("Home", '<p class="text-xs text-on-surface-variant mb-2">Constituency: Milenge</p>'+''.join(pcard(f'<div class="flex items-center justify-between"><div><p class="text-sm font-semibold">Project #{i}</p><p class="text-xs text-on-surface-variant">Borehole · Active</p></div><span class="material-symbols-outlined text-outline">chevron_right</span></div>', href=R["M3"]) for i in range(1,5)),
  footer=f'<div class="p-3 border-t border-outline-variant">{btn("+ New capture","primary",href=R["M3"])}</div>', tab="M2")

S["M3_capture"] = phone("Capture", '<div class="h-48 rounded-xl bg-ink/90 flex items-center justify-center text-white/60 text-sm mb-3">[ camera viewfinder ]</div>'+
  '<div class="flex items-center gap-2 text-xs text-risk-low mb-1"><span class="material-symbols-outlined" style="font-size:16px">my_location</span><span class="mono">-15.41, 28.30 · locked</span></div>'+
  '<div class="text-xs text-on-surface-variant mb-3">🕑 timestamp auto-captured</div>'+
  field("Category","Borehole")+field("Note","Optional…")+pcard('<div class="flex items-center gap-2 text-xs text-risk-mid"><span class="material-symbols-outlined" style="font-size:16px">wifi_off</span>Offline — will sync</div>'),
  footer=f'<div class="p-3 border-t border-outline-variant">{btn("Submit",None if False else "primary",href=R["M4"])}</div>', tab="M3")

S["M4_review"] = phone("Review", '<div class="h-40 rounded-xl bg-surface-2 mb-3"></div>'+pcard('<p class="mono text-xs">-15.41, 28.30 · 2026-06-02 11:20</p>')+pcard('<p class="text-sm">Category: Borehole</p><p class="text-xs text-on-surface-variant">Note: foundation complete</p>'),
  footer=f'<div class="p-3 border-t border-outline-variant">{btn("Submit submission","primary",href=R["M5"])}</div>')

S["M5_sync"] = phone("My submissions", ''.join(pcard(f'<div class="flex items-center justify-between"><div><p class="text-sm font-semibold">Submission #{i}</p><p class="text-xs text-on-surface-variant">Project #{i}</p></div><span class="text-xs text-{("risk-low" if i<3 else "risk-mid")} font-semibold">{"synced ✓" if i<3 else "pending ⟳"}</span></div>', href=R["M6"]) for i in range(1,6)),
  footer=f'<div class="p-3 border-t border-outline-variant">{btn("Sync now","accent")}</div>', tab="M5")

S["M6_detail"] = phone("Submission", f'<div class="mb-3 text-xs text-on-surface-variant"><a href="{R["M5"]}">← My submissions</a></div>'+'<div class="h-44 rounded-xl bg-surface-2 mb-3"></div>'+pcard('<p class="text-sm font-semibold">Borehole · Milenge</p><p class="mono text-xs text-on-surface-variant">CID Qm…9f</p>')+pcard('<p class="text-sm">Status: confirmed by 2 parties</p><p class="text-xs text-on-surface-variant">Tamper-evident on IPFS</p>'))

S["M7_confirm"] = phone("Confirm", ''.join(pcard(f'<div class="flex gap-2"><div class="w-16 h-16 rounded-lg bg-surface-2 shrink-0"></div><div class="flex-1"><p class="text-sm font-semibold">Submission #{i}</p><p class="mono text-[11px] text-on-surface-variant">-15.4,28.3</p><div class="flex gap-2 mt-2"><button class="text-xs bg-primary text-white px-2 py-1 rounded">Confirm</button><button class="text-xs border border-outline-variant px-2 py-1 rounded">Reject</button></div></div></div>') for i in range(1,4)), tab="M7")

S["M8_profile"] = phone("Profile", pcard('<p class="text-sm font-semibold">A. Monitor</p><p class="text-xs text-on-surface-variant">Milenge · Community monitor</p>')+pcard('<p class="text-sm">Storage & sync settings</p>')+pcard('<p class="text-sm">High-contrast mode</p>')+pcard('<p class="text-sm">Language</p>'),
  footer=f'<div class="p-3 border-t border-outline-variant">{btn("Sign out","ghost",href=R["M1"])}</div>', tab="M8")

# ---- SHARED ----
def centered(title, inner): return page(title, f'<div class="min-h-screen flex items-center justify-center bg-surface-2"><div class="w-[360px] bg-card rounded-2xl p-7 border border-outline-variant">{inner}</div></div>')
S["X1_login"] = centered("Login", '<h2 class="disp font-bold mb-4">Sign in</h2>'+field("Email")+field("Password","","","password")+btn("Sign in","primary",href=R["X2"])+f'<p class="text-xs text-primary mt-3"><a href="{R["X3"]}">Forgot password?</a></p><p class="text-xs text-center text-on-surface-variant mt-4"><a href="{R["P1"]}" class="hover:text-ink">← Back to public portal</a></p>')
S["X2_mfa"] = centered("MFA", '<h2 class="disp font-bold mb-1">Two-factor code</h2><p class="text-xs text-on-surface-variant mb-4">Enter the 6-digit code from your authenticator.</p><div class="flex gap-2 justify-between mono mb-4">'+''.join('<input class="w-11 h-12 text-center rounded-lg border border-outline-variant" maxlength="1"/>' for _ in range(6))+'</div>'+btn("Verify","primary",href=R["O2"]))
S["X3_reset"] = centered("Reset password", '<h2 class="disp font-bold mb-4">Reset password</h2>'+field("New password","","","password")+field("Confirm password","","","password")+'<div class="mb-3 text-xs text-risk-low">Strength: strong</div>'+btn("Set password","primary",href=R["X1"]))
_acct_profile = card("Profile", field("Name", "Frank B.") + field("Email", "frank@example.zm"))
_acct_sessions = card("Active sessions",
    "<div class='text-sm text-on-surface-variant'>Chrome &middot; Lusaka &middot; now<br>Edge &middot; Lusaka &middot; 2 days ago</div>"
    + "<div class='mt-3'>" + btn("Sign out everywhere", "danger") + "</div>")
S["X4_account"] = page("Account", public_nav("")
    + '<main class="max-w-[760px] mx-auto px-12 py-10">'
    + topbar("Account &amp; sessions", "Profile, MFA device and active sessions.")
    + _acct_profile + '<div class="h-4"></div>' + _acct_sessions + '</main>')
S["X5_errors"] = page("Status states", f'<div class="min-h-screen flex items-center justify-center bg-surface-2"><div class="grid grid-cols-2 gap-6">'+''.join(f'<div class="w-72 bg-card border border-outline-variant rounded-2xl p-8 text-center"><span class="material-symbols-outlined text-outline" style="font-size:40px">{ic}</span><h3 class="disp font-bold mt-2">{t}</h3><p class="text-xs text-on-surface-variant mb-3">{d}</p>{btn(b,"secondary",href=R["P1"])}</div>' for t,d,ic,b in [("403 Forbidden","You don't have access.","block","Go back"),("404 Not found","That page doesn't exist.","search_off","Home"),("Something went wrong","Please retry.","error","Retry"),("Offline","You're offline — changes will sync.","wifi_off","Dismiss")])+'</div></div>')
S["X6_consent"] = centered("Data notice", '<h2 class="disp font-bold mb-3">Data protection</h2><p class="text-sm text-on-surface-variant mb-4">We collect only what a report needs. Personal data stays off-chain and can be erased; only cryptographic hashes are anchored to the ledger.</p>'+btn("I understand","primary",href=R["P1"]))

# =================================================================== WRITE
out=HERE
for name, html in S.items():
    open(os.path.join(out, name+".html"), "w", encoding="utf-8").write(html)

# ---------------------------------------------------- index = visual flow map
stitch=[("P1 Landing","../stitch_export/landing_home/screen.png",R["P1"]),
        ("P3 National map","../stitch_export/national_project_map/screen.png",R["P3"]),
        ("P4 Constituency","../stitch_export/constituency_detail/screen.png",R["P4"]),
        ("P5 Project detail","../stitch_export/project_transparency_detail/screen.png",R["P5"]),
        ("P6 Verification portal","../stitch_export/verification_portal/screen.png",R["P6"])]

def node(label, key):
    fn = R[key]
    return f'<a href="{fn}" class="block bg-card border border-outline-variant rounded-lg px-3 py-2 hover:border-primary hover:shadow-sm transition"><span class="text-sm font-semibold">{label}</span><span class="block text-[11px] text-on-surface-variant mono">{key}</span></a>'

def flow_row(label, keys):
    chips=('<span class="text-outline mx-1">→</span>').join(node(k.split("|")[1], k.split("|")[0]) for k in keys)
    return f'<div class="mb-5"><p class="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold mb-2">{label}</p><div class="flex flex-wrap items-center gap-1">{chips}</div></div>'

flows = (
  flow_row("Public · verify a contract", ["P1|Landing","P6|Verify portal","P5|Project detail","P3|National map"])
  + flow_row("Public · explore spending", ["P1|Landing","P2|National dashboard","P3|National map","P4|Constituency","P5|Project"])
  + flow_row("Public · live ledger", ["P1|Landing","P10|Audit trail","P9|How it works"])
  + flow_row("Oversight · flag → case", ["O1|Login","O2|Risk dashboard","O3|Contract list","O4|Contract detail","O10|Cases"])
  + flow_row("Oversight · ghost project", ["O2|Dashboard","O6|Ghost queue","O7|Disbursement","O10|Case"])
  + flow_row("Oversight · confirm field evidence", ["O2|Dashboard","O8|Verification review","O9|Doc verify"])
  + flow_row("Admin", ["S1|Admin home","S3|Weights","S4|Thresholds","S5|Ingestion","S6|Ledger","S8|Audit"])
  + flow_row("CDF Pulse · capture → sync → confirm", ["M1|Login","M2|Home","M3|Capture","M4|Review","M5|Sync","M6|Detail","M7|Confirm"])
)

def group_grid(title, keys):
    cells="".join(node(k.split("|")[1], k.split("|")[0]) for k in keys)
    return f'<h2 class="disp font-semibold text-ink mt-8 mb-3">{title}</h2><div class="grid grid-cols-4 gap-3">{cells}</div>'

inv = (
  group_grid("Public portal (PUB)", ["P1|Landing","P2|National dashboard","P3|National map","P4|Constituency","P5|Project detail","P6|Verify portal","P7|Procurement risk","P8|Open data","P9|About","P10|Audit trail"])
  + group_grid("Oversight console (OVS)", ["O1|Login","O2|Risk dashboard","O3|Contract list","O4|Contract detail","O5|Supplier network","O6|Ghost queue","O7|Disbursement","O8|Verif. review","O9|Doc verify","O10|Cases","O11|Analytics","O12|Reports","O13|Notifications"])
  + group_grid("Admin console (ADM)", ["S1|Admin home","S2|Users","S3|Weights","S4|Thresholds","S5|Ingestion","S6|Ledger","S7|Institutions","S8|Audit","S9|Notif config"])
  + group_grid("CDF Pulse (PWA)", ["M1|Login","M2|Home","M3|Capture","M4|Review","M5|Sync","M6|Detail","M7|Confirm","M8|Profile"])
  + group_grid("Shared (X)", ["X1|Login","X2|MFA","X3|Reset","X4|Account","X5|Status states","X6|Data notice"])
)

stitch_cards="".join(f'<a href="{c}" class="block bg-card border border-outline-variant rounded-xl overflow-hidden hover:border-primary"><img src="{p}" class="w-full h-32 object-cover object-top border-b border-outline-variant"/><div class="p-3"><p class="font-semibold text-sm">{l}</p></div></a>' for l,p,c in stitch)

body=('<header class="sticky top-0 z-40 bg-card border-b border-outline-variant px-10 h-16 flex items-center gap-2.5">'
  '<img src="../assets/coat_of_arms.png" class="h-8 w-8 object-contain"/>'
  '<span class="disp font-bold tracking-tight">CDF Integrity <span class="text-outline font-normal">|</span> Screen Map</span>'
  f'<a href="{R["P1"]}" class="ml-auto text-sm text-primary font-semibold">Open the live landing →</a></header>'
  '<main class="max-w-[1180px] mx-auto px-10 py-10">'
  '<h1 class="disp text-3xl font-bold text-ink mb-1">Screen Map &amp; Flows</h1>'
  '<p class="text-on-surface-variant mb-8 max-w-2xl">Every screen, grouped by app, and the primary journeys that connect them. '
  'Click any node to open the prototype; arrows show the intended path. Nav, sidebars and buttons inside each screen are wired to these same routes.</p>'
  '<section class="bg-surface-2/50 border border-outline-variant rounded-2xl p-6 mb-4">'
  '<h2 class="disp font-semibold text-ink mb-4">Key user flows</h2>'+flows+'</section>'
  '<h2 class="disp font-semibold text-ink mt-8 mb-3">Designed in Stitch (hi-fi)</h2>'
  f'<div class="grid grid-cols-5 gap-3">{stitch_cards}</div>'
  +inv+
  '</main>')
open(os.path.join(out,"index.html"),"w",encoding="utf-8").write(page("Screen Map & Flows",body))
print("generated", len(S), "screens + index.html (flow map)  ->", out)
