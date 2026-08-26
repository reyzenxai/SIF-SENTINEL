"use client";
import { useEffect, useState } from "react";
import { AppSidebar } from "@/components/AppSidebar";
import { AppHeader } from "@/components/AppHeader";
import { KpiCard3D } from "@/components/KpiCards3D";
import { Heatmap3D } from "@/components/Heatmap3D";
import { EmergingPatterns } from "@/components/EmergingPatterns";
import { RiskDiagnostics } from "@/components/RiskDiagnostics";
import { api } from "@/lib/api";

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
  id: string;
  title: string;
  trend: string;
  trend_pct: number;
  sif_score: number;
  report_count: number;
}
interface HeatmapSite {
  site: string;
  score: number;
  count: number;
  risk_level: string;
}

export default function DashboardPage() {
  const [kpis, setKpis] = useState<Kpis | null>(null);
  const [radar, setRadar] = useState<RadarPattern[]>([]);
  const [heatmap, setHeatmap] = useState<HeatmapSite[]>([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadAll() {
    setError(null);
    try {
      const [k, r, h] = await Promise.all([
        api.kpis(),
        api.patternsRadar(),
        api.heatmap(),
      ]);
      setKpis(k);
      setRadar(r);
      setHeatmap(h);
    } catch {
      setError(
        "Could not reach the SIF Sentinel API. Is the backend running on :8000?",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    Promise.resolve().then(() => loadAll());
  }, []);

  async function handleSeed() {
    setSeeding(true);
    setLoading(true);
    try {
      await api.demoSeed();
      await loadAll();
    } finally {
      setSeeding(false);
    }
  }

  return (
    <>
      <AppSidebar />
      <div className="pl-72">
        <AppHeader />

        <main className="relative pt-16 min-h-screen bg-background dark:bg-slate-900 transition-colors">
          <div className="flex flex-col w-full h-full relative p-container-margin gap-stack-md">
            {error && (
              <div className="bg-error-container text-on-error-container p-6 rounded-xl relative z-20">
                {error}
              </div>
            )}

            {!error && loading && (
              <div className="flex items-center justify-center py-24 text-on-surface-variant dark:text-slate-400 gap-2 relative z-20">
                <span className="material-symbols-outlined animate-spin">
                  sync
                </span>{" "}
                Loading safety intelligence…
              </div>
            )}

            {!error && !loading && kpis && kpis.total_reports === 0 && (
              <div className="bg-surface-container/70 dark:bg-slate-800/80 backdrop-blur-xl p-10 rounded-xl text-center relative z-20 shadow-md dark:shadow-black/50">
                <p className="text-[14px] text-on-surface-variant dark:text-slate-300 mb-4">
                  No reports have been ingested yet.
                </p>
                <button
                  onClick={handleSeed}
                  disabled={seeding}
                  className="bg-primary text-on-primary text-[14px] font-semibold px-6 py-3 rounded-xl hover:bg-primary/90 disabled:opacity-50 transition-colors"
                >
                  {seeding
                    ? "Generating & analyzing 1,000 synthetic reports…"
                    : "Load Synthetic Demo Dataset (1,000 reports)"}
                </button>
              </div>
            )}

            {!error && !loading && kpis && kpis.total_reports > 0 && (
              <>
                {/* 3D KPI Row */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-gutter w-full z-10 perspective-1000">
                  <KpiCard3D
                    title="Active SIF Patterns"
                    value={kpis.total_patterns}
                    icon="warning"
                    colorClass="primary"
                    badgeText="LIVE"
                    subText={
                      <span className="text-error text-[14px] flex items-center mb-2">
                        <span className="material-symbols-outlined text-[16px] mr-1">
                          trending_up
                        </span>
                        +3
                      </span>
                    }
                  />
                  <KpiCard3D
                    title="Critical Alerts"
                    value={kpis.critical_patterns}
                    icon="emergency"
                    colorClass="error"
                    badgeText="CRITICAL"
                    pulseBadge={true}
                    subText={
                      <span className="text-on-surface-variant dark:text-slate-400 text-[14px] mb-2">
                        Requires Action
                      </span>
                    }
                  />
                  <KpiCard3D
                    title="Reports Processed"
                    value={kpis.total_reports.toLocaleString()}
                    icon="analytics"
                    colorClass="secondary"
                    badgeText="24H"
                    subText={
                      <span className="text-secondary text-[14px] flex items-center mb-2">
                        <span className="material-symbols-outlined text-[16px] mr-1">
                          check_circle
                        </span>
                        98%
                      </span>
                    }
                  />
                  <KpiCard3D
                    title="High-Risk Sites"
                    value={kpis.high_risk_sites}
                    icon="shield"
                    colorClass="tertiary"
                    badgeText="YTD"
                    subText={
                      <span className="text-on-surface-variant dark:text-slate-400 text-[14px] mb-2">
                        Aggregated
                      </span>
                    }
                  />
                </div>

                {/* Mid section: 3D Heatmap + Emerging Patterns */}
                <div className="flex flex-col xl:flex-row gap-gutter min-h-[600px] z-10 relative">
                  <Heatmap3D data={heatmap} />
                  <EmergingPatterns patterns={radar} />
                </div>

                {/* Bottom section: Risk Diagnostics */}
                <RiskDiagnostics kpis={kpis} />
              </>
            )}
          </div>
        </main>
      </div>
    </>
  );
}
