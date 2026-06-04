// P10 — Public Audit Trail / Live Ledger. Faithful port of design/screens/P10_audit_trail.html.
import { Link } from "react-router-dom";
import { ROUTES } from "../lib/routes";

const FEED = [
  { icon: "anchor", color: "text-primary", title: "Contract anchored", meta: "0xa1b2…9f · ocds-zm-000123 · Hyperledger Fabric" },
  { icon: "verified", color: "text-risk-low", title: "Project verified · Milenge", meta: "3 confirmations · IPFS Qm…f1" },
  { icon: "gpp_maybe", color: "text-risk-high", title: "Ghost-project flag · Kafue", meta: "disbursed, unverified — routed to review" },
  { icon: "fact_check", color: "text-accent", title: "Field evidence submitted", meta: "-15.41,28.30 · borehole · CDF Pulse" },
  { icon: "anchor", color: "text-primary", title: "Audit batch anchored", meta: "0x91c4… · 142 actions · Polygon" },
];

export default function AuditTrail() {
  return (
    <main className="max-w-[1200px] mx-auto px-6 md:px-12 py-10">
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="disp text-2xl font-bold text-ink">Public Audit Trail · Live Ledger</h1>
          <p className="text-sm text-on-surface-variant mt-1">Every anchor, verification and flag, in the order it happened. Tamper-evident and public.</p>
        </div>
        <div className="flex gap-2">
          <Link to={ROUTES.VERIFY} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
            <span className="material-symbols-outlined">shield</span>Verify a contract
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {[["Events today","1,284","anchors + verifications","text-ink"],["Last block","#48,210","Hyperledger Fabric","text-ink"],["Anchor backlog","0","fully synced","text-risk-low"]].map(([l,v,s,c]) => (
          <div key={l} className="bg-card border border-outline-variant rounded-xl p-4 h-full">
            <p className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">{l}</p>
            <p className={`disp text-2xl font-bold mt-1 ${c}`}>{v}</p>
            <p className="text-xs text-on-surface-variant mt-0.5">{s}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="disp font-semibold text-ink">Live ledger feed</h3>
              <span className="flex items-center gap-1.5 text-[11px] font-bold text-risk-low"><span className="w-1.5 h-1.5 rounded-full bg-risk-low" />LIVE</span>
            </div>
            {FEED.map((e, i) => (
              <div key={i} className="flex items-start gap-3 py-3 border-b border-outline-variant/60 last:border-0">
                <span className={`material-symbols-outlined ${e.color}`} style={{ fontSize: 20 }}>{e.icon}</span>
                <div className="flex-1"><p className="text-sm font-semibold">{e.title}</p><p className="mono text-[11px] text-on-surface-variant">{e.meta}</p></div>
                <span className="mono text-[11px] text-on-surface-variant">just now</span>
              </div>
            ))}
          </div>
        </div>
        <div>
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-center justify-between mb-4"><h3 className="disp font-semibold text-ink">What is this?</h3></div>
            <p className="text-sm text-on-surface-variant mb-3">The ledger records a hash of every contract and confirmation. Records cannot be altered retroactively without a public, detectable trail.</p>
            <Link to={ROUTES.ABOUT} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
              <span className="material-symbols-outlined">menu_book</span>How it works
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
