import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { pulseApi } from "../lib/api";

// QR-style placeholder: 5x5 grid, true = filled square (matches design/screens/M1_login.html)
const QR_CELLS = [
  false, false, true, false, true,
  true, false, true, true, false,
  true, false, false, true, true,
  false, false, true, false, true,
  true, false, true, true, false,
];

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true); setError(null);
    try {
      const res = await pulseApi.login(email, password);
      if (res.data.access_token) {
        localStorage.setItem("pulse_token", res.data.access_token);
        localStorage.setItem("pulse_refresh", res.data.refresh_token ?? "");
        navigate("/home");
      } else if (res.data.mfa_challenge_token) {
        sessionStorage.setItem("mfa_token", res.data.mfa_challenge_token);
        navigate("/mfa");
      }
    } catch {
      setError("Sign-in failed. Check your credentials.");
    } finally { setLoading(false); }
  }

  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2 bg-surface text-on-surface">
      {/* LEFT: Pulse field-app hero */}
      <div className="bg-primary text-white p-8 sm:p-12 flex flex-col justify-between gap-10 lg:min-h-screen">
        <div className="flex items-center gap-2.5">
          <img src="/coat_of_arms.png" alt="Coat of arms" className="h-8 w-8 object-contain" />
          <span className="font-display font-bold tracking-tight">
            CDF Pulse <span className="text-white/50 font-normal">|</span> Field Verification
          </span>
        </div>

        <div className="max-w-md">
          <span className="inline-flex items-center gap-1.5 text-[11px] font-bold tracking-widest text-white bg-white/15 px-3 py-1 rounded-full">
            <span className="material-symbols-outlined text-base">eco</span>
            COMMUNITY MONITORING · OFFLINE-FIRST
          </span>
          <h1 className="font-display text-3xl sm:text-4xl font-bold leading-tight mt-5">
            Capture proof that<br />projects are real
          </h1>
          <p className="text-white/80 mt-4">
            Community monitors and institutional confirmers record geo-tagged, timestamped,
            tamper-evident evidence from the field. Works offline and syncs to the ledger
            when you're back online.
          </p>

          <div className="flex items-center gap-4 mt-6 bg-white/10 border border-white/15 rounded-xl p-4">
            <div className="w-24 h-24 rounded-lg bg-white border border-white/20 grid grid-cols-5 grid-rows-5 gap-0.5 p-1.5 shrink-0">
              {QR_CELLS.map((on, i) => (
                <span key={i} className={`rounded-[1px] ${on ? "bg-ink" : "bg-transparent"}`} />
              ))}
            </div>
            <div>
              <p className="text-sm font-semibold">Install the app</p>
              <p className="text-xs text-white/70">
                Scan to install CDF Pulse on your phone, or use it right here in your browser.
              </p>
            </div>
          </div>
        </div>

        <a
          href="http://localhost:5173"
          className="text-xs text-white/80 hover:text-white inline-flex items-center gap-1"
        >
          <span className="material-symbols-outlined text-base">arrow_back</span>
          Back to public portal
        </a>
      </div>

      {/* RIGHT: sign-in */}
      <div className="bg-surface flex items-center justify-center p-6 sm:p-8 lg:min-h-screen">
        <form
          onSubmit={submit}
          className="w-full max-w-[380px] bg-card rounded-2xl p-7 border border-outline-variant"
        >
          <h2 className="font-display font-bold text-ink mb-1">Sign in</h2>
          <p className="text-xs text-on-surface-variant mb-5">
            Field monitor or institutional confirmer.
          </p>

          <label className="block mb-3">
            <span className="block text-xs font-semibold text-on-surface-variant mb-1">
              Phone or credential
            </span>
            <input
              type="text"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="monitor@cdf.zm"
              className="w-full rounded-lg border border-outline-variant bg-card px-3 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none"
            />
          </label>

          <label className="block mb-3">
            <span className="block text-xs font-semibold text-on-surface-variant mb-1">
              Password
            </span>
            <input
              type="password"
              required
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Password"
              className="w-full rounded-lg border border-outline-variant bg-card px-3 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none"
            />
          </label>

          <div className="my-2">
            <button
              type="button"
              className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-primary text-white"
            >
              <span className="material-symbols-outlined text-base">sms</span>
              Send code
            </button>
          </div>

          <p className="text-xs text-on-surface-variant mb-2">Enter the 6-digit code</p>
          <div className="flex gap-2 justify-between font-mono mb-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <input
                key={i}
                maxLength={1}
                inputMode="numeric"
                className="w-11 h-12 text-center rounded-lg border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary outline-none"
              />
            ))}
          </div>

          {error && <p className="text-risk-high text-sm mb-3">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full text-sm font-semibold px-4 py-2.5 rounded-lg inline-flex items-center justify-center gap-2 bg-accent text-white disabled:opacity-50"
          >
            {loading ? "Verifying…" : "Verify & continue"}
          </button>

          <p className="text-[11px] text-on-surface-variant mt-4 flex items-center gap-1.5">
            <span className="material-symbols-outlined text-base">smartphone</span>
            This device is bound to your account. Offline grace: 7 days.
          </p>
        </form>
      </div>
    </div>
  );
}
