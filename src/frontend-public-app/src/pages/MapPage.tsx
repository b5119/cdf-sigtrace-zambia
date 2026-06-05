// P3 — National Project Map. Full-bleed choropleth + institutional filters + constituency detail drawer.
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { publicApi, type MapFeature } from "../lib/api";
import ZambiaMap from "../components/ui/ZambiaMap";
import { constituencyPath } from "../lib/routes";

// Risk colour matching the reference design legend (#138636 / #B45309 / #B91C1C).
function riskColor(s: number | null): string {
  if (s == null) return "#6f7974";
  return s >= 70 ? "#B91C1C" : s >= 40 ? "#B45309" : "#138636";
}

function riskNote(s: number | null): string {
  if (s == null) return "Awaiting ledger reconciliation.";
  if (s >= 70) return "Critical variance detected between ledger and field audits.";
  if (s >= 40) return "Moderate variance pending field review.";
  return "Minimal variance detected between ledger and field audits.";
}

function fmtZmk(v: number | null): string {
  if (v == null) return "—";
  if (v >= 1_000_000_000) return `ZMK ${(v / 1_000_000_000).toFixed(1)}B`;
  if (v >= 1_000_000) return `ZMK ${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `ZMK ${(v / 1_000).toFixed(0)}K`;
  return `ZMK ${v}`;
}

// Design sample fallback so the page renders before / without live API data.
const SAMPLE: MapFeature[] = [
  { id: "LSK-001", name: "Lusaka", province: "Lusaka", lat: 0, lng: 0, project_count: 24, verified_count: 18, risk_score: 82, risk_tier: "high", cdf_allocation: 14_200_000 },
  { id: "LSK-002", name: "Kafue", province: "Lusaka", lat: 0, lng: 0, project_count: 12, verified_count: 7, risk_score: 71, risk_tier: "high", cdf_allocation: 8_400_000 },
  { id: "MCG-001", name: "Chinsali", province: "Muchinga", lat: 0, lng: 0, project_count: 9, verified_count: 5, risk_score: 57, risk_tier: "medium", cdf_allocation: 6_100_000 },
  { id: "NWP-001", name: "Solwezi", province: "North-Western", lat: 0, lng: 0, project_count: 11, verified_count: 8, risk_score: 46, risk_tier: "medium", cdf_allocation: 7_300_000 },
  { id: "CPB-003", name: "Kabwe", province: "Central", lat: 0, lng: 0, project_count: 14, verified_count: 11, risk_score: 40, risk_tier: "medium", cdf_allocation: 9_000_000 },
  { id: "CPB-001", name: "Ndola", province: "Copperbelt", lat: 0, lng: 0, project_count: 19, verified_count: 16, risk_score: 38, risk_tier: "low", cdf_allocation: 12_800_000 },
  { id: "EPV-001", name: "Chipata", province: "Eastern", lat: 0, lng: 0, project_count: 13, verified_count: 11, risk_score: 34, risk_tier: "low", cdf_allocation: 7_900_000 },
  { id: "CPB-002", name: "Kitwe", province: "Copperbelt", lat: 0, lng: 0, project_count: 21, verified_count: 19, risk_score: 33, risk_tier: "low", cdf_allocation: 13_500_000 },
  { id: "LPV-001", name: "Mansa", province: "Luapula", lat: 0, lng: 0, project_count: 8, verified_count: 7, risk_score: 29, risk_tier: "low", cdf_allocation: 5_400_000 },
  { id: "WPV-001", name: "Mongu", province: "Western", lat: 0, lng: 0, project_count: 7, verified_count: 6, risk_score: 26, risk_tier: "low", cdf_allocation: 4_800_000 },
  { id: "SPV-001", name: "Livingstone", province: "Southern", lat: 0, lng: 0, project_count: 10, verified_count: 9, risk_score: 21, risk_tier: "low", cdf_allocation: 6_700_000 },
];

export default function MapPage() {
  const { data } = useQuery({ queryKey: ["map"], queryFn: () => publicApi.map().then(r => r.data), staleTime: 300_000 });

  const features = useMemo(() => {
    const src = data?.features && data.features.length ? data.features : SAMPLE;
    return src.slice().sort((a, b) => (b.risk_score ?? 0) - (a.risk_score ?? 0));
  }, [data]);

  const riskById: Record<string, number> = {};
  features.forEach(f => { if (f.risk_score != null) riskById[f.id] = f.risk_score; });

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selected = features.find(f => f.id === selectedId) ?? null;

  const totalBudget = features.reduce((acc, f) => acc + (f.cdf_allocation ?? 0), 0);

  return (
    <main className="relative flex flex-col flex-1 overflow-hidden bg-surface-2 min-h-[680px]">
      {/* Filters overlay */}
      <div className="absolute top-6 left-6 z-30 w-72 flex flex-col gap-4">
        <div className="bg-card/95 backdrop-blur-md p-6 rounded-xl border border-outline-variant shadow-sm">
          <h3 className="text-[12px] font-bold uppercase tracking-[0.05em] mb-4 text-ink/60 border-b border-outline-variant pb-2">
            Institutional Filters
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-[0.05em] text-on-surface-variant mb-1">Province</label>
              <select className="w-full bg-surface border border-outline-variant rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary">
                <option>All 10 Provinces</option>
                <option>Lusaka</option>
                <option>Copperbelt</option>
                <option>Central</option>
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-[0.05em] text-on-surface-variant mb-1">Development Sector</label>
              <select className="w-full bg-surface border border-outline-variant rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary">
                <option>All Sectors</option>
                <option>Health &amp; Sanitation</option>
                <option>Education</option>
                <option>Infrastructure</option>
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-[0.05em] text-on-surface-variant mb-1">Audit Status</label>
              <div className="flex flex-col gap-2 mt-2">
                {([["Verified", "#138636"], ["Pending", "#B45309"], ["Mismatch", "#B91C1C"]] as const).map(([label, color]) => (
                  <label key={label} className="flex items-center gap-2 cursor-pointer">
                    <input defaultChecked className="rounded border-outline-variant text-primary focus:ring-primary" type="checkbox" />
                    <span className="text-sm flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full" style={{ background: color }} /> {label}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-card/95 backdrop-blur-md p-6 rounded-xl border border-outline-variant shadow-sm">
          <h3 className="text-[12px] font-bold uppercase tracking-[0.05em] mb-2 text-ink/60">National Aggregate</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="mono text-[20px] font-bold text-primary">{features.length}</p>
              <p className="text-[10px] font-bold uppercase tracking-[0.05em] text-on-surface-variant">Constituencies</p>
            </div>
            <div>
              <p className="mono text-[20px] font-bold text-accent">{fmtZmk(totalBudget)}</p>
              <p className="text-[10px] font-bold uppercase tracking-[0.05em] text-on-surface-variant">Total Budget</p>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive map */}
      <div className="flex-1 w-full h-full relative">
        <ZambiaMap riskById={riskById} height="h-full" showControls />
      </div>

      {/* Side drawer — constituency detail */}
      {selected && (
        <div className="absolute inset-y-0 right-0 w-full max-w-[420px] bg-card shadow-2xl z-50 flex flex-col border-l border-outline-variant transition-transform duration-300 ease-in-out">
          <div className="p-4 flex justify-between items-center border-b border-outline-variant">
            <h2 className="disp text-2xl font-bold">{selected.name}</h2>
            <button
              onClick={() => setSelectedId(null)}
              className="p-2 hover:bg-surface-2 rounded-full transition-colors"
              aria-label="Close detail"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {/* Verification seal */}
            <div className="flex justify-center py-4">
              <div className="relative w-32 h-32 rounded-full border border-accent flex flex-col items-center justify-center p-4 text-center">
                <div className="w-12 h-12 mb-1 rounded-full bg-surface-container flex items-center justify-center">
                  <span className="material-symbols-outlined text-accent">verified_user</span>
                </div>
                <p className="text-[8px] font-bold uppercase tracking-[0.05em] leading-tight text-accent">
                  Verified on Ledger<br />Republic of Zambia
                </p>
                <div className="absolute -bottom-2 bg-card px-2">
                  <span className="mono text-[9px] text-on-surface-variant">{selected.id.toLowerCase()}</span>
                </div>
              </div>
            </div>

            {/* Risk gauge */}
            <div className="bg-surface rounded-xl p-4 border border-outline-variant">
              <div className="flex justify-between items-end mb-2">
                <p className="text-[11px] font-bold uppercase tracking-[0.05em] text-on-surface-variant">Aggregated Risk Score</p>
                <p className="mono text-2xl" style={{ color: riskColor(selected.risk_score) }}>
                  {selected.risk_score ?? "—"}/100
                </p>
              </div>
              <div className="w-full h-3 bg-surface-container rounded-full overflow-hidden">
                <div
                  className="h-full transition-all duration-500"
                  style={{ width: `${selected.risk_score ?? 0}%`, background: riskColor(selected.risk_score) }}
                />
              </div>
              <p className="text-[12px] text-on-surface-variant mt-2 italic">{riskNote(selected.risk_score)}</p>
            </div>

            {/* Stat cards */}
            <div className="grid grid-cols-2 gap-4">
              <div className="border border-outline-variant p-4 rounded-xl">
                <p className="text-[10px] font-bold uppercase tracking-[0.05em] text-on-surface-variant">Allocated</p>
                <p className="mono text-[18px] font-bold">{fmtZmk(selected.cdf_allocation)}</p>
              </div>
              <div className="border border-outline-variant p-4 rounded-xl">
                <p className="text-[10px] font-bold uppercase tracking-[0.05em] text-on-surface-variant">Projects</p>
                <p className="mono text-[18px] font-bold">{selected.project_count} Active</p>
              </div>
            </div>

            {/* Verified count card */}
            <div className="space-y-3">
              <h3 className="text-[12px] font-bold uppercase tracking-[0.05em] text-on-surface-variant flex items-center gap-2">
                <span className="material-symbols-outlined text-[18px]">list_alt</span> Audit Coverage
              </h3>
              <div className="space-y-2">
                <div className="p-4 bg-surface rounded-lg border border-outline-variant flex justify-between items-start">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[11px] font-bold uppercase tracking-[0.05em] bg-primary/10 text-primary px-2 py-0.5 rounded">Verified</span>
                    </div>
                    <h4 className="font-bold text-sm mb-1">{selected.verified_count} of {selected.project_count} projects reconciled</h4>
                    <p className="text-[13px] text-on-surface-variant line-clamp-1">{selected.province} Province · On-ledger audit</p>
                  </div>
                </div>
                <div className="p-4 bg-surface rounded-lg border border-outline-variant flex justify-between items-start">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[11px] font-bold uppercase tracking-[0.05em] bg-accent/10 text-accent px-2 py-0.5 rounded">Risk</span>
                    </div>
                    <h4 className="font-bold text-sm mb-1">{selected.risk_tier ? `${selected.risk_tier} tier` : "Tier pending"}</h4>
                    <p className="text-[13px] text-on-surface-variant line-clamp-1">{riskNote(selected.risk_score)}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="p-4 bg-surface border-t border-outline-variant">
            <Link
              to={constituencyPath(selected.id)}
              className="w-full bg-primary text-white py-3 rounded-xl font-bold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
            >
              <span className="material-symbols-outlined">analytics</span>
              Generate Constituency Report
            </Link>
          </div>
        </div>
      )}

      {/* Constituency list overlay (right) — visible when no drawer open */}
      {!selected && (
        <div className="absolute top-6 right-6 z-30 w-72 bg-card/95 backdrop-blur-md rounded-xl border border-outline-variant shadow-sm flex flex-col max-h-[calc(100%-3rem)]">
          <p className="text-[12px] font-bold uppercase tracking-[0.05em] text-ink/60 px-6 pt-6 pb-2 border-b border-outline-variant">
            Constituencies ({features.length})
          </p>
          <div className="flex flex-col gap-2 overflow-y-auto p-4">
            {features.map(f => (
              <button
                key={f.id}
                onClick={() => setSelectedId(f.id)}
                className="text-left bg-surface border border-outline-variant rounded-lg p-3 hover:border-primary transition-colors flex items-center justify-between gap-3 group"
              >
                <div className="min-w-0">
                  <p className="font-medium text-sm truncate">{f.name}</p>
                  <p className="text-xs text-on-surface-variant truncate">{f.province} · {f.project_count} projects</p>
                </div>
                <span
                  className="text-xs font-semibold px-2 py-0.5 rounded-full shrink-0"
                  style={{ background: `${riskColor(f.risk_score)}1a`, color: riskColor(f.risk_score) }}
                >
                  {f.risk_score ?? "—"}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}
