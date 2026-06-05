import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { casesApi, type CaseItem, type CaseNote } from "../lib/api";

// Sample fallback data — renders fully when the backend is down.
const SAMPLE_CASES: CaseItem[] = [
  { id: "001", subject_type: "contract", subject_ref: "ocds-…001", title: "Case #001", assignee_id: null, status: "open", priority: "high", created_by: "officer", created_at: "2026-06-01T08:00:00Z", closed_at: null, notes: [] },
  { id: "002", subject_type: "contract", subject_ref: "ocds-…002", title: "Case #002", assignee_id: null, status: "open", priority: "medium", created_by: "officer", created_at: "2026-06-01T08:00:00Z", closed_at: null, notes: [] },
  { id: "003", subject_type: "contract", subject_ref: "ocds-…003", title: "Case #003", assignee_id: null, status: "open", priority: "medium", created_by: "officer", created_at: "2026-06-01T08:00:00Z", closed_at: null, notes: [] },
  { id: "004", subject_type: "contract", subject_ref: "ocds-…004", title: "Case #004", assignee_id: null, status: "open", priority: "low", created_by: "officer", created_at: "2026-06-01T08:00:00Z", closed_at: null, notes: [] },
];

const SAMPLE_NOTES: CaseNote[] = [
  { id: "n1", case_id: "001", author_id: "system", body: "2026-06-01 · Opened from contract risk list.", created_at: "2026-06-01T09:00:00Z" },
  { id: "n2", case_id: "001", author_id: "officer", body: "2026-06-02 · Note added by officer.", created_at: "2026-06-02T11:00:00Z" },
];

export default function Cases() {
  const qc = useQueryClient();
  const [selected, setSelected] = useState<string>("001");
  const [noteText, setNoteText] = useState("");

  const { data } = useQuery({ queryKey: ["cases"], queryFn: () => casesApi.list().then(r => r.data) });
  const { data: detail } = useQuery({
    queryKey: ["case", selected], queryFn: () => casesApi.get(selected).then(r => r.data), enabled: !!selected,
  });

  const noteM = useMutation({
    mutationFn: ({ id, body }: { id: string; body: string }) => casesApi.addNote(id, body),
    onSuccess: () => { setNoteText(""); qc.invalidateQueries({ queryKey: ["case", selected] }); },
  });
  const escalateM = useMutation({
    mutationFn: (id: string) => casesApi.escalate(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["cases"] }); qc.invalidateQueries({ queryKey: ["case", selected] }); },
  });

  const cases = data?.cases ?? SAMPLE_CASES;
  const active = detail ?? SAMPLE_CASES.find(c => c.id === selected) ?? SAMPLE_CASES[0];
  const notes = (detail?.notes && detail.notes.length > 0) ? detail.notes : SAMPLE_NOTES;
  const headline = active.id === "001" ? "Case #001 — Signing gap, Lusaka CC" : `${active.title} — ${active.subject_ref}`;

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="disp text-2xl font-bold text-ink">Cases</h1>
          <p className="text-sm text-on-surface-variant mt-1">Investigations &amp; escalations</p>
        </div>
        <div className="flex gap-2"></div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Case list */}
        <div className="col-span-1 space-y-2">
          {cases.map(c => {
            const isActive = c.id === selected;
            return (
              <button
                key={c.id}
                onClick={() => setSelected(c.id)}
                className={`w-full text-left bg-card border border-outline-variant rounded-xl p-3 ${isActive ? "ring-2 ring-primary" : ""}`}
              >
                <p className="text-sm font-semibold">{c.title}</p>
                <p className="text-xs text-on-surface-variant">Contract {c.subject_ref} · Open</p>
              </button>
            );
          })}
        </div>

        {/* Case detail */}
        <div className="col-span-2">
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="disp font-semibold text-ink">{headline}</h3>
            </div>
            <div className="space-y-3 text-sm">
              <div className="flex gap-2">
                <a
                  href="#"
                  className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 border border-accent text-accent"
                >
                  <span className="material-symbols-outlined">description</span>Open contract
                </a>
                <button
                  onClick={() => escalateM.mutate(active.id)}
                  className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-accent text-white"
                >
                  <span className="material-symbols-outlined">priority_high</span>Escalate to ACC
                </button>
              </div>

              <div className="border-l-2 border-outline-variant pl-3 space-y-2 text-on-surface-variant">
                {notes.map(n => (
                  <p key={n.id}>{n.body}</p>
                ))}
              </div>

              <textarea
                value={noteText}
                onChange={e => setNoteText(e.target.value)}
                className="w-full rounded-lg border border-outline-variant p-2"
                placeholder="Add a note…"
              />
              <button
                onClick={() => noteText && noteM.mutate({ id: active.id, body: noteText })}
                className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-primary text-white"
              >
                <span className="material-symbols-outlined">save</span>Save note
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
