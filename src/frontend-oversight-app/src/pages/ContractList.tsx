import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { contractsApi } from "../lib/api";
import { contractPath } from "../lib/routes";
import RiskScore from "../components/ui/RiskScore";

export default function ContractList() {
  const [page, setPage] = useState(1);
  const [minScore, setMinScore] = useState<number | undefined>(undefined);
  const size = 20;

  const { data, isLoading } = useQuery({
    queryKey: ["contracts", { page, size, min_score: minScore }],
    queryFn: () => contractsApi.list({ page, size, min_score: minScore }).then(r => r.data),
  });

  const contracts = data?.contracts ?? [];
  const total = data?.total ?? 0;
  const pages = Math.ceil(total / size);

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">Contract Risk List</h1>
          <p className="text-sm text-on-surface-variant mt-1">{total} contracts · sortable by risk score</p>
        </div>
        <div className="flex gap-2 items-center">
          <select value={minScore ?? ""} onChange={e => { setMinScore(e.target.value ? Number(e.target.value) : undefined); setPage(1); }}
            className="text-sm border border-outline-variant rounded-lg px-3 py-2 bg-card">
            <option value="">All scores</option>
            <option value="70">High risk (≥70)</option>
            <option value="40">Medium+ (≥40)</option>
            <option value="1">Any flagged (≥1)</option>
          </select>
        </div>
      </div>

      <div className="bg-card border border-outline-variant rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-surface-2">
              <tr>
                {["OCID", "Procuring Entity", "Supplier", "Value", "Award Date", "Risk", "Status", ""].map(h => (
                  <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-3 px-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading
                ? [...Array(8)].map((_, i) => <tr key={i}><td colSpan={8}><div className="h-10 m-2 bg-surface-2 rounded animate-pulse" /></td></tr>)
                : contracts.map((c, i) => (
                  <tr key={c.ocid} className={`${i % 2 ? "bg-surface-2/40" : ""} border-b border-outline-variant/60 hover:bg-surface-2/70`}>
                    <td className="py-2.5 px-3 text-sm"><Link to={contractPath(c.ocid)} className="mono text-primary hover:underline text-xs">{c.ocid}</Link></td>
                    <td className="py-2.5 px-3 text-sm">{c.procuring_entity}</td>
                    <td className="py-2.5 px-3 text-sm">{c.supplier?.name ?? "—"}</td>
                    <td className="py-2.5 px-3 text-sm mono text-xs">{c.value ? `K ${c.value.toLocaleString()}` : "—"}</td>
                    <td className="py-2.5 px-3 text-sm">{c.award_date ?? "—"}</td>
                    <td className="py-2.5 px-3 text-sm"><RiskScore score={c.risk_score} size="sm" /></td>
                    <td className="py-2.5 px-3 text-sm capitalize">{c.status}</td>
                    <td className="py-2.5 px-3 text-sm">
                      <Link to={contractPath(c.ocid)} className="text-on-surface-variant hover:text-primary">
                        <span className="material-symbols-outlined text-base">chevron_right</span>
                      </Link>
                    </td>
                  </tr>
                ))}
              {!isLoading && contracts.length === 0 && (
                <tr><td colSpan={8} className="py-8 text-center text-on-surface-variant text-sm">No contracts found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
        {pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-outline-variant">
            <span className="text-xs text-on-surface-variant">Page {page} of {pages}</span>
            <div className="flex gap-2">
              <button disabled={page <= 1} onClick={() => setPage(p => p - 1)}
                className="text-sm px-3 py-1.5 rounded border border-outline-variant disabled:opacity-40 hover:bg-surface-2">Prev</button>
              <button disabled={page >= pages} onClick={() => setPage(p => p + 1)}
                className="text-sm px-3 py-1.5 rounded border border-outline-variant disabled:opacity-40 hover:bg-surface-2">Next</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
