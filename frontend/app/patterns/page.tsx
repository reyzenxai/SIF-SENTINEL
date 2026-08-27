"use client";
import { useEffect, useState } from "react";
import { AppSidebar } from "@/components/AppSidebar";
import { AppHeader } from "@/components/AppHeader";
import { PatternLink } from "@/components/ui";
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
    <div className="bg-background dark:bg-slate-900 font-body-md text-on-surface dark:text-slate-100 min-h-screen overflow-x-hidden">
      <AppSidebar />
      <div className="pl-72 flex flex-col min-h-screen">
        <AppHeader />
        <main className="relative pt-16 flex-1 p-container-margin">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-headline-md font-semibold text-on-surface dark:text-slate-100">SIF Precursor Patterns & Clusters</h1>
              <p className="text-body-md text-on-surface-variant dark:text-slate-400 mt-1">
                Semantically clustered hazard intelligence across heterogeneous incident descriptions.
              </p>
            </div>
            <select
              value={trendFilter}
              onChange={(e) => setTrendFilter(e.target.value)}
              className="text-body-md bg-surface dark:bg-slate-800 border border-outline-variant/40 dark:border-slate-700 rounded-xl px-4 py-2 text-on-surface dark:text-slate-100 outline-none shadow-sm"
            >
              <option value="">All Trends</option>
              <option value="increasing">Increasing Velocity</option>
              <option value="decreasing">Decreasing Velocity</option>
              <option value="stable">Stable Frequency</option>
              <option value="new">Newly Emerging</option>
            </select>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-28 text-on-surface-variant dark:text-slate-400 gap-3">
              <Loader2 className="animate-spin" size={24} />
              <span className="text-body-md">Clustering pattern telemetry?</span>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {patterns.map((p) => {
                const risk = riskColor(p.sif_risk_level);
                const trend = trendLabel(p.trend);
                const isCritical = p.sif_risk_level === "CRITICAL" || p.sif_score >= 80;
                const isHigh = p.sif_risk_level === "HIGH" || (p.sif_score >= 60 && p.sif_score < 80);
                
                return (
                  <PatternLink key={p.id} id={p.id}>
                    <div className={`relative bg-surface-container/70 dark:bg-slate-800/80 backdrop-blur-xl rounded-xl p-6 shadow-sm dark:shadow-black/50 overflow-hidden group transition-all duration-300 ease-out hover:-translate-y-1 hover:shadow-xl dark:hover:shadow-black/70 border border-white/40 dark:border-white/10 ${
                      isCritical ? "border-l-4 border-l-error" : isHigh ? "border-l-4 border-l-tertiary" : "border-l-4 border-l-secondary"
                    }`}>
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div>
                          <span className="text-label-caps text-on-surface-variant dark:text-slate-400 font-bold uppercase tracking-wider">
                            {p.common_hazard || "UNCLASSIFIED HAZARD"}
                          </span>
                          <h3 className="text-title-lg text-on-surface dark:text-slate-100 font-semibold mt-1 group-hover:text-primary dark:group-hover:text-primary-fixed-dim transition-colors">
                            {p.title}
                          </h3>
                        </div>
                        <span className={`shrink-0 text-label-caps font-bold px-2.5 py-1 rounded-md ${risk.bg} ${risk.text} border ${risk.border}`}>
                          SIF {p.sif_score}/100
                        </span>
                      </div>
                      <p className="text-body-md text-on-surface-variant dark:text-slate-300 mt-2 line-clamp-2">
                        {p.summary}
                      </p>
                      <div className="flex items-center gap-4 mt-4 text-mono-data text-on-surface-variant dark:text-slate-400 text-[12px]">
                        <span>{p.report_count} incident reports</span>
                        <span>?</span>
                        <span>{p.locations.length} locations</span>
                        <span>?</span>
                        <span>{p.contractors.length} contractors</span>
                      </div>
                      <div className="flex items-center justify-between mt-4 pt-3 border-t border-outline-variant/20 dark:border-slate-700/60">
                        <span className={`text-body-md font-semibold ${trend.color} flex items-center gap-1`}>
                          {trend.icon} {trend.word} {p.trend_pct !== 0 && `(${p.trend_pct > 0 ? "+" : ""}${p.trend_pct}%)`}
                        </span>
                        <span className="text-mono-data text-on-surface-variant dark:text-slate-400 text-[12px]">
                          Last seen {formatDate(p.last_seen)}
                        </span>
                      </div>
                    </div>
                  </PatternLink>
                );
              })}
              {patterns.length === 0 && (
                <div className="relative bg-surface-container/70 dark:bg-slate-800/80 backdrop-blur-xl rounded-xl p-12 text-center col-span-2 border border-white/40 dark:border-white/10">
                  <p className="text-body-md text-on-surface-variant dark:text-slate-400">No patterns match your selected trend filter.</p>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
