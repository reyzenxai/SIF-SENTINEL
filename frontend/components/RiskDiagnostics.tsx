"use client";
import React from "react";

export function RiskDiagnostics({ kpis }: { kpis: any }) {
  const severity = kpis ? kpis.avg_sif_score / 10 : 6.1;
  const controlFailure = kpis ? Math.min(10, kpis.control_failures_detected / (kpis.total_reports || 1) * 20) : 8.4;
  const exposure = kpis ? Math.min(10, kpis.high_risk_sites * 2) : 7.2;

  return (
    <div className="bg-surface-container/70 dark:bg-slate-800/80 backdrop-blur-xl rounded-xl p-6 relative shadow-md dark:shadow-black/50 mb-8 transition-colors">
      <div className="absolute inset-0 bg-gradient-to-br from-white/30 to-transparent dark:from-white/5 pointer-events-none rounded-xl"></div>
      <div className="absolute -top-[1px] -left-[1px] w-full h-full border-t border-l border-white/50 dark:border-white/10 pointer-events-none rounded-xl"></div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative z-10">
        <div className="col-span-1 flex flex-col justify-center">
          <h2 className="text-[24px] font-semibold text-on-surface dark:text-slate-100 mb-2">Risk Engine Diagnostics</h2>
          <p className="text-[14px] text-on-surface-variant dark:text-slate-400 mb-6">Aggregate analysis of underlying SIF drivers across all active facilities. Control failure and Exposure rates require immediate intervention.</p>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-error"></div>
                <span className="text-[14px] text-on-surface dark:text-slate-200">Control Failure</span>
              </div>
              <span className="text-[13px] text-on-surface dark:text-slate-100 font-bold">{controlFailure.toFixed(1)} / 10</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-tertiary"></div>
                <span className="text-[14px] text-on-surface dark:text-slate-200">Exposure</span>
              </div>
              <span className="text-[13px] text-on-surface dark:text-slate-100 font-bold">{exposure.toFixed(1)} / 10</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-primary"></div>
                <span className="text-[14px] text-on-surface dark:text-slate-200">Severity</span>
              </div>
              <span className="text-[13px] text-on-surface dark:text-slate-100 font-bold">{severity.toFixed(1)} / 10</span>
            </div>
          </div>
        </div>
        
        <div className="col-span-1 md:col-span-2 flex items-center justify-center h-64 relative">
          <svg className="w-full h-full max-w-sm drop-shadow-xl dark:drop-shadow-[0_20px_13px_rgba(0,0,0,0.8)] overflow-visible" viewBox="0 0 400 400">
            {/* Spider Web Background */}
            <g className="text-outline-variant/30 dark:text-slate-600/50" fill="none" stroke="currentColor" strokeWidth="1">
              <polygon points="200,50 342,154 288,321 112,321 58,154"></polygon>
              <polygon points="200,100 295,169 259,280 141,280 105,169"></polygon>
              <polygon points="200,150 247,184 229,240 171,240 153,184"></polygon>
              <line x1="200" x2="200" y1="200" y2="50"></line>
              <line x1="200" x2="342" y1="200" y2="154"></line>
              <line x1="200" x2="288" y1="200" y2="321"></line>
              <line x1="200" x2="112" y1="200" y2="321"></line>
              <line x1="200" x2="58" y1="200" y2="154"></line>
            </g>
            
            {/* Data Polygon */}
            <polygon 
              className="text-primary/20 dark:text-primary-fixed-dim/20" 
              fill="currentColor" 
              points="200,110 320,165 240,290 130,260 110,140" 
              stroke="var(--color-primary)" 
              strokeWidth="3"
            ></polygon>
            
            {/* Data Points */}
            <circle className="text-primary dark:text-primary-fixed-dim" cx="200" cy="110" fill="currentColor" r="5"></circle>
            <circle className="text-primary dark:text-primary-fixed-dim" cx="320" cy="165" fill="currentColor" r="5"></circle>
            <circle className="text-error" cx="240" cy="290" fill="currentColor" r="5"></circle>
            <circle className="text-tertiary" cx="130" cy="260" fill="currentColor" r="5"></circle>
            <circle className="text-primary dark:text-primary-fixed-dim" cx="110" cy="140" fill="currentColor" r="5"></circle>
            
            {/* Labels */}
            <text className="text-[12px] tracking-wider fill-on-surface-variant dark:fill-slate-400 font-bold" textAnchor="middle" x="200" y="30">SEVERITY</text>
            <text className="text-[12px] tracking-wider fill-on-surface-variant dark:fill-slate-400 font-bold" textAnchor="start" x="360" y="160">RECURRENCE</text>
            <text className="text-[12px] tracking-wider fill-error font-bold" textAnchor="middle" x="300" y="345">CONTROL FAILURE</text>
            <text className="text-[12px] tracking-wider fill-on-surface-variant dark:fill-slate-400 font-bold" textAnchor="middle" x="100" y="345">CONSEQUENCE</text>
            <text className="text-[12px] tracking-wider fill-tertiary font-bold" textAnchor="end" x="40" y="160">EXPOSURE</text>
          </svg>
        </div>
      </div>
    </div>
  );
}
