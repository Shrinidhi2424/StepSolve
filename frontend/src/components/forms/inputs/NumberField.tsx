"use client";

import React from "react";

interface NumberFieldProps {
  name: string;
  label: string;
  value: number | string;
  onChange: (val: number) => void;
  step?: string | number;
}

export function NumberField({
  name,
  label,
  value,
  onChange,
  step = "any",
}: NumberFieldProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={name} className="text-xs font-semibold uppercase tracking-wider text-slate-400">
        {label}
      </label>
      <input
        type="number"
        id={name}
        name={name}
        step={step}
        value={value ?? ""}
        onChange={(e) => {
          const val = parseFloat(e.target.value);
          onChange(isNaN(val) ? 0 : val);
        }}
        className="w-full rounded-lg border border-white/10 bg-slate-900/90 px-3.5 py-2 text-sm font-medium text-slate-100 placeholder-slate-500 shadow-inner outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
      />
    </div>
  );
}
