"use client";

import React from "react";
import { CheckCircle, Award } from "lucide-react";

interface ResultSummaryProps {
  summary: string;
  result: Record<string, any>;
  hasWarnings?: boolean;
}

export function ResultSummary({
  summary,
  result,
  hasWarnings = false,
}: ResultSummaryProps) {
  return (
    <div
      className={`relative overflow-hidden rounded-2xl border p-5 sm:p-6 transition-all shadow-xl ${
        hasWarnings
          ? "border-amber-500/30 bg-gradient-to-br from-amber-950/20 via-slate-900/90 to-slate-950 shadow-amber-500/5"
          : "border-emerald-500/30 bg-gradient-to-br from-emerald-950/20 via-slate-900/90 to-slate-950 shadow-emerald-500/5"
      }`}
    >
      <div className="flex items-start gap-4">
        <div
          className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border ${
            hasWarnings
              ? "border-amber-500/30 bg-amber-500/10 text-amber-400"
              : "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
          }`}
        >
          {hasWarnings ? (
            <Award className="h-6 w-6" />
          ) : (
            <CheckCircle className="h-6 w-6" />
          )}
        </div>

        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-2">
            <span
              className={`rounded-md px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                hasWarnings
                  ? "bg-amber-500/20 text-amber-300"
                  : "bg-emerald-500/20 text-emerald-300"
              }`}
            >
              Final Answer
            </span>
          </div>

          <h3 className="text-lg sm:text-xl font-bold tracking-tight text-white font-mono">
            {summary}
          </h3>

          {result && Object.keys(result).length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2 pt-2 border-t border-white/5 font-mono text-xs">
              {Object.entries(result).map(([k, v]) => {
                if (typeof v === "object" && v !== null) return null;
                return (
                  <div
                    key={k}
                    className="flex items-center gap-1.5 rounded-md bg-white/5 px-2.5 py-1 text-slate-300 border border-white/5"
                  >
                    <span className="text-slate-500">{k}:</span>
                    <span className="font-semibold text-slate-100">
                      {typeof v === "number" ? (Number.isInteger(v) ? v : v.toFixed(6)) : String(v)}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
