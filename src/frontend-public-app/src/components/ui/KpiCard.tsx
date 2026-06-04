interface KpiCardProps {
  icon: string;
  label: string;
  value: string | number;
  sub?: string;
  accent?: boolean;
}

export default function KpiCard({ icon, label, value, sub, accent }: KpiCardProps) {
  return (
    <div className={`bg-card border rounded-xl p-5 flex flex-col gap-1 ${accent ? "border-accent/30 bg-accent/5" : "border-outline-variant"}`}>
      <span className="material-symbols-outlined text-2xl text-primary">{icon}</span>
      <p className="text-xs text-on-surface-variant font-medium uppercase tracking-wide mt-1">{label}</p>
      <p className="font-display text-3xl font-bold text-on-surface">{value}</p>
      {sub && <p className="text-xs text-on-surface-variant">{sub}</p>}
    </div>
  );
}
