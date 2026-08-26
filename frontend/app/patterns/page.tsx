"use client";
import { useEffect, useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, SectionHeading, PatternLink } from "@/components/ui";
import { api } from "@/lib/api";
import { riskColor, trendLabel, formatDate } from "@/lib/utils";
import { Loader2 } from "lucide-react";

interface Pattern {
  id: string; title: string; summary: string; report_count: number;
  trend: string; trend_pct: number; sif_score: number; sif_risk_level: string;
  common_hazard: string; locations: string[]; contractors: string[];
  first_seen: string; last_seen: string;
}

export default function PatternsPage() {
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [trendFilter, setTrendFilter] = useState<string>("");

  useEffect(() => {
    setLoading(true);
    api.patterns(trendFilter ? { trend: trendFilter } : undefined)
      .then((res) => setPatterns(res.patterns))
      .finally(() => setLoading(false));
  }, [trendFilter]);

  return (
    <div className="flex-1 flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-[1400px] w-full mx-auto px-6 py-6">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">SIF Precursor Patterns</h1>
            <p className="text-sm text-slate-500 mt-0.5">Semantically discovered patterns across reports with different wording, same underlying hazard.</p>
          </div>
          <select
            value={trendFilter}
            onChange={(e) => setTrendFilter(e.target.value)}
            className="text-sm border border-slate-300 rounded px-2.5 py-1.5 bg-white"
          >
            <option value="">All trends</option>
            <option value="increasing">Increasing</option>
            <option value="decreasing">Decreasing</option>
            <option value="stable">Stable</option>
            <option value="new">Newly Emerging</option>
          </select>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-24 text-slate-400 gap-2">
            <Loader2 className="animate-spin" size={18} /> Loading patterns…
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {patterns.map((p) => {
              const risk = riskColor(p.sif_risk_level);
              const trend = trendLabel(p.trend);
              return (
                <PatternLink key={p.id} id={p.id}>
                  <Card className={`p-4 h-full hover:shadow-sm transition-shadow border-l-4`} >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="text-xs font-semibold text-slate-400 uppercase">{p.common_hazard}</div>
                        <h3 className="text-base font-semibold text-slate-900 mt-0.5">{p.title}</h3>
                      </div>
                      <span className={`shrink-0 text-xs font-bold px-2 py-1 rounded ${risk.bg} ${risk.text} border ${risk.border}`}>
                        {p.sif_score}/100
                      </span>
                    </div>
                    <p className="text-sm text-slate-500 mt-2 line-clamp-2">{p.summary}</p>
                    <div className="flex items-center gap-4 mt-3 text-xs text-slate-500">
                      <span>{p.report_count} reports</span>
                      <span>{p.locations.length} locations</span>
                      <span>{p.contractors.length} contractors</span>
                    </div>
                    <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100">
                      <span className={`text-sm font-semibold ${trend.color}`}>
                        {trend.icon} {trend.word} {p.trend_pct !== 0 && `(${p.trend_pct > 0 ? "+" : ""}${p.trend_pct}%)`}
                      </span>
                      <span className="text-xs text-slate-400">Last seen {formatDate(p.last_seen)}</span>
                    </div>
                  </Card>
                </PatternLink>
              );
            })}
            {patterns.length === 0 && (
              <Card className="p-10 text-center col-span-2">
                <p className="text-sm text-slate-400">No patterns match this filter.</p>
              </Card>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
