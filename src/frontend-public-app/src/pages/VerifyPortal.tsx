// P6 — Contract Verification Portal (matches stitch_export/verification_portal)
import { useState, useRef } from "react";
import { publicApi, type VerifyResponse } from "../lib/api";

type Verdict = "match" | "mismatch" | "not_registered";


function SealIcon({ verdict }: { verdict: Verdict }) {
  const color = verdict === "match" ? "#0E5C46" : verdict === "mismatch" ? "#B91C1C" : "#B45309";
  const icon  = verdict === "match" ? "✓"       : verdict === "mismatch" ? "✗"       : "?";
  return (
    <svg viewBox="0 0 200 200" className="w-40 h-40 mx-auto">
      <circle cx="100" cy="100" r="95" fill="none" stroke={color} strokeWidth="1.5" strokeDasharray="4 3" className="seal-ring" />
      <circle cx="100" cy="100" r="78" fill={color} fillOpacity="0.12" stroke={color} strokeWidth="1.5" />
      <text x="100" y="40" textAnchor="middle" fill={color} fontSize="7.5" fontFamily="Space Grotesk" fontWeight="700" letterSpacing="2.5">
        {verdict === "match" ? "VERIFIED ON LEDGER" : verdict === "mismatch" ? "INTEGRITY MISMATCH" : "NOT REGISTERED"}
      </text>
      <text x="100" y="115" textAnchor="middle" fill={color} fontSize="52" fontWeight="700" fontFamily="Space Grotesk">{icon}</text>
    </svg>
  );
}

export default function VerifyPortal() {
  const [ocid, setOcid]       = useState("");
  const [file, setFile]       = useState<File | null>(null);
  const [result, setResult]   = useState<VerifyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleVerify() {
    if (!ocid.trim() || !file) return;
    setLoading(true); setError(null); setResult(null);
    try {
      const res = await publicApi.verifyContract(ocid.trim(), file);
      setResult(res.data);
    } catch (e: unknown) {
      setError("Verification failed — check the OCID and try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f?.type === "application/pdf" || f?.name.endsWith(".pdf")) setFile(f);
  }

  const verdictColors: Record<Verdict, string> = {
    match:          "border-risk-low/30 bg-risk-low/5",
    mismatch:       "border-risk-high/30 bg-risk-high/5",
    not_registered: "border-risk-mid/30 bg-risk-mid/5",
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="mb-8 text-center">
        <h1 className="font-display text-3xl font-bold">Contract Verification Portal</h1>
        <p className="text-on-surface-variant mt-2">
          Upload a signed contract PDF. The server computes its SHA-256 and checks it against the Fabric ledger.
          The file is never stored — only the hash is compared.
        </p>
      </div>

      {/* Input form */}
      <div className="bg-card border border-outline-variant rounded-2xl p-6 space-y-4 mb-6">
        <div>
          <label className="block text-sm font-semibold mb-1.5">Contract OCID</label>
          <input
            value={ocid}
            onChange={e => setOcid(e.target.value)}
            placeholder="ocds-zm-zppa-001"
            className="w-full border border-outline-variant rounded-lg px-3 py-2 mono text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 bg-surface"
          />
        </div>

        {/* Drop zone */}
        <div
          onClick={() => inputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={e => e.preventDefault()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
            file ? "border-primary/50 bg-primary/5" : "border-outline-variant hover:border-primary/40"
          }`}
        >
          <span className="material-symbols-outlined text-4xl text-on-surface-variant mb-2 block">upload_file</span>
          {file
            ? <p className="font-medium text-primary">{file.name} <span className="text-on-surface-variant text-sm">({(file.size/1024).toFixed(0)} KB)</span></p>
            : <p className="text-on-surface-variant text-sm">Drag & drop a PDF here, or click to browse</p>
          }
          <input ref={inputRef} type="file" accept=".pdf,application/pdf" className="hidden"
            onChange={e => setFile(e.target.files?.[0] ?? null)} />
        </div>

        <button
          onClick={handleVerify}
          disabled={!ocid.trim() || !file || loading}
          className="w-full bg-primary hover:bg-primary-h disabled:opacity-50 text-white font-semibold py-3 rounded-lg flex items-center justify-center gap-2 transition-colors"
        >
          {loading ? <><span className="animate-spin material-symbols-outlined text-base">autorenew</span>Verifying…</> : <><span className="material-symbols-outlined">verified</span>Verify Contract</>}
        </button>

        {error && <p className="text-risk-high text-sm text-center">{error}</p>}
      </div>

      {/* Result */}
      {result && (
        <div className={`bg-card border rounded-2xl p-6 ${verdictColors[result.verdict]}`}>
          <SealIcon verdict={result.verdict} />
          <p className="text-center font-display text-lg font-bold mt-4 mb-2">{result.message}</p>

          <div className="space-y-2 mt-6 text-sm">
            {[
              ["Uploaded hash",  result.provided_hash],
              ["Anchored hash",  result.anchored_hash],
              ["Ledger",         result.ledger],
              ["Transaction ID", result.ledger_tx],
              ["Block ref",      result.block_ref],
              ["Anchored at",    result.anchored_at ? new Date(result.anchored_at).toLocaleString() : null],
            ].filter(([,v]) => v).map(([label, value]) => (
              <div key={String(label)} className="flex items-center justify-between gap-4 bg-surface/50 rounded-lg px-3 py-2">
                <span className="text-on-surface-variant shrink-0">{label}</span>
                <span className="mono text-xs text-on-surface text-right break-all">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
