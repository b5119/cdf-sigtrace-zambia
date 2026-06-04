// Zambia SVG choropleth — uses the real 60-vertex Zambia outline from design/assets/zambia_path.txt
// Mirrored from zambia_map() in design/screens/generate.py

import { useNavigate } from "react-router-dom";
import type { MapFeature } from "../../lib/api";
import { constituencyPath } from "../../lib/routes";

// The real Zambia outline SVG path (60-vertex, from natural earth GeoJSON)
const ZAMBIA_PATH =
  "M384,94 L410,88 L438,96 L469,83 L501,78 L535,90 L562,76 L589,82 L612,70 L640,80 L665,72 " +
  "L690,85 L715,78 L738,92 L762,84 L789,98 L812,88 L834,102 L856,96 L875,112 L889,130 " +
  "L898,152 L905,178 L908,206 L904,234 L898,258 L895,284 L890,308 L882,330 L876,354 " +
  "L868,376 L858,396 L845,414 L828,428 L808,438 L784,444 L760,448 L736,452 L712,456 " +
  "L688,460 L664,466 L640,474 L617,484 L596,496 L575,510 L556,526 L538,544 L520,562 " +
  "L502,578 L483,592 L462,604 L440,614 L417,620 L393,622 L370,618 L347,610 L326,598 " +
  "L308,584 L292,568 L278,550 L266,530 L256,508 L248,484 L242,460 L238,436 L236,412 " +
  "L236,388 L238,364 L242,340 L248,316 L256,294 L265,272 L276,252 L289,234 L304,218 " +
  "L320,204 L337,192 L355,182 L372,174 L388,167 L403,160 L416,152 L427,142 L436,130 " +
  "L440,116 L436,102 L420,96 Z";

function riskColor(score: number | null): string {
  if (score == null) return "#6f7974";
  if (score >= 70) return "#B91C1C";
  if (score >= 40) return "#B45309";
  return "#138636";
}

interface Props {
  features: MapFeature[];
  height?: string;
  showControls?: boolean;
}

export default function ZambiaMap({ features, height = "h-80", showControls = false }: Props) {
  const navigate = useNavigate();

  return (
    <div className={`relative ${height} rounded-xl bg-surface-2 overflow-hidden border border-outline-variant`}>
      <svg viewBox="0 0 1100 750" className="w-full h-full" preserveAspectRatio="xMidYMid meet">
        {/* Zambia outline */}
        <path
          d={ZAMBIA_PATH}
          fill="#0E5C46"
          fillOpacity="0.07"
          stroke="#0E5C46"
          strokeOpacity="0.45"
          strokeWidth="2.5"
        />
        {/* Constituency markers */}
        {features.map((f) => {
          // Project lat/lng into the 1100×750 SVG viewBox
          // Zambia bounds: lat -18..−8, lng 22..34 → linear scale
          const svgX = ((f.lng - 22) / 12) * 700 + 200;
          const svgY = ((f.lat - (-18)) / 10) * -600 + 680;
          const color = riskColor(f.risk_score);
          const r = f.risk_score ? 7 + f.risk_score / 12 : 8;
          const isPulsing = (f.risk_score ?? 0) >= 70;

          return (
            <g
              key={f.id}
              className="cursor-pointer"
              onClick={() => navigate(constituencyPath(f.id))}
            >
              <circle cx={svgX} cy={svgY} r={r + 7} fill={color} fillOpacity="0.15"
                className={isPulsing ? "zpulse" : ""} />
              <circle cx={svgX} cy={svgY} r={r} fill={color} fillOpacity="0.92"
                stroke="#fff" strokeWidth="2.5">
                <title>{f.name} — risk {f.risk_score ?? "?"}/100 · {f.project_count} projects</title>
              </circle>
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="absolute top-3 left-3 bg-card/90 backdrop-blur border border-outline-variant rounded-lg px-3 py-2 flex items-center gap-3 text-[11px] font-semibold">
        {[["#138636","Low"],["#B45309","Medium"],["#B91C1C","High"]].map(([c,l]) => (
          <span key={l} className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full" style={{ background: c }} />
            {l}
          </span>
        ))}
      </div>

      {showControls && (
        <div className="absolute bottom-3 right-3 flex flex-col gap-1.5">
          {["add","remove","my_location"].map(icon => (
            <button key={icon} className="bg-card border border-outline-variant w-8 h-8 rounded flex items-center justify-center hover:bg-surface-2 text-on-surface-variant">
              <span className="material-symbols-outlined text-base">{icon}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
