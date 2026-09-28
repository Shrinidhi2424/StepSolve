"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ChevronRight,
  Calculator,
  ArrowLeft,
  ArrowRight,
  AlertCircle,
  RotateCcw,
  Sparkles,
} from "lucide-react";
import { getTopic, getTopics, solve } from "@/lib/api";
import { Topic, SolveResponse } from "@/lib/types";
import { DynamicSolverForm } from "@/components/forms/DynamicSolverForm";
import { ResultSummary } from "@/components/results/ResultSummary";
import { WarningsBanner } from "@/components/results/WarningsBanner";
import { IterationTable } from "@/components/results/IterationTable";
import { StepList } from "@/components/results/StepList";
import { SolverChart } from "@/components/results/SolverChart";
import { getModuleTheme } from "@/lib/moduleTheme";

const TOPIC_ORDER = [
  "fixed_point_iteration",
  "secant_method",
  "gauss_jordan_solve",
  "lagrange_interpolation",
  "cubic_spline_interpolation",
  "least_squares_fit",
  "newton_forward_difference",
  "trapezoidal_rule",
  "simpsons_one_third_rule",
  "euler_method",
  "modified_euler_method",
  "runge_kutta_4",
  "finite_difference_bvp",
  "heat_equation_explicit",
  "matrix_inversion_gauss_jordan",
];

