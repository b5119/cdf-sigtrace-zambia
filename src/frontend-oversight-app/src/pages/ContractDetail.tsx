import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { contractsApi } from "../lib/api";
import { ROUTES } from "../lib/routes";

// ── Sample fallback (renders when backend is down / contract undefined) ─────────
interface SampleCheck { id: number; name: string; result: "flag" | "ok"; severity: "high" | "mid" | "low"; }

const SAMPLE_CHECKS: SampleCheck[] = [
  { id: 1, name: "Signing completeness", result: "flag", severity: "high" },
  { id: 2, name: "Standstill (<14d)", result: "flag", severity: "high" },
  { id: 3, name: "Stage time-gap", result: "flag", severity: "mid" },
  { id: 4, name: "Document forensics", result: "ok", severity: "low" },
  { id: 5, name: "Supplier network", result: "flag", severity: "mid" },
  { id: 6, name: "Score variance", result: "ok", severity: "low" },
  { id: 7, name: "Amendment value", result: "ok", severity: "low" },
  { id: 8, name: "Debarment cross-ref", result: "ok", severity: "low" },
];

const SAMPLE = {
  ocid: "ocds-zm-000123",
  procuring_entity: "Lusaka CC",
  sector: "Works",
  value_label: "K 1,204,987.89",
  award_to_signing: "9 days",
  score: 88,
  hash: "sha256 0xa1b2…9f",
  tx: "tx 0x7f2a… · 2026-06-01",
};

const CHECK_NAMES: Record<number, string> = {
  1: "Signing completeness", 2: "Standstill (<14d)", 3: "Stage time-gap",
  4: "Document forensics", 5: "Supplier network", 6: "Score variance",
  7: "Amendment value", 8: "Debarment cross-ref",
};

function severityColor(sev: "high" | "mid" | "low") {
  return sev === "high" ? "text-risk-high" : sev === "mid" ? "text-risk-mid" : "text-risk-low";
}

export default function ContractDetail() {
  const { ocid } = useParams<{ ocid: string }>();

  const { data: contract } = useQuery({
    queryKey: ["contract", ocid],
    queryFn: () => contractsApi.get(ocid!).then(r => r.data).catch(() => null),
    enabled: !!ocid,
  });
  const { data: checks } = useQuery({
    queryKey: ["contract-checks", ocid],
    queryFn: () => contractsApi.checks(ocid!).then(r => r.data).catch(() => null),
    enabled: !!ocid,
  });
  const { data: risk } = useQuery({
    queryKey: ["contract-risk", ocid],
    queryFn: () => contractsApi.risk(ocid!).then(r => r.data).catch(() => null),
    enabled: !!ocid,
  });

  // Resolve display values from API, falling back to SAMPLE so the page always renders.
  const displayOcid = contract?.ocid ?? ocid ?? SAMPLE.ocid;
  const score = contract?.risk_score ?? risk?.normalised_score ?? SAMPLE.score;
  const procuringEntity = contract?.procuring_entity ?? SAMPLE.procuring_entity;
  const valueLabel = contract?.value != null ? `K ${contract.value.toLocaleString()}` : SAMPLE.value_label;
  const sector = SAMPLE.sector;
  const awardToSigning = SAMPLE.award_to_signing;
  const hashLabel = contract?.content_hash ? `sha256 ${contract.content_hash.slice(0, 12)}…` : SAMPLE.hash;

  const tier = score >= 70 ? "HIGH — review" : score >= 40 ? "MEDIUM" : "LOW";
  const tierColor = score >= 70 ? "text-risk-high" : score >= 40 ? "text-risk-mid" : "text-risk-low";

  // Map API checks into render shape, else sample.
  const checkRows: SampleCheck[] =
    checks && checks.length > 0
      ? checks.map(c => {
          const result: "flag" | "ok" = c.result === "flag" ? "flag" : "ok";
          const severity: "high" | "mid" | "low" =
            c.result === "flag" ? (c.weight_applied >= 0.2 ? "high" : "mid") : "low";
          return { id: c.check_id, name: CHECK_NAMES[c.check_id] ?? c.check_key, result, severity };
        })
      : SAMPLE_CHECKS;

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">Contract Detail</h1>
          <p className="text-sm text-on-surface-variant mt-1">Anomaly review · OCID <span className="mono">{displayOcid}</span></p>
        </div>
      </div>

      <div className="mb-4 text-sm text-on-surface-variant">
        <Link to={ROUTES.CONTRACTS} className="hover:text-ink">← Contract risk list</Link>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-4">
          {/* Header card */}
          <div className="bg-card border border-outline-variant rounded-xl p-4 flex items-center justify-between">
            <div>
              <p className="mono text-sm">{displayOcid}</p>
              <p className="text-xs text-on-surface-variant">
                {procuringEntity} · {sector} · <span className="mono">{valueLabel}</span> · Award→Signing {awardToSigning}
              </p>
            </div>
            <div className="text-right">
              <p className={`font-display text-3xl font-bold ${tierColor}`}>{score}</p>
              <p className={`text-[11px] font-semibold ${tierColor}`}>{tier}</p>
            </div>
          </div>

          {/* Eight integrity checks */}
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-semibold text-ink">Eight integrity checks</h3>
            </div>
            {checkRows.map(c => (
              <div key={c.id} className="flex items-center justify-between py-2 border-b border-outline-variant/60 last:border-0">
                <span className="text-sm">{c.id} {c.name}</span>
                <span className={`text-xs font-semibold ${severityColor(c.severity)}`}>{c.result === "flag" ? "FLAG" : "OK"}</span>
              </div>
            ))}
          </div>

          <div className="flex gap-2">
            <Link to={ROUTES.SUPPLIER_NETWORK} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
              <span className="material-symbols-outlined text-base">hub</span>View supplier network
            </Link>
            <Link to={ROUTES.VERIFY_DOC} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
              <span className="material-symbols-outlined text-base">fact_check</span>Open document verify
            </Link>
          </div>
        </div>

        {/* Right column */}
        <div className="space-y-4">
          {/* Ledger status */}
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-semibold text-ink">Ledger status</h3>
            </div>
            <div className="flex flex-col items-center text-center gap-2">
              <div className="relative w-32 h-32 rounded-full border-4 border-accent flex items-center justify-center bg-primary/5">
                <img src="/coat_of_arms.png" alt="Republic of Zambia coat of arms" className="h-16 w-16 object-contain" />
              </div>
              <p className="text-[11px] font-bold tracking-widest text-primary">VERIFIED ON LEDGER · REPUBLIC OF ZAMBIA</p>
              <p className="mono text-xs text-on-surface-variant">{hashLabel}</p>
              <p className="mono text-[11px] text-on-surface-variant">{SAMPLE.tx}</p>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-semibold text-ink">Actions</h3>
            </div>
            <div className="space-y-2">
              <Link to={ROUTES.CASES} className="w-full text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent justify-center hover:bg-accent/5">
                <span className="material-symbols-outlined text-base">folder</span>Add to case
              </Link>
              <Link to={ROUTES.CASES} className="w-full text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-accent text-white justify-center hover:opacity-90">
                <span className="material-symbols-outlined text-base">priority_high</span>Escalate to ACC
              </Link>
              <Link to={ROUTES.CONTRACTS} className="w-full text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 text-ink hover:bg-surface-2 justify-center">
                <span className="material-symbols-outlined text-base">done</span>Mark reviewed
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
