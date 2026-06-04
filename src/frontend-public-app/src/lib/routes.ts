// Canonical route table — mirrors design/screens/generate.py route table R
export const ROUTES = {
  HOME:         "/",
  DASHBOARD:    "/dashboard",
  MAP:          "/map",
  CONSTITUENCY: "/constituencies/:id",
  CONSTITUENCIES: "/constituencies",
  PROJECT:      "/projects/:id",
  RISK:         "/risk",
  OPEN_DATA:    "/open-data",
  ABOUT:        "/about",
  AUDIT_TRAIL:  "/ledger",
  VERIFY:       "/verify",
  CONSENT:      "/data-protection",
} as const;

export function constituencyPath(id: string) {
  return `/constituencies/${id}`;
}

export function projectPath(id: string) {
  return `/projects/${id}`;
}
