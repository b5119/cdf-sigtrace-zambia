export const ROUTES = {
  LOGIN: "/login",
  MFA: "/mfa",
  DASHBOARD: "/dashboard",
  CONTRACTS: "/contracts",
  CONTRACT: "/contracts/:ocid",
  SUPPLIER_NETWORK: "/suppliers/network",
  VERIFICATION_REVIEW: "/verification-review",
  ANALYTICS: "/analytics",
  REPORTS: "/reports",
  NOTIFICATIONS: "/notifications",
  AUDIT: "/audit",
  ADMIN: "/admin",
} as const;
export const contractPath = (ocid: string) => `/contracts/${ocid}`;
