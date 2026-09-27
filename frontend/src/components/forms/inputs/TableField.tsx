"use client";

import React from "react";
import { Plus, Trash2 } from "lucide-react";

interface TableFieldProps {
  name: string;
  label: string;
  value: number[][];
  onChange: (val: number[][]) => void;
  minRows?: number;
}

export function TableField({
  name,
  label,
  value,
  onChange,
  minRows = 2,
}: TableFieldProps) {
  const rows: number[][] =
    Array.isArray(value) && value.length > 0 ? value : [[0, 0], [1, 1]];

  const handleCellChange = (rowIndex: number, colIndex: 0 | 1, newVal: number) => {
    const next: number[][] = rows.map((r, i) => {
      if (i === rowIndex) {
        const copy: number[] = [r[0] ?? 0, r[1] ?? 0];
        copy[colIndex] = newVal;
        return copy;
      }
      return r;
    });
    onChange(next);
  };

  const handleAddRow = () => {
    const lastRow = rows[rows.length - 1];
    const nextX = lastRow ? (lastRow[0] ?? 0) + 1 : rows.length;
    const nextY = lastRow ? (lastRow[1] ?? 0) : 0;
    onChange([...rows, [nextX, nextY]]);
  };

  const handleRemoveRow = (idx: number) => {
    if (rows.length <= minRows) return;
    onChange(rows.filter((_, i) => i !== idx));
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {label} ({rows.length} points)
        </label>
        <button
          type="button"
          onClick={handleAddRow}
          className="flex items-center gap-1 rounded bg-indigo-600/30 px-2 py-1 text-xs font-medium text-indigo-300 hover:bg-indigo-600/50 transition cursor-pointer"
        >
          <Plus className="h-3 w-3" /> Add Point
        </button>
      </div>

      <div className="overflow-hidden rounded-lg border border-white/10 bg-slate-900/90">
        <table className="w-full text-left text-xs">
          <thead className="border-b border-white/10 bg-slate-800/50 text-slate-400">
            <tr>
              <th className="px-3 py-2 font-semibold">#</th>
              <th className="px-3 py-2 font-semibold">x</th>
              <th className="px-3 py-2 font-semibold">y / f(x)</th>
              <th className="px-3 py-2 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 font-mono">
            {rows.map((row, idx) => (
              <tr key={idx} className="hover:bg-white/[0.02]">
                <td className="px-3 py-1.5 text-slate-500">{idx + 1}</td>
                <td className="px-3 py-1.5">
                  <input
                    type="number"
                    step="any"
                    value={row[0]}
                    onChange={(e) =>
                      handleCellChange(idx, 0, parseFloat(e.target.value) || 0)
                    }
                    className="w-24 rounded border border-white/10 bg-slate-950 px-2 py-1 text-slate-200 outline-none focus:border-indigo-500"
                  />
                </td>
                <td className="px-3 py-1.5">
                  <input
                    type="number"
                    step="any"
                    value={row[1]}
                    onChange={(e) =>
                      handleCellChange(idx, 1, parseFloat(e.target.value) || 0)
                    }
                    className="w-24 rounded border border-white/10 bg-slate-950 px-2 py-1 text-slate-200 outline-none focus:border-indigo-500"
                  />
                </td>
                <td className="px-3 py-1.5 text-right">
                  <button
                    type="button"
                    disabled={rows.length <= minRows}
                    onClick={() => handleRemoveRow(idx)}
                    className="text-slate-500 hover:text-rose-400 disabled:opacity-30 disabled:hover:text-slate-500 transition cursor-pointer"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
