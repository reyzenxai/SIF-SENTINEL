"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/navbar";
import { Card, SectionHeading } from "@/components/ui";
import { api } from "@/lib/api";
import { Loader2, Sparkles } from "lucide-react";

export default function AnalyzeReportPage() {
  const router = useRouter();
  const [description, setDescription] = useState("");
  const [reportType, setReportType] = useState("NEAR_MISS");
  const [location, setLocation] = useState("");
  const [contractor, setContractor] = useState("");
  const [department, setDepartment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze(e: React.FormEvent) {
    e.preventDefault();
    if (!description.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const result = await api.createReport({
        description, report_type: reportType, location, contractor, department,
      });
      router.push(`/reports/${result.id}`);
    } catch (err) {
      setError("Could not analyze this report. Is the backend running?");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-[720px] w-full mx-auto px-6 py-8">
        <h1 className="text-xl font-semibold text-slate-900 mb-1 flex items-center gap-2">
          <Sparkles size={18} className="text-amber-500" /> Report Analyzer
        </h1>
        <p className="text-sm text-slate-500 mb-6">
          Paste a safety report to see structured AI extraction, SIF risk scoring, and explainability — evidence → interpretation → risk → action.
        </p>

        <Card className="p-5">
          <form onSubmit={handleAnalyze} className="space-y-4">
            <div>
              <label className="text-xs font-medium text-slate-500 uppercase">Report Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                placeholder='e.g. "During maintenance, technician entered the pump area before electrical isolation was verified."'
                className="w-full mt-1 text-sm border border-slate-300 rounded px-3 py-2 outline-none focus:border-slate-500"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-slate-500 uppercase">Report Type</label>
                <select value={reportType} onChange={(e) => setReportType(e.target.value)} className="w-full mt-1 text-sm border border-slate-300 rounded px-3 py-2 bg-white">
                  <option value="NEAR_MISS">Near Miss</option>
                  <option value="UNSAFE_ACT">Unsafe Act</option>
                  <option value="UNSAFE_CONDITION">Unsafe Condition</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500 uppercase">Location</label>
                <input value={location} onChange={(e) => setLocation(e.target.value)} className="w-full mt-1 text-sm border border-slate-300 rounded px-3 py-2" placeholder="Site Alpha" />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500 uppercase">Department</label>
                <input value={department} onChange={(e) => setDepartment(e.target.value)} className="w-full mt-1 text-sm border border-slate-300 rounded px-3 py-2" placeholder="Maintenance" />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500 uppercase">Contractor</label>
                <input value={contractor} onChange={(e) => setContractor(e.target.value)} className="w-full mt-1 text-sm border border-slate-300 rounded px-3 py-2" placeholder="Contractor name" />
              </div>
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <button
              type="submit"
              disabled={submitting || !description.trim()}
              className="w-full bg-slate-900 text-white text-sm font-medium py-2.5 rounded hover:bg-slate-800 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {submitting ? <><Loader2 size={14} className="animate-spin" /> Analyzing…</> : "Analyze Report"}
            </button>
          </form>
        </Card>
      </main>
    </div>
  );
}
