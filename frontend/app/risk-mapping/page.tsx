"use client";
import { useEffect, useState } from "react";
import { AppSidebar } from "@/components/AppSidebar";
import { AppHeader } from "@/components/AppHeader";
import { Heatmap3D, HeatmapSite } from "@/components/Heatmap3D";
import { api } from "@/lib/api";
import { Loader2, ShieldAlert, Layers, MapPin, Activity } from "lucide-react";

export default function RiskMappingPage() {
  const [heatmap, setHeatmap] = useState<HeatmapSite[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"isometric" | "topological">("isometric");

  useEffect(() => {
    api.heatmap()
      .then((res) => setHeatmap(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="bg-background dark:bg-slate-900 font-body-md text-on-surface dark:text-slate-100 min-h-screen overflow-x-hidden">
      <AppSidebar />
      <div className="pl-72 flex flex-col min-h-screen">
        <AppHeader />
        <main className="relative pt-16 flex-1 p-container-margin">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-headline-md font-semibold text-on-surface dark:text-slate-100">3D Volumetric Risk Mapping & Geospatial Telemetry</h1>
              <p className="text-body-md text-on-surface-variant dark:text-slate-400 mt-1">
                Real-time structural hazard density across physical facilities, equipment manifolds, and contractor work zones.
              </p>
            </div>
            <div className="flex items-center gap-2 bg-surface-container/70 dark:bg-slate-800 p-1 rounded-xl border border-outline-variant/30">
              <button 
                onClick={() => setActiveTab("isometric")}
                className={`px-3 py-1.5 rounded-lg text-[13px] font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                  activeTab === "isometric" ? "bg-primary text-on-primary shadow-sm" : "text-on-surface-variant dark:text-slate-400"
                }`}
              >
                <Layers size={15} /> 3D Isometric View
              </button>
              <button 
                onClick={() => setActiveTab("topological")}
                className={`px-3 py-1.5 rounded-lg text-[13px] font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                  activeTab === "topological" ? "bg-primary text-on-primary shadow-sm" : "text-on-surface-variant dark:text-slate-400"
                }`}
              >
                <Activity size={15} /> Facility Matrix
              </button>
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-28 text-on-surface-variant dark:text-slate-400 gap-3">
              <Loader2 className="animate-spin" size={24} />
              <span className="text-body-md">Rendering 3D spatial terrain?</span>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Primary 3D Heatmap Component */}
              <div className="min-h-[480px]">
                <Heatmap3D data={heatmap} />
              </div>

              {/* Facility Telemetry Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {heatmap.map((site) => {
                  const isCrit = site.risk_level === "CRITICAL" || site.score >= 80;
                  const isHigh = site.risk_level === "HIGH" || (site.score >= 60 && site.score < 80);
                  return (
                    <div 
                      key={site.site}
                      className="bg-surface-container/70 dark:bg-slate-800/80 backdrop-blur-xl rounded-xl p-6 border border-white/40 dark:border-white/10 shadow-sm transition-all hover:shadow-md"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                            isCrit ? "bg-error/20 text-error" : isHigh ? "bg-tertiary/20 text-tertiary" : "bg-primary/20 text-primary dark:text-primary-fixed-dim"
                          }`}>
                            <MapPin size={18} />
                          </div>
                          <div>
                            <h3 className="text-title-lg font-bold text-on-surface dark:text-slate-100">{site.site}</h3>
                            <p className="text-[12px] text-on-surface-variant dark:text-slate-400">Sector Alpha / Offshore Rig</p>
                          </div>
                        </div>
                        <span className={`text-[11px] font-bold px-2 py-0.5 rounded border ${
                          isCrit ? "bg-error/10 text-error border-error/30" : isHigh ? "bg-tertiary/10 text-tertiary border-tertiary/30" : "bg-secondary/10 text-secondary border-secondary/30"
                        }`}>
                          {site.risk_level}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mt-4 pt-3 border-t border-outline-variant/20 dark:border-slate-700/60 text-body-sm">
                        <div>
                          <span className="text-[11px] text-on-surface-variant dark:text-slate-400 uppercase tracking-wider block">SIF Severity Index</span>
                          <span className="text-[20px] font-bold text-primary dark:text-primary-fixed-dim">{site.score} / 100</span>
                        </div>
                        <div>
                          <span className="text-[11px] text-on-surface-variant dark:text-slate-400 uppercase tracking-wider block">Logged Telemetry</span>
                          <span className="text-[20px] font-bold text-on-surface dark:text-slate-100">{site.count} Incidents</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
