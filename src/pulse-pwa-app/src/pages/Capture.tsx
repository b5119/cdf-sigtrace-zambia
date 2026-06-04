import { useState, useEffect, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import PhoneShell from "../components/PhoneShell";
import { useOnline } from "../store/useOnline";
import { queueSubmission, newClientUuid } from "../lib/db";
import { syncPending } from "../lib/sync";

export default function Capture() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const online = useOnline();
  const projectId = params.get("project") ?? "proj-001";

  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [gpsStatus, setGpsStatus] = useState<"locking" | "locked" | "denied">("locking");
  const [photo, setPhoto] = useState<Blob | null>(null);
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [category, setCategory] = useState("Borehole");
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  // Auto GPS lock
  useEffect(() => {
    if (!navigator.geolocation) { setGpsStatus("denied"); return; }
    const id = navigator.geolocation.watchPosition(
      pos => { setCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude }); setGpsStatus("locked"); },
      () => {
        // Fallback to a known constituency coord when GPS denied (demo/dev)
        setCoords({ lat: -11.432, lng: 29.456 }); setGpsStatus("denied");
      },
      { enableHighAccuracy: true, maximumAge: 10_000 }
    );
    return () => navigator.geolocation.clearWatch(id);
  }, []);

  function onPhoto(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (f) { setPhoto(f); setPhotoUrl(URL.createObjectURL(f)); }
  }

  async function submit() {
    if (!coords) return;
    setSaving(true);
    const sub = {
      client_uuid: newClientUuid(),
      project_id: projectId,
      constituency_id: "LPV-002",
      lat: coords.lat,
      lng: coords.lng,
      category,
      note: note || undefined,
      captured_at: new Date().toISOString(),
      photo_blob: photo ?? undefined,
      sync_status: "pending" as const,
      created_at: new Date().toISOString(),
    };
    // Always queue locally first (works fully offline)
    await queueSubmission(sub);
    // If online, attempt immediate sync
    if (online) { try { await syncPending(); } catch { /* stays queued */ } }
    setSaving(false);
    navigate("/submissions?new=1");
  }

  return (
    <PhoneShell title="Capture">
      <div className="p-4">
        {/* Viewfinder / photo */}
        <div onClick={() => fileRef.current?.click()}
          className="h-48 rounded-xl bg-ink/90 flex items-center justify-center text-white/60 text-sm mb-3 overflow-hidden cursor-pointer">
          {photoUrl
            ? <img src={photoUrl} alt="capture" className="w-full h-full object-cover" />
            : <div className="text-center"><span className="material-symbols-outlined text-4xl">photo_camera</span><p>Tap to capture photo</p></div>}
          <input ref={fileRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={onPhoto} />
        </div>

        {/* GPS + timestamp */}
        <div className="flex items-center gap-2 text-xs mb-1">
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>my_location</span>
          {gpsStatus === "locked"
            ? <span className="mono text-risk-low">{coords?.lat.toFixed(4)}, {coords?.lng.toFixed(4)} · locked</span>
            : gpsStatus === "denied"
              ? <span className="mono text-risk-mid">{coords?.lat.toFixed(4)}, {coords?.lng.toFixed(4)} · approx</span>
              : <span className="text-on-surface-variant">acquiring GPS…</span>}
        </div>
        <p className="text-xs text-on-surface-variant mb-3">🕑 timestamp auto-captured on submit</p>

        {/* Category + note */}
        <label className="block mb-3">
          <span className="block text-xs font-semibold text-on-surface-variant mb-1">Category</span>
          <input value={category} onChange={e => setCategory(e.target.value)}
            className="w-full rounded-lg border border-outline-variant bg-card px-3 py-2 text-sm focus:border-primary outline-none" />
        </label>
        <label className="block mb-3">
          <span className="block text-xs font-semibold text-on-surface-variant mb-1">Note</span>
          <input value={note} onChange={e => setNote(e.target.value)} placeholder="Optional…"
            className="w-full rounded-lg border border-outline-variant bg-card px-3 py-2 text-sm focus:border-primary outline-none" />
        </label>

        {/* Offline indicator */}
        {!online && (
          <div className="bg-card border border-risk-mid/30 bg-risk-mid/5 rounded-xl p-3 mb-3">
            <div className="flex items-center gap-2 text-xs text-risk-mid">
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>wifi_off</span>
              Offline — saved to device, will sync when connected
            </div>
          </div>
        )}

        <button onClick={submit} disabled={!coords || saving}
          className="w-full bg-primary text-white text-sm font-semibold py-3 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50">
          {saving ? "Saving…" : <><span className="material-symbols-outlined">check</span>Submit evidence</>}
        </button>
      </div>
    </PhoneShell>
  );
}
