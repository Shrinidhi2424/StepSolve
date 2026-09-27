"use client";

import React from "react";

interface MatrixFieldProps {
  name: string;
  label: string;
  value: number[][];
  onChange: (val: number[][]) => void;
}

export function MatrixField({
  name,
  label,
  value,
  onChange,
}: MatrixFieldProps) {
  const matrix = Array.isArray(value) && value.length > 0 ? value : [[1, 0], [0, 1]];
  const rows = matrix.length;
  const cols = matrix[0]?.length || 0;

  const handleCellChange = (rIdx: number, cIdx: number, newVal: number) => {
    const updated = matrix.map((row, r) =>
      row.map((cell, c) => (r === rIdx && c === cIdx ? newVal : cell))
    );
    onChange(updated);
  };

  const handleResize = (newSize: number) => {
    const newMatrix: number[][] = [];
    for (let r = 0; r < newSize; r++) {
      const row: number[] = [];
      for (let c = 0; c < (cols === 1 ? 1 : newSize); c++) {
        if (matrix[r] && matrix[r][c] !== undefined) {
          row.push(matrix[r][c]);
        } else {
          row.push(r === c && cols !== 1 ? 1 : 0);
        }
      }
      newMatrix.push(row);
    }
    onChange(newMatrix);
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {label} ({rows}×{cols})
        </label>
        {cols > 1 && (
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <span>Size:</span>
            {[2, 3, 4].map((size) => (
              <button
                key={size}
                type="button"
                onClick={() => handleResize(size)}
                className={`rounded px-2 py-0.5 text-xs font-mono transition cursor-pointer ${
                  rows === size
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                }`}
              >
                {size}×{size}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="overflow-x-auto rounded-lg border border-white/10 bg-slate-900/90 p-3">
        <div
          className="grid gap-2 font-mono"
          style={{
            gridTemplateColumns: `repeat(${cols}, minmax(4rem, 1fr))`,
          }}
        >
          {matrix.map((row, r) =>
            row.map((cell, c) => (
              <input
                key={`${r}-${c}`}
                type="number"
                step="any"
                value={cell}
                onChange={(e) =>
                  handleCellChange(r, c, parseFloat(e.target.value) || 0)
                }
                className="w-full rounded border border-white/10 bg-slate-950 px-2 py-1.5 text-center text-xs text-slate-100 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
