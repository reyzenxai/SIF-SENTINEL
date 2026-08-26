const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function request(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("sif_token") : null;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  get: (path: string) => request(path),
  post: (path: string, body?: unknown) =>
    request(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  del: (path: string) => request(path, { method: "DELETE" }),

  login: (username: string, password: string) =>
    request("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),
  demoCredentials: () => request("/auth/demo-credentials"),

  kpis: () => request("/dashboard/kpis"),
  heatmap: () => request("/dashboard/heatmap"),
  hazardBreakdown: () => request("/dashboard/hazard-breakdown"),
  contractorAnalytics: () => request("/dashboard/contractor-analytics"),

  patternsRadar: () => request("/patterns/radar"),
  patterns: (params?: Record<string, string>) =>
    request(`/patterns${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  pattern: (id: string) => request(`/patterns/${id}`),

  reports: (params?: Record<string, string>) =>
    request(`/reports${params ? "?" + new URLSearchParams(params).toString() : ""}`),
  report: (id: string) => request(`/reports/${id}`),
  createReport: (body: unknown) => request("/reports", { method: "POST", body: JSON.stringify(body) }),

  ontology: () => request("/ontology/hazards"),

  demoStatus: () => request("/demo/status"),
  demoSeed: () => request("/demo/seed", { method: "POST" }),
};

export async function uploadCsv(file: File) {
  const form = new FormData();
  form.append("file", file);
  const token = typeof window !== "undefined" ? localStorage.getItem("sif_token") : null;
  const res = await fetch(`${API_URL}/reports/upload`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    body: form,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
