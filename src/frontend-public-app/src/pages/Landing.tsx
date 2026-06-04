// P1 — Public Landing. Faithful port of design/screens/landing_enhanced.html (LOCKED).
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { publicApi } from "../lib/api";
import { ROUTES } from "../lib/routes";

const OFFICIALS = "http://localhost:5174";   // oversight console (O1 login)
const PULSE = "http://localhost:5175";       // CDF Pulse field app (M1 login)

// Real Zambia outline (from design/assets) — basemap + 3 travelling flag-colour pulses
const ZM = "M917.4,81.6L956.2,118.4L977.1,188.2L963.1,210.5L946.6,277.2L962.4,345.4L936.5,374.0L911.5,450.4L954.8,471.8L705.1,539.6L712.9,598.1L650.6,609.4L603.7,642.2L593.7,670.7L564.3,677.2L492.7,744.8L447.1,798.1L419.4,800.0L392.6,790.5L300.7,781.5L285.9,775.4L285.3,768.5L252.8,750.0L199.4,745.3L132.1,764.0L78.4,712.6L22.9,645.2L26.7,383.4L198.0,384.5L191.0,356.1L203.2,325.3L188.8,286.7L198.1,246.8L189.4,221.2L217.8,223.3L222.5,248.9L261.1,246.9L313.3,254.5L340.8,291.8L406.7,303.3L457.0,277.3L475.5,320.4L538.5,331.9L568.9,367.0L602.6,412.3L665.6,413.0L658.7,324.2L636.2,339.2L578.6,307.2L556.4,292.5L566.6,209.9L581.2,112.5L562.8,76.2L586.2,23.7L608.3,13.9L718.8,0L751.2,8.4L785.6,29.3L818.4,43.1L870.7,56.9L917.4,81.6Z";

function NavDropdown({ label, items }: { label: string; items: { to: string; text: string; ext?: boolean }[] }) {
  return (
    <div className="relative group">
      <button className="flex items-center gap-1 text-on-surface-variant hover:text-ink">
        {label}<span className="material-symbols-outlined" style={{ fontSize: 16 }}>expand_more</span>
      </button>
      <div className="absolute left-0 top-full pt-2 hidden group-hover:block z-50">
        <div className="w-56 bg-card border border-outline-variant rounded-xl shadow-lg p-2">
          {items.map(i => i.ext
            ? <a key={i.text} href={i.to} className="block px-3 py-2 rounded-lg hover:bg-surface-2">{i.text}</a>
            : <Link key={i.text} to={i.to} className="block px-3 py-2 rounded-lg hover:bg-surface-2">{i.text}</Link>)}
        </div>
      </div>
    </div>
  );
}

