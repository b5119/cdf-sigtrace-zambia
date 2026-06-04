// P10 — Public Ledger / Audit Trail (matches design/screens/P10_audit_trail.html)
import { useQuery } from "@tanstack/react-query";
import { publicApi } from "../lib/api";

// Seed ledger events for prototype — real events stream from INC-018 (anchored audit log)
const SEED_EVENTS = [
  { id: "e1", type: "anchor",   ocid: "ocds-zm-zppa-001", hash: "a1b2c3d4e5f6789a",  tx: "mock-tx-9f2a1c",  block: "mock-block-42", time: "2026-06-02T14:22:00Z" },
  { id: "e2", type: "verify",   ocid: "ocds-zm-zppa-001", hash: "a1b2c3d4e5f6789a",  tx: "mock-tx-9f2a1c",  block: "mock-block-42", time: "2026-06-02T15:10:00Z" },
  { id: "e3", type: "anchor",   ocid: "ocds-zm-zppa-005", hash: "b2c3d4e5f6789abc",  tx: "mock-tx-8e1b2d",  block: "mock-block-43", time: "2026-06-02T16:04:00Z" },
  { id: "e4", type: "mismatch", ocid: "ocds-zm-zppa-003", hash: "deadbeef00000001",  tx: null,               block: null,             time: "2026-06-03T09:30:00Z" },
  { id: "e5", type: "anchor",   ocid: "ocds-zm-zppa-006", hash: "c3d4e5f6789abcde",  tx: "mock-tx-7d0c3e",  block: "mock-block-44", time: "2026-06-03T11:00:00Z" },
];

const TYPE_STYLE: Record<string, { icon: string; color: string; label: string }> = {
  anchor:   { icon: "link",    color: "text-primary",   label: "Anchored"  },
  verify:   { icon: "verified",color: "text-risk-low",  label: "Verified"  },
  mismatch: { icon: "warning", color: "text-risk-high", label: "Mismatch"  },
};

function truncate(s: string, n = 12) { return s.length > n ? `${s.slice(0, n)}…` : s; }

export default function AuditTrail() {
  const { data: kpis } = useQuery({
    queryKey: ["overview"],
    queryFn: () => publicApi.overview().then(r => r.data),
    staleTime: 120_000,
  });

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold">Public Ledger</h1>
        <p className="text-on-surface-variant mt-1">
          Immutable record of contract anchoring and verification events on Hyperledger Fabric.
          All events are public; no named data is included.
        </p>
      </div>

      {/* Ledger stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: "Anchored Contracts", value: kpis?.verified_contracts ?? 189, icon: "link" },
          { label: "Ledger",             value: "Hyperledger Fabric 2.5",         icon: "hub" },
          { label: "Chain ID",           value: "sigtrace-channel",               icon: "tag" },
        ].map(({ label, value, icon }) => (
          <div key={label} className="bg-card border border-outline-variant rounded-xl p-4">
            <span className="material-symbols-outlined text-primary text-xl mb-1 block">{icon}</span>
            <p className="font-display text-xl font-bold">{value}</p>
            <p className="text-xs text-on-surface-variant">{label}</p>
          </div>
        ))}
      </div>

      {/* Event feed */}
      <div className="bg-card border border-outline-variant rounded-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-outline-variant flex items-center justify-between">
          <h2 className="font-display font-semibold">Recent Ledger Events</h2>
          <span className="flex items-center gap-1.5 text-xs text-risk-low font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-risk-low animate-pulse" />
            Live
          </span>
        </div>
        <div className="divide-y divide-outline-variant">
          {SEED_EVENTS.map(ev => {
            const style = TYPE_STYLE[ev.type] ?? TYPE_STYLE.verify;
            return (
              <div key={ev.id} className="px-6 py-4 flex items-start gap-4">
                <span className={`material-symbols-outlined text-xl mt-0.5 shrink-0 ${style.color}`}>{style.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`text-xs font-bold uppercase ${style.color}`}>{style.label}</span>
                    <span className="mono text-xs text-on-surface-variant">{ev.ocid}</span>
                  </div>
                  <div className="flex items-center gap-4 mt-1 flex-wrap">
                    <span className="mono text-xs text-on-surface-variant">hash: {truncate(ev.hash, 16)}</span>
                    {ev.tx && <span className="mono text-xs text-on-surface-variant">tx: {truncate(ev.tx, 16)}</span>}
                    {ev.block && <span className="mono text-xs text-on-surface-variant">{ev.block}</span>}
                  </div>
                </div>
                <time className="text-xs text-on-surface-variant shrink-0">
                  {new Date(ev.time).toLocaleString()}
                </time>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
