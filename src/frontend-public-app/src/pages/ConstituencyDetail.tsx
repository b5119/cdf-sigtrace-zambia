// P4 — Constituency Detail (matches stitch_export/constituency_detail)
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { publicApi } from "../lib/api";
import RiskBadge from "../components/ui/RiskBadge";
import { ROUTES } from "../lib/routes";

function fmt(n: number | null | undefined) {
  if (n == null) return "—";
  return `ZMW ${(n / 1_000_000).toFixed(1)}M`;
}

// Seed project rows for prototype — real data comes from INC-010/014
// IDs mirror the backend pulse project ids so the public project page (P5) resolves
const SEED_PROJECTS = [
  { id: "proj-001", title: "Borehole Drilling — Ward 3",       category: "Water & Sanitation", status: "completed", verified: true  },
  { id: "proj-002", title: "Community Health Post",            category: "Health",              status: "ongoing",   verified: false },
  { id: "proj-003", title: "Market Stall Construction",        category: "Economic Dev",        status: "ongoing",   verified: false },
  { id: "proj-004", title: "Solar Electrification — School",   category: "Energy",              status: "completed", verified: true  },
];

const STATUS_STYLE: Record<string, string> = {
  completed: "bg-risk-low/10 text-risk-low border-risk-low/20",
  ongoing:   "bg-info/10 text-info border-info/20",
  stalled:   "bg-risk-mid/10 text-risk-mid border-risk-mid/20",
};

export default function ConstituencyDetail() {
  const { id } = useParams<{ id: string }>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["constituency", id],
    queryFn: () => publicApi.constituency(id!).then(r => r.data),
    enabled: !!id,
  });

  if (isLoading) return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-4">
      {[1,2,3].map(i => <div key={i} className="h-24 bg-surface-2 rounded-xl animate-pulse" />)}
    </div>
  );

  if (isError || !data) return (
    <div className="max-w-4xl mx-auto px-4 py-16 text-center">
      <span className="material-symbols-outlined text-5xl text-outline mb-4 block">search_off</span>
      <h2 className="font-display text-xl font-bold mb-2">Constituency not found</h2>
      <Link to={ROUTES.MAP} className="text-primary hover:underline">← Back to map</Link>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-on-surface-variant mb-6">
        <Link to={ROUTES.MAP} className="hover:text-primary">Map</Link>
        <span>/</span>
        <span className="text-on-surface font-medium">{data.name}</span>
      </div>

      {/* Header */}
      <div className="bg-card border border-outline-variant rounded-2xl p-6 mb-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl font-bold">{data.name}</h1>
            <p className="text-on-surface-variant">{data.province} Province</p>
          </div>
          <RiskBadge tier={data.risk_aggregate} />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          {[
            { label: "CDF Allocation",  value: fmt(data.cdf_allocation) },
            { label: "Total Projects",  value: data.project_count },
            { label: "Verified",        value: data.verified_count },
            { label: "Verification Rate", value: data.project_count ? `${Math.round((data.verified_count/data.project_count)*100)}%` : "—" },
          ].map(({ label, value }) => (
            <div key={label} className="bg-surface-2 rounded-lg p-3">
              <p className="text-xs text-on-surface-variant">{label}</p>
              <p className="font-display text-xl font-bold">{value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Projects table */}
      <div className="bg-card border border-outline-variant rounded-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-outline-variant flex items-center justify-between">
          <h2 className="font-display font-semibold">Projects</h2>
          <span className="text-xs text-on-surface-variant">De-identified public view</span>
        </div>
        <div className="divide-y divide-outline-variant">
          {SEED_PROJECTS.map(p => (
            <Link key={p.id} to={`/projects/${p.id}`}
              className="px-6 py-4 flex items-center justify-between gap-4 hover:bg-surface-2/50 transition-colors">
              <div className="min-w-0">
                <p className="font-medium text-sm">{p.title}</p>
                <p className="text-xs text-on-surface-variant">{p.category}</p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className={`inline-flex items-center px-2 py-0.5 rounded-full border text-xs font-semibold ${STATUS_STYLE[p.status]}`}>
                  {p.status}
                </span>
                {p.verified && (
                  <span className="inline-flex items-center gap-1 text-xs text-risk-low font-semibold">
                    <span className="material-symbols-outlined text-sm">verified</span>
                    Verified
                  </span>
                )}
                <span className="material-symbols-outlined text-outline text-base">chevron_right</span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
