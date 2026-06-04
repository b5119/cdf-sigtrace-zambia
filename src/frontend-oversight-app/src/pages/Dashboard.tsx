import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { contractsApi } from "../lib/api";
import { contractPath } from "../lib/routes";
import RiskScore from "../components/ui/RiskScore";

function KpiCard({ label, value, sub, color }: { label: string; value: string | number; sub: string; color: string }) {
  return (
    <div className="bg-card border border-outline-variant rounded-xl p-4 hover:border-primary transition-colors">
      <p className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">{label}</p>
      <p className={`font-display text-2xl font-bold mt-1 ${color}`}>{value}</p>
      <p className="text-xs text-on-surface-variant mt-0.5">{sub}</p>
    </div>
  );
}

export default function Dashboard() {
  const { data } = useQuery({
    queryKey: ["contracts", { min_score: 1, size: 50 }],
    queryFn: () => contractsApi.list({ min_score: 1, size: 50 }).then(r => r.data),
  });

  const contracts = data?.contracts ?? [];
  const highRisk = contracts.filter(c => (c.risk_score ?? 0) >= 70);
  const recent = contracts.slice(0, 6);

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">Risk Dashboard</h1>
          <p className="text-sm text-on-surface-variant mt-1">System-wide integrity signals across all sources</p>
        </div>
        <div className="flex gap-2">
          <button className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
            <span className="material-symbols-outlined text-base">download</span>Export
          </button>
          <button className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-accent text-white">
            <span className="material-symbols-outlined text-base">play_arrow</span>Run monitor
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        <KpiCard label="Total contracts" value={data?.total ?? 0} sub="in registry" color="text-ink" />
        <KpiCard label="High-risk contracts" value={highRisk.length} sub="≥ 70 score" color="text-risk-high" />
        <KpiCard label="Scored" value={contracts.length} sub="with risk score" color="text-accent" />
        <KpiCard label="Open cases" value={0} sub="under review" color="text-ink" />
      </div>

      <div className="bg-card border border-outline-variant rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display font-semibold text-ink">Recent high-risk contracts</h3>
          <Link to="/contracts" className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
            <span className="material-symbols-outlined text-base">table_rows</span>View all
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-outline">
                {["OCID", "Entity", "Risk", "Status", ""].map(h => (
                  <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-2 px-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {recent.map((c, i) => (
                <tr key={c.ocid} className={`${i % 2 ? "bg-surface-2/40" : ""} border-b border-outline-variant/60 hover:bg-surface-2/70`}>
                  <td className="py-2.5 px-3 text-sm">
                    <Link to={contractPath(c.ocid)} className="mono text-primary hover:underline">{c.ocid}</Link>
                  </td>
                  <td className="py-2.5 px-3 text-sm">{c.procuring_entity}</td>
                  <td className="py-2.5 px-3 text-sm"><RiskScore score={c.risk_score} size="sm" /></td>
                  <td className="py-2.5 px-3 text-sm capitalize">{c.status}</td>
                  <td className="py-2.5 px-3 text-sm">
                    <Link to={contractPath(c.ocid)} className="text-sm font-semibold px-3 py-1.5 rounded-lg inline-flex items-center gap-1 text-ink hover:bg-surface-2">
                      Open <span className="material-symbols-outlined text-base">chevron_right</span>
                    </Link>
                  </td>
                </tr>
              ))}
              {recent.length === 0 && (
                <tr><td colSpan={5} className="py-8 text-center text-on-surface-variant text-sm">
                  No contracts scored yet. Run ingestion + analysis to populate.
                </td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
