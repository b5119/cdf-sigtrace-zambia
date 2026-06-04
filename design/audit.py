# Comprehensive routing/semantic/tier/date audit for the CDF screen prototype.
import re,os,glob,collections
ROOT=os.getcwd()
def reln(p): return os.path.normpath(p)
def absn(base,h): return reln(os.path.join(os.path.dirname(base),h))

R={'P1':'screens/landing_enhanced.html','P2':'screens/P2_dashboard.html','P3':'stitch_export/national_project_map/code.html','P4':'stitch_export/constituency_detail/code.html','P5':'stitch_export/project_transparency_detail/code.html','P6':'stitch_export/verification_portal/code.html','P7':'screens/P7_procurement_risk.html','P8':'screens/P8_open_data.html','P9':'screens/P9_about.html','P10':'screens/P10_audit_trail.html','O1':'screens/O1_login.html','O2':'screens/O2_dashboard.html','O3':'screens/O3_contract_list.html','O4':'screens/O4_contract_detail.html','O5':'screens/O5_supplier_network.html','O6':'screens/O6_ghost_queue.html','O7':'screens/O7_mismatch.html','O8':'screens/O8_verify_review.html','O9':'screens/O9_doc_verify.html','O10':'screens/O10_cases.html','O11':'screens/O11_analytics.html','O12':'screens/O12_reports.html','O13':'screens/O13_notifications.html','S1':'screens/S1_admin_home.html','S2':'screens/S2_users.html','S3':'screens/S3_weights.html','S4':'screens/S4_thresholds.html','S5':'screens/S5_ingestion.html','S6':'screens/S6_ledger.html','S7':'screens/S7_institutions.html','S8':'screens/S8_audit.html','S9':'screens/S9_notif_config.html','M1':'screens/M1_login.html','M2':'screens/M2_home.html','M3':'screens/M3_capture.html','M4':'screens/M4_review.html','M5':'screens/M5_sync.html','M6':'screens/M6_detail.html','M7':'screens/M7_confirm.html','M8':'screens/M8_profile.html','X1':'screens/X1_login.html','X2':'screens/X2_mfa.html','X3':'screens/X3_reset.html','X4':'screens/X4_account.html','X5':'screens/X5_errors.html','X6':'screens/X6_consent.html','MAP':'screens/index.html'}
abs2id={reln(v):k for k,v in R.items()}
files=glob.glob('screens/*.html')+glob.glob('stitch_export/*/code.html')
def fid(f):
    r=reln(f); return abs2id.get(r,'?'+os.path.basename(f))
AUTH={'X1','X2','X3'}  # generic auth/bridge screens (login/MFA/reset) — tier-neutral
def tier(f):
    b=fid(f)
    if b in AUTH: return 'A'
    return 'M' if b[:1]=='M' else ('S' if b[:1]=='S' else ('O' if b[:1]=='O' else 'P'))

anchors=collections.defaultdict(list); edges=collections.defaultdict(set); indeg=collections.defaultdict(set)
for f in files:
    h=open(f,encoding='utf-8').read()
    for a in re.finditer(r'<a\b([^>]*)>(.*?)</a>',h,re.S):
        attrs=a.group(1); txt=re.sub(r'<[^>]+>',' ',a.group(2)); txt=re.sub(r'\s+',' ',txt).strip().lower()
        m=re.search(r'href="([^"]*)"',attrs); href=m.group(1) if m else ''
        tgt=None
        if href and not href.startswith('http') and href.split('#')[0].endswith('.html'):
            tgt=absn(f,href.split('#')[0]); tid=abs2id.get(tgt,'?'+os.path.basename(tgt))
            edges[fid(f)].add(tid); indeg[tid].add(fid(f))
        anchors[f].append((txt,tgt,href))

print('# CDF SCREEN ROUTING AUDIT  (year baseline 2026-06-03)')
print('screens:',len(files),'| mapped ids:',sum(1 for f in files if not fid(f).startswith('?')))

# B. dead href=#
dead=[(fid(f),t or '(icon/empty)') for f in files for t,tg,hr in anchors[f] if hr.strip()=='#']
print('\n## B. dead href=\"#\" links:',len(dead))
byf=collections.defaultdict(list)
for i,t in dead: byf[i].append(t)
for i in sorted(byf): print('  ',i,'->',byf[i])

# C. broken
broken=[(fid(f),hr) for f in files for t,tg,hr in anchors[f] if tg and not os.path.exists(tg)]
print('\n## C. broken links:',len(broken),broken[:10])

# D. semantic
SEM={'national dashboard':'P2','national map':'P3','map':'P3','constituencies':'P4','constituency detail':'P4','projects':'P5','project detail':'P5','procurement risk':'P7','open data & datasets':'P8','open data':'P8','public api':'P8','api documentation':'P8','open data policy':'P8','public reports':'P8','public ledger (audit trail)':'P10','audit trail':'P10','methodology':'P9','how it works':'P9','faq':'P9','contact':'P9','data protection':'X6','privacy protocol':'X6','verify a contract':'P6','verify':'P6','explore the map':'P3','for officials':'O1','portal login':'O1','registry':'P2','allocations':'P2','about':'P9','screen map':'MAP','risk dashboard':'O2','contract risk list':'O3','view all contracts':'O3','ghost-project queue':'O6','supplier network':'O5','view supplier network':'O5','disbursement explorer':'O7','cases':'O10','verify document':'O9','open document verify':'O9','verification review':'O8','analytics':'O11','reports':'O12','admin home':'S1','users & roles':'S2','check weights':'S3','thresholds':'S4','ingestion':'S5','ledger & nodes':'S6','institutions':'S7','audit log':'S8','capture':'M3','submissions':'M5','profile':'M8'}
mm=[]
for f in files:
    if fid(f)=='MAP': continue
    for t,tg,hr in anchors[f]:
        exp=SEM.get(t)
        if t=='home': exp='M2' if tier(f)=='M' else 'P1'
        if t=='notifications': exp='S9' if tier(f)=='S' else 'O13'
        if fid(f) in AUTH and t in('verify','continue','sign in','set password'): continue  # auth action, not contract-verify
        if not exp or not tg: continue
        got=abs2id.get(tg,'?')
        if got!=exp: mm.append((fid(f),t,'exp',exp,'got',got))
