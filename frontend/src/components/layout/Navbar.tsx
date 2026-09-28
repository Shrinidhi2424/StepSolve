"use client";

import React from "react";
import Link from "next/link";
import { Calculator, BookOpen, Layers } from "lucide-react";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 shadow-md shadow-indigo-500/25 transition group-hover:scale-105">
            <Calculator className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                StepSolve
              </span>
              <div className="flex items-center gap-1 ml-1" title="Modules 1 to 5 Active">
                <span className="h-1.5 w-1.5 rounded-full bg-[#6d6af8]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#2dd4bf]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#fb923c]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#f472b6]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#34d399]" />
              </div>
            </div>
            <span className="rounded-md bg-indigo-500/10 px-1.5 py-0.5 text-[9px] font-semibold tracking-wider text-indigo-400 border border-indigo-500/20">
              NUMERICAL METHODS
            </span>
          </div>
        </Link>

        <nav className="flex items-center gap-2 sm:gap-4">
          <Link
            href="/"
            className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-slate-300 transition hover:bg-white/5 hover:text-white"
          >
            <BookOpen className="h-4 w-4 text-slate-400" />
            <span>Modules</span>
          </Link>

          <Link
            href="/calculator"
            className="flex items-center gap-1.5 rounded-lg bg-indigo-600/20 px-3.5 py-2 text-sm font-semibold text-indigo-300 border border-indigo-500/30 transition hover:bg-indigo-600/30 hover:text-white"
          >
            <Layers className="h-4 w-4 text-indigo-400" />
            <span>Calculator (15 Topics)</span>
          </Link>
        </nav>
      </div>
    </header>
  );
}
