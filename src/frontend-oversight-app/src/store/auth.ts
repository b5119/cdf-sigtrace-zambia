import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { MeResponse } from "../lib/api";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: MeResponse | null;
  mfaChallengeToken: string | null;
  setTokens: (access: string, refresh: string) => void;
  setMfaChallenge: (token: string) => void;
  setUser: (user: MeResponse) => void;
  logout: () => void;
}

export const useAuth = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      mfaChallengeToken: null,
      setTokens: (access, refresh) => {
        localStorage.setItem("access_token", access);
        set({ accessToken: access, refreshToken: refresh, mfaChallengeToken: null });
      },
      setMfaChallenge: (token) => set({ mfaChallengeToken: token }),
      setUser: (user) => set({ user }),
      logout: () => {
        localStorage.removeItem("access_token");
        set({ accessToken: null, refreshToken: null, user: null, mfaChallengeToken: null });
      },
    }),
    { name: "auth-store", partialize: (s) => ({ accessToken: s.accessToken, refreshToken: s.refreshToken }) }
  )
);
