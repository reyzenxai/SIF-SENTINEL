export function riskColor(level?: string | null) {
  switch (level) {
    case "CRITICAL":
      return { bg: "bg-red-50", text: "text-red-700", border: "border-red-200", dot: "bg-red-600", ring: "ring-red-600" };
    case "HIGH":
      return { bg: "bg-orange-50", text: "text-orange-700", border: "border-orange-200", dot: "bg-orange-500", ring: "ring-orange-500" };
    case "MODERATE":
      return { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200", dot: "bg-amber-500", ring: "ring-amber-500" };
    default:
      return { bg: "bg-slate-100", text: "text-slate-600", border: "border-slate-200", dot: "bg-slate-400", ring: "ring-slate-400" };
  }
}

export function trendLabel(trend?: string | null) {
  switch (trend) {
    case "increasing":
      return { icon: "↑", color: "text-red-600", word: "Increasing" };
    case "decreasing":
      return { icon: "↓", color: "text-emerald-600", word: "Decreasing" };
    case "new":
      return { icon: "●", color: "text-blue-600", word: "Newly Emerging" };
    default:
      return { icon: "→", color: "text-slate-500", word: "Stable" };
  }
}

export function formatDate(iso?: string | null) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}
