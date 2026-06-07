import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { casesApi, type CaseItem, type CaseNote } from "../lib/api";
import { useAuth } from "../store/auth";
import { contractPath } from "../lib/routes";

const INST_NAME: Record<string, string> = {
  OAG: "Office of the Auditor General",
  ACC: "Anti-Corruption Commission",
  ZPPA: "Zambia Public Procurement Authority",
};
const ALL_INSTITUTIONS = ["ACC", "ZPPA", "OAG"];

// Sample fallback — institution-segregated, with one OAG→ACC escalation.
const SAMPLE_CASES: CaseItem[] = [
  { id: "001", subject_type: "contract", subject_ref: "ocds-zm-zppa-003", title: "Signing gap — Ministry of Roads", assignee_id: null, status: "open", priority: "high", owner_institution: "OAG", escalated_to: null, created_by: "officer", created_at: "2026-06-01T08:00:00Z", closed_at: null, notes: [] },
  { id: "002", subject_type: "contract", subject_ref: "ocds-zm-zppa-002", title: "Procurement irregularity — Ministry of Education", assignee_id: null, status: "escalated", priority: "high", owner_institution: "OAG", escalated_to: "ACC", created_by: "officer", created_at: "2026-06-01T08:00:00Z", closed_at: null, notes: [] },
  { id: "003", subject_type: "ghost_project", subject_ref: "proj-001", title: "Ghost project — Milenge borehole", assignee_id: null, status: "in_review", priority: "medium", owner_institution: "OAG", escalated_to: null, created_by: "officer", created_at: "2026-06-01T08:00:00Z", closed_at: null, notes: [] },
];
const SAMPLE_NOTES: CaseNote[] = [
  { id: "n1", case_id: "001", author_id: "system", body: "2026-06-01 · Opened from contract risk list.", created_at: "2026-06-01T09:00:00Z" },
  { id: "n2", case_id: "001", author_id: "officer", body: "2026-06-02 · Note added by officer.", created_at: "2026-06-02T11:00:00Z" },
];

