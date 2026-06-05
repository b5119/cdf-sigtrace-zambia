import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { contractsApi, monitorApi, casesApi } from "../lib/api";
import { ROUTES, contractPath } from "../lib/routes";
import ZambiaMap from "../components/ui/ZambiaMap";

// ── Sample fallbacks (design numbers) — shown when backend is down ──────────────
interface KpiRow { open_flags: number; high_risk: number; ghost_signals: number; open_cases: number; }
const SAMPLE_KPIS: KpiRow = { open_flags: 37, high_risk: 12, ghost_signals: 5, open_cases: 8 };

interface ContractRow { ocid: string; entity: string; score: number; flags: string; }
const SAMPLE_CONTRACTS: ContractRow[] = [
  { ocid: "ocds-zm-000123", entity: "Lusaka CC", score: 88, flags: "2 flags" },
  { ocid: "ocds-zm-000124", entity: "Kafue DC", score: 74, flags: "1 flag" },
  { ocid: "ocds-zm-000125", entity: "Ndola CC", score: 69, flags: "1 flag" },
  { ocid: "ocds-zm-000126", entity: "Kitwe CC", score: 41, flags: "—" },
];

function riskBg(score: number): string {
  return score >= 70 ? "bg-risk-high" : score >= 40 ? "bg-risk-mid" : "bg-risk-low";
}

function KpiCard({ to, label, value, sub, color }: { to: string; label: string; value: number; sub: string; color: string }) {
  return (
    <Link to={to} className="block">
      <div className="bg-card border border-outline-variant rounded-xl p-4 h-full hover:border-primary transition-colors">
        <p className="text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold">{label}</p>
        <p className={`disp text-2xl font-bold mt-1 ${color}`}>{value}</p>
        <p className="text-xs text-on-surface-variant mt-0.5">{sub}</p>
      </div>
    </Link>
  );
}

