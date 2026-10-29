/* eslint-disable @typescript-eslint/no-explicit-any */
export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// All calls go to /api/*, which next.config.mjs proxies to the Python backend.
export async function api<T = any>(path: string): Promise<T> {
  const res = await fetch(`/api${path}`, { cache: "no-store" });
  if (!res.ok) {
    let detail = res.statusText || "Request failed";
    try {
      const body = await res.json();
      if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* not JSON */
    }
    throw new ApiError(res.status, detail);
  }
  return res.json();
}

// yfpy responses sometimes wrap items like {team: {...}}; this handles both shapes.
export const unwrap = (o: any, key: string) => o?.[key] ?? o;
export const show = (v: unknown) => (v === null || v === undefined || v === "" ? "—" : String(v));
