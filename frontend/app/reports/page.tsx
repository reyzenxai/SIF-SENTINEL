"use client";
import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AppSidebar } from "@/components/AppSidebar";
import { AppHeader } from "@/components/AppHeader";
import { RiskBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { Search, Loader2, Upload, AlertTriangle } from "lucide-react";

interface ReportRow {
  id: string; title: string; report_type: string; location: string; department: string;
  contractor: string; report_date: string; severity: string; sif_score: number | null;
  risk_level: string | null; hazard_category: string | null;
}

export default function ReportsPage() {
  const router = useRouter();
  const [reports, setReports] = useState<ReportRow[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState("");
  const [semantic, setSemantic] = useState("");
  const [riskFilter, setRiskFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");

  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    const params: Record<string, string> = { size: "40" };
    if (keyword) params.keyword = keyword;
    if (semantic) params.semantic_query = semantic;
    if (riskFilter) params.risk_level = riskFilter;
    if (typeFilter) params.report_type = typeFilter;
    
    api.reports(params)
      .then((res) => { 
        setReports(res.reports); 
        setTotal(res.total); 
      })
      .catch((err) => {
        setError("Could not reach the SIF Sentinel API. Is the backend running on :8000?");
        console.error(err);
      })
      .finally(() => setLoading(false));
  }, [keyword, semantic, riskFilter, typeFilter]);

  useEffect(() => { 
    Promise.resolve().then(() => load()); 
  }, [load]);

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    load();
  }

  return (
    <div className="bg-background dark:bg-slate-900 font-body-md text-on-surface dark:text-slate-100 min-h-screen overflow-x-hidden">
      <AppSidebar />
      <div className="pl-72 flex flex-col min-h-screen">
        <AppHeader />
        <main className="relative pt-16 flex-1 p-container-margin">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-headline-md font-semibold text-on-surface dark:text-slate-100">Incident & Safety Reports</h1>
              <p className="text-body-md text-on-surface-variant dark:text-slate-400 mt-1">
                {total.toLocaleString()} reports indexed ? Real-time NLP, hazard categorization & SIF risk tiering
              </p>
            </div>
            <Link 
              href="/reports/upload" 
              className="flex items-center gap-2 px-4 py-2 bg-primary text-on-primary rounded-xl text-label-caps font-semibold hover:bg-primary/90 transition-colors shadow-sm"
            >
              <Upload size={16} /> Upload CSV
            </Link>
          </div>

          <div className="relative bg-surface-container/70 dark:bg-slate-800/80 backdrop-blur-xl rounded-xl p-4 shadow-sm dark:shadow-black/50 mb-6 border border-white/40 dark:border-white/10">
            <form onSubmit={handleSearchSubmit} className="flex flex-wrap items-center gap-3">
              <div className="flex-1 min-w-[240px] flex items-center gap-2 bg-surface dark:bg-slate-900 border border-outline-variant/40 dark:border-slate-700 rounded-xl px-3 py-2">
                <Search size={16} className="text-on-surface-variant dark:text-slate-400" />
                <input
                  value={semantic}
                  onChange={(e) => setSemantic(e.target.value)}
                  placeholder='Semantic vector search, e.g. "electrical isolation failure"'
                  className="flex-1 text-body-md bg-transparent outline-none text-on-surface dark:text-slate-100 placeholder:text-on-surface-variant/60 dark:placeholder:text-slate-500"
                />
              </div>
              <input
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="Keyword filter..."
                className="text-body-md bg-surface dark:bg-slate-900 border border-outline-variant/40 dark:border-slate-700 rounded-xl px-3 py-2 w-48 text-on-surface dark:text-slate-100"
              />
              <select 
                value={riskFilter} 
                onChange={(e) => setRiskFilter(e.target.value)} 
                className="text-body-md bg-surface dark:bg-slate-900 border border-outline-variant/40 dark:border-slate-700 rounded-xl px-3 py-2 text-on-surface dark:text-slate-100 outline-none"
              >
                <option value="">All Risk Tiers</option>
                <option value="CRITICAL">Critical Risk</option>
                <option value="HIGH">High Risk</option>
                <option value="MODERATE">Moderate Risk</option>
                <option value="LOW">Low Risk</option>
              </select>
              <select 
                value={typeFilter} 
                onChange={(e) => setTypeFilter(e.target.value)} 
                className="text-body-md bg-surface dark:bg-slate-900 border border-outline-variant/40 dark:border-slate-700 rounded-xl px-3 py-2 text-on-surface dark:text-slate-100 outline-none"
              >
                <option value="">All Event Types</option>
                <option value="UNSAFE_ACT">Unsafe Act</option>
                <option value="UNSAFE_CONDITION">Unsafe Condition</option>
                <option value="NEAR_MISS">Near Miss</option>
              </select>
              <button 
                type="submit" 
                className="px-5 py-2 bg-primary text-on-primary rounded-xl text-label-caps font-semibold hover:bg-primary/90 transition-colors"
              >
                Search
              </button>
            </form>
          </div>

          <div className="relative bg-surface-container/70 dark:bg-slate-800/80 backdrop-blur-xl rounded-xl shadow-md dark:shadow-black/50 overflow-hidden border border-white/40 dark:border-white/10">
            {error ? (
              <div className="p-8 text-center flex flex-col items-center justify-center text-error dark:text-red-400 gap-2">
                <AlertTriangle size={32} />
                <p className="font-semibold">{error}</p>
              </div>
            ) : loading ? (
              <div className="flex items-center justify-center py-20 text-on-surface-variant dark:text-slate-400 gap-3">
                <Loader2 className="animate-spin" size={20} />
                <span className="text-body-md">Loading intelligence reports?</span>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-body-md">
                  <thead className="bg-surface-container-high/60 dark:bg-slate-900/60 border-b border-outline-variant/30 dark:border-slate-800 text-label-caps text-on-surface-variant dark:text-slate-400 uppercase tracking-wider">
                    <tr>
                      <th className="px-6 py-3.5 font-semibold">Report Summary</th>
                      <th className="px-4 py-3.5 font-semibold">Hazard Category</th>
                      <th className="px-4 py-3.5 font-semibold">Facility / Location</th>
                      <th className="px-4 py-3.5 font-semibold">Contractor</th>
                      <th className="px-4 py-3.5 font-semibold">Date</th>
                      <th className="px-4 py-3.5 font-semibold">SIF Score</th>
                      <th className="px-6 py-3.5 font-semibold text-right">Risk Level</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant/20 dark:divide-slate-800/60">
                    {reports.map((r) => (
                      <tr 
                        key={r.id} 
                        className="hover:bg-surface-container-high/50 dark:hover:bg-slate-700/40 cursor-pointer transition-colors" 
                        onClick={() => router.push(`/reports/${r.id}`)}
                      >
                        <td className="px-6 py-4 font-semibold max-w-sm truncate text-on-surface dark:text-slate-100">
                          {r.title}
                        </td>
                        <td className="px-4 py-4 text-on-surface-variant dark:text-slate-300">
                          {r.hazard_category || "?"}
                        </td>
                        <td className="px-4 py-4 text-on-surface-variant dark:text-slate-300">
                          {r.location}
                        </td>
                        <td className="px-4 py-4 text-on-surface-variant dark:text-slate-300">
                          {r.contractor}
                        </td>
                        <td className="px-4 py-4 text-mono-data text-on-surface-variant dark:text-slate-400">
                          {formatDate(r.report_date)}
                        </td>
                        <td className="px-4 py-4 text-mono-data font-bold text-primary dark:text-primary-fixed-dim">
                          {r.sif_score ?? "?"}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <RiskBadge level={r.risk_level} />
                        </td>
                      </tr>
                    ))}
                    {reports.length === 0 && (
                      <tr>
                        <td colSpan={7} className="text-center text-on-surface-variant dark:text-slate-400 py-16">
                          No reports match your selected criteria.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
