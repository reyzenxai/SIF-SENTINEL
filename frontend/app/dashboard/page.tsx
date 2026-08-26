"use client";
import { useEffect, useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, KpiCard, SectionHeading, PatternLink } from "@/components/ui";
import { api } from "@/lib/api";
import { riskColor, trendLabel } from "@/lib/utils";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { AlertTriangle, TrendingUp, MapPin, Building2, Loader2 } from "lucide-react";

interface Kpis {
  total_reports: number;
  sif_precursors: number;
  critical_patterns: number;
  emerging_patterns: number;
  total_patterns: number;
  high_risk_sites: number;
  hazards_extracted: number;
  control_failures_detected: number;
  avg_sif_score: number;
}
interface RadarPattern {
  id: string; title: string; trend: string; trend_pct: number; sif_score: number; report_count: number;
}
interface HeatmapSite { site: string; score: number; count: number; risk_level: string }
interface HazardBreakdown { hazard_category: string; count: number }

export default function DashboardPage() {
  const [kpis, setKpis] = useState<Kpis | null>(null);
  const [radar, setRadar] = useState<RadarPattern[]>([]);
  const [heatmap, setHeatmap] = useState<HeatmapSite[]>([]);
  const [hazards, setHazards] = useState<HazardBreakdown[]>([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadAll() {
    setLoading(true);
    setError(null);
    try {
      const [k, r, h, hz] = await Promise.all([
        api.kpis(), api.patternsRadar(), api.heatmap(), api.hazardBreakdown(),
      ]);
      setKpis(k); setRadar(r); setHeatmap(h); setHazards(hz);
    } catch (e) {
      setError("Could not reach the SIF Sentinel API. Is the backend running on :8000?");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadAll(); }, []);

  async function handleSeed() {
    setSeeding(true);
    try {
      await api.demoSeed();
      await loadAll();
    } finally {
      setSeeding(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-[1400px] w-full mx-auto px-6 py-6">
        {/* Header + ethics banner */}
        <div className="mb-5">
          <div className="flex items-baseline justify-between">
            <div>
              <h1 className="text-xl font-semibold text-slate-900">Safety Command Center</h1>
              <p className="text-sm text-slate-500 mt-0.5">From safety reports to preventive action.</p>
            </div>
          </div>
          <div className="mt-3 text-xs text-amber-800 bg-amber-50 border border-amber-200 rounded px-3 py-2">
            Prototype demonstration uses synthetic/anonymized safety-report data. Production deployment would require authorized OIL data.
          </div>
        </div>

        {error && (
          <Card className="p-6 text-center mb-6">
            <p className="text-sm text-slate-600">{error}</p>
          </Card>
        )}

        {!error && loading && (
          <div className="flex items-center justify-center py-24 text-slate-400 gap-2">
            <Loader2 className="animate-spin" size={18} /> Loading safety intelligence…
          </div>
        )}

        {!error && !loading && kpis && kpis.total_reports === 0 && (
          <Card className="p-10 text-center">
            <p className="text-sm text-slate-600 mb-4">No reports have been ingested yet.</p>
            <button
              onClick={handleSeed}
              disabled={seeding}
              className="bg-slate-900 text-white text-sm font-medium px-4 py-2 rounded hover:bg-slate-800 disabled:opacity-50"
            >
              {seeding ? "Generating & analyzing 1,000 synthetic reports…" : "Load Synthetic Demo Dataset (1,000 reports)"}
            </button>
          </Card>
        )}

        {!error && !loading && kpis && kpis.total_reports > 0 && (
          <>
            {/* KPI row */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
              <KpiCard label="Reports Analyzed" value={kpis.total_reports.toLocaleString()} />
              <KpiCard label="SIF Precursors" value={kpis.sif_precursors.toLocaleString()} sub="High/Critical risk" />
              <KpiCard label="Emerging Patterns" value={kpis.emerging_patterns} />
              <KpiCard label="Critical Patterns" value={kpis.critical_patterns} />
              <KpiCard label="High-Risk Sites" value={kpis.high_risk_sites} />
              <KpiCard label="Avg SIF Score" value={kpis.avg_sif_score} sub="/ 100" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              {/* Emerging SIF Radar */}
              <Card className="lg:col-span-2 p-4">
                <SectionHeading title="Emerging SIF Radar" />
                <div className="divide-y divide-slate-100">
                  {radar.map((p) => {
                    const trend = trendLabel(p.trend);
                    const risk = riskColor(p.sif_score >= 80 ? "CRITICAL" : p.sif_score >= 60 ? "HIGH" : p.sif_score >= 35 ? "MODERATE" : "LOW");
                    return (
                      <PatternLink key={p.id} id={p.id} className="py-3 px-2 -mx-2 rounded flex items-center justify-between group">
                        <div className="flex items-center gap-3">
                          <span className={`w-2 h-2 rounded-full ${risk.dot}`} />
                          <div>
                            <div className="text-sm font-medium text-slate-800 group-hover:text-slate-950">{p.title}</div>
                            <div className="text-xs text-slate-400">{p.report_count} related reports</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-xs text-slate-500 tabular-nums">SIF {p.sif_score}</span>
                          <span className={`text-sm font-semibold tabular-nums ${trend.color}`}>
                            {trend.icon} {Math.abs(p.trend_pct)}%
                          </span>
                        </div>
                      </PatternLink>
                    );
                  })}
                  {radar.length === 0 && <p className="text-sm text-slate-400 py-6 text-center">No patterns discovered yet.</p>}
                </div>
              </Card>

              {/* Hazard breakdown */}
              <Card className="p-4">
                <SectionHeading title="Hazard Category Breakdown" />
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={hazards} layout="vertical" margin={{ left: 8, right: 16 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 11, fill: "#64748b" }} />
                    <YAxis
                      type="category"
                      dataKey="hazard_category"
                      width={110}
                      tick={{ fontSize: 11, fill: "#334155" }}
                    />
                    <Tooltip contentStyle={{ fontSize: 12, borderRadius: 6 }} />
                    <Bar dataKey="count" radius={[0, 3, 3, 0]}>
                      {hazards.map((_, i) => (
                        <Cell key={i} fill={["#dc2626", "#ea580c", "#d97706", "#0891b2", "#475569", "#7c3aed", "#059669"][i % 7]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* SIF Heatmap */}
            <Card className="p-4 mt-5">
              <SectionHeading title="SIF Heatmap — Site-Level Intelligence" />
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                {heatmap.map((site) => {
                  const c = riskColor(site.risk_level);
                  return (
                    <div key={site.site} className={`rounded-lg border p-3 ${c.bg} ${c.border}`}>
                      <div className="flex items-center gap-1.5 text-xs text-slate-500 mb-1">
                        <MapPin size={12} /> {site.site}
                      </div>
                      <div className={`text-2xl font-semibold tabular-nums ${c.text}`}>{site.score}</div>
                      <div className="flex items-center justify-between mt-1">
                        <span className={`text-[11px] font-semibold ${c.text}`}>{site.risk_level}</span>
                        <span className="text-[11px] text-slate-400">{site.count} reports</span>
                      </div>
                    </div>
                  );
                })}
              </div>
              <p className="text-[11px] text-slate-400 mt-3 flex items-center gap-1">
                <AlertTriangle size={11} /> Site-level aggregation from synthetic demo data; not exact geographic coordinates.
              </p>
            </Card>
          </>
        )}
      </main>
    </div>
  );
}
