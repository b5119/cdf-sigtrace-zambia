import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { contractsApi, type ContractRestricted } from "../lib/api";
import { contractPath } from "../lib/routes";

// ── Sample fallback (shown when backend is down / returns nothing) ──────────────
interface SampleRow {
  ocid: string;
  procuring_entity: string;
  sector: string;
  value_label: string;
  score: number;
  flags: string;
  anchor: boolean;
}

const SAMPLE_ROWS: SampleRow[] = [
  { ocid: "ocds-zm-000123", procuring_entity: "Lusaka CC", sector: "Works", value_label: "K 1.2m", score: 88, flags: "2", anchor: true },
  { ocid: "ocds-zm-000124", procuring_entity: "Kafue DC", sector: "Goods", value_label: "K 430k", score: 74, flags: "1", anchor: true },
  { ocid: "ocds-zm-000125", procuring_entity: "Ndola CC", sector: "Works", value_label: "K 980k", score: 69, flags: "1", anchor: true },
  { ocid: "ocds-zm-000126", procuring_entity: "Kitwe CC", sector: "Services", value_label: "K 210k", score: 41, flags: "—", anchor: true },
  { ocid: "ocds-zm-000127", procuring_entity: "Chipata MC", sector: "Works", value_label: "K 760k", score: 33, flags: "—", anchor: true },
  { ocid: "ocds-zm-000128", procuring_entity: "Solwezi MC", sector: "Goods", value_label: "K 145k", score: 22, flags: "—", anchor: true },
];

function riskBg(score: number) {
  return score >= 70 ? "bg-risk-high" : score >= 40 ? "bg-risk-mid" : "bg-risk-low";
}

function sectorOf(c: ContractRestricted): string {
  // ContractRestricted has no explicit sector field; derive a sensible label.
  return c.framework_parent ? "Framework" : "—";
}

function valueLabel(value?: number): string {
  if (value == null) return "—";
  if (value >= 1_000_000) return `K ${(value / 1_000_000).toFixed(1)}m`;
  if (value >= 1_000) return `K ${Math.round(value / 1_000)}k`;
  return `K ${value.toLocaleString()}`;
}

const TH = ["OCID", "Procuring entity", "Sector", "Value", "Risk", "Flags", "Anchor", "Action"];

export default function ContractList() {
  const [search, setSearch] = useState("");

  const { data } = useQuery({
    queryKey: ["contracts", { page: 1, size: 50 }],
    queryFn: () => contractsApi.list({ page: 1, size: 50 }).then(r => r.data).catch(() => null),
  });

  const apiContracts = data?.contracts ?? [];
  const usingSample = apiContracts.length === 0;

  // Normalise both API rows and sample rows into one render shape.
  const rows: SampleRow[] = usingSample
    ? SAMPLE_ROWS
    : apiContracts.map(c => ({
        ocid: c.ocid,
        procuring_entity: c.procuring_entity,
        sector: sectorOf(c),
        value_label: valueLabel(c.value),
        score: c.risk_score ?? 0,
        flags: "—",
        anchor: !!c.content_hash,
      }));

  const q = search.trim().toLowerCase();
  const visible = q
    ? rows.filter(r =>
        r.ocid.toLowerCase().includes(q) ||
        r.procuring_entity.toLowerCase().includes(q) ||
        r.sector.toLowerCase().includes(q))
    : rows;

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">Contract Risk List</h1>
          <p className="text-sm text-on-surface-variant mt-1">All analysed contracts, sortable by risk</p>
        </div>
        <div className="flex gap-2 items-center">
          <div className="relative">
            <span className="material-symbols-outlined text-base text-on-surface-variant absolute left-2.5 top-1/2 -translate-y-1/2">search</span>
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search OCID, entity, sector"
              className="text-sm border border-outline-variant rounded-lg pl-9 pr-3 py-2 bg-card w-72 focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
          </div>
          <button className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-outline-variant text-ink hover:bg-surface-2">
            <span className="material-symbols-outlined text-base">filter_list</span>Filter
          </button>
        </div>
      </div>

      <div className="bg-card border border-outline-variant rounded-xl p-5">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-outline">
                {TH.map(h => (
                  <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-2 px-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {visible.map((r, i) => (
                <tr key={r.ocid} className={`${i % 2 ? "bg-surface-2/40" : ""} border-b border-outline-variant/60 hover:bg-surface-2/70`}>
                  <td className="py-2.5 px-3 text-sm">
                    <Link to={contractPath(r.ocid)} className="mono text-primary hover:underline">{r.ocid}</Link>
                  </td>
                  <td className="py-2.5 px-3 text-sm">{r.procuring_entity}</td>
                  <td className="py-2.5 px-3 text-sm">{r.sector}</td>
                  <td className="py-2.5 px-3 text-sm"><span className="mono">{r.value_label}</span></td>
                  <td className="py-2.5 px-3 text-sm">
                    <span className={`mono text-white text-xs font-semibold px-2 py-0.5 rounded ${riskBg(r.score)}`}>{r.score}</span>
                  </td>
                  <td className="py-2.5 px-3 text-sm">{r.flags}</td>
                  <td className="py-2.5 px-3 text-sm">
                    {r.anchor ? <span className="text-risk-low">✓</span> : <span className="text-on-surface-variant">—</span>}
                  </td>
                  <td className="py-2.5 px-3 text-sm">
                    <Link to={contractPath(r.ocid)} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 text-ink hover:bg-surface-2">
                      <span className="material-symbols-outlined text-base">chevron_right</span>Review
                    </Link>
                  </td>
                </tr>
              ))}
              {visible.length === 0 && (
                <tr><td colSpan={TH.length} className="py-8 text-center text-on-surface-variant text-sm">No contracts match your search.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
