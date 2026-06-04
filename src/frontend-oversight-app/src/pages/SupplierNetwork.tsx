export default function SupplierNetwork() {
  // O5 — related-party graph (shared address/phone/shareholders)
  const edges = [[300,210,160,110,"#B8762A"],[300,210,150,300,"#B8762A"],[300,210,470,120,"#6f7974"],
    [300,210,460,310,"#6f7974"],[160,110,150,300,"#B8762A"],[160,110,90,210,"#B8762A"],[150,300,90,210,"#B8762A"]];
  const nodes = [[300,210,26,"#0E5C46","Tender"],[160,110,20,"#B91C1C","Supplier A"],
    [150,300,20,"#B91C1C","Supplier B"],[470,120,18,"#138636","Supplier C"],
    [460,310,18,"#138636","Supplier D"],[90,210,16,"#B8762A","Shared director"]];

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink mb-1">Supplier Network</h1>
      <p className="text-sm text-on-surface-variant mb-6">Related-party graph — shared address, phone, or shareholders flag potential collusion</p>

      <div className="relative h-[460px] rounded-xl bg-card border border-outline-variant overflow-hidden">
        <svg viewBox="0 0 600 420" className="w-full h-full">
          {edges.map((e, i) => (
            <line key={i} x1={e[0] as number} y1={e[1] as number} x2={e[2] as number} y2={e[3] as number}
              stroke={e[4] as string} strokeWidth={e[4] !== "#6f7974" ? 3 : 1.5} strokeOpacity="0.7" />
          ))}
          {nodes.map((n, i) => (
            <g key={i}>
              <circle cx={n[0] as number} cy={n[1] as number} r={n[2] as number} fill={n[3] as string} stroke="#fff" strokeWidth="2">
                <title>{n[4]}</title>
              </circle>
              <text x={n[0] as number} y={(n[1] as number) + (n[2] as number) + 14} textAnchor="middle" fontSize="12" fontWeight="600" fill="#0B1F1A">{n[4]}</text>
            </g>
          ))}
        </svg>
        <div className="absolute top-3 left-3 bg-card/90 backdrop-blur border border-outline-variant rounded-lg px-3 py-1.5 text-[11px] font-semibold flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-accent" />copper = shared attribute (flagged)
        </div>
      </div>
    </div>
  );
}
