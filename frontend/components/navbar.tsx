"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, LayoutDashboard, FileSearch, Radar, Search } from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Command Center", icon: LayoutDashboard },
  { href: "/patterns", label: "SIF Patterns", icon: Radar },
  { href: "/reports", label: "Reports", icon: FileSearch },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <header className="border-b border-slate-800 bg-slate-900 text-slate-100">
      <div className="max-w-[1400px] mx-auto px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center gap-2 font-semibold tracking-tight">
            <Shield size={18} className="text-amber-400" strokeWidth={2.2} />
            <span>SIF Sentinel</span>
          </Link>
          <nav className="flex items-center gap-1">
            {NAV_ITEMS.map((item) => {
              const active = pathname?.startsWith(item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                    active ? "bg-slate-800 text-white" : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/60"
                  }`}
                >
                  <Icon size={15} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/reports/analyze"
            className="flex items-center gap-1.5 text-sm font-medium bg-amber-500 hover:bg-amber-400 text-slate-900 px-3 py-1.5 rounded transition-colors"
          >
            <Search size={14} />
            Analyze Report
          </Link>
        </div>
      </div>
    </header>
  );
}
