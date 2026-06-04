// P2 — National CDF Dashboard. Faithful port of design/screens/P2_dashboard.html.
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { publicApi } from "../lib/api";
import ZambiaMap from "../components/ui/ZambiaMap";
import { ROUTES, constituencyPath } from "../lib/routes";

export default function Dashboard() {
  const { data: kpis } = useQuery({ queryKey: ["overview"], queryFn: () => publicApi.overview().then(r => r.data), staleTime: 120_000 });
  const { data: mapData } = useQuery({ queryKey: ["map"], queryFn: () => publicApi.map().then(r => r.data), staleTime: 300_000 });

  // live risk overrides keyed by constituency id (the map keeps the design's fixed coords)
  const riskById: Record<string, number> = {};
  (mapData?.features ?? []).forEach(f => { if (f.risk_score != null) riskById[f.id] = f.risk_score; });
  const recent = (mapData?.features ?? []).filter(f => f.verified_count > 0).slice(0, 4);

  const verifiedPct = kpis && kpis.total_contracts ? Math.round((kpis.verified_contracts / kpis.total_contracts) * 100) : 61;

  return (
    <main className="max-w-[1200px] mx-auto px-6 md:px-12 py-10">
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="disp text-2xl font-bold text-ink">National CDF Dashboard</h1>
          <p className="text-sm text-on-surface-variant mt-1">Top-line oversight across all 156 constituencies. Public, aggregated, tamper-evident.</p>
        </div>
        <div className="flex gap-2">
          <Link to={ROUTES.MAP} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
            <span className="material-symbols-outlined">map</span>Open the map
          </Link>
        </div>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Link to={ROUTES.MAP} className="block"><div className="bg-card border border-outline-variant rounded-xl p-4 h-full hover:border-primary transition-colors">
          <p className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">Total allocation</p>
          <p className="disp text-2xl font-bold text-ink mt-1">K 1.6 bn</p>
          <p className="text-xs text-on-surface-variant mt-0.5">FY2026</p></div></Link>
        <Link to={ROUTES.MAP} className="block"><div className="bg-card border border-outline-variant rounded-xl p-4 h-full hover:border-primary transition-colors">
          <p className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">Projects tracked</p>
          <p className="disp text-2xl font-bold text-ink mt-1">8,742</p>
          <p className="text-xs text-on-surface-variant mt-0.5">across 156 constituencies</p></div></Link>
        <Link to={ROUTES.MAP} className="block"><div className="bg-card border border-outline-variant rounded-xl p-4 h-full hover:border-primary transition-colors">
          <p className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">Verified on ledger</p>
          <p className="disp text-2xl font-bold text-risk-low mt-1">{verifiedPct}%</p>
          <p className="text-xs text-on-surface-variant mt-0.5">{kpis?.verified_contracts.toLocaleString() ?? "5,332"} anchored</p></div></Link>
        <Link to={ROUTES.RISK} className="block"><div className="bg-card border border-outline-variant rounded-xl p-4 h-full hover:border-primary transition-colors">
          <p className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">Flagged for review</p>
          <p className="disp text-2xl font-bold text-accent mt-1">{kpis?.high_risk_contracts ?? 23}</p>
          <p className="text-xs text-on-surface-variant mt-0.5">risk signals only</p></div></Link>
      </div>

      {/* Heat-map + Recently verified */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="disp font-semibold text-ink">Constituency risk heat-map</h3>
              <Link to={ROUTES.MAP} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 text-ink hover:bg-surface-2">
                <span className="material-symbols-outlined">open_in_full</span>Open full map
              </Link>
            </div>
            <ZambiaMap riskById={riskById} height="h-72" />
          </div>
        </div>
        <div>
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-center justify-between mb-4"><h3 className="disp font-semibold text-ink">Recently verified</h3></div>
            {recent.map(f => (
              <Link key={f.id} to={constituencyPath(f.id)} className="flex items-center gap-2 py-2 border-b border-outline-variant/60 last:border-0">
                <span className="material-symbols-outlined text-risk-low" style={{ fontSize: 18 }}>verified</span>
                <div><p className="text-sm font-semibold">{f.name}</p><p className="text-xs text-on-surface-variant">{f.province} · verified</p></div>
              </Link>
            ))}
            {recent.length === 0 && [1,2,3,4].map(i => (
              <div key={i} className="flex items-center gap-2 py-2 border-b border-outline-variant/60 last:border-0">
                <span className="material-symbols-outlined text-risk-low" style={{ fontSize: 18 }}>verified</span>
                <div><p className="text-sm font-semibold">Project #{i}</p><p className="text-xs text-on-surface-variant">Constituency {i} · verified</p></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
