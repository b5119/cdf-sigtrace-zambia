import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../lib/api";
import { useAuth } from "../store/auth";
import { ROUTES } from "../lib/routes";

const DEMO_ACCOUNTS = [
  { label: "A. Banda — Oversight Officer (OAG)", email: "officer@oag.gov.zm", password: "Officer123!" },
  { label: "System Admin — ICT (CDF)", email: "admin@cdf.zm", password: "AdminPass123!" },
];

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showQuickFill, setShowQuickFill] = useState(false);
  const navigate = useNavigate();
  const { setTokens, setMfaChallenge } = useAuth();

  // Shift+D — demo account quick-fill (scoped to the login form).
  function handleFormKeyDown(e: React.KeyboardEvent<HTMLFormElement>) {
    if (e.shiftKey && (e.key === "D" || e.key === "d")) { e.preventDefault(); setShowQuickFill(v => !v); }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true); setError(null);
    try {
      const res = await authApi.login(email, password);
      const data = res.data;
      if (data.mfa_challenge_token) {
        setMfaChallenge(data.mfa_challenge_token);
        navigate(ROUTES.MFA);
      } else if (data.access_token && data.refresh_token) {
        setTokens(data.access_token, data.refresh_token);
        navigate(ROUTES.DASHBOARD);
      }
    } catch {
      setError("Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2">
      {/* LEFT: officials-tailored hero */}
      <div className="bg-ink text-white p-8 sm:p-12 flex flex-col justify-between lg:min-h-screen gap-10">
        <div className="flex items-center gap-2.5">
          <img src="/coat_of_arms.png" alt="Coat of arms" className="h-8 w-8 object-contain" />
          <span className="disp font-bold tracking-tight">
            SigTrace <span className="text-white/40 font-normal">|</span> Oversight &amp; Audit Console
          </span>
        </div>

        <div className="max-w-md">
          <span className="inline-flex items-center gap-1.5 text-[11px] font-bold tracking-widest text-accent bg-accent/15 px-3 py-1 rounded-full">
            <span className="material-symbols-outlined" style={{ fontSize: 14 }}>lock</span>
            RESTRICTED · AUTHORISED INSTITUTIONS ONLY
          </span>
          <h1 className="disp text-4xl font-bold leading-tight mt-5">
            The officials' portal for<br />contract &amp; CDF oversight
          </h1>
          <p className="text-white/70 mt-4">
            Investigate procurement risk signals, confirm field evidence, manage cases and anchor
            audit actions to the ledger. Access is institutional, MFA-protected and fully audit-logged.
          </p>
          <div className="flex flex-wrap gap-2 mt-6">
            <span className="text-xs font-semibold bg-white/10 border border-white/15 px-3 py-1.5 rounded-lg">Office of the Auditor General</span>
            <span className="text-xs font-semibold bg-white/10 border border-white/15 px-3 py-1.5 rounded-lg">Anti-Corruption Commission</span>
            <span className="text-xs font-semibold bg-white/10 border border-white/15 px-3 py-1.5 rounded-lg">ZPPA</span>
          </div>
        </div>

        <div className="text-xs text-white/50 space-y-1">
          <p>This is a separate, restricted system from the public portal.</p>
          <a href="http://localhost:5175" className="text-white/80 hover:text-white font-semibold inline-flex items-center gap-1">
            Institutional confirmer? Open the CDF Pulse field app
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>arrow_forward</span>
          </a>
          <a href="http://localhost:5173" className="block text-white/80 hover:text-white font-semibold">
            Looking for public information? Go to the public portal →
          </a>
        </div>
      </div>

      {/* RIGHT: sign-in */}
      <div className="bg-surface flex items-center justify-center p-8 lg:min-h-screen">
        <form onSubmit={handleSubmit} onKeyDown={handleFormKeyDown} className="w-full max-w-[380px] bg-card rounded-2xl p-7 border border-outline-variant">
          <div className="flex items-center justify-between mb-1">
            <h2 className="disp font-bold text-ink">Sign in</h2>
            <button type="button" onClick={() => setShowQuickFill(v => !v)}
              className="text-[10px] font-semibold text-on-surface-variant border border-outline-variant rounded px-1.5 py-0.5 hover:bg-surface-2" title="Demo accounts (Shift+D)">
              ⇧D demo
            </button>
          </div>
          {showQuickFill && (
            <div className="mb-4 rounded-lg border border-accent/30 bg-accent/5 p-2 space-y-1">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-accent px-1 pb-0.5">Quick-fill a demo account</p>
              {DEMO_ACCOUNTS.map(a => (
                <button key={a.email} type="button"
                  onClick={() => { setEmail(a.email); setPassword(a.password); setShowQuickFill(false); }}
                  className="w-full text-left text-xs px-2 py-1.5 rounded hover:bg-card flex items-center justify-between gap-2">
                  <span className="font-medium text-ink">{a.label}</span>
                  <span className="mono text-[10px] text-on-surface-variant">{a.email}</span>
                </button>
              ))}
            </div>
          )}
          <p className="text-xs text-on-surface-variant mb-5">Use your institutional credentials.</p>

          <label className="block mb-3">
            <span className="block text-xs font-semibold text-on-surface-variant mb-1">Institutional email</span>
            <input
              type="email"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="officer@oag.gov.zm"
              className="w-full rounded-lg border border-outline-variant bg-card px-3 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary"
            />
          </label>

          <label className="block mb-3">
            <span className="block text-xs font-semibold text-on-surface-variant mb-1">Password</span>
            <input
              type="password"
              required
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full rounded-lg border border-outline-variant bg-card px-3 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary"
            />
          </label>

          {error && <p className="text-risk-high text-sm mb-3">{error}</p>}

          <div className="mt-1">
            <button
              type="submit"
              disabled={loading}
              className="text-sm font-semibold px-4 py-2 rounded-lg inline-flex items-center gap-2 bg-primary hover:bg-primary-h disabled:opacity-50 text-white"
            >
              {loading ? "Signing in…" : <>Continue <span className="material-symbols-outlined" style={{ fontSize: 16 }}>arrow_forward</span></>}
            </button>
          </div>

          <p className="text-[11px] text-on-surface-variant mt-5 flex items-center gap-1.5">
            <span className="material-symbols-outlined text-risk-low" style={{ fontSize: 15 }}>verified_user</span>
            Every sign-in and action is recorded in the immutable audit log.
          </p>
          <p className="text-xs text-center text-on-surface-variant mt-3">
            <a href="http://localhost:5173" className="hover:text-ink">← Back to public portal</a>
          </p>
        </form>
      </div>
    </div>
  );
}
