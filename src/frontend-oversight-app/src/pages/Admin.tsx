import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi, auditApi, ingestionApi, type WeightItem, type AdminUser, type AuditEntry } from "../lib/api";

const TABS = ["Health", "Users", "Weights", "Thresholds", "Ingestion", "Ledger", "Institutions", "Audit", "Notifications"] as const;
type Tab = typeof TABS[number];

const STATUS_DOT: Record<string, string> = {
  ok: "bg-risk-low", live: "bg-risk-low", configured: "bg-info",
  mock: "bg-accent", degraded: "bg-risk-mid", error: "bg-risk-high", not_configured: "bg-outline",
};

// ── Sample fallbacks (rendered when backend at localhost:8000 is down) ─────────

const SAMPLE_HEALTH = {
  status: "ok",
  components: {
    database: "ok", ocds_ingestion: "ok", object_storage: "ok",
    fabric_ledger: "ok", polygon_anchor: "configured", notifications: "ok",
  } as Record<string, string>,
};

const SAMPLE_USERS: AdminUser[] = [
  { id: "u-1001", name: "Mwila Banda", email: "m.banda@oag.gov.zm", role: "oag_officer", active: true, mfa_enabled: true },
  { id: "u-1002", name: "Chanda Phiri", email: "c.phiri@acc.gov.zm", role: "acc_investigator", active: true, mfa_enabled: true },
  { id: "u-1003", name: "Naomi Tembo", email: "n.tembo@zppa.gov.zm", role: "zppa_analyst", active: true, mfa_enabled: false },
  { id: "u-1004", name: "System Admin", email: "admin@cdf-integrity.gov.zm", role: "admin", active: true, mfa_enabled: true },
  { id: "u-1005", name: "Joseph Mulenga", email: "j.mulenga@oag.gov.zm", role: "oag_officer", active: false, mfa_enabled: false },
];

const SAMPLE_WEIGHTS: WeightItem[] = [
  { id: 1, key: "supplier_debarred", name: "Supplier debarred", weight: 20, severity: "high", enabled: true },
  { id: 2, key: "single_bid", name: "Single-bid award", weight: 15, severity: "high", enabled: true },
  { id: 3, key: "price_outlier", name: "Price outlier", weight: 15, severity: "high", enabled: true },
  { id: 4, key: "framework_split", name: "Framework splitting", weight: 12, severity: "mid", enabled: true },
  { id: 5, key: "rapid_award", name: "Rapid award timeline", weight: 12, severity: "mid", enabled: true },
  { id: 6, key: "repeat_supplier", name: "Repeat supplier", weight: 10, severity: "mid", enabled: true },
  { id: 7, key: "missing_docs", name: "Missing documents", weight: 8, severity: "low", enabled: true },
  { id: 8, key: "amendment_inflation", name: "Amendment inflation", weight: 8, severity: "low", enabled: true },
];

const SAMPLE_THRESHOLDS: Record<string, number> = {
  high_risk_score: 70, mid_risk_score: 40, price_outlier_pct: 25, ghost_overdue_days: 90,
};

const SAMPLE_LEDGER: Record<string, any> = {
  "Hyperledger Fabric": { mode: "live", peer_oag: "online", peer_zppa: "online", peer_acc: "online", last_block: "#48,210" },
  Polygon: { mode: "configured", contract: "0x8fa3…", signer: "ready", anchor_backlog: 0 },
};

const SAMPLE_AUDIT: AuditEntry[] = [
  { id: "a-9001", actor_id: "u-1004sys", action: "weights.updated", target_type: "config", target_ref: "weights:v12", meta: {}, created_at: "2026-06-05T08:14:00Z", anchored: true, anchor_tx: "0xabc123" },
  { id: "a-9002", actor_id: "u-1001oag", action: "case.escalated", target_type: "case", target_ref: "CASE-2026-0042", meta: {}, created_at: "2026-06-04T16:02:00Z", anchored: true, anchor_tx: "0xdef456" },
  { id: "a-9003", actor_id: null, action: "ingestion.completed", target_type: "run", target_ref: "run:58", meta: {}, created_at: "2026-06-04T03:00:00Z", anchored: true, anchor_tx: "0x789abc" },
  { id: "a-9004", actor_id: "u-1002acc", action: "user.disabled", target_type: "user", target_ref: "u-1005abcd", meta: {}, created_at: "2026-06-03T11:45:00Z", anchored: false, anchor_tx: null },
];

