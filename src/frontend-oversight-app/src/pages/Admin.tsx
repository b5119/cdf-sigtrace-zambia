import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, type WeightItem } from "../lib/api";

const TABS = ["Health", "Users", "Weights", "Thresholds", "Ledger"] as const;
type Tab = typeof TABS[number];

const STATUS_DOT: Record<string, string> = {
  ok: "bg-risk-low", live: "bg-risk-low", configured: "bg-info",
  mock: "bg-accent", degraded: "bg-risk-mid", error: "bg-risk-high", not_configured: "bg-outline",
};

function HealthTab() {
  const { data } = useQuery({ queryKey: ["admin-health"], queryFn: () => adminApi.health().then(r => r.data) });
  return (
    <div className="bg-card border border-outline-variant rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-display font-semibold">System Health</h3>
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${data?.status === "ok" ? "bg-risk-low/10 text-risk-low" : "bg-risk-mid/10 text-risk-mid"}`}>{data?.status ?? "…"}</span>
      </div>
      <div className="grid grid-cols-2 gap-3">
        {Object.entries(data?.components ?? {}).map(([k, v]) => (
          <div key={k} className="flex items-center justify-between py-2 px-3 bg-surface-2 rounded-lg">
            <span className="text-sm capitalize">{k.replace(/_/g, " ")}</span>
            <span className="flex items-center gap-1.5 text-xs font-semibold">
              <span className={`w-2 h-2 rounded-full ${STATUS_DOT[v] ?? "bg-outline"}`} />{v}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function UsersTab() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["admin-users"], queryFn: () => adminApi.users().then(r => r.data) });
  const toggleM = useMutation({
    mutationFn: ({ id, active }: { id: string; active: boolean }) => adminApi.updateUser(id, { active }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-users"] }),
  });
  return (
    <div className="bg-card border border-outline-variant rounded-xl overflow-hidden">
      <table className="w-full">
        <thead className="bg-surface-2">
          <tr>{["Name", "Email", "Role", "MFA", "Active", ""].map(h => (
            <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-3 px-3">{h}</th>
          ))}</tr>
        </thead>
        <tbody className="divide-y divide-outline-variant/60">
          {(data?.users ?? []).map(u => (
            <tr key={u.id} className="hover:bg-surface-2/50">
              <td className="py-2.5 px-3 text-sm">{u.name}</td>
              <td className="py-2.5 px-3 text-sm">{u.email}</td>
              <td className="py-2.5 px-3 text-xs"><span className="bg-surface-2 px-2 py-0.5 rounded mono">{u.role}</span></td>
              <td className="py-2.5 px-3 text-xs">{u.mfa_enabled ? "✓" : "—"}</td>
              <td className="py-2.5 px-3 text-xs">{u.active ? <span className="text-risk-low">active</span> : <span className="text-on-surface-variant">disabled</span>}</td>
              <td className="py-2.5 px-3">
                <button onClick={() => toggleM.mutate({ id: u.id, active: !u.active })}
                  className="text-xs font-semibold text-primary hover:underline">{u.active ? "Disable" : "Enable"}</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function WeightsTab() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["admin-weights"], queryFn: () => adminApi.getWeights().then(r => r.data) });
  const [edits, setEdits] = useState<Record<string, number>>({});
  const saveM = useMutation({
    mutationFn: (weights: Record<string, number>) => adminApi.updateWeights(weights),
    onSuccess: () => { setEdits({}); qc.invalidateQueries({ queryKey: ["admin-weights"] }); },
  });
  const weights: WeightItem[] = data?.weights ?? [];
  const total = weights.reduce((sum, w) => sum + (edits[w.key] ?? w.weight), 0);
  return (
    <div className="bg-card border border-outline-variant rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-display font-semibold">Check Weights</h3>
        <span className="text-xs text-on-surface-variant">Total: <span className={`mono font-bold ${Math.abs(total - 100) < 0.01 ? "text-risk-low" : "text-risk-mid"}`}>{total.toFixed(0)}</span>/100</span>
      </div>
      <div className="space-y-3">
        {weights.map(w => (
          <div key={w.key} className="flex items-center gap-3">
            <span className="text-sm w-40 shrink-0">{w.name}</span>
            <input type="range" min="0" max="40" step="1"
              value={edits[w.key] ?? w.weight}
              onChange={e => setEdits({ ...edits, [w.key]: Number(e.target.value) })}
              className="flex-1 accent-primary" />
            <span className="mono text-sm w-10 text-right">{edits[w.key] ?? w.weight}</span>
          </div>
        ))}
      </div>
      <button disabled={Object.keys(edits).length === 0 || saveM.isPending}
        onClick={() => saveM.mutate(edits)}
        className="mt-4 bg-primary text-white text-sm font-semibold px-4 py-2 rounded-lg disabled:opacity-50">
        {saveM.isPending ? "Saving…" : "Save weights"}
      </button>
      <p className="text-xs text-on-surface-variant mt-2">Changing a weight recomputes contract risk scores on the next analysis run.</p>
    </div>
  );
}

function ThresholdsTab() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["admin-thresholds"], queryFn: () => adminApi.getThresholds().then(r => r.data) });
  const [edits, setEdits] = useState<Record<string, number>>({});
  const saveM = useMutation({
    mutationFn: (t: Record<string, number>) => adminApi.updateThresholds(t),
    onSuccess: () => { setEdits({}); qc.invalidateQueries({ queryKey: ["admin-thresholds"] }); },
  });
  const thresholds = data?.thresholds ?? {};
  return (
    <div className="bg-card border border-outline-variant rounded-xl p-5">
      <h3 className="font-display font-semibold mb-4">Thresholds</h3>
      <div className="space-y-3">
        {Object.entries(thresholds).map(([k, v]) => (
          <div key={k} className="flex items-center justify-between gap-3">
            <span className="text-sm capitalize">{k.replace(/_/g, " ")}</span>
            <input type="number" value={edits[k] ?? v}
              onChange={e => setEdits({ ...edits, [k]: Number(e.target.value) })}
              className="w-28 border border-outline-variant rounded px-2 py-1 text-sm mono bg-surface outline-none" />
          </div>
        ))}
      </div>
      <button disabled={Object.keys(edits).length === 0 || saveM.isPending}
        onClick={() => saveM.mutate(edits)}
        className="mt-4 bg-primary text-white text-sm font-semibold px-4 py-2 rounded-lg disabled:opacity-50">Save thresholds</button>
    </div>
  );
}

function LedgerTab() {
  const { data } = useQuery({ queryKey: ["admin-ledger"], queryFn: () => adminApi.ledger().then(r => r.data) });
  return (
    <div className="grid grid-cols-3 gap-4">
      {Object.entries(data ?? {}).map(([name, info]: [string, any]) => (
        <div key={name} className="bg-card border border-outline-variant rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-display font-semibold capitalize">{name}</h3>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${info.mode === "live" ? "bg-risk-low/10 text-risk-low" : "bg-accent/10 text-accent"}`}>{info.mode}</span>
          </div>
          <dl className="space-y-1.5 text-xs">
            {Object.entries(info).filter(([k]) => k !== "mode").map(([k, v]) => (
              <div key={k} className="flex justify-between"><dt className="text-on-surface-variant capitalize">{k.replace(/_/g, " ")}</dt><dd className="mono">{String(v)}</dd></div>
            ))}
          </dl>
        </div>
      ))}
    </div>
  );
}

export default function Admin() {
  const [tab, setTab] = useState<Tab>("Health");
  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink mb-1">Admin Console</h1>
      <p className="text-sm text-on-surface-variant mb-6">System health, users, check weights, thresholds, and ledger governance</p>

      <div className="flex gap-1 mb-6 border-b border-outline-variant">
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${tab === t ? "border-primary text-primary" : "border-transparent text-on-surface-variant hover:text-on-surface"}`}>{t}</button>
        ))}
      </div>

      {tab === "Health" && <HealthTab />}
      {tab === "Users" && <UsersTab />}
      {tab === "Weights" && <WeightsTab />}
      {tab === "Thresholds" && <ThresholdsTab />}
      {tab === "Ledger" && <LedgerTab />}
    </div>
  );
}
