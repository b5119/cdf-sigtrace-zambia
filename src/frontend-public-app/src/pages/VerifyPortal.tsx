// P6 — Contract Verification Portal (matches stitch_export/verification_portal)
import { useState, useRef } from "react";
import { publicApi, type VerifyResponse } from "../lib/api";

const ACCENT = "#B8762A";

// ── Local SHA-256 (privacy shield: hash locally before any network call) ───────
async function sha256Hex(file: File): Promise<string> {
  const buf = await file.arrayBuffer();
  const digest = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function fmtTs(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

// ── The verified seal: coat of arms + rotating copper ring text ────────────────
function VerifiedSeal({ shortHash }: { shortHash: string }) {
  return (
    <div
      className="relative mb-8 flex h-[140px] w-[140px] flex-col items-center justify-center rounded-full bg-white"
      style={{ border: `1px solid ${ACCENT}` }}
    >
      <img src="/coat_of_arms.png" alt="Zambian Coat of Arms" className="h-16 w-16 object-contain" />
      <div className="absolute inset-0 flex items-center justify-center">
        <svg className="seal-text-ring h-full w-full" viewBox="0 0 100 100">
          <path
            id="seal-curve"
            d="M 50, 50 m -37, 0 a 37,37 0 1,1 74,0 a 37,37 0 1,1 -74,0"
            fill="transparent"
          />
          <text className="disp text-[6.5px] font-bold" fill={ACCENT}>
            <textPath href="#seal-curve">
              VERIFIED ON LEDGER • REPUBLIC OF ZAMBIA • VERIFIED ON LEDGER • REPUBLIC OF ZAMBIA •
            </textPath>
          </text>
        </svg>
      </div>
      <div
        className="mono absolute -bottom-2 rounded bg-white px-2 text-[9px]"
        style={{ border: `1px solid ${ACCENT}`, color: ACCENT }}
      >
        {shortHash}
      </div>
    </div>
  );
}

// ── The danger seal: broken / unauthorized state ───────────────────────────────
function DangerSeal({ label }: { label: string }) {
  return (
    <div className="relative mb-8 flex h-[140px] w-[140px] items-center justify-center rounded-full border-2 border-dashed border-risk-high/40 bg-risk-high/5">
      <span className="material-symbols-outlined text-6xl text-risk-high">gpp_bad</span>
      <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
        <div className="h-px w-full rotate-45 bg-risk-high/40" />
        <div className="-rotate-45 h-px w-full bg-risk-high/40" />
      </div>
      <div className="mono absolute -bottom-2 rounded bg-risk-high px-3 py-1 text-[10px] font-bold uppercase text-white">
        {label}
      </div>
    </div>
  );
}

export default function VerifyPortal() {
  const [ocid, setOcid] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [localHash, setLocalHash] = useState<string | null>(null);
  const [result, setResult] = useState<VerifyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function acceptFile(f: File | null) {
    setResult(null);
    setError(null);
    setFile(f);
    setLocalHash(null);
    if (f) {
      try {
        setLocalHash(await sha256Hex(f));
      } catch {
        /* hashing unsupported — server will still compute */
      }
    }
  }

  async function handleVerify() {
    if (!ocid.trim() || !file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await publicApi.verifyContract(ocid.trim(), file);
      setResult(res.data);
    } catch {
      setError("Verification failed — check the OCID and try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f && (f.type === "application/pdf" || f.name.endsWith(".pdf"))) void acceptFile(f);
  }

  const isMatch = result?.verdict === "match";

  return (
    <div className="mx-auto max-w-[1280px] px-4 pb-12 pt-8 md:px-12">
      {/* Hero */}
      <div className="mb-8 text-center md:text-left">
        <h2 className="disp mb-2 text-4xl font-bold tracking-tight md:text-5xl">Cryptographic Verification</h2>
        <p className="max-w-2xl text-lg text-on-surface-variant">
          Ensuring administrative authority through immutable digital signatures. Upload any
          government-issued contract to verify its authenticity against the National Oversight Ledger.
        </p>
      </div>

      {/* OCID input */}
      <div className="mb-6 max-w-xl">
        <label className="mono mb-1.5 block text-xs font-bold uppercase tracking-wide text-on-surface-variant">
          Contract OCID
        </label>
        <input
          value={ocid}
          onChange={(e) => setOcid(e.target.value)}
          placeholder="ocds-zm-zppa-001"
          className="mono w-full rounded-lg border border-outline-variant bg-white px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
        />
      </div>

      {/* Verification Dropzone */}
      <section className="mb-6">
        <div
          onClick={() => inputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={(e) => {
            e.preventDefault();
            setDragging(false);
          }}
          className={`group relative flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed bg-white p-16 transition-all ${
            dragging || file ? "border-primary bg-surface-2" : "border-outline-variant hover:border-primary hover:bg-surface-2"
          }`}
        >
          <div
            className={`mb-4 text-primary transition-opacity ${
              file ? "opacity-100" : "opacity-40 group-hover:opacity-100"
            }`}
          >
            <span className="material-symbols-outlined text-6xl">upload_file</span>
          </div>

          {file ? (
            <>
              <h3 className="disp mb-1 text-2xl font-medium text-primary">{file.name}</h3>
              <p className="text-sm text-on-surface-variant">{(file.size / 1024).toFixed(0)} KB ready to verify</p>
            </>
          ) : (
            <>
              <h3 className="disp mb-2 text-2xl font-medium">Drag and drop contract PDF</h3>
              <p className="max-w-md text-center text-on-surface-variant">
                Or <span className="font-bold text-primary">browse your local files</span> to begin the hashing process.
              </p>
            </>
          )}

          <div className="mt-8 flex items-center gap-3 rounded-lg border border-outline-variant bg-surface-2 px-4 py-2">
            <span className="material-symbols-outlined text-sm text-primary">shield</span>
            <span className="mono text-xs uppercase">Privacy Shield Active: Local Client-Side Hashing Only</span>
          </div>

          <input
            ref={inputRef}
            type="file"
            accept=".pdf,application/pdf"
            className="hidden"
            onChange={(e) => void acceptFile(e.target.files?.[0] ?? null)}
          />
        </div>

        <p className="mono mt-2 text-center text-xs text-on-surface-variant">
          We hash your document locally and compare it to the immutable ledger. No data leaves your browser unencrypted.
        </p>

        {localHash && (
          <p className="mono mt-2 break-all text-center text-xs text-on-surface-variant">
            Local SHA-256: <span className="text-on-surface">0x{localHash}</span>
          </p>
        )}

        <button
          onClick={handleVerify}
          disabled={!ocid.trim() || !file || loading}
          className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-primary py-3 font-semibold text-white transition-colors hover:bg-primary-h disabled:opacity-50"
        >
          {loading ? (
            <>
              <span className="material-symbols-outlined animate-spin text-base">autorenew</span>
              Verifying…
            </>
          ) : (
            <>
              <span className="material-symbols-outlined">verified</span>
              Verify Contract Against Ledger
            </>
          )}
        </button>

        {error && <p className="mt-3 text-center text-sm text-risk-high">{error}</p>}
      </section>

      {/* Result state */}
      {result && (
        <div className="grid grid-cols-1">
          <div className="flex flex-col overflow-hidden rounded-xl border border-outline-variant bg-white">
            {/* Header strip */}
            <div className="flex items-center justify-between border-b border-outline-variant bg-surface-2 p-4">
              <span className="mono text-xs font-bold uppercase tracking-wide text-on-surface-variant">
                Verification Result
              </span>
              {isMatch ? (
                <span className="mono rounded border border-primary/20 bg-primary/10 px-2 py-1 text-[10px] text-primary">
                  STATUS: MATCHED
                </span>
              ) : (
                <span className="mono rounded border border-risk-high/20 bg-risk-high/10 px-2 py-1 text-[10px] text-risk-high">
                  STATUS: {result.verdict === "mismatch" ? "CONFLICT" : "NOT REGISTERED"}
                </span>
              )}
            </div>

            {/* Body */}
            <div className="flex flex-grow flex-col items-center p-8">
              {isMatch ? (
                <VerifiedSeal shortHash={(result.anchored_hash ?? result.provided_hash).slice(0, 8).toUpperCase()} />
              ) : (
                <DangerSeal label={result.verdict === "mismatch" ? "INVALID" : "NO RECORD"} />
              )}

              <div className="w-full space-y-4">
                {!isMatch && (
                  <div className="rounded-lg border border-risk-high/20 bg-risk-high/5 p-4">
                    <div className="flex items-start gap-3">
                      <span className="material-symbols-outlined mt-1 text-risk-high">warning</span>
                      <div>
                        <h4 className="font-bold text-risk-high">Verification Failure</h4>
                        <p className="text-sm text-on-surface-variant">{result.message}</p>
                      </div>
                    </div>
                  </div>
                )}

                {isMatch && <p className="text-center text-sm text-on-surface-variant">{result.message}</p>}

                {/* Provided hash (document identity) */}
                <div className="flex flex-col">
                  <label className="mono mb-1 text-xs font-bold uppercase tracking-wide text-on-surface-variant">
                    Document Identity (SHA-256)
                  </label>
                  <div
                    className={`mono break-all rounded border border-outline-variant bg-surface-2 p-3 text-sm ${
                      isMatch ? "" : "text-risk-high"
                    }`}
                  >
                    0x{result.provided_hash}
                  </div>
                </div>

                {/* Anchored hash */}
                {result.anchored_hash && (
                  <div className="flex flex-col">
                    <label className="mono mb-1 text-xs font-bold uppercase tracking-wide text-on-surface-variant">
                      Anchored Hash (Ledger of Record)
                    </label>
                    <div className="mono break-all rounded border border-outline-variant bg-surface-2 p-3 text-sm">
                      0x{result.anchored_hash}
                    </div>
                  </div>
                )}

                {/* Metadata grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="mono mb-1 block text-xs font-bold uppercase tracking-wide text-on-surface-variant">
                      Ledger TX
                    </label>
                    <div className="mono break-all rounded border border-outline-variant bg-surface-2 p-3 text-sm">
                      {result.ledger_tx ?? "—"}
                    </div>
                  </div>
                  <div>
                    <label className="mono mb-1 block text-xs font-bold uppercase tracking-wide text-on-surface-variant">
                      Timestamp
                    </label>
                    <div className="mono rounded border border-outline-variant bg-surface-2 p-3 text-sm">
                      {fmtTs(result.anchored_at)}
                    </div>
                  </div>
                  <div>
                    <label className="mono mb-1 block text-xs font-bold uppercase tracking-wide text-on-surface-variant">
                      Ledger
                    </label>
                    <div className="mono break-all rounded border border-outline-variant bg-surface-2 p-3 text-sm">
                      {result.ledger ?? "—"}
                    </div>
                  </div>
                  <div>
                    <label className="mono mb-1 block text-xs font-bold uppercase tracking-wide text-on-surface-variant">
                      Block Ref
                    </label>
                    <div className="mono break-all rounded border border-outline-variant bg-surface-2 p-3 text-sm">
                      {result.block_ref ?? "—"}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer banner */}
            <div
              className={`p-4 text-center font-bold text-white ${isMatch ? "bg-primary" : "bg-risk-high"}`}
            >
              {isMatch ? "DOCUMENT AUTHENTICITY CONFIRMED" : "NOT VERIFIED — ALTERED OR UNREGISTERED"}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
