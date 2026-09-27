"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ChevronRight,
  Calculator,
  ArrowLeft,
  AlertCircle,
  HelpCircle,
  Info,
} from "lucide-react";
import { getTopic, solve } from "@/lib/api";
import { Topic, SolveResponse } from "@/lib/types";
import { DynamicSolverForm } from "@/components/forms/DynamicSolverForm";
import { ResultSummary } from "@/components/results/ResultSummary";
import { WarningsBanner } from "@/components/results/WarningsBanner";
import { IterationTable } from "@/components/results/IterationTable";
import { StepList } from "@/components/results/StepList";
import { SolverChart } from "@/components/results/SolverChart";

export default function TopicSolverPage() {
  const params = useParams();
  const topicId = params.topicId as string;

  const [topic, setTopic] = useState<Topic | null>(null);
  const [response, setResponse] = useState<SolveResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [topicLoading, setTopicLoading] = useState(true);

  useEffect(() => {
    async function loadTopic() {
      try {
        setTopicLoading(true);
        const data = await getTopic(topicId);
        setTopic(data);
        setError(null);
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

  if (topicLoading) {
    return (
      <div className="mx-auto flex max-w-7xl items-center justify-center py-24 text-slate-400">
        <p className="text-sm">Loading method configuration...</p>
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
      <nav className="mb-6 flex items-center gap-2 text-xs font-medium text-slate-400">
        <Link href="/" className="hover:text-white transition">
          Home
        </Link>
        <ChevronRight className="h-3.5 w-3.5 text-slate-600" />
        <Link href="/calculator" className="hover:text-white transition">
          Calculator
        </Link>
        <ChevronRight className="h-3.5 w-3.5 text-slate-600" />
        <span className="rounded bg-white/5 px-2 py-0.5 text-slate-300">
          Module {topic?.module}
        </span>
        <ChevronRight className="h-3.5 w-3.5 text-slate-600" />
        <span className="text-indigo-400 font-semibold">{topic?.title}</span>
      </nav>

      {/* Main Grid: Left Panel (Form) & Right Panel (Results) */}
      <div className="grid gap-8 lg:grid-cols-12">
        {/* Left Form Column */}
        <div className="lg:col-span-5">
          <div className="sticky top-20 rounded-2xl border border-white/10 bg-slate-900/70 p-6 shadow-xl backdrop-blur-md">
            <div className="mb-5 pb-5 border-b border-white/5">
              <div className="flex items-center justify-between mb-2">
                <span className="rounded-md bg-indigo-500/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-indigo-400 border border-indigo-500/20">
                  Module {topic?.module}
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  ID: {topic?.id}
                </span>
              </div>
              <h1 className="text-xl font-bold tracking-tight text-white">
                {topic?.title}
              </h1>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
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
          {/* Error Notice */}
          {error && (
            <div className="rounded-2xl border border-rose-500/30 bg-rose-950/20 p-5 text-rose-300 shadow-lg">
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
          {!response && !error && (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 bg-slate-900/30 p-12 text-center text-slate-400">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/5 text-slate-500 mb-4">
                <Calculator className="h-6 w-6" />
              </div>
              <h3 className="text-base font-bold text-slate-200">
                Ready for Computation
              </h3>
              <p className="mt-1.5 max-w-sm text-xs text-slate-400">
                Adjust input parameters on the left and click &quot;Solve &amp; Show Steps&quot; to inspect the step-by-step derivation, iteration history, and graphs.
              </p>
            </div>
          )}

          {/* Result view */}
          {response && (
            <>
              {/* Result Summary */}
              <ResultSummary
                summary={response.result_summary}
                result={response.result}
                hasWarnings={response.warnings && response.warnings.length > 0}
              />

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
            </>
          )}
        </div>
      </div>
    </div>
  );
}
