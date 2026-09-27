"use client";

import React, { useState } from "react";
import { Step } from "@/lib/types";
import { ChevronDown, ChevronRight, ListOrdered } from "lucide-react";

interface StepListProps {
  steps: Step[];
}

export function StepList({ steps }: StepListProps) {
  const [expandedIndices, setExpandedIndices] = useState<Record<number, boolean>>({
    0: true, // First step expanded by default
  });

  if (!steps || steps.length === 0) return null;

  const toggleStep = (idx: number) => {
    setExpandedIndices((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  const expandAll = () => {
    const all: Record<number, boolean> = {};
    steps.forEach((_, idx) => (all[idx] = true));
    setExpandedIndices(all);
  };

  const collapseAll = () => {
    setExpandedIndices({});
  };

  const renderValue = (val: any) => {
    if (val === null || val === undefined) return null;

    // Check if 2D array (e.g. matrix state or difference table)
    if (Array.isArray(val) && val.length > 0 && Array.isArray(val[0])) {
      return (
        <div className="mt-2 overflow-x-auto rounded-lg border border-white/10 bg-slate-950 p-3">
          <table className="border-collapse font-mono text-xs">
            <tbody>
              {val.map((row: any[], rIdx: number) => (
                <tr key={rIdx} className="border-b border-white/5 last:border-none">
                  {row.map((cell: any, cIdx: number) => (
                    <td key={cIdx} className="px-3 py-1.5 text-center text-slate-300">
                      {cell === null ? "" : typeof cell === "number" ? cell.toFixed(4) : String(cell)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    if (Array.isArray(val)) {
      return (
        <div className="mt-2 font-mono text-xs text-indigo-300">
          [{val.map((v) => (typeof v === "number" ? v.toFixed(6) : String(v))).join(", ")}]
        </div>
      );
    }

    return (
      <div className="mt-2 font-mono text-xs text-indigo-300">
        Result: {typeof val === "number" ? val.toFixed(6) : String(val)}
      </div>
    );
  };

  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ListOrdered className="h-4 w-4 text-indigo-400" />
          <h4 className="text-sm font-bold tracking-tight text-white uppercase">
            Step-by-Step Derivation ({steps.length} Steps)
          </h4>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <button
            type="button"
            onClick={expandAll}
            className="rounded bg-white/5 px-2.5 py-1 text-slate-400 hover:bg-white/10 hover:text-white transition cursor-pointer"
          >
            Expand All
          </button>
          <button
            type="button"
            onClick={collapseAll}
            className="rounded bg-white/5 px-2.5 py-1 text-slate-400 hover:bg-white/10 hover:text-white transition cursor-pointer"
          >
            Collapse All
          </button>
        </div>
      </div>

      <div className="flex flex-col gap-2.5">
        {steps.map((step, idx) => {
          const isExpanded = !!expandedIndices[idx];
          return (
            <div
              key={idx}
              className="overflow-hidden rounded-xl border border-white/5 bg-slate-950/60 transition"
            >
              <button
                type="button"
                onClick={() => toggleStep(idx)}
                className="flex w-full items-center justify-between px-4 py-3 text-left transition hover:bg-white/[0.02] cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-indigo-500/20 text-xs font-bold text-indigo-400 border border-indigo-500/30">
                    {step.step_number || idx + 1}
                  </span>
                  <span className="text-sm font-semibold text-slate-200">
                    {step.title}
                  </span>
                </div>
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4 text-slate-400" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-slate-400" />
                )}
              </button>

              {isExpanded && (
                <div className="border-t border-white/5 px-4 py-3.5 space-y-3 bg-slate-900/30">
                  {step.description && (
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {step.description}
                    </p>
                  )}

                  {step.formula && (
                    <div className="flex flex-col gap-1 rounded-lg bg-slate-950/80 p-2.5 border border-white/5">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                        Formula Applied
                      </span>
                      <code className="font-mono text-xs text-indigo-300 overflow-x-auto whitespace-pre-wrap">
                        {step.formula}
                      </code>
                    </div>
                  )}

                  {step.substitution && (
                    <div className="flex flex-col gap-1 rounded-lg bg-slate-950/80 p-2.5 border border-white/5">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                        Numerical Substitution
                      </span>
                      <code className="font-mono text-xs text-emerald-300 overflow-x-auto whitespace-pre-wrap">
                        {step.substitution}
                      </code>
                    </div>
                  )}

                  {renderValue(step.value)}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
