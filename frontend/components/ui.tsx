import Link from "next/link";
import { riskColor } from "@/lib/utils";

export function RiskBadge({ level }: { level?: string | null }) {
  const c = riskColor(level);
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-semibold border ${c.bg} ${c.text} ${c.border}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      {level || "UNKNOWN"}
    </span>
  );
}

export function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white border border-slate-200 rounded-lg ${className}`}>
      {children}
    </div>
  );
}

export function KpiCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <Card className="p-4">
      <div className="text-xs font-medium text-slate-500 uppercase tracking-wide">{label}</div>
      <div className="text-2xl font-semibold text-slate-900 mt-1.5 tabular-nums">{value}</div>
      {sub && <div className="text-xs text-slate-400 mt-1">{sub}</div>}
    </Card>
  );
}

export function SectionHeading({ title, action }: { title: string; action?: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between mb-3">
      <h2 className="text-sm font-semibold text-slate-800 uppercase tracking-wide">{title}</h2>
      {action}
    </div>
  );
}

export function PatternLink({ id, children, className = "" }: { id: string; children: React.ReactNode; className?: string }) {
  return (
    <Link href={`/patterns/${id}`} className={`block hover:bg-slate-50 transition-colors ${className}`}>
      {children}
    </Link>
  );
}
