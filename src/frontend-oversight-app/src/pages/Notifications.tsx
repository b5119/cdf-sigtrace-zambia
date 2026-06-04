import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notificationsApi } from "../lib/api";

const TYPE_STYLE: Record<string, { icon: string; color: string }> = {
  case_opened:    { icon: "folder", color: "text-primary" },
  case_assigned:  { icon: "assignment_ind", color: "text-info" },
  case_escalated: { icon: "priority_high", color: "text-risk-high" },
  high_risk:      { icon: "warning", color: "text-risk-high" },
  ghost_signal:   { icon: "report", color: "text-accent" },
};

function label(type: string, payload: Record<string, unknown>): string {
  switch (type) {
    case "case_opened":    return `Case opened: ${payload.title ?? ""}`;
    case "case_assigned":  return `Case assigned to you: ${payload.title ?? ""}`;
    case "case_escalated": return `Case escalated to ${payload.target ?? "ACC"}: ${payload.title ?? ""}`;
    default:               return type.replace(/_/g, " ");
  }
}

export default function Notifications() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["notifications"], queryFn: () => notificationsApi.list().then(r => r.data) });
  const readM = useMutation({
    mutationFn: (id: string) => notificationsApi.markRead(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const items = data?.notifications ?? [];

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink mb-1">Notifications</h1>
      <p className="text-sm text-on-surface-variant mb-6">{data?.unread ?? 0} unread of {data?.total ?? 0}</p>

      <div className="bg-card border border-outline-variant rounded-xl divide-y divide-outline-variant/60">
        {items.map(n => {
          const style = TYPE_STYLE[n.type] ?? { icon: "notifications", color: "text-on-surface-variant" };
          return (
            <div key={n.id} className={`flex items-center gap-3 px-5 py-4 ${n.read ? "opacity-60" : ""}`}>
              <span className={`material-symbols-outlined ${style.color}`}>{style.icon}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm">{label(n.type, n.payload)}</p>
                <p className="text-xs text-on-surface-variant">{new Date(n.created_at).toLocaleString()}</p>
              </div>
              {!n.read && (
                <button onClick={() => readM.mutate(n.id)}
                  className="text-xs font-semibold text-primary hover:underline">Mark read</button>
              )}
            </div>
          );
        })}
        {items.length === 0 && <p className="px-5 py-8 text-center text-on-surface-variant text-sm">No notifications.</p>}
      </div>
    </div>
  );
}
