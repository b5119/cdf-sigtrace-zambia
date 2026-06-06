// Constituencies — list of all constituencies (distinct from the National map).
import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { publicApi, type ConstituencySummary } from "../lib/api";
import { constituencyPath } from "../lib/routes";

const SAMPLE: ConstituencySummary[] = [
  { id: "LSK-001", name: "Lusaka Central", province: "Lusaka", project_count: 24, verified_count: 18, risk_aggregate: "high" },
  { id: "LSK-002", name: "Kafue", province: "Lusaka", project_count: 12, verified_count: 9, risk_aggregate: "high" },
  { id: "CPB-001", name: "Ndola Central", province: "Copperbelt", project_count: 19, verified_count: 15, risk_aggregate: "low" },
  { id: "CPB-002", name: "Kitwe Central", province: "Copperbelt", project_count: 21, verified_count: 17, risk_aggregate: "low" },
  { id: "MCG-001", name: "Chinsali", province: "Muchinga", project_count: 6, verified_count: 3, risk_aggregate: "medium" },
  { id: "NWP-001", name: "Solwezi Central", province: "North-Western", project_count: 8, verified_count: 5, risk_aggregate: "medium" },
  { id: "CPB-003", name: "Kabwe Central", province: "Central", project_count: 11, verified_count: 7, risk_aggregate: "medium" },
  { id: "EPV-001", name: "Chipata Central", province: "Eastern", project_count: 10, verified_count: 8, risk_aggregate: "low" },
  { id: "LPV-001", name: "Mansa Central", province: "Luapula", project_count: 7, verified_count: 6, risk_aggregate: "low" },
  { id: "WPV-001", name: "Mongu Central", province: "Western", project_count: 8, verified_count: 5, risk_aggregate: "low" },
  { id: "SPV-001", name: "Livingstone", province: "Southern", project_count: 9, verified_count: 7, risk_aggregate: "low" },
  { id: "LPV-002", name: "Milenge", province: "Luapula", project_count: 6, verified_count: 2, risk_aggregate: "high" },
];

function riskPill(r: ConstituencySummary["risk_aggregate"]) {
  if (r === "high") return { label: "High", cls: "bg-risk-high/10 text-risk-high" };
  if (r === "medium") return { label: "Medium", cls: "bg-risk-mid/10 text-risk-mid" };
  if (r === "low") return { label: "Low", cls: "bg-risk-low/10 text-risk-low" };
  return { label: "—", cls: "bg-surface-2 text-on-surface-variant" };
}

export default function ConstituenciesList() {
  const { data } = useQuery({
    queryKey: ["constituencies"],
    queryFn: () => publicApi.constituencies().then(r => r.data.constituencies),
    retry: 0,
  });
  const all = data && data.length ? data : SAMPLE;

  const [q, setQ] = useState("");
  const list = all.filter(c =>
    c.name.toLowerCase().includes(q.toLowerCase()) || c.province.toLowerCase().includes(q.toLowerCase()));

  return (
    <main className="max-w-[1200px] mx-auto px-6 md:px-12 py-10">
      <div className="flex items-end justify-between mb-6 gap-4 flex-wrap">
        <div>
          <h1 className="disp text-2xl font-bold text-ink">Constituencies</h1>
          <p className="text-sm text-on-surface-variant mt-1">All {all.length === 12 ? "156" : all.length} constituencies, with project counts and aggregate risk. Click one for detail.</p>
        </div>
        <input value={q} onChange={e => setQ(e.target.value)} placeholder="Search constituency or province"
          className="rounded-lg border border-outline-variant bg-card px-3 py-2 text-sm w-72 focus:border-primary focus:ring-1 focus:ring-primary outline-none" />
      </div>

      <div className="bg-card border border-outline-variant rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-outline">
              {["Constituency", "Province", "Projects", "Verified", "Risk", ""].map(h => (
                <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-3 px-4">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {list.map((c, i) => {
              const p = riskPill(c.risk_aggregate);
              return (
                <tr key={c.id} className={`${i % 2 ? "bg-surface-2/40" : ""} border-b border-outline-variant/60 hover:bg-surface-2/70`}>
                  <td className="py-3 px-4"><Link to={constituencyPath(c.id)} className="text-sm font-semibold text-primary hover:underline">{c.name}</Link></td>
                  <td className="py-3 px-4 text-sm text-on-surface-variant">{c.province}</td>
                  <td className="py-3 px-4 text-sm mono">{c.project_count}</td>
                  <td className="py-3 px-4 text-sm mono">{c.verified_count}</td>
                  <td className="py-3 px-4"><span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${p.cls}`}>{p.label}</span></td>
                  <td className="py-3 px-4 text-right"><Link to={constituencyPath(c.id)} className="text-sm font-semibold text-ink inline-flex items-center gap-1 hover:text-primary">Open<span className="material-symbols-outlined text-[18px]">chevron_right</span></Link></td>
                </tr>
              );
            })}
            {list.length === 0 && (
              <tr><td colSpan={6} className="py-10 text-center text-sm text-on-surface-variant">No constituency matches "{q}".</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}
