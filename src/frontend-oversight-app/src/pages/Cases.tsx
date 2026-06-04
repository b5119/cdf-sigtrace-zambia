import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { casesApi } from "../lib/api";

const PRIORITY_STYLE: Record<string, string> = {
  high: "bg-risk-high/10 text-risk-high", medium: "bg-risk-mid/10 text-risk-mid", low: "bg-surface-2 text-on-surface-variant",
};
const STATUS_STYLE: Record<string, string> = {
  open: "bg-info/10 text-info", in_review: "bg-accent/10 text-accent",
  escalated: "bg-risk-high/10 text-risk-high", closed: "bg-risk-low/10 text-risk-low",
};

export default function Cases() {
  const qc = useQueryClient();
  const [selected, setSelected] = useState<string | null>(null);
  const [noteText, setNoteText] = useState("");

  const { data } = useQuery({ queryKey: ["cases"], queryFn: () => casesApi.list().then(r => r.data) });
  const { data: detail } = useQuery({
    queryKey: ["case", selected], queryFn: () => casesApi.get(selected!).then(r => r.data), enabled: !!selected,
  });

  const noteM = useMutation({
    mutationFn: ({ id, body }: { id: string; body: string }) => casesApi.addNote(id, body),
    onSuccess: () => { setNoteText(""); qc.invalidateQueries({ queryKey: ["case", selected] }); },
  });
  const statusM = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => casesApi.update(id, { status }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["cases"] }); qc.invalidateQueries({ queryKey: ["case", selected] }); },
  });
  const escalateM = useMutation({
    mutationFn: (id: string) => casesApi.escalate(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["cases"] }); qc.invalidateQueries({ queryKey: ["case", selected] }); },
  });

  const cases = data?.cases ?? [];

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink mb-1">Cases</h1>
      <p className="text-sm text-on-surface-variant mb-6">{data?.total ?? 0} cases · open from a contract or ghost-project signal</p>

      <div className="grid grid-cols-3 gap-6">
        {/* Case list */}
        <div className="col-span-1 space-y-2">
          {cases.map(c => (
            <button key={c.id} onClick={() => setSelected(c.id)}
              className={`w-full text-left bg-card border rounded-xl p-3 transition-colors ${selected === c.id ? "border-primary ring-1 ring-primary/30" : "border-outline-variant hover:border-primary/40"}`}>
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="text-sm font-semibold truncate">{c.title}</span>
                <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full shrink-0 ${PRIORITY_STYLE[c.priority]}`}>{c.priority}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${STATUS_STYLE[c.status]}`}>{c.status}</span>
                <span className="text-xs text-on-surface-variant mono truncate">{c.subject_ref}</span>
              </div>
            </button>
          ))}
          {cases.length === 0 && <p className="text-sm text-on-surface-variant py-8 text-center">No cases yet.</p>}
        </div>

        {/* Case detail */}
        <div className="col-span-2">
          {detail ? (
            <div className="bg-card border border-outline-variant rounded-xl p-5">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="font-display font-semibold text-lg">{detail.title}</h2>
                  <p className="text-xs text-on-surface-variant mono">{detail.subject_type} · {detail.subject_ref}</p>
                </div>
                <div className="flex gap-2">
                  <select value={detail.status} onChange={e => statusM.mutate({ id: detail.id, status: e.target.value })}
                    className="text-xs border border-outline-variant rounded px-2 py-1 bg-card">
                    {["open", "in_review", "escalated", "closed"].map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                  <button onClick={() => escalateM.mutate(detail.id)}
                    className="text-xs font-semibold px-3 py-1 rounded bg-accent text-white">Escalate to ACC</button>
                </div>
              </div>

              {/* Notes */}
              <h3 className="font-semibold text-sm mb-2">Notes</h3>
              <div className="space-y-2 mb-3 max-h-64 overflow-y-auto">
                {detail.notes.map(n => (
                  <div key={n.id} className="bg-surface-2 rounded-lg p-3">
                    <p className="text-sm">{n.body}</p>
                    <p className="text-[10px] text-on-surface-variant mt-1">{new Date(n.created_at).toLocaleString()}</p>
                  </div>
                ))}
                {detail.notes.length === 0 && <p className="text-xs text-on-surface-variant">No notes yet.</p>}
              </div>
              <div className="flex gap-2">
                <input value={noteText} onChange={e => setNoteText(e.target.value)} placeholder="Add a note…"
                  className="flex-1 border border-outline-variant rounded-lg px-3 py-2 text-sm bg-surface outline-none focus:ring-2 focus:ring-primary/30" />
                <button onClick={() => noteText && noteM.mutate({ id: detail.id, body: noteText })}
                  className="bg-primary text-white text-sm font-semibold px-4 rounded-lg">Add</button>
              </div>
            </div>
          ) : (
            <div className="bg-card border border-outline-variant rounded-xl p-12 text-center text-on-surface-variant">
              <span className="material-symbols-outlined text-4xl mb-2 block">folder_open</span>
              <p className="text-sm">Select a case to view detail</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
