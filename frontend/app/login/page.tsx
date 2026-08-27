"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Loader2 } from "lucide-react";

const DEMO_ACCOUNTS = [
  { username: "safety.manager", role: "Safety Manager" },
  { username: "site.officer", role: "Site Safety Officer" },
  { username: "admin", role: "Administrator" },
];

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("safety.manager");
  const [password, setPassword] = useState("demo1234");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.login(username, password);
      localStorage.setItem("sif_token", res.access_token);
      localStorage.setItem("sif_role", res.role);
      localStorage.setItem("sif_username", res.username);
      router.push("/dashboard");
    } catch {
      setError("Invalid username or password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 font-body-md text-slate-100 px-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-[linear-gradient(rgba(28,96,144,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(28,96,144,0.08)_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none"></div>
      <div className="absolute -top-32 -left-32 w-96 h-96 bg-primary/20 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-secondary/20 rounded-full blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-md relative z-10">
        <div className="flex items-center gap-3 justify-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-primary/20 border border-primary/40 flex items-center justify-center shadow-[0_0_20px_rgba(28,96,144,0.4)]">
            <span className="material-symbols-outlined text-primary-fixed-dim text-3xl">shield</span>
          </div>
          <span className="text-headline-md font-bold tracking-tight text-white">SIF Sentinel</span>
        </div>

        <div className="relative bg-slate-900/80 backdrop-blur-2xl rounded-2xl p-8 shadow-2xl border border-white/10 overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary via-primary-container to-secondary"></div>
          
          <h1 className="text-title-lg font-bold text-white mb-1">Command Center Access</h1>
          <p className="text-body-md text-slate-400 mb-6">AI-Powered Safety Early Warning & SIF Prevention Intelligence</p>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="text-label-caps text-slate-400 font-semibold uppercase tracking-wider block mb-1.5">Username</label>
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-slate-950/70 border border-slate-700 rounded-xl px-4 py-2.5 text-body-md text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all"
                placeholder="Enter username"
              />
            </div>
            <div>
              <label className="text-label-caps text-slate-400 font-semibold uppercase tracking-wider block mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-950/70 border border-slate-700 rounded-xl px-4 py-2.5 text-body-md text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all"
                placeholder="????????"
              />
            </div>
            {error && (
              <div className="p-3 rounded-lg bg-error/10 border border-error/30 text-error text-body-md flex items-center gap-2">
                <span className="material-symbols-outlined text-[18px]">error</span>
                {error}
              </div>
            )}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary hover:bg-primary/90 text-on-primary font-semibold text-body-md py-3 rounded-xl shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2 mt-2 cursor-pointer"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : "Authenticate & Enter"}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-slate-800">
            <p className="text-label-caps text-slate-400 font-semibold uppercase tracking-wider mb-2.5">Demo Presets (password: demo1234)</p>
            <div className="flex flex-wrap gap-2">
              {DEMO_ACCOUNTS.map((a) => (
                <button
                  key={a.username}
                  onClick={() => setUsername(a.username)}
                  className={`text-[12px] font-medium border rounded-lg px-3 py-1.5 transition-all cursor-pointer ${
                    username === a.username
                      ? "bg-primary/20 border-primary text-primary-fixed-dim"
                      : "bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                  }`}
                >
                  {a.role}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
