"use client";

import React from "react";
import { AlertTriangle } from "lucide-react";

interface WarningsBannerProps {
  warnings: string[];
}

export function WarningsBanner({ warnings }: WarningsBannerProps) {
  if (!warnings || warnings.length === 0) return null;

  return (
    <div className="flex items-start gap-3 rounded-xl border border-amber-500/30 bg-amber-950/30 p-4 text-amber-200 shadow-md">
      <AlertTriangle className="h-5 w-5 shrink-0 text-amber-400 mt-0.5" />
      <div className="flex-1 space-y-1">
        <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400">
          Convergence / Precision Notes
        </h4>
        <ul className="list-inside list-disc text-xs space-y-0.5 text-amber-200/90">
          {warnings.map((w, idx) => (
            <li key={idx}>{w}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
