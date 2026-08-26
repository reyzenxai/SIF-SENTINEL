"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Navbar } from "@/components/navbar";
import { Card, RiskBadge, SectionHeading } from "@/components/ui";
import { api } from "@/lib/api";
import { riskColor, formatDate } from "@/lib/utils";
import { ArrowLeft, Loader2, Sparkles, Wrench } from "lucide-react";

interface ReportDetail {
  report: {
    id: string; description: string; report_type: string; location: string; site: string;
    department: string; contractor: string; reporter_role: string; report_date: string;
    severity: string; is_synthetic: boolean;
  };
  extraction: {
    activity: string | null; hazard: string | null; hazard_category: string | null;
    unsafe_act: string | null; unsafe_condition: string | null; control_failure: string | null;
    equipment: string | null; potential_consequence: string | null; exposure_context: string | null;
    sif_relevance_score: number; extraction_confidence: number; extraction_method: string;
    evidence_spans: string[];
  } | null;
  assessment: {
    severity_score: number; exposure_score: number; control_failure_score: number;
    recurrence_score: number; consequence_score: number; overall_sif_score: number;
    risk_level: string; reasoning: string[];
  } | null;
  patterns: { id: string; title: string; sif_score: number; trend: string }[];
  recommendations: { id: string; priority: string; action: string; rationale: string; pattern_title: string }[];
}

const SCORE_MAX: Record<string, number> = {
  severity_score: 25, control_failure_score: 25, exposure_score: 20, recurrence_score: 20, consequence_score: 10,
};
const SCORE_LABELS: Record<string, string> = {
  severity_score: "Severity", control_failure_score: "Control Failure", exposure_score: "Exposure",
  recurrence_score: "Recurrence", consequence_score: "Consequence",
};

