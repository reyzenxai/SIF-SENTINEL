"use client";
import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Navbar } from "@/components/navbar";
import { Card, RiskBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { Search, Loader2, Upload } from "lucide-react";

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
    <div className="flex-1 flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-[1400px] w-full mx-auto px-6 py-6">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">Safety Reports</h1>
            <p className="text-sm text-slate-500 mt-0.5">{total.toLocaleString()} reports · keyword, hazard, contractor, or semantic search</p>
          </div>
          <Link href="/reports/upload" className="flex items-center gap-1.5 text-sm font-medium border border-slate-300 bg-white px-3 py-1.5 rounded hover:bg-slate-50">
            <Upload size={14} /> Upload CSV
          </Link>
        </div>

        <Card className="p-3 mb-4">
          <form onSubmit={handleSearchSubmit} className="flex flex-wrap gap-2">
            <div className="flex-1 min-w-[220px] flex items-center gap-2 border border-slate-300 rounded px-2.5 bg-white">
              <Search size={14} className="text-slate-400" />
              <input
                value={semantic}
                onChange={(e) => setSemantic(e.target.value)}
                placeholder='Semantic search, e.g. "electrical isolation"'
                className="flex-1 text-sm py-1.5 outline-none"
              />
            </div>
            <input
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="Keyword filter"
              className="text-sm border border-slate-300 rounded px-2.5 py-1.5 w-40"
            />
            <select value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)} className="text-sm border border-slate-300 rounded px-2 py-1.5 bg-white">
              <option value="">Any risk</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MODERATE">Moderate</option>
              <option value="LOW">Low</option>
            </select>
            <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)} className="text-sm border border-slate-300 rounded px-2 py-1.5 bg-white">
              <option value="">Any type</option>
              <option value="UNSAFE_ACT">Unsafe Act</option>
              <option value="UNSAFE_CONDITION">Unsafe Condition</option>
              <option value="NEAR_MISS">Near Miss</option>
            </select>
            <button type="submit" className="text-sm font-medium bg-slate-900 text-white px-3 py-1.5 rounded hover:bg-slate-800">
              Search
            </button>
          </form>
        </Card>

        <Card className="overflow-hidden">
          {error ? (
            <div className="bg-red-50 text-red-600 p-6 flex items-center justify-center">
              {error}
            </div>
          ) : loading ? (
            <div className="flex items-center justify-center py-16 text-slate-400 gap-2">
              <Loader2 className="animate-spin" size={16} /> Loading reports…
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200 text-xs text-slate-500 uppercase">
                <tr>
                  <th className="text-left px-4 py-2.5 font-medium">Report</th>
                  <th className="text-left px-4 py-2.5 font-medium">Hazard</th>
                  <th className="text-left px-4 py-2.5 font-medium">Location</th>
                  <th className="text-left px-4 py-2.5 font-medium">Contractor</th>
                  <th className="text-left px-4 py-2.5 font-medium">Date</th>
                  <th className="text-left px-4 py-2.5 font-medium">SIF Score</th>
                  <th className="text-left px-4 py-2.5 font-medium">Risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {reports.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50 cursor-pointer" onClick={() => router.push(`/reports/${r.id}`)}>
                    <td className="px-4 py-2.5 max-w-[320px] truncate text-slate-800">{r.title}</td>
                    <td className="px-4 py-2.5 text-slate-500">{r.hazard_category || "—"}</td>
                    <td className="px-4 py-2.5 text-slate-500">{r.location}</td>
                    <td className="px-4 py-2.5 text-slate-500">{r.contractor}</td>
                    <td className="px-4 py-2.5 text-slate-500">{formatDate(r.report_date)}</td>
                    <td className="px-4 py-2.5 tabular-nums text-slate-700">{r.sif_score ?? "—"}</td>
                    <td className="px-4 py-2.5"><RiskBadge level={r.risk_level} /></td>
                  </tr>
                ))}
                {reports.length === 0 && (
                  <tr><td colSpan={7} className="text-center text-slate-400 py-10">No reports match this search.</td></tr>
                )}
              </tbody>
            </table>
          )}
        </Card>
      </main>
    </div>
  );
}
