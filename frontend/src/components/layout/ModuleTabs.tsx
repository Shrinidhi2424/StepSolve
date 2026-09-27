"use client";

import React from "react";

interface ModuleTabsProps {
  activeModule: number | null;
  onSelectModule: (moduleNumber: number | null) => void;
}

const MODULES = [
  { id: null, label: "All Modules (15)" },
  { id: 1, label: "Mod I: Equations & Systems" },
  { id: 2, label: "Mod II: Interpolation" },
  { id: 3, label: "Mod III: Calc & Quadrature" },
  { id: 4, label: "Mod IV: ODE Initial Value" },
  { id: 5, label: "Mod V: BVP & Inversion" },
];

export function ModuleTabs({ activeModule, onSelectModule }: ModuleTabsProps) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
      {MODULES.map((tab) => {
        const isActive = activeModule === tab.id;
        return (
          <button
            key={tab.label}
            onClick={() => onSelectModule(tab.id)}
            className={`whitespace-nowrap rounded-lg px-3.5 py-1.5 text-xs font-semibold transition cursor-pointer ${
              isActive
                ? "bg-indigo-600 text-white shadow-sm shadow-indigo-500/30"
                : "bg-slate-900 text-slate-400 border border-white/5 hover:bg-slate-800 hover:text-slate-200"
            }`}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
