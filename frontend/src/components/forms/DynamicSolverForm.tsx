"use client";

import React, { useState, useEffect } from "react";
import { Topic, TopicField } from "@/lib/types";
import { NumberField } from "./inputs/NumberField";
import { FunctionField } from "./inputs/FunctionField";
import { TableField } from "./inputs/TableField";
import { MatrixField } from "./inputs/MatrixField";
import { Play, RotateCcw, Loader2 } from "lucide-react";

interface DynamicSolverFormProps {
  topic: Topic;
  onSolve: (payload: Record<string, any>) => void;
  isLoading: boolean;
}

export function DynamicSolverForm({
  topic,
  onSolve,
  isLoading,
}: DynamicSolverFormProps) {
  const [formData, setFormData] = useState<Record<string, any>>({});

  useEffect(() => {
    // Initialize form values from topic schema defaults
    const initial: Record<string, any> = {};
    topic.input_schema.forEach((field) => {
      initial[field.name] = field.default;
    });
    setFormData(initial);
  }, [topic]);

  const handleChange = (name: string, val: any) => {
    setFormData((prev) => ({ ...prev, [name]: val }));
  };

  const handleReset = () => {
    const initial: Record<string, any> = {};
    topic.input_schema.forEach((field) => {
      initial[field.name] = field.default;
    });
    setFormData(initial);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSolve(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      <div className="flex flex-col gap-4">
        {topic.input_schema.map((field: TopicField) => {
          const val = formData[field.name] ?? field.default;

          if (field.type === "function") {
            return (
              <FunctionField
                key={field.name}
                name={field.name}
                label={field.label}
                value={val || ""}
                onChange={(newVal) => handleChange(field.name, newVal)}
              />
            );
          }

          if (field.type === "table") {
            return (
              <TableField
                key={field.name}
                name={field.name}
                label={field.label}
                value={val || []}
                onChange={(newVal) => handleChange(field.name, newVal)}
              />
            );
          }

          if (field.type === "matrix") {
            return (
              <MatrixField
                key={field.name}
                name={field.name}
                label={field.label}
                value={val || [[]]}
                onChange={(newVal) => handleChange(field.name, newVal)}
              />
            );
          }

          return (
            <NumberField
              key={field.name}
              name={field.name}
              label={field.label}
              value={val ?? 0}
              onChange={(newVal) => handleChange(field.name, newVal)}
            />
          );
        })}
      </div>

      <div className="flex items-center gap-3 pt-2">
        <button
          type="submit"
          disabled={isLoading}
          className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-600/25 transition hover:from-indigo-500 hover:to-violet-500 focus:ring-2 focus:ring-indigo-400 disabled:opacity-50 cursor-pointer"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Solving...</span>
            </>
          ) : (
            <>
              <Play className="h-4 w-4 fill-current" />
              <span>Solve & Show Steps</span>
            </>
          )}
        </button>

        <button
          type="button"
          onClick={handleReset}
          title="Reset to sample values"
          className="rounded-xl border border-white/10 bg-slate-900 p-3 text-slate-400 hover:bg-slate-800 hover:text-white transition cursor-pointer"
        >
          <RotateCcw className="h-4 w-4" />
        </button>
      </div>
    </form>
  );
}
