import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { contractsApi } from "../lib/api";
import CheckRow from "../components/ui/CheckRow";

export default function ContractDetail() {
  const { ocid } = useParams<{ ocid: string }>();

  const { data: contract, isLoading } = useQuery({
    queryKey: ["contract", ocid],
    queryFn: () => contractsApi.get(ocid!).then(r => r.data),
    enabled: !!ocid,
  });
  const { data: checks } = useQuery({
    queryKey: ["contract-checks", ocid],
    queryFn: () => contractsApi.checks(ocid!).then(r => r.data),
    enabled: !!ocid,
  });
  const { data: risk } = useQuery({
    queryKey: ["contract-risk", ocid],
    queryFn: () => contractsApi.risk(ocid!).then(r => r.data).catch(() => null),
    enabled: !!ocid,
  });

  if (isLoading) return <div className="space-y-4">{[...Array(3)].map((_, i) => <div key={i} className="h-32 bg-surface-2 rounded-xl animate-pulse" />)}</div>;
  if (!contract) return (
    <div className="text-center py-16">
      <span className="material-symbols-outlined text-5xl text-outline">search_off</span>
      <p className="font-display text-xl font-bold mt-3">Contract not found</p>
      <Link to="/contracts" className="text-primary hover:underline mt-2 inline-block">← Back to list</Link>
    </div>
  );

  const score = contract.risk_score ?? risk?.normalised_score ?? 0;
  const tier = score >= 70 ? "HIGH — review" : score >= 40 ? "MEDIUM" : "LOW";
  const tierColor = score >= 70 ? "text-risk-high" : score >= 40 ? "text-risk-mid" : "text-risk-low";

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">Contract Detail</h1>
          <p className="text-sm text-on-surface-variant mt-1">Anomaly review · <span className="mono">{contract.ocid}</span></p>
        </div>
      </div>
      <div className="mb-4"><Link to="/contracts" className="text-sm text-on-surface-variant hover:text-ink">← Contract risk list</Link></div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-4">
          {/* Summary */}
          <div className="bg-card border border-outline-variant rounded-xl p-4 flex items-center justify-between">
            <div>
              <p className="mono text-sm">{contract.ocid}</p>
              <p className="text-xs text-on-surface-variant mt-1">
                {contract.procuring_entity} · {contract.supplier?.name ?? "—"} ·
                <span className="mono"> {contract.value ? `K ${contract.value.toLocaleString()}` : "—"}</span>
              </p>
              {contract.award_date && contract.signing_date && (
                <p className="text-xs text-on-surface-variant">Award {contract.award_date} → Signing {contract.signing_date}</p>
              )}
            </div>
            <div className="text-right">
              <p className={`font-display text-3xl font-bold ${tierColor}`}>{score}</p>
              <p className={`text-[11px] font-semibold ${tierColor}`}>{tier}</p>
            </div>
          </div>

          {/* 8 checks */}
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <h3 className="font-display font-semibold text-ink mb-3">Eight integrity checks</h3>
            {checks && checks.length > 0
              ? checks.map(c => <CheckRow key={c.check_id} checkId={c.check_id} checkKey={c.check_key} result={c.result} evidence={c.evidence_note} />)
              : <p className="text-sm text-on-surface-variant py-4">No check results — run analysis for this contract.</p>
            }
          </div>

          <div className="flex gap-2">
            <Link to="/suppliers/network" className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
              <span className="material-symbols-outlined text-base">hub</span>View supplier network
            </Link>
          </div>
        </div>

        {/* Right column */}
        <div className="space-y-4">
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <h3 className="font-display font-semibold text-ink mb-4">Ledger status</h3>
            <div className="flex flex-col items-center text-center gap-2">
              <div className="relative w-32 h-32 rounded-full border-4 border-accent flex items-center justify-center bg-primary/5">
                <span className="text-accent text-5xl">◈</span>
              </div>
              {contract.content_hash ? (
                <>
                  <p className="text-[11px] font-bold tracking-widest text-primary">VERIFIED ON LEDGER</p>
                  <p className="mono text-xs text-on-surface-variant break-all">sha256 {contract.content_hash.slice(0, 16)}…</p>
                </>
              ) : (
                <p className="text-[11px] font-bold tracking-widest text-on-surface-variant">NOT YET ANCHORED</p>
              )}
            </div>
          </div>

          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <h3 className="font-display font-semibold text-ink mb-4">Actions</h3>
            <div className="space-y-2">
              <button className="w-full text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent justify-center">
                <span className="material-symbols-outlined text-base">folder</span>Add to case
              </button>
              <button className="w-full text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-accent text-white justify-center">
                <span className="material-symbols-outlined text-base">priority_high</span>Escalate to ACC
              </button>
              <button className="w-full text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 text-ink hover:bg-surface-2 justify-center">
                <span className="material-symbols-outlined text-base">done</span>Mark reviewed
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
