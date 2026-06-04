const RESULT_STYLE: Record<string, { color: string; label: string }> = {
  flag: { color: "text-risk-high", label: "FLAG" },
  ok:   { color: "text-risk-low",  label: "OK" },
  skip: { color: "text-on-surface-variant", label: "SKIP" },
};

const CHECK_NAMES: Record<number, string> = {
  1: "Signing completeness", 2: "Standstill (<14d)", 3: "Stage time-gap",
  4: "Document forensics", 5: "Supplier network", 6: "Score variance",
  7: "Amendment value", 8: "Debarment cross-ref",
};

export default function CheckRow({ checkId, checkKey, result, evidence }: {
  checkId: number; checkKey: string; result: string; evidence: string;
}) {
  const style = RESULT_STYLE[result] ?? RESULT_STYLE.skip;
  return (
    <div className="py-3 border-b border-outline-variant/60 last:border-0">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">{checkId} {CHECK_NAMES[checkId] ?? checkKey}</span>
        <span className={`text-xs font-semibold ${style.color}`}>{style.label}</span>
      </div>
      {evidence && <p className="text-xs text-on-surface-variant mt-1">{evidence}</p>}
    </div>
  );
}
