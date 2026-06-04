import { useEffect, useState } from "react";

// X5 — offline indicator. Shows a banner when the browser loses connectivity.
export default function OfflineBanner() {
  const [offline, setOffline] = useState(!navigator.onLine);
  useEffect(() => {
    const on = () => setOffline(false);
    const off = () => setOffline(true);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => { window.removeEventListener("online", on); window.removeEventListener("offline", off); };
  }, []);
  if (!offline) return null;
  return (
    <div role="alert" className="bg-risk-mid text-white text-sm text-center py-2 px-4 flex items-center justify-center gap-2">
      <span className="material-symbols-outlined text-base" aria-hidden="true">wifi_off</span>
      You are offline. Some data may be unavailable until your connection is restored.
    </div>
  );
}
