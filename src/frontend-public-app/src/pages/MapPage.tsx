// P3 — National Project Map (matches stitch_export/national_project_map)
import { useQuery } from "@tanstack/react-query";
import { publicApi } from "../lib/api";
import ZambiaMap from "../components/ui/ZambiaMap";
import RiskBadge from "../components/ui/RiskBadge";
import { Link } from "react-router-dom";
import { constituencyPath } from "../lib/routes";

export default function MapPage() {
  const { data: mapData, isLoading } = useQuery({
    queryKey: ["map"],
    queryFn: () => publicApi.map().then(r => r.data),
    staleTime: 300_000,
  });

  const features = mapData?.features ?? [];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="font-display text-3xl font-bold">Constituency Risk Map</h1>
        <p className="text-on-surface-variant mt-1">
          156 constituencies · click a marker to view detail · risk score = weighted anomaly engine output
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Map — full height */}
        <div className="lg:col-span-2">
          {isLoading
            ? <div className="h-[540px] bg-surface-2 rounded-xl animate-pulse" />
            : <ZambiaMap features={features} height="h-[540px]" showControls />
          }
        </div>

        {/* Sidebar — constituency list */}
        <div className="flex flex-col gap-3 max-h-[540px] overflow-y-auto pr-1">
          <p className="text-xs font-semibold text-on-surface-variant uppercase tracking-wide sticky top-0 bg-surface pb-1">
            Constituencies ({features.length} shown)
          </p>
          {features
            .slice()
            .sort((a, b) => (b.risk_score ?? 0) - (a.risk_score ?? 0))
            .map(f => (
              <Link key={f.id} to={constituencyPath(f.id)}
                className="bg-card border border-outline-variant rounded-lg p-3 hover:border-primary/30 transition-colors flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <p className="font-medium text-sm truncate">{f.name}</p>
                  <p className="text-xs text-on-surface-variant">{f.province} · {f.project_count} projects</p>
                </div>
                <RiskBadge tier={f.risk_tier} score={f.risk_score} />
              </Link>
            ))}
        </div>
      </div>
    </div>
  );
}
