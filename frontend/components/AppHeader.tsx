"use client";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function AppHeader() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <header className="fixed top-0 left-72 right-0 h-16 bg-surface/70 dark:bg-slate-900/80 backdrop-blur-xl z-40 flex items-center px-container-margin justify-between shadow-[0_1px_8px_rgba(0,0,0,0.04)] dark:shadow-[0_1px_8px_rgba(0,0,0,0.5)] dark:border-b dark:border-slate-800">
      <div className="relative w-96">
        <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant dark:text-slate-400 text-[20px]">search</span>
        <input 
          className="w-full bg-surface-container/50 dark:bg-slate-800/80 border border-white/40 dark:border-slate-700 rounded-full py-2 pl-10 pr-4 text-[14px] text-on-surface dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all placeholder:dark:text-slate-400" 
          placeholder="Search telemetry..." 
          type="text"
        />
      </div>
      <div className="flex items-center gap-stack-md">
        {mounted && (
          <div className="flex items-center bg-surface-container/50 dark:bg-slate-800/80 border border-white/40 dark:border-slate-700 rounded-full p-1 gap-1 backdrop-blur-sm">
            <button 
              onClick={() => setTheme("light")}
              className={`w-8 h-8 flex items-center justify-center rounded-full transition-all duration-300 ${
                theme === "light" 
                  ? "bg-primary text-on-primary shadow-sm" 
                  : "text-on-surface-variant dark:text-slate-400 hover:bg-surface-container-high dark:hover:bg-slate-700"
              }`} 
              title="Light Mode"
            >
              <span className="material-symbols-outlined text-[18px]">light_mode</span>
            </button>
            <button 
              onClick={() => setTheme("dark")}
              className={`w-8 h-8 flex items-center justify-center rounded-full transition-all duration-300 ${
                theme === "dark" 
                  ? "bg-primary text-on-primary shadow-sm" 
                  : "text-on-surface-variant dark:text-slate-400 hover:bg-surface-container-high dark:hover:bg-slate-700"
              }`} 
              title="Dark Mode"
            >
              <span className="material-symbols-outlined text-[18px]">dark_mode</span>
            </button>
          </div>
        )}
        <button className="p-2 rounded-full hover:bg-surface-container-high dark:hover:bg-slate-800 transition-colors relative">
          <span className="material-symbols-outlined text-on-surface-variant dark:text-slate-300">notifications</span>
          <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full"></span>
        </button>
        <button className="p-2 rounded-full hover:bg-surface-container-high dark:hover:bg-slate-800 transition-colors">
          <span className="material-symbols-outlined text-on-surface-variant dark:text-slate-300">settings</span>
        </button>
      </div>
    </header>
  );
}
