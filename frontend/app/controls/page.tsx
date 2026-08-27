"use client";
import { useState } from "react";
import { AppSidebar } from "@/components/AppSidebar";
import { AppHeader } from "@/components/AppHeader";
import { Shield, AlertCircle, CheckCircle2, Sliders, ShieldAlert, ArrowRight } from "lucide-react";

export default function SafetyControlsPage() {
  const [controls, setControls] = useState([
    { id: 1, name: "Energy Isolation (LOTO)", standard: "IOGP LSR #1", verified: 94, degraded: 6, status: "Active & Monitored" },
    { id: 2, name: "Working at Height Fall Arrest", standard: "IOGP LSR #2", verified: 88, degraded: 12, status: "Review Required" },
    { id: 3, name: "Confined Space Gas Detection", standard: "IOGP LSR #3", verified: 98, degraded: 2, status: "Verified Healthy" },
    { id: 4, name: "Line of Fire Zone Protection", standard: "IOGP LSR #4", verified: 82, degraded: 18, status: "High Priority Action" },
    { id: 5, name: "Hot Work Spark Containment", standard: "IOGP LSR #5", verified: 96, degraded: 4, status: "Verified Healthy" },
    { id: 6, name: "Pressure Relief Valve Inspection", standard: "API 520/526", verified: 91, degraded: 9, status: "Active & Monitored" },
  ]);

  return (
    <div className="bg-background dark:bg-slate-900 font-body-md text-on-surface dark:text-slate-100 min-h-screen overflow-x-hidden">
      <AppSidebar />
      <div className="pl-72 flex flex-col min-h-screen">
        <AppHeader />
        <main className="relative pt-16 flex-1 p-container-margin">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-headline-md font-semibold text-on-surface dark:text-slate-100">Industrial Safety Controls & Critical Barrier Integrity</h1>
              <p className="text-body-md text-on-surface-variant dark:text-slate-400 mt-1">
                Real-time tracking of IOGP Life-Saving Rules barriers, mechanical interlocks, and procedural compliance.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {controls.map((ctrl) => {
              const isDegraded = ctrl.degraded >= 10;
              return (
                <div 
                  key={ctrl.id} 
                  className="bg-surface-container/70 dark:bg-slate-800/80 backdrop-blur-xl rounded-xl p-6 border border-white/40 dark:border-white/10 shadow-sm flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-primary/10 text-primary dark:text-primary-fixed-dim border border-primary/20">
                        {ctrl.standard}
                      </span>
                      <span className={`text-[11px] font-bold px-2 py-0.5 rounded border ${
                        isDegraded ? "bg-error/10 text-error border-error/30" : "bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/30"
                      }`}>
                        {ctrl.status}
                      </span>
                    </div>
                    <h3 className="text-title-lg font-bold text-on-surface dark:text-slate-100 mb-2">{ctrl.name}</h3>
                    <p className="text-body-sm text-on-surface-variant dark:text-slate-400 mb-4">
                      Physical and operational barrier verification across all active operational work permits.
                    </p>
                  </div>

                  <div>
                    <div className="flex items-center justify-between text-[12px] mb-1.5 font-semibold">
                      <span className="text-on-surface dark:text-slate-200">Barrier Health: {ctrl.verified}%</span>
                      <span className={isDegraded ? "text-error" : "text-on-surface-variant dark:text-slate-400"}>
                        {ctrl.degraded}% Precursor Risk
                      </span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-surface-container-high dark:bg-slate-700 overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${isDegraded ? "bg-amber-500" : "bg-primary"}`}
                        style={{ width: `${ctrl.verified}%` }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </main>
      </div>
    </div>
  );
}
