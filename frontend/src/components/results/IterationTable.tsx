"use client";

import React from "react";
import { Table } from "lucide-react";

interface IterationTableProps {
  iterations: Record<string, any>[] | null | undefined;
}

export function IterationTable({ iterations }: IterationTableProps) {
  if (!iterations || iterations.length === 0) return null;

  const headers = Object.keys(iterations[0]);

  const formatHeader = (key: string) => {
    return key
      .replace(/_/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase());
  };

  const formatCellValue = (val: any) => {
    if (val === null || val === undefined) return "-";
    if (typeof val === "number") {
      if (Number.isInteger(val)) return val.toString();
      // Use scientific notation for very small numbers, otherwise 6 decimal places
      if (Math.abs(val) < 1e-4 && val !== 0) {
        return val.toExponential(4);
      }
      return val.toFixed(6);
    }
    return String(val);
  };

  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Table className="h-4 w-4 text-indigo-400" />
          <h4 className="text-sm font-bold tracking-tight text-white uppercase">
            Iteration History Table
          </h4>
        </div>
        <span className="rounded-md bg-white/5 px-2 py-0.5 text-xs font-mono text-slate-400 border border-white/5">
          {iterations.length} {iterations.length === 1 ? "step" : "iterations"}
        </span>
      </div>

      <div className="overflow-x-auto rounded-xl border border-white/10 bg-slate-950/80">
        <table className="w-full text-left text-xs font-mono">
          <thead className="border-b border-white/10 bg-slate-900 text-slate-400 font-sans">
            <tr>
              {headers.map((h) => (
                <th key={h} className="px-3.5 py-2.5 font-semibold tracking-wider">
                  {formatHeader(h)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {iterations.map((row, idx) => {
              const isLast = idx === iterations.length - 1;
              return (
                <tr
                  key={idx}
                  className={`transition hover:bg-white/[0.03] ${
                    isLast
                      ? "bg-indigo-950/30 font-semibold text-indigo-200"
                      : "text-slate-300"
                  }`}
                >
                  {headers.map((h) => (
                    <td key={h} className="px-3.5 py-2 whitespace-nowrap">
                      {formatCellValue(row[h])}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