export default function Landing() {
  const { data: kpis } = useQuery({
    queryKey: ["overview"],
    queryFn: () => publicApi.overview().then(r => r.data),
    staleTime: 120_000,
  });
  const verifiedAudits = kpis ? kpis.verified_contracts.toLocaleString() : "4,912";
  const flagged = kpis ? kpis.high_risk_contracts.toString() : "24";

  return (
    <div className="bg-surface text-on-surface">
      {/* Header */}
      <header className="sticky top-0 z-50 flex justify-between items-center px-6 md:px-12 h-16 bg-card/90 backdrop-blur border-b border-outline-variant">
        <Link to={ROUTES.HOME} className="flex items-center gap-2.5">
          <img src="/coat_of_arms.png" className="h-8 w-8 object-contain" alt="Republic of Zambia" />
          <span className="disp font-bold tracking-tight text-ink">REP. OF ZAMBIA <span className="text-outline font-normal">|</span> LEDGER</span>
        </Link>
        <nav className="hidden md:flex items-center gap-7 text-sm">
          <NavDropdown label="Explore" items={[
            { to: ROUTES.DASHBOARD, text: "National dashboard" },
            { to: ROUTES.MAP, text: "National map" },
            { to: ROUTES.MAP, text: "Constituencies" },
            { to: ROUTES.MAP, text: "Projects" },
            { to: ROUTES.RISK, text: "Procurement risk" },
          ]} />
          <NavDropdown label="Data" items={[
            { to: ROUTES.OPEN_DATA, text: "Open data & datasets" },
            { to: ROUTES.OPEN_DATA, text: "Public API" },
            { to: ROUTES.ABOUT, text: "Methodology" },
          ]} />
          <NavDropdown label="About" items={[
            { to: ROUTES.ABOUT, text: "How it works" },
            { to: ROUTES.ABOUT, text: "FAQ" },
            { to: ROUTES.CONSENT, text: "Data protection" },
          ]} />
        </nav>
        <div className="flex items-center gap-5">
          <a href={OFFICIALS} className="hidden md:flex items-center gap-1.5 text-sm text-on-surface-variant hover:text-ink">
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>lock</span>For officials
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>chevron_right</span>
          </a>
          <Link to={ROUTES.VERIFY} className="bg-primary text-white text-sm font-semibold px-4 py-2 rounded-lg flex items-center gap-2">
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>shield</span>Verify a contract
          </Link>
        </div>
      </header>

      {/* HERO with morphing Zambia map */}
      <section className="relative overflow-hidden min-h-[680px] flex items-center">
        <div className="mapbg" aria-hidden="true">
          <svg viewBox="0 0 1000 800">
            <defs>
              <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="4" result="b" />
                <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
            </defs>
            <path className="basemap" d={ZM} />
            <path className="pulse a" pathLength={1000} d={ZM} />
            <path className="pulse b" pathLength={1000} d={ZM} />
            <path className="pulse c" pathLength={1000} d={ZM} />
          </svg>
        </div>
        <div className="absolute inset-0 z-[1] pointer-events-none"
          style={{ background: "radial-gradient(ellipse 62% 52% at 50% 40%, #F6F8F6 0%, rgba(246,248,246,.55) 42%, transparent 78%)" }} />

        <div className="relative z-10 max-w-3xl mx-auto px-6 py-14 text-center w-full">
          <span className="inline-flex items-center gap-1.5 text-[11px] font-bold tracking-widest text-accent bg-accent/10 px-3 py-1 rounded-full">
            <span className="w-1.5 h-1.5 rounded-full bg-accent" />LIVE CRYPTOGRAPHIC OVERSIGHT
          </span>
          <h1 className="disp text-4xl md:text-6xl font-bold text-ink leading-[1.05] mt-5">
            See how Zambia's CDF<br />money is <span className="text-primary">really spent</span>
          </h1>
          <p className="text-on-surface-variant text-lg mt-5 max-w-xl mx-auto">
            Independent, tamper-evident verification of Constituency Development Fund allocations — across all 156 constituencies. Trust, verified through code.
          </p>
          <div className="flex items-center justify-center gap-3 mt-7">
            <Link to={ROUTES.VERIFY} className="bg-primary text-white font-semibold px-6 py-3 rounded-lg flex items-center gap-2">
              Verify a contract<span className="material-symbols-outlined" style={{ fontSize: 18 }}>arrow_forward</span>
            </Link>
            <Link to={ROUTES.MAP} className="border border-outline-variant bg-card text-ink font-semibold px-6 py-3 rounded-lg">Explore the map</Link>
          </div>
          <Link to={ROUTES.DASHBOARD} className="inline-flex items-center gap-6 mt-9 bg-card/80 backdrop-blur border border-outline-variant rounded-xl px-6 py-3 hover:border-primary transition-colors">
            <div><p className="disp text-2xl font-bold text-accent mono">K6.245B</p><p className="text-[11px] text-on-surface-variant">Annual allocation</p></div>
            <div className="w-px h-8 bg-outline-variant" />
            <div><p className="disp text-2xl font-bold text-ink mono">156</p><p className="text-[11px] text-on-surface-variant">Constituencies tracked</p></div>
            <div className="w-px h-8 bg-outline-variant" />
            <div><p className="disp text-2xl font-bold text-risk-low mono">{verifiedAudits}</p><p className="text-[11px] text-on-surface-variant">Verified audits</p></div>
          </Link>
        </div>
      </section>

      {/* BENTO */}
      <section className="relative z-10 max-w-[1200px] mx-auto px-6 md:px-12 pt-10 pb-16 grid grid-cols-12 gap-5 items-stretch">
        <Link to={ROUTES.VERIFY} className="col-span-12 md:col-span-7 bg-ink rounded-2xl overflow-hidden relative aspect-[16/9] block">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative">
              <span className="absolute inset-0 rounded-full border-2 border-accent pulse-ring" />
              <button className="relative w-16 h-16 rounded-full bg-accent text-white flex items-center justify-center">
                <span className="material-symbols-outlined" style={{ fontSize: 32 }}>play_arrow</span>
              </button>
            </div>
          </div>
          <div className="absolute top-4 left-4 text-[11px] font-bold tracking-widest text-white/60">WATCH · HOW VERIFICATION WORKS</div>
          <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between">
            <p className="mono text-xs text-white/70">verifying ocds-zm-000123 → <span className="text-[#8fd5b8]">MATCH ✓</span></p>
            <span className="text-[11px] bg-black/40 text-white px-2 py-0.5 rounded mono">0:12</span>
          </div>
        </Link>

        <Link to={ROUTES.AUDIT_TRAIL} className="col-span-12 md:col-span-5 bg-card border border-outline-variant rounded-2xl p-5 block hover:border-primary transition-colors">
          <div className="flex items-center gap-2 mb-3"><span className="w-2 h-2 rounded-full bg-risk-low animate-pulse" /><h3 className="disp font-semibold text-ink text-sm tracking-wide">LIVE LEDGER</h3></div>
          <div className="lstack">
            <div className="levent"><div className="flex items-start gap-2"><span className="material-symbols-outlined text-primary" style={{ fontSize: 20 }}>anchor</span><div><p className="text-sm font-semibold">Contract anchored</p><p className="mono text-[11px] text-on-surface-variant">0xa1b2…9f · Hyperledger Fabric · 2s ago</p></div></div></div>
            <div className="levent"><div className="flex items-start gap-2"><span className="material-symbols-outlined text-risk-low" style={{ fontSize: 20 }}>verified</span><div><p className="text-sm font-semibold">Project verified · Milenge</p><p className="mono text-[11px] text-on-surface-variant">3 confirmations · IPFS Qm…f1 · 6s ago</p></div></div></div>
            <div className="levent"><div className="flex items-start gap-2"><span className="material-symbols-outlined text-risk-high" style={{ fontSize: 20 }}>gpp_maybe</span><div><p className="text-sm font-semibold">Ghost-project flag · Kafue</p><p className="mono text-[11px] text-on-surface-variant">disbursed, unverified · review · 11s ago</p></div></div></div>
            <div className="levent"><div className="flex items-start gap-2"><span className="material-symbols-outlined text-accent" style={{ fontSize: 20 }}>fact_check</span><div><p className="text-sm font-semibold">Field evidence submitted</p><p className="mono text-[11px] text-on-surface-variant">-15.41,28.30 · borehole · 14s ago</p></div></div></div>
          </div>
        </Link>

        <Link to={ROUTES.MAP} className="col-span-12 md:col-span-5 bg-card border border-outline-variant rounded-2xl p-5 block hover:border-primary transition-colors">
          <span className="material-symbols-outlined text-accent">photo_camera</span>
          <h3 className="disp font-semibold text-ink mt-2">Track Delivery</h3>
          <p className="text-sm text-on-surface-variant mt-1">Community monitors capture geo-tagged, tamper-evident photographic proof that projects exist where they're claimed.</p>
          <p className="mono text-[11px] text-primary mt-3 font-semibold">VIEW THE EVIDENCE →</p>
        </Link>

        <Link to={ROUTES.ABOUT} className="col-span-12 md:col-span-7 bg-ink text-white rounded-2xl p-6 flex items-center justify-between hover:ring-2 hover:ring-accent/40 transition">
          <div className="max-w-sm"><h3 className="disp font-semibold text-lg">Audit Trail Integrity</h3>
            <p className="text-sm text-white/70 mt-1">Every allocation is recorded on an immutable ledger. A figure cannot be changed retroactively without a public, detectable trail.</p>
            <p className="mono text-[11px] text-white/50 mt-3">HASH 0xa1b2…9f · verified by 3 independent nodes</p></div>
          <div className="relative w-20 h-20 rounded-full border border-accent/50 flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-[#8fd5b8]" style={{ fontSize: 30 }}>verified_user</span></div>
        </Link>
      </section>

      {/* dark stat strip */}
      <section className="bg-ink text-white"><div className="max-w-[1200px] mx-auto px-6 md:px-12 py-5 grid grid-cols-2 md:grid-cols-4 gap-6">
        <div><p className="text-[11px] uppercase tracking-wider text-white/50">Active projects</p><p className="disp text-2xl font-bold mono">1,248</p></div>
        <div><p className="text-[11px] uppercase tracking-wider text-white/50">Verified audits</p><p className="disp text-2xl font-bold mono">{verifiedAudits}</p></div>
        <div><p className="text-[11px] uppercase tracking-wider text-white/50">Flagged risks</p><p className="disp text-2xl font-bold mono text-[#ff9a9a]">{flagged}</p></div>
        <div><p className="text-[11px] uppercase tracking-wider text-white/50">Uptime</p><p className="disp text-2xl font-bold mono">99.98%</p></div>
      </div></section>

      {/* footer seal */}
      <footer className="max-w-[1200px] mx-auto px-6 md:px-12 py-12 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="relative w-16 h-16 rounded-full border-2 border-accent flex items-center justify-center">
            <img src="/coat_of_arms.png" className="h-10 w-10 object-contain" alt="seal" />
            <svg className="seal-spin absolute inset-0" viewBox="0 0 100 100">
              <defs><path id="c" d="M50,50 m-39,0 a39,39 0 1,1 78,0 a39,39 0 1,1 -78,0" /></defs>
              <text fill="#B8762A" fontSize="6" fontFamily="Inter" fontWeight="700" letterSpacing="1.8"><textPath href="#c">VERIFIED ON LEDGER • REPUBLIC OF ZAMBIA • </textPath></text>
            </svg>
          </div>
          <div><p className="disp font-semibold text-ink">Republic of Zambia · Public Ledger</p>
            <p className="text-xs text-on-surface-variant">Verified via cryptographic audit. Risk signals require review.</p></div>
        </div>
        <div className="flex flex-wrap gap-6 text-xs text-on-surface-variant">
          <a href={PULSE} className="hover:text-ink font-semibold text-primary">CDF Pulse (field app)</a>
          <Link to={ROUTES.CONSENT} className="hover:text-ink">Privacy Protocol</Link>
          <Link to={ROUTES.OPEN_DATA} className="hover:text-ink">Open Data Policy</Link>
          <Link to={ROUTES.OPEN_DATA} className="hover:text-ink">API Documentation</Link>
        </div>
      </footer>
    </div>
  );
}
