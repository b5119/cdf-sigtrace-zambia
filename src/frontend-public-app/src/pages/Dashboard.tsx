// P2 — National Dashboard (matches design/screens/P2_dashboard.html)
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { publicApi } from "../lib/api";
import KpiCard from "../components/ui/KpiCard";
import ZambiaMap from "../components/ui/ZambiaMap";
import RiskBadge from "../components/ui/RiskBadge";
import { ROUTES, constituencyPath } from "../lib/routes";

function fmt(n: number | null | undefined) {
  if (n == null) return "—";
  if (n >= 1_000_000) return `ZMW ${(n / 1_000_000).toFixed(1)}M`;
  return n.toLocaleString();
}

export default function Dashboard() {
  const { data: kpis } = useQuery({
    queryKey: ["overview"],
    queryFn: () => publicApi.overview().then(r => r.data),
    staleTime: 120_000,
  });
  const { data: mapData } = useQuery({
    queryKey: ["map"],
    queryFn: () => publicApi.map().then(r => r.data),
    staleTime: 300_000,
  });

  const features = mapData?.features ?? [];
  const recentFeed = features.slice(0, 5);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold text-on-surface">National Dashboard</h1>
        <p className="text-on-surface-variant mt-1">Real-time CDF accountability — de-identified public view</p>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <KpiCard icon="description"    label="Contracts Tracked"  value={kpis?.total_contracts ?? "—"} sub={fmt(kpis?.total_value_zmw)} />
        <KpiCard icon="verified"       label="Anchored on Ledger" value={kpis?.verified_contracts ?? "—"} sub="Fabric-verified" accent />
        <KpiCard icon="warning"        label="High Risk"          value={kpis?.high_risk_contracts ?? "—"} sub="Score ≥ 60" />
        <KpiCard icon="ghost_off"      label="Ghost Signals"      value={kpis?.ghost_project_signals ?? "—"} sub="No verified completion" />
      </div>

      {/* Map + feed */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <div className="md:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-display font-semibold text-lg">Constituency Risk Map</h2>
            <Link to={ROUTES.MAP} className="text-sm text-primary hover:underline flex items-center gap-1">
              Full map <span className="material-symbols-outlined text-base">open_in_new</span>
            </Link>
          </div>
          {features.length > 0
            ? <ZambiaMap features={features} height="h-80" />
            : <div className="h-80 bg-surface-2 rounded-xl animate-pulse" />
          }
        </div>

        {/* Recent verified feed */}
        <div>
          <h2 className="font-display font-semibold text-lg mb-3">Recently Active</h2>
          <div className="flex flex-col gap-3">
            {recentFeed.map(f => (
              <Link key={f.id} to={constituencyPath(f.id)}
                className="bg-card border border-outline-variant rounded-lg p-3 hover:border-primary/30 transition-colors">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-sm text-on-surface truncate">{f.name}</span>
                  <RiskBadge tier={f.risk_tier} score={f.risk_score} />
                </div>
                <p className="text-xs text-on-surface-variant">{f.province} · {f.project_count} projects · {f.verified_count} verified</p>
              </Link>
            ))}
            {recentFeed.length === 0 && (
              <div className="space-y-3">
                {[1,2,3].map(i => <div key={i} className="h-16 bg-surface-2 rounded-lg animate-pulse" />)}
              </div>
            )}
          </div>
          <Link to={ROUTES.CONSTITUENCIES}
            className="mt-3 w-full text-center text-sm text-primary border border-outline-variant rounded-lg py-2 block hover:bg-surface-2 transition-colors">
            All constituencies →
          </Link>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-surface-2 border border-outline-variant rounded-lg p-4 text-xs text-on-surface-variant">
        <span className="font-semibold text-on-surface">Note: </span>
        All outputs are risk signals requiring review by authorised oversight bodies.
        This dashboard shows aggregated, de-identified data only. Named contract data is available exclusively to
        authorised OAG, ACC and ZPPA officers via the{" "}
        <a href="#officials" className="text-primary underline">officials portal</a>.
      </div>
    </div>
  );
}