function InstBadge({ code }: { code: string }) {
  return <span className="text-[10px] font-bold tracking-wide px-1.5 py-0.5 rounded bg-sidebar/10 text-ink" title={INST_NAME[code] ?? code}>{code}</span>;
}
function statusPill(s: string) {
  const m: Record<string, string> = { open: "bg-primary/10 text-primary", in_review: "bg-risk-mid/10 text-risk-mid", escalated: "bg-accent/10 text-accent", closed: "bg-surface-2 text-on-surface-variant" };
  return <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${m[s] ?? "bg-surface-2"}`}>{s.replace("_", " ")}</span>;
}

export default function Cases() {
  const qc = useQueryClient();
  const myInst = useAuth().user?.institution?.type ?? null;
  const [tab, setTab] = useState<"relevant" | "ours" | "escalated">("relevant");
  const [selected, setSelected] = useState<string>("001");
  const [noteText, setNoteText] = useState("");
  const [showEscalate, setShowEscalate] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const { data } = useQuery({ queryKey: ["cases", tab], queryFn: () => casesApi.list(tab).then(r => r.data) });
  const { data: detail } = useQuery({ queryKey: ["case", selected], queryFn: () => casesApi.get(selected).then(r => r.data), enabled: !!selected });

  const noteM = useMutation({
    mutationFn: ({ id, body }: { id: string; body: string }) => casesApi.addNote(id, body),
    onSuccess: () => { setNoteText(""); qc.invalidateQueries({ queryKey: ["case", selected] }); },
  });
  const escalateM = useMutation({
    mutationFn: ({ id, target }: { id: string; target: string }) => casesApi.escalate(id, target),
    onSuccess: (_d, v) => { setShowEscalate(false); setMsg(`Escalated — now in the ${INST_NAME[v.target] ?? v.target} inbox.`); qc.invalidateQueries({ queryKey: ["cases"] }); qc.invalidateQueries({ queryKey: ["case", selected] }); },
  });

  const cases = data?.cases ?? SAMPLE_CASES;
  const active = detail ?? cases.find(c => c.id === selected) ?? cases[0];
  const notes = (detail?.notes && detail.notes.length > 0) ? detail.notes : SAMPLE_NOTES;
  const escalateTargets = ALL_INSTITUTIONS.filter(i => i !== (active?.owner_institution ?? myInst));
  const incoming = active && myInst && active.escalated_to === myInst && active.owner_institution !== myInst;

  const TABS: [typeof tab, string][] = [["relevant", "All relevant"], ["ours", "Our cases"], ["escalated", "Escalated to us"]];

  return (
    <div>
      <div className="flex items-end justify-between mb-4">
        <div>
          <h1 className="disp text-2xl font-bold text-ink">Cases</h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Investigations &amp; escalations{myInst ? <> · viewing as <b className="text-ink">{INST_NAME[myInst] ?? myInst}</b></> : null}
          </p>
        </div>
      </div>

      <div className="flex gap-1 border-b border-outline-variant mb-5">
        {TABS.map(([k, label]) => (
          <button key={k} onClick={() => setTab(k)}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px ${tab === k ? "border-primary text-primary" : "border-transparent text-on-surface-variant hover:text-ink"}`}>
            {label}
          </button>
        ))}
      </div>

      {msg && <div className="bg-primary/5 border border-primary/20 rounded-lg px-4 py-2.5 text-sm text-primary mb-4">{msg}</div>}

      <div className="grid grid-cols-3 gap-6">
        {/* Case list */}
        <div className="col-span-1 space-y-2">
          {cases.length === 0 && <p className="text-sm text-on-surface-variant px-1">No cases in this view.</p>}
          {cases.map(c => (
            <button key={c.id} onClick={() => { setSelected(c.id); setShowEscalate(false); setMsg(null); }}
              className={`w-full text-left bg-card border border-outline-variant rounded-xl p-3 ${c.id === selected ? "ring-2 ring-primary" : "hover:border-primary/40"}`}>
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-semibold truncate">{c.title}</p>
                {statusPill(c.status)}
              </div>
              <div className="flex items-center gap-1.5 mt-1.5 text-xs text-on-surface-variant">
                {c.owner_institution && <InstBadge code={c.owner_institution} />}
                {c.escalated_to && <span className="text-accent">→ <InstBadge code={c.escalated_to} /></span>}
                <span className="mono truncate">{c.subject_ref}</span>
              </div>
            </button>
          ))}
        </div>

        {/* Case detail */}
        <div className="col-span-2">
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-start justify-between gap-3 mb-1">
              <h3 className="disp font-semibold text-ink">{active?.title}</h3>
              {active && statusPill(active.status)}
            </div>
            <div className="flex items-center gap-2 text-xs text-on-surface-variant mb-4">
              {active?.owner_institution && <>Owned by <InstBadge code={active.owner_institution} /></>}
              {active?.escalated_to && <span className="text-accent flex items-center gap-1">· escalated to <InstBadge code={active.escalated_to} /> ({INST_NAME[active.escalated_to]})</span>}
            </div>

            {incoming && (
              <div className="mb-4 rounded-lg border border-accent/30 bg-accent/5 px-3 py-2 text-sm text-accent flex items-center gap-2">
                <span className="material-symbols-outlined" style={{ fontSize: 18 }}>move_to_inbox</span>
                Escalated to your institution by {INST_NAME[active!.owner_institution ?? ""] ?? active!.owner_institution} — pending {INST_NAME[myInst!]} action.
              </div>
            )}

            <div className="space-y-3 text-sm">
              <div className="flex gap-2 flex-wrap">
                {active?.subject_type === "contract" && (
                  <Link to={contractPath(active.subject_ref)} className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent">
                    <span className="material-symbols-outlined">description</span>Open contract
                  </Link>
                )}
                {!active?.escalated_to && (
                  <div className="relative">
                    <button onClick={() => setShowEscalate(v => !v)}
                      className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-accent text-white">
                      <span className="material-symbols-outlined">priority_high</span>Escalate to…
                    </button>
                    {showEscalate && (
                      <div className="absolute z-20 mt-1 w-72 bg-card border border-outline-variant rounded-xl shadow-lg p-2">
                        <p className="text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant px-2 py-1">Route this case to</p>
                        {escalateTargets.map(t => (
                          <button key={t} disabled={escalateM.isPending} onClick={() => active && escalateM.mutate({ id: active.id, target: t })}
                            className="w-full text-left px-2 py-2 rounded-lg hover:bg-surface-2 flex items-center justify-between gap-2">
                            <span><span className="font-semibold text-ink">{t}</span> <span className="text-xs text-on-surface-variant">— {INST_NAME[t]}</span></span>
                            <span className="material-symbols-outlined text-on-surface-variant" style={{ fontSize: 18 }}>arrow_forward</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="border-l-2 border-outline-variant pl-3 space-y-2 text-on-surface-variant">
                {notes.map(n => <p key={n.id}>{n.body}</p>)}
              </div>

              <textarea value={noteText} onChange={e => setNoteText(e.target.value)} rows={2}
                className="w-full rounded-lg border border-outline-variant p-2" placeholder="Add a note…" />
              <button onClick={() => noteText && active && noteM.mutate({ id: active.id, body: noteText })}
                className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-primary text-white">
                <span className="material-symbols-outlined">save</span>Save note
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
