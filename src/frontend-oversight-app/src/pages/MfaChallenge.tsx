import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../lib/api";
import { useAuth } from "../store/auth";
import { ROUTES } from "../lib/routes";

export default function MfaChallenge() {
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { mfaChallengeToken, setTokens } = useAuth();

  if (!mfaChallengeToken) { navigate(ROUTES.LOGIN); return null; }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true); setError(null);
    try {
      const res = await authApi.mfaVerify(mfaChallengeToken!, code);
      const data = res.data;
      if (data.access_token && data.refresh_token) {
        setTokens(data.access_token, data.refresh_token);
        navigate(ROUTES.DASHBOARD);
      }
    } catch {
      setError("Invalid code. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-ink flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <span className="material-symbols-outlined text-accent text-5xl">phonelink_lock</span>
          <h1 className="text-white font-display text-2xl font-bold mt-3">Two-Factor Authentication</h1>
          <p className="text-sidebar-muted text-sm mt-1">Enter the 6-digit code from your authenticator app</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-card rounded-2xl p-8 space-y-4">
          <input value={code} onChange={e => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
            inputMode="numeric" autoFocus required
            className="w-full border border-outline-variant rounded-lg px-3 py-3 text-center mono text-2xl tracking-[0.5em] focus:outline-none focus:ring-2 focus:ring-primary/30 bg-surface"
            placeholder="000000" />
          {error && <p className="text-risk-high text-sm text-center">{error}</p>}
          <button type="submit" disabled={loading || code.length !== 6}
            className="w-full bg-primary hover:bg-primary-h disabled:opacity-50 text-white font-semibold py-3 rounded-lg">
            {loading ? "Verifying…" : "Verify & sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
