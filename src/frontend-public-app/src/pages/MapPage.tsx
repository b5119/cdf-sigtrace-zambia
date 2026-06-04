// P3 — National Project Map. Full-bleed choropleth + constituency sidebar.
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { publicApi } from "../lib/api";
import ZambiaMap from "../components/ui/ZambiaMap";
import { constituencyPath } from "../lib/routes";

function riskTier(s: number | null) {
  if (s == null) return { label: "—", color: "bg-surface-2 text-on-surface-variant" };
  if (s >= 70) return { label: `High · ${s}`, color: "bg-risk-high/10 text-risk-high" };
  if (s >= 40) return { label: `Medium · ${s}`, color: "bg-risk-mid/10 text-risk-mid" };
  return { label: `Low · ${s}`, color: "bg-risk-low/10 text-risk-low" };
}

export default function MapPage() {
  const { data } = useQuery({ queryKey: ["map"], queryFn: () => publicApi.map().then(r => r.data), staleTime: 300_000 });
  const features = (data?.features ?? []).slice().sort((a, b) => (b.risk_score ?? 0) - (a.risk_score ?? 0));
  const riskById: Record<string, number> = {};
  features.forEach(f => { if (f.risk_score != null) riskById[f.id] = f.risk_score; });

  return (
    <main className="max-w-[1200px] mx-auto px-6 md:px-12 py-10">
      <div className="mb-6">
        <h1 className="disp text-2xl font-bold text-ink">National Project Map</h1>
        <p className="text-sm text-on-surface-variant mt-1">156 constituencies, coloured by risk. Click a marker to drill into a constituency.</p>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ZambiaMap riskById={riskById} height="h-[540px]" showControls />
        </div>
        <div className="flex flex-col gap-2 max-h-[540px] overflow-y-auto pr-1">
          <p className="text-xs font-semibold text-on-surface-variant uppercase tracking-wide sticky top-0 bg-surface pb-1">Constituencies ({features.length})</p>
          {features.map(f => {
            const t = riskTier(f.risk_score);
            return (
              <Link key={f.id} to={constituencyPath(f.id)} className="bg-card border border-outline-variant rounded-lg p-3 hover:border-primary/40 transition-colors flex items-center justify-between gap-3">
                <div className="min-w-0"><p className="font-medium text-sm truncate">{f.name}</p><p className="text-xs text-on-surface-variant">{f.province} · {f.project_count} projects</p></div>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full shrink-0 ${t.color}`}>{t.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </main>
  );
}