export default function Dashboard() {
  // Keep live wiring — but always render the full design via sample fallbacks.
  const { data: contractData } = useQuery({
    queryKey: ["contracts", { min_score: 1, size: 50 }],
    queryFn: () => contractsApi.list({ min_score: 1, size: 50 }).then(r => r.data),
  });
  const { data: ghostData } = useQuery({
    queryKey: ["ghost-projects"],
    queryFn: () => monitorApi.ghostQueue().then(r => r.data),
  });
  const { data: casesData } = useQuery({
    queryKey: ["cases"],
    queryFn: () => casesApi.list().then(r => r.data),
  });

  const liveContracts = contractData?.contracts;
  const highRisk = liveContracts?.filter(c => (c.risk_score ?? 0) >= 70).length;

  const kpis: KpiRow = {
    open_flags: liveContracts ? liveContracts.length : SAMPLE_KPIS.open_flags,
    high_risk: highRisk ?? SAMPLE_KPIS.high_risk,
    ghost_signals: ghostData?.total ?? SAMPLE_KPIS.ghost_signals,
    open_cases: casesData?.total ?? SAMPLE_KPIS.open_cases,
  };

  const rows: ContractRow[] = liveContracts && liveContracts.length
    ? liveContracts.slice(0, 4).map(c => ({
        ocid: c.ocid,
        entity: c.procuring_entity,
        score: c.risk_score ?? 0,
        flags: "—",
      }))
    : SAMPLE_CONTRACTS;

  return (
    <div>
      {/* Header */}
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="disp text-2xl font-bold text-ink">Risk Dashboard</h1>
          <p className="text-sm text-on-surface-variant mt-1">System-wide integrity signals across all sources</p>
        </div>
        <div className="flex gap-2">
          <Link to={ROUTES.REPORTS} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
            <span className="material-symbols-outlined">download</span>Export
          </Link>
          <Link to={ROUTES.GHOST_QUEUE} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-accent text-white">
            <span className="material-symbols-outlined">play_arrow</span>Run monitor
          </Link>
        </div>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <KpiCard to={ROUTES.CONTRACTS} label="Open flags" value={kpis.open_flags} sub="needs review" color="text-accent" />
        <KpiCard to={ROUTES.CONTRACTS} label="High-risk contracts" value={kpis.high_risk} sub="≥ 70 score" color="text-risk-high" />
        <KpiCard to={ROUTES.GHOST_QUEUE} label="Ghost signals" value={kpis.ghost_signals} sub="overdue delivery" color="text-accent" />
        <KpiCard to={ROUTES.CASES} label="Open cases" value={kpis.open_cases} sub="2 escalated" color="text-ink" />
      </div>

      {/* Heat-map + Alert feed */}
      <div className="grid grid-cols-3 gap-6 mb-6">
        <div className="col-span-2">
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="disp font-semibold text-ink">Constituency risk heat-map</h3>
              <span className="text-xs text-on-surface-variant">click a marker → contract</span>
            </div>
            <ZambiaMap height="h-72" showControls />
          </div>
        </div>
        <div>
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="disp font-semibold text-ink">Alert feed</h3>
            </div>
            <Link to={contractPath("ocds-zm-000123")} className="flex items-center gap-2 py-2.5 border-b border-outline-variant/60 last:border-0">
              <span className="material-symbols-outlined text-risk-high" style={{ fontSize: "18px" }}>priority_high</span>
              <p className="text-sm flex-1">High-risk contract flagged (88)</p>
            </Link>
            <Link to={ROUTES.GHOST_QUEUE} className="flex items-center gap-2 py-2.5 border-b border-outline-variant/60 last:border-0">
              <span className="material-symbols-outlined text-accent" style={{ fontSize: "18px" }}>report</span>
              <p className="text-sm flex-1">Ghost signal — Milenge</p>
            </Link>
            <Link to={ROUTES.VERIFICATION_REVIEW} className="flex items-center gap-2 py-2.5 border-b border-outline-variant/60 last:border-0">
              <span className="material-symbols-outlined text-info" style={{ fontSize: "18px" }}>fact_check</span>
              <p className="text-sm flex-1">Confirmation requested #214</p>
            </Link>
            <Link to={ROUTES.CASES} className="flex items-center gap-2 py-2.5 border-b border-outline-variant/60 last:border-0">
              <span className="material-symbols-outlined text-primary" style={{ fontSize: "18px" }}>folder</span>
              <p className="text-sm flex-1">Case #001 assigned</p>
            </Link>
          </div>
        </div>
      </div>

      {/* Recent high-risk contracts */}
      <div className="bg-card border border-outline-variant rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="disp font-semibold text-ink">Recent high-risk contracts</h3>
          <Link to={ROUTES.CONTRACTS} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
            <span className="material-symbols-outlined">table_rows</span>View all contracts
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-outline">
                {["OCID", "Entity", "Risk", "Flags", "Anchor", ""].map((h, i) => (
                  <th key={i} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-2 px-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((c, i) => (
                <tr key={c.ocid} className={`${i % 2 ? "bg-surface-2/40" : ""} border-b border-outline-variant/60 hover:bg-surface-2/70`}>
                  <td className="py-2.5 px-3 text-sm">
                    <Link to={contractPath(c.ocid)} className="mono text-primary hover:underline">{c.ocid}</Link>
                  </td>
                  <td className="py-2.5 px-3 text-sm">{c.entity}</td>
                  <td className="py-2.5 px-3 text-sm">
                    <span className={`mono text-white text-xs font-semibold px-2 py-0.5 rounded ${riskBg(c.score)}`}>{c.score}</span>
                  </td>
                  <td className="py-2.5 px-3 text-sm">{c.flags}</td>
                  <td className="py-2.5 px-3 text-sm"><span className="text-risk-low">✓</span></td>
                  <td className="py-2.5 px-3 text-sm">
                    <Link to={contractPath(c.ocid)} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 text-ink hover:bg-surface-2">
                      <span className="material-symbols-outlined">chevron_right</span>Open
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
