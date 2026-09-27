"use client";

import React from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import { TrendingUp } from "lucide-react";

interface SolverChartProps {
  plotData: any;
  title?: string;
}

export function SolverChart({ plotData, title = "Visual Solution" }: SolverChartProps) {
  if (!plotData) return null;

  // Multi-line chart (e.g. snapshots for heat equation)
  if (plotData.type === "multi_line" && Array.isArray(plotData.series)) {
    // Collect all unique x values
    const dataMap: Record<number, any> = {};
    plotData.series.forEach((s: any) => {
      if (Array.isArray(s.data)) {
        s.data.forEach((pt: any) => {
          const xVal = Number(pt.x.toFixed(4));
          if (!dataMap[xVal]) {
            dataMap[xVal] = { x: xVal };
          }
          dataMap[xVal][s.name] = pt.y !== undefined ? pt.y : pt.u;
        });
      }
    });

    const chartData = Object.values(dataMap).sort((a, b) => a.x - b.x);
    const colors = ["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"];

    return (
      <div className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-indigo-400" />
          <h4 className="text-sm font-bold tracking-tight text-white uppercase">
            {title}
          </h4>
        </div>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
              <XAxis dataKey="x" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f172a",
                  borderColor: "#334155",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
              {plotData.series.map((s: any, idx: number) => (
                <Line
                  key={s.name}
                  type="monotone"
                  dataKey={s.name}
                  stroke={colors[idx % colors.length]}
                  strokeWidth={2}
                  dot={false}
                />
              ))}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  // Single line ODE or BVP trajectory
  if (plotData.type === "line" && Array.isArray(plotData.series)) {
    const series = plotData.series[0];
    const data = series?.data || [];
    return (
      <div className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-indigo-400" />
          <h4 className="text-sm font-bold tracking-tight text-white uppercase">
            {title} — {series?.name || "Solution Curve"}
          </h4>
        </div>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
              <XAxis dataKey="x" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f172a",
                  borderColor: "#334155",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
              <Line
                type="monotone"
                dataKey="y"
                stroke="#6366f1"
                strokeWidth={2.5}
                dot={{ r: 3, fill: "#818cf8" }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  // Scatter + Fitted line / Interpolated curve
  if (plotData.type === "scatter_line") {
    const scatterData = plotData.scatter || [];
    const lineData = plotData.line || [];
    const highlighted = plotData.highlighted || [];

    return (
      <div className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-indigo-400" />
          <h4 className="text-sm font-bold tracking-tight text-white uppercase">
            {title}
          </h4>
        </div>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
              <XAxis dataKey="x" type="number" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis dataKey="y" type="number" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f172a",
                  borderColor: "#334155",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
              {lineData.length > 0 && (
                <Line
                  data={lineData}
                  name="Fitted / Interpolated Curve"
                  type="monotone"
                  dataKey="y"
                  stroke="#818cf8"
                  strokeWidth={2}
                  dot={false}
                />
              )}
              {scatterData.length > 0 && (
                <Scatter
                  data={scatterData}
                  name="Observed Points"
                  dataKey="y"
                  fill="#38bdf8"
                  shape="circle"
                />
              )}
              {highlighted.length > 0 && (
                <Scatter
                  data={highlighted}
                  name="Target Point"
                  dataKey="y"
                  fill="#f43f5e"
                  shape="cross"
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  return null;
}
