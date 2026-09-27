"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowRight, Calculator, Layers, AlertCircle, Loader2 } from "lucide-react";
import { getTopics } from "@/lib/api";
import { Topic } from "@/lib/types";
import { ModuleTabs } from "@/components/layout/ModuleTabs";

export default function CalculatorPickerPage() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedModule, setSelectedModule] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setIsLoading(true);
        const data = await getTopics();
        setTopics(data);
        setError(null);
      } catch (err: any) {
        setError(
          err.message || "Failed to load topics from backend. Ensure backend is running."
        );
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  const filteredTopics =
    selectedModule === null
      ? topics
      : topics.filter((t) => t.module === selectedModule);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-2">
          <Layers className="h-4 w-4" />
          <span>Interactive Calculator Suite</span>
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
          Choose a Numerical Topic
        </h1>
        <p className="mt-2 text-sm text-slate-400">
          Select any of the 15 methods to enter parameters, calculate roots/integrals/solutions, and view textbook-style derivations.
        </p>
      </div>

      {/* Module filter tabs */}
      <div className="mb-6">
        <ModuleTabs
          activeModule={selectedModule}
          onSelectModule={(mod) => setSelectedModule(mod)}
        />
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center py-20 text-slate-400">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-500 mb-3" />
          <p className="text-sm">Fetching syllabus topics from backend...</p>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-5 text-rose-300 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 shrink-0 text-rose-400" />
          <div>
            <h4 className="font-semibold text-sm">Connection Warning</h4>
            <p className="text-xs text-rose-300/80 mt-1">{error}</p>
            <p className="text-xs text-rose-300/60 mt-2">
              Start the FastAPI backend with: <code className="bg-rose-950 px-1 py-0.5 rounded font-mono">uvicorn app.main:app --reload</code>
            </p>
          </div>
        </div>
      )}

      {/* Topics Grid */}
      {!isLoading && !error && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredTopics.map((topic) => (
            <Link
              key={topic.id}
              href={`/calculator/${topic.id}`}
              className="group flex flex-col justify-between rounded-xl border border-white/10 bg-slate-900/60 p-5 shadow-sm transition hover:border-indigo-500/40 hover:bg-slate-900/90 hover:shadow-indigo-500/10 cursor-pointer"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="rounded-md bg-white/5 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-slate-400 border border-white/5">
                    Module {topic.module}
                  </span>
                  <span className="text-[11px] font-mono text-slate-500">
                    {topic.input_schema?.length || 0} inputs
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-100 group-hover:text-indigo-300 transition">
                  {topic.title}
                </h3>
                <p className="mt-1.5 text-xs text-slate-400 leading-relaxed line-clamp-2">
                  {topic.short_description}
                </p>
              </div>

              <div className="mt-5 flex items-center justify-between border-t border-white/5 pt-3">
                <span className="text-xs font-semibold text-indigo-400 group-hover:text-indigo-300">
                  Open Calculator
                </span>
                <ArrowRight className="h-4 w-4 text-indigo-400 transition group-hover:translate-x-1" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
