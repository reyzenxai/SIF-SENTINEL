"use client";
import React, { useState } from "react";

export interface HeatmapSite {
  site: string;
  score: number;
  count: number;
  risk_level: string; // CRITICAL, HIGH, MODERATE, LOW
}

export function Heatmap3D({ data }: { data: HeatmapSite[] }) {
  const [selectedSite, setSelectedSite] = useState<string | null>(null);

  // Default sites if initial load or empty
  const defaultSites: HeatmapSite[] = [
    { site: "Site Alpha", score: 84.5, count: 184, risk_level: "CRITICAL" },
    { site: "Site Bravo", score: 72.1, count: 215, risk_level: "HIGH" },
    { site: "Site Charlie", score: 63.8, count: 142, risk_level: "HIGH" },
    { site: "Site Delta", score: 48.2, count: 168, risk_level: "MODERATE" },
    { site: "Site Echo", score: 32.0, count: 153, risk_level: "LOW" },
    { site: "Site Foxtrot", score: 28.4, count: 138, risk_level: "LOW" },
  ];

  const sites = data && data.length > 0 ? data : defaultSites;

  // Grid coordinates on our 3D isometric plane
  const positions = [
    { bottom: "25%", left: "20%" },
    { bottom: "55%", left: "60%" },
    { bottom: "75%", left: "30%" },
    { bottom: "35%", left: "75%" },
    { bottom: "65%", left: "15%" },
    { bottom: "85%", left: "70%" },
  ];

  return (
    <div className="flex-1 bg-surface-container/70 dark:bg-slate-800/80 backdrop-blur-xl rounded-xl p-6 flex flex-col relative overflow-hidden shadow-md dark:shadow-black/50 border border-white/40 dark:border-white/10 transition-colors">
      <div className="flex justify-between items-center mb-4 relative z-10">
        <div>
          <h2 className="text-headline-sm font-semibold text-on-surface dark:text-slate-100 mb-0.5">Volumetric Facility Risk Heatmap</h2>
          <p className="text-body-sm text-on-surface-variant dark:text-slate-400">Multi-site spatial SIF exposure & structural hazard density</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-bold px-2.5 py-1 rounded bg-primary/10 border border-primary/30 text-primary dark:text-primary-fixed-dim uppercase tracking-wider">
            6 Active Zones
          </span>
        </div>
      </div>

      {/* Quick Zone Filter Tabs */}
      <div className="flex flex-wrap gap-2 mb-4 relative z-10">
        <button
          onClick={() => setSelectedSite(null)}
          className={`text-[12px] font-medium px-3 py-1 rounded-lg transition-all cursor-pointer ${
            selectedSite === null
              ? "bg-primary text-on-primary shadow-sm"
              : "bg-surface-container-low dark:bg-slate-900 text-on-surface-variant dark:text-slate-300 hover:bg-surface-container-high dark:hover:bg-slate-700"
          }`}
        >
          All Facilities
        </button>
        {sites.map((s) => (
          <button
            key={s.site}
            onClick={() => setSelectedSite(s.site)}
            className={`text-[12px] font-medium px-3 py-1 rounded-lg transition-all cursor-pointer flex items-center gap-1.5 ${
              selectedSite === s.site
                ? "bg-primary text-on-primary shadow-sm"
                : "bg-surface-container-low dark:bg-slate-900 text-on-surface-variant dark:text-slate-300 hover:bg-surface-container-high dark:hover:bg-slate-700"
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                s.risk_level === "CRITICAL"
                  ? "bg-error"
                  : s.risk_level === "HIGH"
                  ? "bg-tertiary"
                  : s.risk_level === "MODERATE"
                  ? "bg-secondary"
                  : "bg-primary"
              }`}
            />
            {s.site}
          </button>
        ))}
      </div>
      
      {/* 3D Isometric Viewport */}
      <div className="flex-1 relative z-10 bg-surface-container-low dark:bg-slate-950 rounded-xl overflow-hidden min-h-[340px] flex items-center justify-center border border-outline-variant/30 dark:border-slate-800">
        {/* Spatial Grid Lines */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(28,96,144,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(28,96,144,0.08)_1px,transparent_1px)] dark:bg-[linear-gradient(rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.04)_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

        <div 
          className="w-full h-full flex items-center justify-center"
          style={{ perspective: "1000px" }}
        >
          {/* Base Rotated Plane */}
          <div 
            className="w-[75%] h-[75%] relative transition-transform duration-700 ease-out"
            style={{ 
              transform: "rotateX(60deg) rotateZ(-45deg)", 
              transformStyle: "preserve-3d" 
            }}
          >
            {/* Base platform shadow */}
            <div 
              className="absolute inset-0 bg-primary/10 dark:bg-slate-900/90 rounded-2xl border-2 border-primary/30 dark:border-cyan-500/20 shadow-2xl"
              style={{ transform: "translateZ(0px)" }}
            />
            
            {sites.slice(0, 6).map((site, idx) => {
              const pos = positions[idx % positions.length];
              const isDimmed = selectedSite !== null && selectedSite !== site.site;
              const isFocused = selectedSite === site.site;
              
              // Scale score (0-100) to extruded height (40px - 150px)
              const height = Math.max(35, (site.score / 100) * 140);
              
              let bgClass = "bg-primary";
              let glowColor = "rgba(28,96,144,0.5)";
              if (site.risk_level === "CRITICAL") {
                bgClass = "bg-red-600";
                glowColor = "rgba(220,38,38,0.7)";
              } else if (site.risk_level === "HIGH") {
                bgClass = "bg-amber-500";
                glowColor = "rgba(245,158,11,0.7)";
              } else if (site.risk_level === "MODERATE") {
                bgClass = "bg-teal-500";
                glowColor = "rgba(20,184,166,0.6)";
              } else {
                bgClass = "bg-sky-500";
                glowColor = "rgba(14,165,233,0.6)";
              }

              return (
                <div 
                  key={site.site}
                  onClick={() => setSelectedSite(site.site)}
                  className={`absolute w-12 cursor-pointer transition-all duration-300 group/bar ${
                    isDimmed ? "opacity-30 scale-95" : "opacity-100 hover:scale-105"
                  } ${isFocused ? "ring-2 ring-white scale-110" : ""}`}
                  style={{ 
                    bottom: pos.bottom, 
                    left: pos.left, 
                    height: `${height}px`,
                    transformStyle: "preserve-3d",
                    transform: "translateZ(10px)",
                  }}
                >
                  {/* Front column face */}
                  <div 
                    className={`absolute inset-0 ${bgClass} rounded-sm opacity-90`}
                    style={{ 
                      boxShadow: `0 0 20px ${glowColor}`,
                    }}
                  />
                  {/* Top extruded cap */}
                  <div 
                    className={`absolute top-0 left-0 w-full h-12 ${bgClass} brightness-125 opacity-100 rounded-sm`}
                    style={{
                      transformOrigin: "top",
                      transform: "rotateX(-90deg)",
                    }}
                  />
                  {/* Side extruded face */}
                  <div 
                    className={`absolute top-0 right-0 w-12 h-full ${bgClass} brightness-75 opacity-80 rounded-sm`}
                    style={{
                      transformOrigin: "right",
                      transform: "rotateY(90deg)",
                    }}
                  />
                  
                  {/* Tooltip on hover / selection */}
                  <div 
                    className="absolute -top-16 left-1/2 -translate-x-1/2 whitespace-nowrap bg-slate-950/90 text-white px-3 py-1.5 rounded-lg shadow-xl text-[12px] border border-white/20 transition-all pointer-events-none opacity-0 group-hover/bar:opacity-100"
                    style={{
                      transform: "rotateZ(45deg) rotateX(-60deg)",
                    }}
                  >
                    <div className="font-bold flex items-center gap-1.5">
                      <span>{site.site}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/20">{site.risk_level}</span>
                    </div>
                    <div className="text-slate-300 text-[11px]">SIF Score: <strong className="text-white">{site.score}</strong> · {site.count} logs</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Bottom telemetry legend */}
      <div className="flex items-center justify-between mt-4 text-[12px] text-on-surface-variant dark:text-slate-400">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-red-600"></span> Critical (&ge;80)</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> High (60-79)</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-teal-500"></span> Moderate (35-59)</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-sky-500"></span> Low (&lt;35)</span>
        </div>
        <span className="text-mono-data text-[11px]">Volumetric Elevation &propto; SIF Severity</span>
      </div>
    </div>
  );
}
