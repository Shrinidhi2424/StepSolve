"use client";

import React from "react";
import { CheckCircle2, AlertCircle } from "lucide-react";

interface FunctionFieldProps {
  name: string;
  label: string;
  value: string;
  onChange: (val: string) => void;
  placeholder?: string;
  error?: string | null;
}

export function FunctionField({
  name,
  label,
  value,
  onChange,
  placeholder = "e.g. x**3 - x - 2 or cos(x)",
  error,
}: FunctionFieldProps) {
  const isValidSyntax =
    value.trim().length > 0 &&
    !value.includes("__") &&
    !/\b(import|exec|eval|os|sys)\b/i.test(value);

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between">
        <label htmlFor={name} className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {label}
        </label>
        {value.trim().length > 0 && (
          <span className="flex items-center gap-1 text-[11px] font-medium">
            {isValidSyntax ? (
              <span className="text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3" /> Valid expression
              </span>
            ) : (
              <span className="text-rose-400 flex items-center gap-1">
                <AlertCircle className="h-3 w-3" /> Disallowed pattern
              </span>
            )}
          </span>
        )}
      </div>

      <div className="relative">
        <input
          type="text"
          id={name}
          name={name}
          value={value ?? ""}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full font-mono rounded-lg border border-white/10 bg-slate-900/90 px-3.5 py-2 text-sm text-slate-100 placeholder-slate-600 shadow-inner outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      {error && <span className="text-xs text-rose-400">{error}</span>}

      <div className="flex flex-wrap items-center gap-1 text-[11px] text-slate-500">
        <span>Operators:</span>
        <code className="rounded bg-white/5 px-1 py-0.5 text-slate-400">**</code>
        <code className="rounded bg-white/5 px-1 py-0.5 text-slate-400">*</code>
        <code className="rounded bg-white/5 px-1 py-0.5 text-slate-400">/</code>
        <code className="rounded bg-white/5 px-1 py-0.5 text-slate-400">+</code>
        <code className="rounded bg-white/5 px-1 py-0.5 text-slate-400">-</code>
        <span className="ml-1">Functions:</span>
        <code className="rounded bg-white/5 px-1 py-0.5 text-slate-400">sin</code>
        <code className="rounded bg-white/5 px-1 py-0.5 text-slate-400">cos</code>
        <code className="rounded bg-white/5 px-1 py-0.5 text-slate-400">exp</code>
        <code className="rounded bg-white/5 px-1 py-0.5 text-slate-400">log</code>
      </div>
    </div>
  );
}
