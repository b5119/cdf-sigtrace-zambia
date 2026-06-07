// Role-based access (mirrors ZedLedger's lib/access.ts): decode the JWT role, route each
// role to its own home, and gate the sidebar. The backend enforces RBAC on every endpoint;
// this layer is for UX + defence-in-depth so admin and officer get distinct interfaces.
import { ROUTES } from "./routes";

export type Role = "system_admin" | "oversight_officer" | "analyst" | "inst_confirmer" | string;

export function decodeJwt(token: string | null): Record<string, unknown> {
  if (!token) return {};
  try {
    const raw = token.split(".")[1];
    if (!raw) return {};
    const b64 = raw.replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(b64.padEnd(b64.length + ((4 - (b64.length % 4)) % 4), "=")));
  } catch { return {}; }
}

export function roleFromToken(token: string | null): Role {
  return (decodeJwt(token).role as string) || "oversight_officer";
}

export const ROLE_LABEL: Record<string, string> = {
  system_admin: "System Administrator",
  oversight_officer: "Oversight Officer",
  analyst: "Analyst",
  inst_confirmer: "Institutional Confirmer",
};

// Each role lands on its own home screen.
const ROLE_HOME: Record<string, string> = {
  system_admin: ROUTES.ADMIN,
  oversight_officer: ROUTES.DASHBOARD,
  analyst: ROUTES.ANALYTICS,
  inst_confirmer: ROUTES.VERIFICATION_REVIEW,
};
export function roleHome(role: string): string {
  return ROLE_HOME[role] ?? ROUTES.DASHBOARD;
}

// Sidebar routes each role may see. system_admin sees everything.
const ROLE_NAV: Record<string, string[]> = {
  oversight_officer: [
    ROUTES.DASHBOARD, ROUTES.CONTRACTS, ROUTES.GHOST_QUEUE, ROUTES.MISMATCH, ROUTES.SUPPLIER_NETWORK,
    ROUTES.VERIFICATION_REVIEW, ROUTES.VERIFY_DOC, ROUTES.ANALYTICS, ROUTES.CASES, ROUTES.REPORTS, ROUTES.AUDIT, ROUTES.NOTIFICATIONS,
  ],
  analyst: [
    ROUTES.DASHBOARD, ROUTES.CONTRACTS, ROUTES.SUPPLIER_NETWORK, ROUTES.ANALYTICS, ROUTES.REPORTS, ROUTES.AUDIT, ROUTES.NOTIFICATIONS,
  ],
  inst_confirmer: [
    ROUTES.DASHBOARD, ROUTES.VERIFICATION_REVIEW, ROUTES.VERIFY_DOC, ROUTES.GHOST_QUEUE, ROUTES.NOTIFICATIONS,
  ],
};
export function navAllowed(role: string, route: string): boolean {
  if (role === "system_admin") return true;
  const allowed = ROLE_NAV[role];
  return allowed ? allowed.includes(route) : true;
}

export function canAccess(role: string, pathname: string): boolean {
  if (role === "system_admin") return true;
  // Admin console is system_admin only (hard guard). Other routes: the sidebar hides what's
  // not relevant and the backend enforces per-action permissions (defence in depth).
  if (pathname === ROUTES.ADMIN || pathname.startsWith(ROUTES.ADMIN + "/")) return false;
  return true;
}
