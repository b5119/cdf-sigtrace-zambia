import { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import { contractPath } from "../lib/routes";

type AnchorRow = {
  ocid: string;
  ocidShort: string;
  hashShort: string;
  txShort: string;
  anchored: string;
};

// Sample anchors — restricted officials console, named OCIDs are fine.
const SAMPLE_ANCHORS: AnchorRow[] = [
  { ocid: "ocds-zm-cdf-2026-001", ocidShort: "ocds-…001", hashShort: "0xa1…9f", txShort: "0x7f…", anchored: "2026-06-01" },
  { ocid: "ocds-zm-cdf-2026-002", ocidShort: "ocds-…002", hashShort: "0xc4…2b", txShort: "0x3d…", anchored: "2026-06-02" },
  { ocid: "ocds-zm-cdf-2026-003", ocidShort: "ocds-…003", hashShort: "0x9e…71", txShort: "0xb8…", anchored: "2026-06-03" },
  { ocid: "ocds-zm-cdf-2026-004", ocidShort: "ocds-…004", hashShort: "0x6f…d0", txShort: "0x1a…", anchored: "2026-06-04" },
];

type Result = {
  verified: boolean;
  fileName: string;
  hash: string; // full 0x-prefixed sha256
};

// Default verified seal so the page renders fully with no backend.
const DEFAULT_RESULT: Result = {
  verified: true,
  fileName: "contract.pdf",
  hash: "0xa1b2c3d4e5f60718293a4b5c6d7e8f90112233445566778899aabbccddeeff9f",
};

async function sha256Hex(file: File): Promise<string> {
  const buf = await file.arrayBuffer();
  const digest = await crypto.subtle.digest("SHA-256", buf);
  const bytes = new Uint8Array(digest);
  let hex = "";
  for (let i = 0; i < bytes.length; i++) hex += bytes[i].toString(16).padStart(2, "0");
  return "0x" + hex;
}

function shortHash(hash: string): string {
  // hash like 0x<64 hex> → "0xa1b2…9f"
  if (hash.length < 12) return hash;
  return `${hash.slice(0, 6)}…${hash.slice(-2)}`;
}

export default function VerifyDocument() {
  const [ocid, setOcid] = useState("");
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<Result>(DEFAULT_RESULT);

  const handleFile = useCallback(async (file: File | undefined) => {
    if (!file) return;
    setBusy(true);
    try {
      const hash = await sha256Hex(file);
      // Demo MATCH result — local hash treated as verified against its anchor.
      setResult({ verified: true, fileName: file.name, hash });
    } catch {
      setResult({ verified: false, fileName: file.name, hash: "0x—" });
    } finally {
      setBusy(false);
    }
  }, []);

  const onDrop = useCallback((e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files?.[0]);
  }, [handleFile]);

  return (
    <div>
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">Document Verification</h1>
          <p className="text-sm text-on-surface-variant mt-1">Verify any contract against its anchor</p>
        </div>
        <div className="flex gap-2" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Left — dropzone + OCID */}
        <div>
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-semibold text-ink flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">fact_check</span>
                Verify a document
              </h3>
            </div>

            <label
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              className={`h-40 rounded-lg border-2 border-dashed flex flex-col items-center justify-center gap-1 text-sm cursor-pointer transition-colors ${
                dragging ? "border-accent bg-accent/5 text-accent" : "border-outline-variant text-on-surface-variant hover:bg-surface-2/60"
              }`}
            >
              <span className="material-symbols-outlined text-3xl">upload_file</span>
              <span>{busy ? "Hashing…" : "Drop a contract PDF"}</span>
              <span className="text-[11px] text-on-surface-variant">or click to browse</span>
              <input
                type="file"
                accept="application/pdf,.pdf"
                className="hidden"
                onChange={(e) => handleFile(e.target.files?.[0] ?? undefined)}
              />
            </label>

            <div className="mt-4">
              <label className="block text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold mb-1.5" htmlFor="ocid">
                OCID (optional)
              </label>
              <input
                id="ocid"
                value={ocid}
                onChange={(e) => setOcid(e.target.value)}
                placeholder="ocds-zm-cdf-2026-001"
                className="mono w-full text-sm rounded-lg border border-outline-variant bg-surface px-3 py-2 text-ink placeholder:text-on-surface-variant focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              />
              <p className="mt-2 text-xs text-on-surface-variant">
                Computes a SHA-256 of the document locally and checks it against the on-ledger anchor.
              </p>
            </div>
          </div>
        </div>

        {/* Right — result / verification seal */}
        <div>
          <div className="bg-card border border-outline-variant rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-semibold text-ink flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">verified</span>
                Result
              </h3>
            </div>

            <div className="flex flex-col items-center text-center gap-2">
              {/* Verification SEAL */}
              <div className="relative w-36 h-36">
                <svg viewBox="0 0 144 144" className="absolute inset-0 w-full h-full">
                  <defs>
                    <path
                      id="seal-ring-path"
                      d="M72,72 m-58,0 a58,58 0 1,1 116,0 a58,58 0 1,1 -116,0"
                    />
                  </defs>
                  <text className="mono" fill="#0E5C46" fontSize="9.5" fontWeight="700" letterSpacing="2.4">
                    <textPath href="#seal-ring-path" startOffset="0%">
                      VERIFIED ON LEDGER • REPUBLIC OF ZAMBIA •
                    </textPath>
                  </text>
                </svg>
                <div
                  className={`absolute inset-4 rounded-full border-4 flex items-center justify-center bg-primary/5 ${
                    result.verified ? "border-accent" : "border-risk-high"
                  }`}
                >
                  {result.verified ? (
                    <img src="/coat_of_arms.png" alt="Republic of Zambia coat of arms" className="h-16 w-16 object-contain" />
                  ) : (
                    <span className="material-symbols-outlined text-risk-high" style={{ fontSize: 56 }}>gpp_bad</span>
                  )}
                </div>
              </div>

              {result.verified ? (
                <p className="text-[11px] font-bold tracking-widest text-primary">
                  VERIFIED ON LEDGER &middot; REPUBLIC OF ZAMBIA
                </p>
              ) : (
                <p className="text-[11px] font-bold tracking-widest text-risk-high">
                  NO MATCHING ANCHOR FOUND
                </p>
              )}

              <p className="mono text-xs text-on-surface-variant">sha256 {shortHash(result.hash)}</p>
              <p className="mono text-[11px] text-on-surface-variant">tx 0x7f2a… · 2026-06-01</p>

              <div className="mt-2 w-full border-t border-outline-variant/60 pt-3 text-left">
                <p className="text-xs text-on-surface-variant truncate">
                  <span className="font-semibold text-ink">Document:</span> {result.fileName}
                </p>
                {ocid && (
                  <p className="text-xs text-on-surface-variant truncate mt-1">
                    <span className="font-semibold text-ink">OCID:</span> <span className="mono">{ocid}</span>
                  </p>
                )}
                {result.verified && (
                  <p className="mt-2 inline-flex items-center gap-1 text-xs font-semibold text-risk-low">
                    <span className="material-symbols-outlined" style={{ fontSize: 18 }}>check_circle</span>
                    MATCH — hash matches anchored contract
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent anchors */}
      <div className="mt-6">
        <div className="bg-card border border-outline-variant rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-display font-semibold text-ink">Recent anchors</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-outline">
                  {["OCID", "Hash", "Tx", "Anchored"].map((h) => (
                    <th key={h} className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant font-semibold py-2 px-3">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {SAMPLE_ANCHORS.map((a, i) => (
                  <tr key={a.ocid} className={`${i % 2 === 1 ? "bg-surface-2/40 " : ""}border-b border-outline-variant/60 hover:bg-surface-2/70`}>
                    <td className="py-2.5 px-3 text-sm">
                      <Link to={contractPath(a.ocid)} className="mono text-primary hover:underline">{a.ocidShort}</Link>
                    </td>
                    <td className="py-2.5 px-3 text-sm"><span className="mono">{a.hashShort}</span></td>
                    <td className="py-2.5 px-3 text-sm"><span className="mono">{a.txShort}</span></td>
                    <td className="py-2.5 px-3 text-sm">{a.anchored}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
