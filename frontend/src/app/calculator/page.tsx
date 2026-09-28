"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowRight, Calculator, Layers, AlertCircle, Loader2, Sparkles } from "lucide-react";
import { getTopics } from "@/lib/api";
import { Topic } from "@/lib/types";
import { ModuleTabs } from "@/components/layout/ModuleTabs";
import { getModuleTheme } from "@/lib/moduleTheme";

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
        <div className="flex items-center gap-3 mb-2">
          <div className="flex items-center gap-1.5 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
            <Layers className="h-4 w-4" />
            <span>Interactive Calculator Suite</span>
          </div>
          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-[11px] font-bold text-emerald-400 border border-emerald-500/20">
            <Sparkles className="h-3 w-3" />
            15 of 15 Active
          </span>
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
          Choose a Numerical Method
        </h1>
        <p className="mt-2 text-sm text-slate-400 max-w-2xl">
          Select any of the 15 methods to enter problem parameters, evaluate solutions, and view complete step-by-step textbook derivations.
        </p>
      </div>

      {/* Module filter tabs */}
      <div className="mb-8">
        <ModuleTabs
          activeModule={selectedModule}
          onSelectModule={(mod) => setSelectedModule(mod)}
        />
      </div>

      {/* Loading state with shimmer skeleton */}
      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div
              key={i}
              className="h-44 rounded-xl border border-white/5 bg-slate-900/40 p-5 skeleton-shimmer"
            />
          ))}
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
          {filteredTopics.map((topic) => {
            const theme = getModuleTheme(topic.module);
            return (
              <Link
                key={topic.id}
                href={`/calculator/${topic.id}`}
                className={`group flex flex-col justify-between rounded-xl border border-white/10 bg-[#13131a]/80 p-5 shadow-sm transition hover:scale-[1.01] hover:border-white/20 hover:bg-[#181822] cursor-pointer`}
                style={{
                  boxShadow: `0 4px 20px rgba(0,0,0,0.25)`,
                }}
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span
                      className={`rounded-md ${theme.badgeBg} ${theme.badgeText} px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider border border-white/5`}
                    >
                      {theme.shortName}
                    </span>
                    <span className="text-[11px] font-mono text-slate-500">
                      {topic.input_schema?.length || 0} inputs
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-100 group-hover:text-white transition">
                    {topic.title}
                  </h3>
                  <p className="mt-1.5 text-xs text-slate-400 leading-relaxed line-clamp-2">
                    {topic.short_description}
                  </p>
                </div>

                <div className="mt-5 flex items-center justify-between border-t border-white/5 pt-3">
                  <span
                    className={`text-xs font-semibold ${theme.badgeText} group-hover:brightness-110`}
                  >
                    Open Calculator
                  </span>
                  <ArrowRight
                    className={`h-4 w-4 ${theme.badgeText} transition group-hover:translate-x-1`}
                  />
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
