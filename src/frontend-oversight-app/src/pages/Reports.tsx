export default function Reports() {
  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink mb-1">Reports & Exports</h1>
      <p className="text-sm text-on-surface-variant mb-6">Generate restricted reports (PDF/CSV) — every export is logged in the audit trail</p>
      <div className="grid grid-cols-3 gap-4">
        {[
          { icon: "summarize", title: "High-Risk Contract Report", desc: "All contracts scoring ≥70 with full check breakdown" },
          { icon: "report", title: "Ghost-Project Report", desc: "Disbursements with no verified completion" },
          { icon: "hub", title: "Supplier Network Report", desc: "Related-party links across all tenders" },
        ].map(r => (
          <div key={r.title} className="bg-card border border-outline-variant rounded-xl p-5">
            <span className="material-symbols-outlined text-2xl text-primary mb-2 block">{r.icon}</span>
            <p className="font-semibold text-sm">{r.title}</p>
            <p className="text-xs text-on-surface-variant mt-1 mb-4">{r.desc}</p>
            <div className="flex gap-2">
              <button className="text-xs font-semibold px-3 py-1.5 rounded border border-outline-variant hover:bg-surface-2 flex items-center gap-1">
                <span className="material-symbols-outlined text-sm">picture_as_pdf</span>PDF
              </button>
              <button className="text-xs font-semibold px-3 py-1.5 rounded bg-primary text-white hover:bg-primary-h flex items-center gap-1">
                <span className="material-symbols-outlined text-sm">table_view</span>CSV
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
