const NOTIFS = [
  { icon: "priority_high", color: "text-risk-high", text: "High-risk contract flagged (88)", time: "2h ago" },
  { icon: "report", color: "text-accent", text: "Ghost signal — Milenge constituency", time: "5h ago" },
  { icon: "fact_check", color: "text-info", text: "Confirmation requested #214", time: "1d ago" },
  { icon: "folder", color: "text-primary", text: "Case #001 assigned to you", time: "2d ago" },
];
export default function Notifications() {
  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink mb-1">Notifications</h1>
      <p className="text-sm text-on-surface-variant mb-6">Alerts: new high-risk, ghost signals, confirmation requests</p>
      <div className="bg-card border border-outline-variant rounded-xl divide-y divide-outline-variant/60">
        {NOTIFS.map((n, i) => (
          <div key={i} className="flex items-center gap-3 px-5 py-4">
            <span className={`material-symbols-outlined ${n.color}`}>{n.icon}</span>
            <p className="text-sm flex-1">{n.text}</p>
            <time className="text-xs text-on-surface-variant">{n.time}</time>
          </div>
        ))}
      </div>
    </div>
  );
}