interface IngestionRun { id: number; started: string; records_in: number; loaded: number; errors: number; status: string; }
const SAMPLE_INGESTION_RUNS: IngestionRun[] = [
  { id: 58, started: "2026-06-04", records_in: 4210, loaded: 4210, errors: 0, status: "OK" },
  { id: 57, started: "2026-06-03", records_in: 4210, loaded: 4210, errors: 0, status: "OK" },
  { id: 56, started: "2026-06-02", records_in: 4210, loaded: 4210, errors: 0, status: "OK" },
  { id: 55, started: "2026-06-01", records_in: 4210, loaded: 4210, errors: 0, status: "OK" },
];

interface Institution { name: string; type: string; agreement: string; status: string; }
const SAMPLE_INSTITUTIONS: Institution[] = [
  { name: "Office of the Auditor General", type: "Oversight", agreement: "DSA-2026-01", status: "Active" },
  { name: "Anti-Corruption Commission", type: "Enforcement", agreement: "DSA-2026-02", status: "Active" },
  { name: "ZPPA", type: "Regulator", agreement: "DSA-2026-03", status: "Active" },
];

// ── Tabs ──────────────────────────────────────────────────────────────────────

function HealthTab() {
  const { data } = useQuery({
    queryKey: ["admin-health"],
    queryFn: () => adminApi.health().then(r => r.data),
  });
  const health = data ?? SAMPLE_HEALTH;
  const components = (data?.components && Object.keys(data.components).length > 0)
    ? data.components : SAMPLE_HEALTH.components;
  return (
    <div className="bg-card border border-outline-variant rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-display font-semibold">System Health</h3>
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${health.status === "ok" ? "bg-risk-low/10 text-risk-low" : "bg-risk-mid/10 text-risk-mid"}`}>{health.status ?? "…"}</span>
      </div>
      <div className="grid grid-cols-2 gap-3">
        {Object.entries(components).map(([k, v]) => (
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
  const users = (data?.users && data.users.length > 0) ? data.users : SAMPLE_USERS;
  return (
    <div className="bg-card border border-outline-variant rounded-xl overflow-hidden">
      <table className="w-full">
        <thead className="bg-surface-2">
          <tr>{["Name", "Email", "Role", "MFA", "Active", ""].map(h => (
            <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-3 px-3">{h}</th>
          ))}</tr>
        </thead>
        <tbody className="divide-y divide-outline-variant/60">
          {users.map(u => (
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
  const weights: WeightItem[] = (data?.weights && data.weights.length > 0) ? data.weights : SAMPLE_WEIGHTS;
  const total = weights.reduce((sum, w) => sum + (edits[w.key] ?? w.weight), 0);
  return (
    <div className="bg-card border border-outline-variant rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-display font-semibold">Check Weights</h3>
        <span className="text-xs text-on-surface-variant">Total: <span className={`mono font-bold ${Math.abs(total - 100) < 0.01 ? "text-risk-low" : "text-risk-mid"}`}>{total.toFixed(0)}</span>/100</span>
      </div>
      <div className="space-y-3">
        {weights.map(w => {
          const val = edits[w.key] ?? w.weight;
          return (
            <div key={w.key} className="flex items-center gap-3">
              <span className="text-sm w-40 shrink-0">{w.name}</span>
              <input type="range" min="0" max="40" step="1"
                value={val}
                onChange={e => setEdits({ ...edits, [w.key]: Number(e.target.value) })}
                className="flex-1 accent-primary" />
              <div className="w-24 h-1.5 bg-surface-2 rounded-full overflow-hidden hidden sm:block">
                <div className="h-full bg-primary rounded-full" style={{ width: `${(val / 40) * 100}%` }} />
              </div>
              <span className="mono text-sm w-10 text-right">{val}</span>
            </div>
          );
        })}
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
  const thresholds = (data?.thresholds && Object.keys(data.thresholds).length > 0)
    ? data.thresholds : SAMPLE_THRESHOLDS;
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

function IngestionTab() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["admin-ingestion"], queryFn: () => ingestionApi.runs().then(r => r.data) });
  const runM = useMutation({
    mutationFn: () => ingestionApi.trigger("ocds"),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-ingestion"] }),
  });
  const apiRuns: any[] = (data?.runs ?? data) as any[];
  const runs: IngestionRun[] = Array.isArray(apiRuns) && apiRuns.length > 0
    ? apiRuns.map((r: any, i: number) => ({
        id: r.id ?? r.run ?? i,
        started: (r.started ?? r.started_at ?? "").slice(0, 10) || "2026-06-04",
        records_in: r.records_in ?? r.records ?? 0,
        loaded: r.loaded ?? 0,
        errors: r.errors ?? 0,
        status: r.status ?? "OK",
      }))
    : SAMPLE_INGESTION_RUNS;
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-on-surface-variant">OCDS pipeline runs · {runs.length} shown</p>
        <button onClick={() => runM.mutate()} disabled={runM.isPending}
          className="text-sm font-semibold px-4 py-2 rounded-lg bg-primary text-white disabled:opacity-50 flex items-center gap-2">
          <span className="material-symbols-outlined text-base">cloud_sync</span>
          {runM.isPending ? "Running…" : "Run ingestion"}
        </button>
      </div>
      <div className="bg-card border border-outline-variant rounded-xl overflow-hidden">
        <table className="w-full">
          <thead className="bg-surface-2">
            <tr>{["Run", "Started", "Records in", "Loaded", "Errors", "Status"].map(h => (
              <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-3 px-3">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/60">
            {runs.map(r => (
              <tr key={r.id} className="hover:bg-surface-2/50">
                <td className="py-2.5 px-3 text-sm mono">#{r.id}</td>
                <td className="py-2.5 px-3 text-sm">{r.started}</td>
                <td className="py-2.5 px-3 text-sm mono">{r.records_in.toLocaleString()}</td>
                <td className="py-2.5 px-3 text-sm mono">{r.loaded.toLocaleString()}</td>
                <td className="py-2.5 px-3 text-sm mono">{r.errors}</td>
                <td className="py-2.5 px-3 text-sm">
                  <span className={r.status === "OK" ? "text-risk-low font-semibold" : "text-risk-mid font-semibold"}>{r.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function LedgerTab() {
  const { data } = useQuery({ queryKey: ["admin-ledger"], queryFn: () => adminApi.ledger().then(r => r.data) });
  const ledger = (data && Object.keys(data).length > 0) ? data : SAMPLE_LEDGER;
  return (
    <div className="grid grid-cols-2 gap-4">
      {Object.entries(ledger).map(([name, info]: [string, any]) => (
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

function InstitutionsTab() {
  const institutions = SAMPLE_INSTITUTIONS;
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-on-surface-variant">Data-sharing agreements · {institutions.length} institutions</p>
        <button
          className="text-sm font-semibold px-4 py-2 rounded-lg bg-primary text-white flex items-center gap-2">
          <span className="material-symbols-outlined text-base">add</span>
          Add institution
        </button>
      </div>
      <div className="bg-card border border-outline-variant rounded-xl overflow-hidden">
        <table className="w-full">
          <thead className="bg-surface-2">
            <tr>{["Institution", "Type", "Agreement", "Status"].map(h => (
              <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-3 px-3">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/60">
            {institutions.map(i => (
              <tr key={i.agreement} className="hover:bg-surface-2/50">
                <td className="py-2.5 px-3 text-sm">{i.name}</td>
                <td className="py-2.5 px-3 text-xs"><span className="bg-surface-2 px-2 py-0.5 rounded">{i.type}</span></td>
                <td className="py-2.5 px-3 text-sm mono">{i.agreement}</td>
                <td className="py-2.5 px-3 text-xs">
                  <span className="inline-flex items-center gap-1 text-risk-low font-semibold">
                    <span className="w-2 h-2 rounded-full bg-risk-low" />{i.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function AuditTab() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["admin-audit"], queryFn: () => auditApi.list().then(r => r.data) });
  const anchorM = useMutation({
    mutationFn: () => auditApi.anchor(),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-audit"] }),
  });
  const entries = (data?.entries && data.entries.length > 0) ? data.entries : SAMPLE_AUDIT;
  const total = data?.total ?? entries.length;
  const unanchored = entries.filter(e => !e.anchored).length;
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-on-surface-variant">{total} entries · {unanchored} unanchored</p>
        <button onClick={() => anchorM.mutate()} disabled={anchorM.isPending || unanchored === 0}
          className="text-sm font-semibold px-4 py-2 rounded-lg bg-accent text-white disabled:opacity-50 flex items-center gap-2">
          <span className="material-symbols-outlined text-base">link</span>
          {anchorM.isPending ? "Anchoring…" : "Anchor batch to Fabric"}
        </button>
      </div>
      {anchorM.data && (
        <div className="bg-risk-low/5 border border-risk-low/20 rounded-lg px-4 py-2.5 text-xs text-risk-low mb-4">
          Anchored {anchorM.data.data.anchored} entries · batch hash {anchorM.data.data.batch_hash?.slice(0, 16)}…
        </div>
      )}
      <div className="bg-card border border-outline-variant rounded-xl overflow-hidden">
        <table className="w-full">
          <thead className="bg-surface-2">
            <tr>{["Action", "Target", "Actor", "When", "Anchored"].map(h => (
              <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-3 px-3">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/60">
            {entries.map(e => (
              <tr key={e.id} className="hover:bg-surface-2/50">
                <td className="py-2.5 px-3 text-xs"><span className="mono bg-surface-2 px-2 py-0.5 rounded">{e.action}</span></td>
                <td className="py-2.5 px-3 text-xs mono">{e.target_type}{e.target_ref ? `:${e.target_ref.slice(0, 16)}` : ""}</td>
                <td className="py-2.5 px-3 text-xs mono">{e.actor_id ? e.actor_id.slice(0, 8) : "system"}</td>
                <td className="py-2.5 px-3 text-xs text-on-surface-variant">{e.created_at ? new Date(e.created_at).toLocaleString() : "—"}</td>
                <td className="py-2.5 px-3 text-xs">
                  {e.anchored
                    ? <span className="inline-flex items-center gap-1 text-risk-low"><span className="material-symbols-outlined text-sm">verified</span>anchored</span>
                    : <span className="text-on-surface-variant">pending</span>}
                </td>
              </tr>
            ))}
            {entries.length === 0 && <tr><td colSpan={5} className="py-8 text-center text-on-surface-variant text-sm">No audit entries yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const SAMPLE_TEMPLATE = "A new high-risk contract {{ocid}} scored {{score}}.";

function NotificationsTab() {
  const [template, setTemplate] = useState(SAMPLE_TEMPLATE);
  const rules = [
    { signal: "High-risk ≥70", route: "officers", channels: "email + in-app" },
    { signal: "Ghost-project signal", route: "OAG queue", channels: "in-app" },
    { signal: "Confirmation requested", route: "confirmer", channels: "email + in-app" },
  ];
  return (
    <div className="grid grid-cols-2 gap-6">
      <div className="bg-card border border-outline-variant rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display font-semibold text-ink">Rules</h3>
          <span className="material-symbols-outlined text-on-surface-variant text-xl">notifications</span>
        </div>
        <div className="space-y-3">
          {rules.map(r => (
            <div key={r.signal} className="flex items-center gap-2 py-2 px-3 bg-surface-2 rounded-lg text-sm">
              <span className="font-medium">{r.signal}</span>
              <span className="material-symbols-outlined text-base text-on-surface-variant">arrow_forward</span>
              <span className="text-primary font-semibold">{r.route}</span>
              <span className="ml-auto text-xs text-on-surface-variant mono">{r.channels}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="bg-card border border-outline-variant rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display font-semibold text-ink">Template editor</h3>
          <button className="text-xs font-semibold text-primary hover:underline">Save template</button>
        </div>
        <textarea
          value={template}
          onChange={e => setTemplate(e.target.value)}
          className="w-full h-40 rounded-lg border border-outline-variant p-3 text-sm bg-surface outline-none focus:border-primary mono" />
        <p className="text-xs text-on-surface-variant mt-2">Use <span className="mono">{"{{ocid}}"}</span> and <span className="mono">{"{{score}}"}</span> placeholders.</p>
      </div>
    </div>
  );
}

export default function Admin() {
  const [tab, setTab] = useState<Tab>("Health");
  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink mb-1">Admin Console</h1>
      <p className="text-sm text-on-surface-variant mb-6">System health, users, weights, thresholds, ingestion, ledger, institutions, audit, and notifications</p>

      <div className="flex gap-1 mb-6 border-b border-outline-variant flex-wrap">
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${tab === t ? "border-primary text-primary" : "border-transparent text-on-surface-variant hover:text-on-surface"}`}>{t}</button>
        ))}
      </div>

      {tab === "Health" && <HealthTab />}
      {tab === "Users" && <UsersTab />}
      {tab === "Weights" && <WeightsTab />}
      {tab === "Thresholds" && <ThresholdsTab />}
      {tab === "Ingestion" && <IngestionTab />}
      {tab === "Ledger" && <LedgerTab />}
      {tab === "Institutions" && <InstitutionsTab />}
      {tab === "Audit" && <AuditTab />}
      {tab === "Notifications" && <NotificationsTab />}
    </div>
  );
}
