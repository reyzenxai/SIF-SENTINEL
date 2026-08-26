"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Shield, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { Card } from "@/components/ui";

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
    <div className="min-h-screen flex items-center justify-center bg-slate-900 px-6">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2 justify-center mb-6 text-white">
          <Shield size={22} className="text-amber-400" />
          <span className="text-lg font-semibold tracking-tight">SIF Sentinel</span>
        </div>
        <Card className="p-6">
          <h1 className="text-base font-semibold text-slate-900 mb-1">Sign in</h1>
          <p className="text-xs text-slate-500 mb-4">AI-Powered Safety Early Warning & Prevention Intelligence</p>
          <form onSubmit={handleLogin} className="space-y-3">
            <div>
              <label className="text-xs font-medium text-slate-500 uppercase">Username</label>
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full mt-1 text-sm border border-slate-300 rounded px-3 py-2"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-500 uppercase">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full mt-1 text-sm border border-slate-300 rounded px-3 py-2"
              />
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-slate-900 text-white text-sm font-medium py-2.5 rounded hover:bg-slate-800 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 size={14} className="animate-spin" /> : "Sign In"}
            </button>
          </form>
          <div className="mt-4 pt-4 border-t border-slate-100">
            <p className="text-[11px] text-slate-400 mb-1.5">Demo accounts (password: demo1234)</p>
            <div className="flex flex-wrap gap-1.5">
              {DEMO_ACCOUNTS.map((a) => (
                <button
                  key={a.username}
                  onClick={() => setUsername(a.username)}
                  className="text-[11px] border border-slate-200 rounded px-2 py-1 text-slate-600 hover:bg-slate-50"
                >
                  {a.role}
                </button>
              ))}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
