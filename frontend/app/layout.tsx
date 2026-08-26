import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SIF Sentinel | AI-Powered Safety Early Warning & Prevention Intelligence",
  description: "Prototype demonstration uses synthetic/anonymized safety-report data.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body
        className="min-h-full flex flex-col bg-slate-50 text-slate-900"
        style={{ fontFamily: "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" }}
      >
        {children}
      </body>
    </html>
  );
}
