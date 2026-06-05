import { useQuery } from "@tanstack/react-query";
import { notificationsApi, type NotificationItem } from "../lib/api";

interface Row { icon: string; color: string; title: string; when: string; }

const TYPE_STYLE: Record<string, { icon: string; color: string }> = {
  high_risk:      { icon: "priority_high", color: "text-risk-high" },
  ghost_signal:   { icon: "report", color: "text-accent" },
  confirmation:   { icon: "fact_check", color: "text-info" },
  case_assigned:  { icon: "folder", color: "text-primary" },
};

// Sample fallback — renders fully when the backend is down.
const SAMPLE_ROWS: Row[] = [
  { icon: "priority_high", color: "text-risk-high", title: "New high-risk contract flagged (88/100)", when: "2 hours ago" },
  { icon: "report", color: "text-accent", title: "Ghost-project signal raised — Milenge", when: "2 hours ago" },
  { icon: "fact_check", color: "text-info", title: "Confirmation requested on submission #214", when: "2 hours ago" },
  { icon: "folder", color: "text-primary", title: "Case #001 assigned to you", when: "2 hours ago" },
];

function toRow(n: NotificationItem): Row {
  const style = TYPE_STYLE[n.type] ?? { icon: "notifications", color: "text-on-surface-variant" };
  const title = typeof n.payload?.title === "string" ? (n.payload.title as string) : n.type.replace(/_/g, " ");
  const when = n.created_at ? new Date(n.created_at).toLocaleString() : "2 hours ago";
  return { icon: style.icon, color: style.color, title, when };
}

export default function Notifications() {
  const { data } = useQuery({ queryKey: ["notifications"], queryFn: () => notificationsApi.list().then(r => r.data) });

  const rows: Row[] = data?.notifications && data.notifications.length > 0
    ? data.notifications.map(toRow)
    : SAMPLE_ROWS;

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="disp text-2xl font-bold text-ink">Notifications</h1>
          <p className="text-sm text-on-surface-variant mt-1">Alerts across the system</p>
        </div>
        <div className="flex gap-2"></div>
      </div>

      <div className="bg-card border border-outline-variant rounded-xl p-5">
        {rows.map((r, i) => (
          <a
            key={i}
            href="#"
            className="flex items-center gap-3 py-3 border-b border-outline-variant/60 hover:bg-surface-2/60"
          >
            <span className={`material-symbols-outlined ${r.color}`}>{r.icon}</span>
            <div className="flex-1">
              <p className="text-sm font-semibold">{r.title}</p>
              <p className="text-xs text-on-surface-variant">{r.when}</p>
            </div>
            <span className="text-xs text-primary">view →</span>
          </a>
        ))}
      </div>
    </div>
  );
}
