// P1 — Public Landing (matches design/screens/landing_enhanced.html)
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { publicApi } from "../lib/api";
import { ROUTES } from "../lib/routes";

function fmt(n: number | null | undefined): string {
  if (n == null) return "—";
  if (n >= 1_000_000) return `K${(n / 1_000_000).toFixed(1)}M`;
  return n.toLocaleString();
}

export default function Landing() {
  const { data: kpis } = useQuery({
    queryKey: ["overview"],
    queryFn: () => publicApi.overview().then(r => r.data),
    staleTime: 120_000,
  });

  return (
    <div className="min-h-screen bg-ink text-sidebar-text">
      {/* Hero */}
      <div className="max-w-7xl mx-auto px-4 pt-20 pb-16 text-center">
        <div className="inline-flex items-center gap-2 bg-primary/20 border border-primary/30 rounded-full px-4 py-1.5 text-sm text-primary font-semibold mb-8">
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
          Live · Hyperledger Fabric Ledger
        </div>

        {/* Verification Seal */}
        <div className="relative w-40 h-40 mx-auto mb-10">
          <svg viewBox="0 0 200 200" className="w-full h-full">
            <circle cx="100" cy="100" r="95" fill="none" stroke="#B8762A" strokeWidth="1.5" strokeDasharray="4 3" className="seal-ring" />
            <circle cx="100" cy="100" r="78" fill="#0E5C46" fillOpacity="0.15" stroke="#0E5C46" strokeWidth="1" />
            <text x="100" y="40" textAnchor="middle" fill="#B8762A" fontSize="8" fontFamily="Space Grotesk" fontWeight="600" letterSpacing="3">
              REPUBLIC OF ZAMBIA
            </text>
            <text x="100" y="168" textAnchor="middle" fill="#B8762A" fontSize="7" fontFamily="JetBrains Mono" letterSpacing="1">
              VERIFIED ON LEDGER
            </text>
            <text x="100" y="108" textAnchor="middle" fill="#E7EFEA" fontSize="36">◈</text>
          </svg>
        </div>

        <h1 className="font-display text-5xl md:text-6xl font-bold text-white mb-4 leading-tight">
          CDF <span className="text-accent">Integrity</span>
        </h1>
        <p className="text-sidebar-muted text-lg max-w-2xl mx-auto mb-10">
          Blockchain-anchored accountability for Zambia's K6.2 billion Constituency Development Fund.
          Every contract hash immutably recorded. Every flag explainable.
        </p>

        <div className="flex flex-wrap justify-center gap-3 mb-16">
          <Link to={ROUTES.VERIFY}
            className="bg-primary hover:bg-primary-h text-white font-semibold px-6 py-3 rounded-lg flex items-center gap-2 transition-colors">
            <span className="material-symbols-outlined">verified</span>
            Verify a Contract
          </Link>
          <Link to={ROUTES.DASHBOARD}
            className="bg-white/10 hover:bg-white/20 text-white font-semibold px-6 py-3 rounded-lg flex items-center gap-2 transition-colors border border-white/20">
            <span className="material-symbols-outlined">dashboard</span>
            Explore Dashboard
          </Link>
        </div>

        {/* Live KPI bento */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
          {[
            { icon: "description", label: "Contracts Tracked", value: fmt(kpis?.total_contracts), sub: "OCDS records ingested" },
            { icon: "verified",    label: "Anchored",           value: fmt(kpis?.verified_contracts), sub: "On Fabric ledger" },
            { icon: "warning",     label: "High Risk",          value: fmt(kpis?.high_risk_contracts), sub: "Flagged for review" },
            { icon: "location_city", label: "Constituencies",   value: kpis?.constituencies_covered?.toString() ?? "156", sub: "Across 10 provinces" },
          ].map(({ icon, label, value, sub }) => (
            <div key={label} className="bg-white/5 border border-white/10 rounded-xl p-4 text-left">
              <span className="material-symbols-outlined text-primary text-xl">{icon}</span>
              <p className="font-display text-2xl font-bold text-white mt-1">{value}</p>
              <p className="text-xs text-sidebar-muted font-medium">{label}</p>
              <p className="text-xs text-sidebar-muted/70">{sub}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Two front doors */}
      <div className="max-w-7xl mx-auto px-4 pb-20 grid md:grid-cols-2 gap-6">
        <Link to={ROUTES.DASHBOARD} className="group bg-primary/10 border border-primary/20 rounded-2xl p-8 hover:bg-primary/20 transition-colors">
          <span className="material-symbols-outlined text-4xl text-primary mb-4 block">public</span>
          <h2 className="font-display text-xl font-bold text-white mb-2">Citizens & Journalists</h2>
          <p className="text-sidebar-muted text-sm">Explore the public dashboard, verify contracts, and download open data.</p>
          <span className="mt-4 inline-flex items-center gap-1 text-primary text-sm font-semibold group-hover:gap-2 transition-all">
            Enter public portal <span className="material-symbols-outlined text-base">arrow_forward</span>
          </span>
        </Link>
        <a href="#officials" id="officials" className="group bg-accent/10 border border-accent/20 rounded-2xl p-8 hover:bg-accent/20 transition-colors cursor-pointer">
          <span className="material-symbols-outlined text-4xl text-accent mb-4 block">lock</span>
          <h2 className="font-display text-xl font-bold text-white mb-2">OAG / ACC / ZPPA Officers</h2>
          <p className="text-sidebar-muted text-sm">Access the oversight console with named contract data, anomaly review, and case management.</p>
          <span className="mt-4 inline-flex items-center gap-1 text-accent text-sm font-semibold group-hover:gap-2 transition-all">
            Officials portal (restricted) <span className="material-symbols-outlined text-base">arrow_forward</span>
          </span>
        </a>
      </div>
    </div>
  );
}
