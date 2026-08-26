"use client";
import React from "react";

interface HeatmapSite {
  site: string;
  score: number;
  count: number;
  risk_level: string; // CRITICAL, HIGH, MODERATE, LOW
}

export function Heatmap3D({ data }: { data: HeatmapSite[] }) {
  // We'll map the sites to specific positions on our 3D isometric plane
  const positions = [
    { bottom: "20%", left: "20%" },
    { bottom: "50%", left: "60%" },
    { bottom: "70%", left: "30%" },
    { bottom: "30%", left: "80%" },
    { bottom: "60%", left: "10%" },
    { bottom: "80%", left: "70%" },
  ];

  return (
    <div className="flex-1 bg-surface-container/70 dark:bg-slate-800/80 backdrop-blur-xl rounded-xl p-6 flex flex-col relative overflow-hidden shadow-md dark:shadow-black/50 transition-colors">
      <div className="absolute inset-0 bg-gradient-to-br from-white/30 to-transparent dark:from-white/5 pointer-events-none"></div>
      <div className="absolute -top-[1px] -left-[1px] w-full h-full border-t border-l border-white/50 dark:border-white/10 pointer-events-none rounded-xl"></div>
      
      <div className="flex justify-between items-center mb-6 relative z-10">
        <div>
          <h2 className="text-[24px] font-semibold text-on-surface dark:text-slate-100 mb-1">Volumetric Risk Heatmap</h2>
          <p className="text-[14px] text-on-surface-variant dark:text-slate-400">Real-time SIF exposure across zones</p>
        </div>
        <div className="flex gap-2">
          <button className="px-3 py-1 bg-primary text-on-primary rounded text-[12px] font-bold tracking-wider hover:bg-primary/90 transition-colors">ACTIVE ZONES</button>
        </div>
      </div>
      
      <div className="flex-1 relative z-10 bg-surface-container-low dark:bg-slate-900 rounded-lg overflow-hidden group min-h-[300px]">
        {/* Isometric Grid Background */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(28,96,144,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(28,96,144,0.05)_1px,transparent_1px)] dark:bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:20px_20px] pointer-events-none"></div>
        
        <div className="absolute inset-0 flex items-center justify-center perspective-[800px]">
          {/* Base Plane */}
          <div className="w-[80%] h-[80%] relative transform rotate-x-[60deg] rotate-z-[-45deg] preserve-3d group-hover:rotate-z-[-35deg] group-hover:rotate-x-[55deg] transition-transform duration-1000 ease-in-out">
            
            {data.slice(0, 6).map((site, idx) => {
              const pos = positions[idx % positions.length];
              
              // Map score (0-100) to height (40px to 160px)
              const height = Math.max(40, (site.score / 100) * 160);
              
              // Colors based on risk level
              let colorBase = "bg-primary";
              let shadowBase = "rgba(28,96,144,";
              if (site.risk_level === "CRITICAL") {
                colorBase = "bg-error";
                shadowBase = "rgba(186,26,26,";
              } else if (site.risk_level === "HIGH") {
                colorBase = "bg-tertiary";
                shadowBase = "rgba(118,87,0,";
              } else if (site.risk_level === "MODERATE") {
                colorBase = "bg-secondary";
                shadowBase = "rgba(0,106,106,";
              }

              return (
                <div 
                  key={site.site}
                  className={`absolute w-12 ${colorBase}/80 backdrop-blur-sm rounded-sm shadow-[0_0_15px_${shadowBase}0.5)] transform translate-z-[10px] transition-all duration-300 hover:brightness-125 cursor-pointer flex items-end justify-center group/bar`}
                  style={{ bottom: pos.bottom, left: pos.left, height: `${height}px` }}
                  title={`${site.site} - Score: ${site.score}`}
                >
                  {/* Top face */}
                  <div className={`absolute top-0 w-full h-4 ${colorBase}/90 backdrop-blur-sm transform origin-bottom rotate-x-[90deg] shadow-[0_-5px_15px_${shadowBase}0.8)]`}></div>
                  {/* Side face */}
                  <div className={`absolute right-0 w-4 h-full ${colorBase}/60 backdrop-blur-sm transform origin-left rotate-y-[90deg]`}></div>
                  
                  {/* Tooltip on hover */}
                  <div className="absolute bottom-full mb-6 whitespace-nowrap bg-surface-container-high dark:bg-slate-700 text-on-surface dark:text-slate-100 px-3 py-2 rounded shadow-lg dark:shadow-black/70 text-[12px] opacity-0 group-hover/bar:opacity-100 transition-opacity pointer-events-none transform -rotate-z-[-45deg] -rotate-x-[-60deg]">
                    <div className="font-bold">{site.site}</div>
                    <div>Score: {site.score}</div>
                    <div className="text-on-surface-variant dark:text-slate-400">{site.count} reports</div>
                  </div>
                </div>
              );
            })}
            
            {data.length === 0 && (
              <div className="absolute inset-0 flex items-center justify-center transform -rotate-z-[-45deg] -rotate-x-[60deg] text-on-surface-variant dark:text-slate-400">
                No site data available
              </div>
            )}
            
          </div>
        </div>
      </div>
    </div>
  );
}