export default function ReportDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [data, setData] = useState<ReportDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.report(id).then(setData).finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex-1 flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center text-slate-400 gap-2">
          <Loader2 className="animate-spin" size={18} /> Loading report analysis…
        </div>
      </div>
    );
  }
  if (!data) return null;
  const { report, extraction, assessment, patterns, recommendations } = data;
  const risk = riskColor(assessment?.risk_level);

  return (
    <div className="flex-1 flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-[1200px] w-full mx-auto px-6 py-6">
        <Link href="/reports" className="text-sm text-slate-500 hover:text-slate-800 flex items-center gap-1 mb-4">
          <ArrowLeft size={14} /> Back to reports
        </Link>

        {/* Original report */}
        <Card className="p-5 mb-5">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Original Report</div>
          <p className="text-base text-slate-800 leading-relaxed border-l-2 border-slate-300 pl-3 italic">
            &quot;{report.description}&quot;
          </p>
          <div className="flex flex-wrap gap-x-5 gap-y-1 mt-4 text-xs text-slate-500">
            <span><b className="text-slate-700">Type:</b> {report.report_type.replace("_", " ")}</span>
            <span><b className="text-slate-700">Location:</b> {report.location}</span>
            <span><b className="text-slate-700">Department:</b> {report.department}</span>
            <span><b className="text-slate-700">Contractor:</b> {report.contractor}</span>
            <span><b className="text-slate-700">Reporter:</b> {report.reporter_role}</span>
            <span><b className="text-slate-700">Date:</b> {formatDate(report.report_date)}</span>
          </div>
          {report.is_synthetic && (
            <p className="text-[11px] text-amber-700 bg-amber-50 border border-amber-200 rounded px-2 py-1 mt-3 inline-block">
              Synthetic/demonstration report
            </p>
          )}
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* AI Analysis / Extraction */}
          <Card className="p-5">
            <SectionHeading title="AI Analysis" action={
              <span className="text-[11px] text-slate-400 flex items-center gap-1">
                <Sparkles size={12} />
                {extraction?.extraction_method === "llm" ? "LLM extraction" : "Rule-based extraction"}
              </span>
            } />
            {extraction ? (
              <div className="space-y-2.5 text-sm">
                <Field label="Activity" value={extraction.activity} />
                <Field label="Hazard" value={extraction.hazard} />
                <Field label="Hazard Category" value={extraction.hazard_category} />
                <Field label="Control Failure" value={extraction.control_failure} />
                <Field label="Equipment" value={extraction.equipment} />
                <Field label="Potential Consequence" value={extraction.potential_consequence} />
                <div className="flex items-center justify-between pt-2 mt-2 border-t border-slate-100">
                  <span className="text-xs text-slate-400">Extraction confidence</span>
                  <span className="text-xs font-semibold text-slate-700">{Math.round(extraction.extraction_confidence * 100)}%</span>
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-400">Extraction unavailable.</p>
            )}
          </Card>

          {/* SIF Score breakdown */}
          <Card className="p-5">
            <SectionHeading title="SIF Risk Score" action={<RiskBadge level={assessment?.risk_level} />} />
            {assessment ? (
              <>
                <div className={`text-4xl font-bold tabular-nums ${risk.text} mb-3`}>
                  {assessment.overall_sif_score}<span className="text-base text-slate-400">/100</span>
                </div>
                <div className="space-y-2">
                  {Object.entries(SCORE_LABELS).map(([key, label]) => {
                    const val = (assessment as unknown as Record<string, number>)[key];
                    const max = SCORE_MAX[key];
                    return (
                      <div key={key}>
                        <div className="flex justify-between text-xs text-slate-500 mb-0.5">
                          <span>{label}</span>
                          <span className="tabular-nums">{val}/{max}</span>
                        </div>
                        <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                          <div className="h-full bg-slate-700 rounded-full" style={{ width: `${(val / max) * 100}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </>
            ) : (
              <p className="text-sm text-slate-400">Assessment unavailable.</p>
            )}
          </Card>
        </div>

        {/* Why flagged */}
        {assessment && (
          <Card className="p-5 mt-5">
            <SectionHeading title="Why Flagged?" />
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {assessment.reasoning.map((r, i) => (
                <li key={i} className="text-sm text-slate-700 flex gap-2"><span className="text-emerald-600">✓</span> {r}</li>
              ))}
            </ul>
            {extraction && extraction.evidence_spans.length > 0 && (
              <div className="mt-4 pt-4 border-t border-slate-100">
                <div className="text-xs font-semibold text-slate-400 uppercase mb-2">Evidence — Highlighted Spans</div>
                {extraction.evidence_spans.map((s, i) => (
                  <p key={i} className="text-sm bg-amber-50 border border-amber-200 rounded px-2.5 py-1.5 text-slate-700 mb-1.5">
                    &quot;{s}&quot;
                  </p>
                ))}
              </div>
            )}
          </Card>
        )}

        {/* Linked patterns & recommendations */}
        {(patterns.length > 0 || recommendations.length > 0) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-5">
            {patterns.length > 0 && (
              <Card className="p-5">
                <SectionHeading title="Linked SIF Patterns" />
                {patterns.map((p) => (
                  <Link key={p.id} href={`/patterns/${p.id}`} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0 hover:text-amber-700">
                    <span className="text-sm">{p.title}</span>
                    <span className="text-xs text-slate-400">SIF {p.sif_score}</span>
                  </Link>
                ))}
              </Card>
            )}
            {recommendations.length > 0 && (
              <Card className="p-5">
                <SectionHeading title="What Should We Investigate?" action={<Wrench size={14} className="text-slate-400" />} />
                <div className="space-y-2">
                  {recommendations.slice(0, 4).map((a) => (
                    <p key={a.id} className="text-sm text-slate-700">• {a.action}</p>
                  ))}
                </div>
                <p className="text-[11px] text-slate-400 mt-3 pt-2 border-t border-slate-100">Prototype recommendation — not official OIL policy.</p>
              </Card>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="flex justify-between gap-4">
      <span className="text-slate-500">{label}</span>
      <span className="font-medium text-slate-800 text-right">{value || "—"}</span>
    </div>
  );
}
