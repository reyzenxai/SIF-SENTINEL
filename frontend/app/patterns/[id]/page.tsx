"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Navbar } from "@/components/navbar";
import { Card, RiskBadge, SectionHeading } from "@/components/ui";
import { api } from "@/lib/api";
import { riskColor, trendLabel, formatDate } from "@/lib/utils";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { ArrowLeft, MapPin, Building2, Users, Quote, Loader2, ShieldAlert } from "lucide-react";

interface PatternDetail {
  pattern: {
    id: string; title: string; summary: string; report_count: number; locations: string[];
    contractors: string[]; departments: string[]; trend: string; trend_pct: number;
    sif_score: number; sif_risk_level: string; confidence: number; common_hazard: string;
    common_control_failure: string | null; potential_consequence: string | null;
    first_seen: string; last_seen: string;
  };
  trend_chart_data: { month: string; count: number }[];
  related_reports: {
    id: string; title: string; description: string; report_date: string; location: string;
    contractor: string; sif_score: number; risk_level: string; similarity: number;
  }[];
  recommendations: { id: string; priority: string; action: string; rationale: string; evidence_count: number; status: string }[];
  evidence: { report_id: string; snippets: string[] }[];
}

export default function PatternDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [data, setData] = useState<PatternDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.pattern(id).then(setData).finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex-1 flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center text-slate-400 gap-2">
          <Loader2 className="animate-spin" size={18} /> Loading pattern investigation…
        </div>
      </div>
    );
  }

  if (!data) return null;
  const { pattern, trend_chart_data, related_reports, recommendations, evidence } = data;
  const risk = riskColor(pattern.sif_risk_level);
  const trend = trendLabel(pattern.trend);

  return (
    <div className="flex-1 flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-[1400px] w-full mx-auto px-6 py-6">
        <Link href="/patterns" className="text-sm text-slate-500 hover:text-slate-800 flex items-center gap-1 mb-4">
          <ArrowLeft size={14} /> Back to patterns
        </Link>

        {/* Summary header */}
        <Card className={`p-5 border-l-4 mb-5`}>
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Emerging SIF Pattern</div>
              <h1 className="text-2xl font-semibold text-slate-900 mt-0.5">{pattern.title}</h1>
              <p className="text-sm text-slate-500 mt-1.5 max-w-3xl">{pattern.summary}</p>
            </div>
            <div className="text-right shrink-0">
              <div className={`text-3xl font-bold tabular-nums ${risk.text}`}>{pattern.sif_score}<span className="text-base text-slate-400">/100</span></div>
              <RiskBadge level={pattern.sif_risk_level} />
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-5 pt-4 border-t border-slate-100">
            <Stat icon={<ShieldAlert size={14} />} label="Related Reports" value={pattern.report_count} />
            <Stat icon={<MapPin size={14} />} label="Locations" value={pattern.locations.length} />
            <Stat icon={<Users size={14} />} label="Contractors" value={pattern.contractors.length} />
            <Stat icon={<Building2 size={14} />} label="Departments" value={pattern.departments.length} />
          </div>

          <div className="flex items-center gap-6 mt-4 text-sm">
            <span className={`font-semibold ${trend.color}`}>
              {trend.icon} {trend.word} {pattern.trend_pct !== 0 && `(${pattern.trend_pct > 0 ? "+" : ""}${pattern.trend_pct}%)`}
            </span>
            <span className="text-slate-500">Common control failure: <b className="text-slate-700">{pattern.common_control_failure || "—"}</b></span>
            <span className="text-slate-500">Period: {formatDate(pattern.first_seen)} – {formatDate(pattern.last_seen)}</span>
          </div>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Trend chart */}
          <Card className="lg:col-span-2 p-4">
            <SectionHeading title="Report Frequency Trend" />
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={trend_chart_data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#64748b" }} />
                <YAxis tick={{ fontSize: 11, fill: "#64748b" }} allowDecimals={false} />
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 6 }} />
                <Line type="monotone" dataKey="count" stroke="#dc2626" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          {/* Why flagged */}
          <Card className="p-4">
            <SectionHeading title="Why High Risk?" />
            <ul className="space-y-2">
              <li className="text-sm text-slate-700 flex gap-2"><span className="text-emerald-600">✓</span> {pattern.potential_consequence || "Potential severe consequence detected"}</li>
              <li className="text-sm text-slate-700 flex gap-2"><span className="text-emerald-600">✓</span> Recurring control failure: {pattern.common_control_failure || "multiple"}</li>
              <li className="text-sm text-slate-700 flex gap-2"><span className="text-emerald-600">✓</span> Similar events repeated {pattern.report_count} times</li>
              <li className="text-sm text-slate-700 flex gap-2"><span className="text-emerald-600">✓</span> Frequency trend: {trend.word.toLowerCase()}</li>
              <li className="text-sm text-slate-700 flex gap-2"><span className="text-emerald-600">✓</span> {pattern.locations.length} locations, {pattern.contractors.length} contractors affected</li>
            </ul>
            <p className="text-[11px] text-slate-400 mt-3 pt-3 border-t border-slate-100">
              Semantic clustering confidence: {(pattern.confidence * 100).toFixed(0)}%. Prototype methodology — configurable for OIL&apos;s approved safety framework.
            </p>
          </Card>
        </div>

        {/* Evidence */}
        <Card className="p-4 mt-5">
          <SectionHeading title="Evidence — Original Report Excerpts" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {evidence.map((e, i) => (
              <div key={i} className="bg-slate-50 border border-slate-200 rounded p-3">
                {e.snippets.map((s, j) => (
                  <p key={j} className="text-sm text-slate-700 flex gap-2 items-start">
                    <Quote size={13} className="text-slate-400 shrink-0 mt-0.5" />
                    <span>&quot;{s}&quot;</span>
                  </p>
                ))}
                <Link href={`/reports/${e.report_id}`} className="text-xs text-amber-700 hover:underline mt-1.5 inline-block">
                  View full report & AI extraction →
                </Link>
              </div>
            ))}
          </div>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-5">
          {/* Recommended actions */}
          <Card className="p-4">
            <SectionHeading title="Recommended Preventive Action" />
            <div className="space-y-2.5">
              {recommendations.map((a) => {
                const c = riskColor(a.priority);
                return (
                  <div key={a.id} className={`border rounded p-3 ${c.border}`}>
                    <div className="flex items-center justify-between">
                      <span className={`text-[11px] font-bold px-1.5 py-0.5 rounded ${c.bg} ${c.text}`}>{a.priority}</span>
                      <span className="text-[11px] text-slate-400">{a.evidence_count} reports</span>
                    </div>
                    <p className="text-sm font-medium text-slate-800 mt-1.5">{a.action}</p>
                    <p className="text-xs text-slate-500 mt-1">{a.rationale}</p>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Related reports */}
          <Card className="p-4">
            <SectionHeading title={`Related Reports (${related_reports.length})`} />
            <div className="divide-y divide-slate-100 max-h-[420px] overflow-y-auto">
              {related_reports.map((r) => (
                <Link key={r.id} href={`/reports/${r.id}`} className="block py-2.5 hover:bg-slate-50 -mx-1 px-1 rounded">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm text-slate-700 line-clamp-1">{r.title}</p>
                    <RiskBadge level={r.risk_level} />
                  </div>
                  <div className="flex items-center gap-3 text-xs text-slate-400 mt-0.5">
                    <span>{r.location}</span>
                    <span>{r.contractor}</span>
                    <span>{formatDate(r.report_date)}</span>
                  </div>
                </Link>
              ))}
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
}

function Stat({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div>
      <div className="flex items-center gap-1.5 text-xs text-slate-400">{icon} {label}</div>
      <div className="text-lg font-semibold text-slate-800 tabular-nums mt-0.5">{value}</div>
    </div>
  );
}