export default function TopicSolverPage() {
  const params = useParams();
  const topicId = params.topicId as string;

  const [topic, setTopic] = useState<Topic | null>(null);
  const [allTopics, setAllTopics] = useState<Topic[]>([]);
  const [response, setResponse] = useState<SolveResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [topicLoading, setTopicLoading] = useState(true);

  useEffect(() => {
    async function loadTopic() {
      try {
        setTopicLoading(true);
        const [data, topicList] = await Promise.all([
          getTopic(topicId),
          getTopics().catch(() => []),
        ]);
        setTopic(data);
        if (topicList.length > 0) setAllTopics(topicList);
        setError(null);
        setResponse(null); // Clear previous solution when topic changes
      } catch (err: any) {
        setError(err.message || "Failed to load topic configuration.");
      } finally {
        setTopicLoading(false);
      }
    }
    if (topicId) {
      loadTopic();
    }
  }, [topicId]);

  const handleSolve = async (payload: Record<string, any>) => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await solve(topicId, payload);
      setResponse(res);
    } catch (err: any) {
      setError(err.message || "Calculation failed");
      setResponse(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResponse(null);
    setError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // Find previous and next topics for bottom navigation
  const currentIndex = TOPIC_ORDER.indexOf(topicId);
  const prevTopicId = currentIndex > 0 ? TOPIC_ORDER[currentIndex - 1] : null;
  const nextTopicId =
    currentIndex >= 0 && currentIndex < TOPIC_ORDER.length - 1
      ? TOPIC_ORDER[currentIndex + 1]
      : null;

  const prevTopicTitle = allTopics.find((t) => t.id === prevTopicId)?.title || prevTopicId;
  const nextTopicTitle = allTopics.find((t) => t.id === nextTopicId)?.title || nextTopicId;

  const theme = topic ? getModuleTheme(topic.module) : getModuleTheme(1);

  if (topicLoading) {
    return (
      <div className="mx-auto flex max-w-7xl items-center justify-center py-24 text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
          <p className="text-sm">Loading solver configuration...</p>
        </div>
      </div>
    );
  }

  if (!topic && error) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16">
        <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-6 text-rose-300">
          <h2 className="text-lg font-bold">Topic Not Found</h2>
          <p className="mt-2 text-sm">{error}</p>
          <Link
            href="/calculator"
            className="mt-4 inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300"
          >
            <ArrowLeft className="h-4 w-4" /> Back to Calculator Topics
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      {/* Breadcrumb Navigation */}
      <nav className="mb-6 flex flex-wrap items-center gap-2 text-xs font-medium text-slate-400">
        <Link href="/" className="hover:text-white transition">
          Home
        </Link>
        <ChevronRight className="h-3.5 w-3.5 text-slate-600" />
        <Link href="/calculator" className="hover:text-white transition">
          Calculator
        </Link>
        <ChevronRight className="h-3.5 w-3.5 text-slate-600" />
        <span
          className={`rounded ${theme.badgeBg} ${theme.badgeText} px-2 py-0.5 font-bold uppercase text-[10px]`}
        >
          {theme.shortName}
        </span>
        <ChevronRight className="h-3.5 w-3.5 text-slate-600" />
        <span className="text-slate-100 font-semibold">{topic?.title}</span>
      </nav>

      {/* Main Grid: Left Panel (Form) & Right Panel (Results) */}
      <div className="grid gap-8 lg:grid-cols-12">
        {/* Left Form Column */}
        <div className="lg:col-span-5">
          <div
            className={`sticky top-20 rounded-2xl border ${theme.borderAccent} bg-[#13131a] p-6 shadow-xl backdrop-blur-md transition`}
            style={{
              boxShadow: `0 8px 30px ${theme.glowColor}`,
            }}
          >
            <div className="mb-5 pb-5 border-b border-white/5">
              <div className="flex items-center justify-between mb-2">
                <span
                  className={`rounded-md ${theme.badgeBg} ${theme.badgeText} px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider border border-white/5`}
                >
                  {theme.shortName} · {theme.name}
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  ID: {topic?.id}
                </span>
              </div>
              <h1 className="text-xl font-bold tracking-tight text-white">
                {topic?.title}
              </h1>
              <p className="mt-2 text-xs text-slate-300 leading-relaxed">
                {topic?.short_description}
              </p>
            </div>

            {topic && (
              <DynamicSolverForm
                topic={topic}
                onSolve={handleSolve}
                isLoading={isLoading}
              />
            )}
          </div>
        </div>

        {/* Right Results Column */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          {/* Shimmer skeleton while calculating */}
          {isLoading && (
            <div className="flex flex-col gap-4 animate-pulse">
              <div className="h-28 rounded-2xl bg-[#13131a] border border-white/5 skeleton-shimmer" />
              <div className="h-72 rounded-2xl bg-[#13131a] border border-white/5 skeleton-shimmer" />
              <div className="h-64 rounded-2xl bg-[#13131a] border border-white/5 skeleton-shimmer" />
            </div>
          )}

          {/* Error Notice */}
          {error && !isLoading && (
            <div className="rounded-2xl border border-rose-500/30 bg-rose-950/20 p-5 text-rose-300 shadow-lg animate-fade-in">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 shrink-0 text-rose-400 mt-0.5" />
                <div>
                  <h4 className="font-bold text-sm">Calculation Message</h4>
                  <p className="mt-1 text-xs text-rose-200/90 leading-relaxed whitespace-pre-wrap">
                    {error}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Placeholder when not solved yet */}
          {!response && !error && !isLoading && (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 bg-[#13131a]/40 p-12 text-center text-slate-400">
              <div
                className={`flex h-14 w-14 items-center justify-center rounded-2xl ${theme.badgeBg} ${theme.badgeText} mb-4`}
              >
                <Calculator className="h-7 w-7" />
              </div>
              <h3 className="text-base font-bold text-slate-200">
                Ready for Computation
              </h3>
              <p className="mt-1.5 max-w-sm text-xs text-slate-400 leading-relaxed">
                Adjust input parameters on the left and click &quot;Solve &amp; Show Steps&quot; to inspect the step-by-step derivation, iteration history table, and visual charts.
              </p>
            </div>
          )}

          {/* Result view */}
          {response && !isLoading && (
            <div className="flex flex-col gap-6 animate-fade-in">
              {/* Header Action: Reset / Try Different Input */}
              <div className="flex items-center justify-between px-1">
                <div className="flex items-center gap-2">
                  <span className="flex h-2 w-2 rounded-full bg-emerald-400" />
                  <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                    Solution Computed
                  </span>
                </div>
                <button
                  type="button"
                  onClick={handleReset}
                  className="flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-white transition cursor-pointer"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  <span>Try Different Input</span>
                </button>
              </div>

              {/* Result Summary */}
              <div className="animate-glow-pulse rounded-2xl">
                <ResultSummary
                  summary={response.result_summary}
                  result={response.result}
                  hasWarnings={response.warnings && response.warnings.length > 0}
                />
              </div>

              {/* Warnings Banner */}
              <WarningsBanner warnings={response.warnings} />

              {/* Chart */}
              {response.plot_data && (
                <SolverChart
                  plotData={response.plot_data}
                  title={`${topic?.title} Plot`}
                />
              )}

              {/* Iteration Table */}
              {response.iterations_table && (
                <IterationTable iterations={response.iterations_table} />
              )}

              {/* Step Derivations */}
              {response.steps && response.steps.length > 0 && (
                <StepList steps={response.steps} />
              )}
            </div>
          )}
        </div>
      </div>

      {/* Bottom Topic Navigation: Previous Topic / Next Topic */}
      <div className="mt-16 border-t border-white/10 pt-8 flex items-center justify-between">
        {prevTopicId ? (
          <Link
            href={`/calculator/${prevTopicId}`}
            className="group flex items-center gap-2.5 rounded-xl border border-white/10 bg-[#13131a] px-4 py-3 text-xs font-semibold text-slate-300 hover:border-white/20 hover:text-white transition cursor-pointer"
          >
            <ArrowLeft className="h-4 w-4 transition group-hover:-translate-x-1" />
            <div className="text-left">
              <span className="block text-[10px] uppercase tracking-wider text-slate-500 font-normal">
                Previous Topic
              </span>
              <span className="font-semibold">{prevTopicTitle}</span>
            </div>
          </Link>
        ) : (
          <div />
        )}

        {nextTopicId && (
          <Link
            href={`/calculator/${nextTopicId}`}
            className="group flex items-center gap-2.5 rounded-xl border border-white/10 bg-[#13131a] px-4 py-3 text-xs font-semibold text-slate-300 hover:border-white/20 hover:text-white transition cursor-pointer"
          >
            <div className="text-right">
              <span className="block text-[10px] uppercase tracking-wider text-slate-500 font-normal">
                Next Topic
              </span>
              <span className="font-semibold">{nextTopicTitle}</span>
            </div>
            <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
          </Link>
        )}
      </div>
    </div>
  );
}
