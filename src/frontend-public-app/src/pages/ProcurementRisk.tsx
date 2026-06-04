// P7 — Procurement Risk Overview (matches design/screens/P7_procurement_risk.html)
// HARD RULE: entity names are "Entity A" … "Entity E" — NO real names on public tier.
import { useQuery } from "@tanstack/react-query";
import { publicApi } from "../lib/api";

function RiskBar({ value, color }: { value: number; color: string }) {
  return (
    <div className="flex-1 h-3 rounded-full bg-surface-2">
      <div className="h-3 rounded-full transition-all duration-500" style={{ width: `${Math.min(value, 100)}%`, background: color }} />
    </div>
  );
}

function riskColor(score: number | null): string {
  if (score == null) return "#6f7974";
  if (score >= 60) return "#B91C1C";
  if (score >= 35) return "#B45309";
  return "#138636";
}

function fmt(n: number | null | undefined): string {
  if (n == null) return "—";
  if (n >= 1_000_000) return `ZMW ${(n / 1_000_000).toFixed(1)}M`;
  return n.toLocaleString();
}

export default function ProcurementRisk() {
  const { data, isLoading } = useQuery({
    queryKey: ["risk-aggregate"],
    queryFn: () => publicApi.riskAggregate().then(r => r.data),
    staleTime: 300_000,
  });

  const entities = data?.entities ?? [];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold">Procurement Risk Overview</h1>
        <p className="text-on-surface-variant mt-1">
          Aggregated, de-identified risk by sector. Entity names are anonymised — named data is available to authorised officers only.
        </p>
      </div>

      {/* Disclaimer banner */}
      <div className="bg-surface-2 border border-outline-variant rounded-lg px-4 py-3 text-sm text-on-surface-variant mb-8 flex items-start gap-3">
        <span className="material-symbols-outlined text-accent mt-0.5">info</span>
        <span>
          All outputs are <strong className="text-on-surface">risk signals requiring review</strong> — not determinations of wrongdoing.
          Anonymised per Zambia Data Protection Act No. 3 of 2021.
        </span>
      </div>

      {/* Bar chart */}
      <div className="bg-card border border-outline-variant rounded-2xl overflow-hidden mb-6">
        <div className="px-6 py-4 border-b border-outline-variant">
          <h2 className="font-display font-semibold">Average Risk Score by Sector</h2>
        </div>
        <div className="px-6 py-4 space-y-4">
          {isLoading
            ? [1,2,3,4,5].map(i => <div key={i} className="h-10 bg-surface-2 rounded animate-pulse" />)
            : entities.map(e => (
                <div key={e.entity_label} className="flex items-center gap-4">
                  <span className="text-xs font-semibold text-on-surface-variant w-16 shrink-0">{e.entity_label}</span>
                  <span className="text-xs text-on-surface-variant w-20 shrink-0">{e.sector}</span>
                  <RiskBar value={e.avg_risk_score ?? 0} color={riskColor(e.avg_risk_score)} />
                  <span className="mono text-xs w-12 text-right font-bold" style={{ color: riskColor(e.avg_risk_score) }}>
                    {e.avg_risk_score?.toFixed(1) ?? "—"}
                  </span>
                </div>
              ))
          }
        </div>
      </div>

      {/* Summary table */}
      <div className="bg-card border border-outline-variant rounded-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-outline-variant">
          <h2 className="font-display font-semibold">Sector Summary</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-surface-2 text-xs text-on-surface-variant uppercase tracking-wide">
              <tr>
                {["Entity","Sector","Contracts","High Risk","Total Value"].map(h => (
                  <th key={h} className="px-6 py-3 text-left font-semibold">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant">
              {isLoading
                ? [1,2,3,4,5].map(i => (
                    <tr key={i}><td colSpan={5}><div className="h-10 m-2 bg-surface-2 rounded animate-pulse" /></td></tr>
                  ))
                : entities.map(e => (
                    <tr key={e.entity_label} className="hover:bg-surface-2/50">
                      <td className="px-6 py-3 font-semibold">{e.entity_label}</td>
                      <td className="px-6 py-3 text-on-surface-variant">{e.sector}</td>
                      <td className="px-6 py-3 mono">{e.contract_count}</td>
                      <td className="px-6 py-3">
                        <span className="inline-flex items-center gap-1 text-risk-high font-semibold">
                          <span className="material-symbols-outlined text-sm">warning</span>
                          {e.high_risk_count}
                        </span>
                      </td>
                      <td className="px-6 py-3 mono text-right">{fmt(e.total_value_zmw)}</td>
                    </tr>
                  ))
              }
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
