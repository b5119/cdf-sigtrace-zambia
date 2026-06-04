type Tier = "high" | "medium" | "low" | null;

const STYLES: Record<string, string> = {
  high:   "bg-risk-high/10 text-risk-high border-risk-high/20",
  medium: "bg-risk-mid/10 text-risk-mid border-risk-mid/20",
  low:    "bg-risk-low/10 text-risk-low border-risk-low/20",
  default:"bg-surface-2 text-on-surface-variant border-outline-variant",
};

export default function RiskBadge({ tier, score }: { tier: Tier; score?: number | null }) {
  const key = tier ?? "default";
  const label = tier ? tier.charAt(0).toUpperCase() + tier.slice(1) : "—";
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border text-xs font-semibold ${STYLES[key]}`}>
      {label}{score != null ? ` · ${score}` : ""}
    </span>
  );
}
