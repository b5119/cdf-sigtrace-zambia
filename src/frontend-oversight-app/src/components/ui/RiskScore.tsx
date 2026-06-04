export default function RiskScore({ score, size = "md" }: { score?: number | null; size?: "sm" | "md" | "lg" }) {
  const s = score ?? 0;
  const color = s >= 70 ? "bg-risk-high" : s >= 40 ? "bg-risk-mid" : "bg-risk-low";
  const sizes = { sm: "text-xs px-2 py-0.5", md: "text-sm px-2.5 py-1", lg: "text-2xl px-4 py-2" };
  return (
    <span className={`mono text-white font-semibold rounded ${color} ${sizes[size]}`}>
      {score ?? "—"}
    </span>
  );
}
