"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/navbar";
import { Card } from "@/components/ui";
import { uploadCsv } from "@/lib/api";
import { Upload, Loader2, CheckCircle2 } from "lucide-react";

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{ reports_ingested: number; patterns_discovered: number } | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleUpload() {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const res = await uploadCsv(file);
      setResult(res);
    } catch {
      setError("Upload failed. Ensure the CSV has a 'description' column and try again.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-[600px] w-full mx-auto px-6 py-8">
        <h1 className="text-xl font-semibold text-slate-900 mb-1 flex items-center gap-2">
          <Upload size={18} className="text-amber-500" /> Bulk Report Upload
        </h1>
        <p className="text-sm text-slate-500 mb-6">
          Upload a CSV of safety reports for AI extraction, SIF scoring, and semantic pattern discovery.
        </p>

        <Card className="p-6">
          {!result ? (
            <>
              <label className="block border-2 border-dashed border-slate-300 rounded-lg p-8 text-center cursor-pointer hover:border-slate-400">
                <input type="file" accept=".csv" className="hidden" onChange={(e) => setFile(e.target.files?.[0] || null)} />
                <Upload size={24} className="mx-auto text-slate-400 mb-2" />
                <p className="text-sm text-slate-600">{file ? file.name : "Click to select a CSV file"}</p>
                <p className="text-xs text-slate-400 mt-1">Columns: description, report_type, location, department, contractor, report_date</p>
              </label>
              {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
              <button
                onClick={handleUpload}
                disabled={!file || uploading}
                className="w-full mt-4 bg-slate-900 text-white text-sm font-medium py-2.5 rounded hover:bg-slate-800 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {uploading ? <><Loader2 size={14} className="animate-spin" /> Processing & clustering reports…</> : "Upload & Analyze"}
              </button>
            </>
          ) : (
            <div className="text-center py-4">
              <CheckCircle2 size={32} className="mx-auto text-emerald-500 mb-3" />
              <p className="text-sm text-slate-700">
                <b>{result.reports_ingested}</b> reports processed, <b>{result.patterns_discovered}</b> patterns discovered.
              </p>
              <button
                onClick={() => router.push("/dashboard")}
                className="mt-4 bg-slate-900 text-white text-sm font-medium px-4 py-2 rounded hover:bg-slate-800"
              >
                View Safety Command Center
              </button>
            </div>
          )}
        </Card>
      </main>
    </div>
  );
}
