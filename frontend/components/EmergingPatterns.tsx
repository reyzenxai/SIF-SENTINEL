"use client";
import React from "react";
import Link from "next/link";
import { trendLabel } from "@/lib/utils";

interface RadarPattern {
  id: string;
  title: string;
  trend: string;
  trend_pct: number;
  sif_score: number;
  report_count: number;
}

export function EmergingPatterns({ patterns }: { patterns: RadarPattern[] }) {
  return (
    <div className="w-80 bg-surface-container/70 backdrop-blur-xl rounded-xl p-6 flex flex-col relative shadow-md h-full">
      <div className="absolute inset-0 bg-gradient-to-br from-white/30 to-transparent pointer-events-none rounded-xl"></div>
      <div className="absolute -top-[1px] -left-[1px] w-full h-full border-t border-l border-white/50 pointer-events-none rounded-xl"></div>
      
      <h2 className="text-[18px] font-semibold text-on-surface mb-6 relative z-10 flex items-center justify-between">
        Emerging Patterns
        <span className="material-symbols-outlined text-on-surface-variant text-[20px]">sort</span>
      </h2>
      
      <div className="flex-1 overflow-y-auto pr-2 relative z-10 space-y-4" style={{ scrollbarWidth: 'thin' }}>
        {patterns.map((p) => {
          const trend = trendLabel(p.trend);
          let colorBorder = "border-primary";
          let colorText = "text-primary";
          let colorBg = "bg-primary";
          
          if (p.sif_score >= 80) {
            colorBorder = "border-error"; colorText = "text-error"; colorBg = "bg-error";
          } else if (p.sif_score >= 60) {
            colorBorder = "border-tertiary"; colorText = "text-tertiary"; colorBg = "bg-tertiary";
          } else if (p.sif_score >= 35) {
            colorBorder = "border-secondary"; colorText = "text-secondary"; colorBg = "bg-secondary";
          }

          return (
            <Link href={`/patterns/${p.id}`} key={p.id}>
              <div className={`bg-surface rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group cursor-pointer border-l-4 ${colorBorder} mb-4 block`}>
                <div className="flex justify-between items-start mb-2">
                  <span className={`text-[12px] tracking-wider font-bold uppercase truncate pr-2 ${colorText}`}>
                    {p.title.split(' ').slice(0, 2).join(' ')}
                  </span>
                  <span className={`text-[13px] font-bold flex items-center ${colorText}`}>
                    <span className="material-symbols-outlined text-[14px] mr-1">
                      {trend.icon === "↑" ? "arrow_upward" : trend.icon === "↓" ? "arrow_downward" : "horizontal_rule"}
                    </span>
                    {Math.abs(p.trend_pct)}
                  </span>
                </div>
                <p className="text-[14px] text-on-surface font-semibold mb-1 leading-tight group-hover:text-primary transition-colors line-clamp-2">
                  {p.title}
                </p>
                <p className="text-[11px] text-on-surface-variant font-medium">
                  {p.report_count} related reports
                </p>
                <div className="mt-3 w-full bg-surface-container-high h-1 rounded-full overflow-hidden">
                  <div className={`${colorBg} h-full rounded-full`} style={{ width: `${Math.min(100, p.sif_score)}%` }}></div>
                </div>
              </div>
            </Link>
          );
        })}
        {patterns.length === 0 && (
          <p className="text-sm text-on-surface-variant text-center py-4">No patterns found</p>
        )}
      </div>
      
      <Link href="/patterns" className="block text-center mt-4 w-full py-2 bg-surface-container-low text-primary text-[12px] font-bold tracking-wider rounded-lg hover:bg-surface-variant transition-colors border border-outline-variant/30 relative z-10">
        VIEW ALL PATTERNS
      </Link>
    </div>
  );
}
