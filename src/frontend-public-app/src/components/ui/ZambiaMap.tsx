// Zambia choropleth — faithful to zambia_map() in design/screens/generate.py.
// Real outline at viewBox 0 0 1000 800, preserveAspectRatio xMidYMid meet (true aspect),
// markers at the design's FIXED svg coordinates (NOT a lat/lng projection).
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { constituencyPath } from "../../lib/routes";

const ZM = "M917.4,81.6L956.2,118.4L977.1,188.2L963.1,210.5L946.6,277.2L962.4,345.4L936.5,374.0L911.5,450.4L954.8,471.8L705.1,539.6L712.9,598.1L650.6,609.4L603.7,642.2L593.7,670.7L564.3,677.2L492.7,744.8L447.1,798.1L419.4,800.0L392.6,790.5L300.7,781.5L285.9,775.4L285.3,768.5L252.8,750.0L199.4,745.3L132.1,764.0L78.4,712.6L22.9,645.2L26.7,383.4L198.0,384.5L191.0,356.1L203.2,325.3L188.8,286.7L198.1,246.8L189.4,221.2L217.8,223.3L222.5,248.9L261.1,246.9L313.3,254.5L340.8,291.8L406.7,303.3L457.0,277.3L475.5,320.4L538.5,331.9L568.9,367.0L602.6,412.3L665.6,413.0L658.7,324.2L636.2,339.2L578.6,307.2L556.4,292.5L566.6,209.9L581.2,112.5L562.8,76.2L586.2,23.7L608.3,13.9L718.8,0L751.2,8.4L785.6,29.3L818.4,43.1L870.7,56.9L917.4,81.6Z";

// (name, x, y, risk, constituency-id) — coords are the design's CITIES, ids map to the backend seed.
const CITIES: [string, number, number, number, string][] = [
  ["Lusaka", 560, 592, 82, "LSK-001"], ["Kafue", 548, 632, 71, "LSK-002"],
  ["Ndola", 560, 402, 38, "CPB-001"], ["Kitwe", 520, 390, 33, "CPB-002"],
  ["Solwezi", 360, 382, 46, "NWP-001"], ["Mansa", 590, 300, 29, "LPV-001"],
  ["Chinsali", 690, 332, 57, "MCG-001"], ["Chipata", 792, 470, 34, "EPV-001"],
  ["Mongu", 225, 520, 26, "WPV-001"], ["Livingstone", 448, 735, 21, "SPV-001"],
  ["Milenge", 612, 320, 88, "LPV-002"], ["Kabwe", 520, 470, 40, "CPB-003"],
];

function riskColor(s: number): string {
  return s >= 70 ? "#B91C1C" : s >= 40 ? "#B45309" : "#138636";
}

interface Props {
  riskById?: Record<string, number>;  // optional live risk overrides from the API, keyed by constituency id
  height?: string;
  showControls?: boolean;
  // Locator mode (P4/P5): render the outline + a SINGLE highlighted pin, no city markers, no legend.
  // Mirrors minimap() in design/screens/generate.py. x,y are in the 0..1000 / 0..800 viewBox.
  locator?: { x: number; y: number; label: string; gps?: string };
}

export default function ZambiaMap({ riskById, height = "h-72", showControls = false, locator }: Props) {
  const navigate = useNavigate();

  if (locator) {
    return (
      <div className={`relative ${height} rounded-lg bg-surface-2 overflow-hidden border border-outline-variant`}>
        <svg viewBox="0 0 1000 800" className="w-full h-full" preserveAspectRatio="xMidYMid meet">
          <path d={ZM} fill="#EEF3EF" stroke="#0E5C46" strokeOpacity="0.4" strokeWidth="3" />
          <circle cx={locator.x} cy={locator.y} r={52} fill="#B8762A" fillOpacity="0.16" className="zpulse" />
          <circle cx={locator.x} cy={locator.y} r={15} fill="#B8762A" stroke="#fff" strokeWidth="3" />
          <text x={locator.x} y={locator.y - 26} textAnchor="middle" fontFamily="Inter" fontSize="24" fontWeight="700" fill="#0B1F1A">{locator.label}</text>
        </svg>
        {locator.gps && (
          <div className="absolute bottom-2 left-2 bg-white/90 border border-outline-variant rounded px-2 py-1 mono text-[10px]">{locator.gps}</div>
        )}
      </div>
    );
  }

  // zoom is centred on the map's middle (500,400); viewBox shrinks as we zoom in.
  const [zoom, setZoom] = useState(1);
  const vw = 1000 / zoom, vh = 800 / zoom;
  const viewBox = `${(1000 - vw) / 2} ${(800 - vh) / 2} ${vw} ${vh}`;
  const zoomIn = () => setZoom(z => Math.min(+(z * 1.4).toFixed(3), 6));
  const zoomOut = () => setZoom(z => Math.max(+(z / 1.4).toFixed(3), 1));
  const recenter = () => setZoom(1);

  return (
    <div className={`relative ${height} rounded-lg bg-surface-2 overflow-hidden border border-outline-variant`}>
      <svg viewBox={viewBox} className="w-full h-full transition-[viewBox] duration-300" preserveAspectRatio="xMidYMid meet">
        <path d={ZM} fill="#0E5C46" fillOpacity="0.07" stroke="#0E5C46" strokeOpacity="0.45" strokeWidth="2.5" />
        {CITIES.map(([name, x, y, baseRisk, cid]) => {
          const s = riskById?.[cid] ?? baseRisk;
          const c = riskColor(s);
          const r = 7 + s / 10;
          const pulse = s >= 70;
          return (
            <a key={cid} className="cursor-pointer" onClick={() => navigate(constituencyPath(cid))}>
              <circle cx={x} cy={y} r={r + 6} fill={c} fillOpacity="0.16" className={pulse ? "zpulse" : ""} />
              <circle cx={x} cy={y} r={r} fill={c} fillOpacity="0.92" stroke="#fff" strokeWidth="2.5">
                <title>{name} — risk {s}/100</title>
              </circle>
            </a>
          );
        })}
      </svg>
      {/* legend */}
      <div className="absolute top-4 left-4 bg-card/90 backdrop-blur border border-outline-variant rounded-lg px-3 py-2 flex items-center gap-3 text-[11px] font-semibold">
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full" style={{ background: "#138636" }} />Low</span>
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full" style={{ background: "#B45309" }} />Medium</span>
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full" style={{ background: "#B91C1C" }} />High</span>
      </div>
      {showControls && (
        <div className="absolute bottom-4 left-4 z-40 flex flex-col gap-2">
          {([["add", zoomIn, "Zoom in"], ["remove", zoomOut, "Zoom out"], ["my_location", recenter, "Reset view"]] as const).map(([icon, fn, label]) => (
            <button key={icon} type="button" onClick={fn} aria-label={label} title={label}
              disabled={icon === "remove" && zoom <= 1}
              className="bg-card border border-outline-variant w-9 h-9 rounded-lg flex items-center justify-center shadow-sm hover:bg-surface-2 active:scale-95 disabled:opacity-40 disabled:pointer-events-none transition">
              <span className="material-symbols-outlined">{icon}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