print('\n## D. semantic mismatches:',len(mm))
for x in mm[:40]: print('  ',x)

# E. reachability
def bfs(starts):
    seen=set(starts); q=list(starts)
    while q:
        n=q.pop()
        for m2 in edges.get(n,()):
            if m2 not in seen and not m2.startswith('?'): seen.add(m2); q.append(m2)
    return seen
allids=set(fid(f) for f in files if not fid(f).startswith('?'))
reach=bfs(['P1','MAP'])  # public entry + dev map
reach_o=bfs(['O1','X1'])
reach_m=bfs(['M1'])
unreached=allids-reach-reach_o-reach_m
print('\n## E. reachability: public-from-P1/MAP=',len(reach),' oversight-from-O1/X1=',len(reach_o),' pulse-from-M1=',len(reach_m))
print('   UNREACHABLE from any entry:',sorted(unreached))

# F. orphans (no inbound) & dead-ends (no outbound)
orphan=sorted(i for i in allids if not indeg.get(i) and i not in('P1','MAP'))
deadend=sorted(i for i in allids if not edges.get(i))
print('\n## F. orphans(no inbound):',orphan)
print('   dead-ends(no outbound):',deadend)

# G. tier isolation: public must only reach officials via O1
viol=[]
for f in files:
    if tier(f)!='P': continue
    for t,tg,hr in anchors[f]:
        if not tg: continue
        gid=abs2id.get(tg,'?')
        if gid[:1] in ('O','S') and gid!='O1': viol.append((fid(f),t,gid))
print('\n## G. tier isolation (public->officials except O1):',len(viol))
for v in viol[:20]: print('  ',v)
# officials->public leaks (other than O1->P1 back-bridge)
leak=[]
for f in files:
    if tier(f) not in ('O','S'): continue
    for t,tg,hr in anchors[f]:
        if not tg: continue
        gid=abs2id.get(tg,'?')
        if gid[:1]=='P' and not (fid(f)=='O1'): leak.append((fid(f),t,gid))
print('   officials->public leaks (excl O1 back):',len(leak),leak[:10])

# H. stale years
print('\n## H. non-2026 years in visible text (context):')
cnt=0
for f in files:
    h=open(f,encoding='utf-8').read(); txt=re.sub(r'<script.*?</script>','',h,flags=re.S)
    txt=re.sub(r'<[^>]+>',' ',txt)
    for m in re.finditer(r'\b(19|20)\d\d\b',txt):
        y=m.group(0)
        if y!='2026':
            seg=re.sub(r'\s+',' ',txt[max(0,m.start()-30):m.start()+34]).strip()
            print('  ',fid(f),y,'::',seg); cnt+=1
print('   total non-2026 year mentions:',cnt)

# I. src asset existence
missrc=[]
for f in files:
    for s in re.findall(r'src="([^"]+)"',open(f,encoding='utf-8').read()):
        if s.startswith('http'): continue
        if not os.path.exists(absn(f,s)): missrc.append((fid(f),s))
print('\n## I. missing local image src:',len(missrc),missrc[:10])
# J. can every screen navigate BACK to a home hub of its tier?
def fwd(n):
    seen={n}; q=[n]
    while q:
        x=q.pop()
        for y in edges.get(x,()):
            if y not in seen and not y.startswith('?'): seen.add(y); q.append(y)
    return seen
hub={'P':'P1','A':'O2','O':'O2','S':'O2','M':'M2'}  # auth screens complete into the officials console
noback=[]
for f in files:
    i=fid(f)
    if i.startswith('?') or i in('P1','MAP'): continue
    h=hub[tier(f)]
    if h not in fwd(i): noback.append((i,'cannot reach',h))
print('\n## J. screens that cannot navigate back to their home hub:',len(noback),noback[:15])

# K. title/purpose sanity — title must be non-empty and on-theme
EXP={'P2':'dashboard','P7':'risk','P8':'open data','P9':'about','P10':'audit','O2':'dashboard','O3':'contract','O4':'contract','O5':'supplier','O6':'ghost','O7':'disburs','O8':'verif','O9':'document','O10':'case','O11':'analytic','O12':'report','O13':'notif','S1':'admin','S2':'user','S3':'weight','S4':'threshold','S5':'ingest','S6':'ledger','S7':'institution','S8':'audit','S9':'notif','M2':'home','M3':'captur','M5':'submiss','M7':'confirm','M8':'profile','O1':'official'}
badtitle=[]
for f in files:
    h=open(f,encoding='utf-8').read(); m=re.search(r'<title>(.*?)</title>',h,re.S)
    t=(m.group(1).strip().lower() if m else '')
    i=fid(f)
    if not t: badtitle.append((i,'EMPTY')); continue
    if i in EXP and EXP[i] not in t: badtitle.append((i,'title=%r expected~%r'%(t,EXP[i])))
print('\n## K. title/purpose mismatches:',len(badtitle))
for b in badtitle: print('  ',b)
print('\nDONE')
