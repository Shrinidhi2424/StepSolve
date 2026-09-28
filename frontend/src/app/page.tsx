import Link from "next/link";
import {
  Calculator,
  ArrowRight,
  Sparkles,
  FunctionSquare,
  Spline,
  Sigma,
  Activity,
  Layers,
  BookOpen,
  CheckCircle2,
} from "lucide-react";
import { getTopics } from "@/lib/api";
import { Topic } from "@/lib/types";
import { MODULE_THEMES } from "@/lib/moduleTheme";

const MODULE_ICONS: Record<number, any> = {
  1: FunctionSquare,
  2: Spline,
  3: Sigma,
  4: Activity,
  5: Layers,
};

const MODULE_DESCRIPTIONS: Record<number, string> = {
  1: "Fixed Point Iteration, Secant Method root-finding, and Gauss-Jordan direct linear system elimination.",
  2: "Lagrange Interpolation (unequal intervals), Natural Cubic Splines via Thomas algorithm, and Least Squares regression.",
  3: "Newton Forward Difference differentiation, Composite Trapezoidal rule, and Simpson's 1/3 numerical quadrature.",
  4: "Initial value ODE solutions via standard Euler, Modified Euler (Heun predictor-corrector), and 4th-Order Runge-Kutta.",
  5: "Central difference for 2-point ODE BVPs, 1D Heat Equation (FTCS explicit), and Gauss-Jordan matrix inversion.",
};

// Fallback topics if API is not reachable during build
const FALLBACK_TOPICS: Partial<Topic>[] = [
  { id: "fixed_point_iteration", module: 1, title: "Fixed Point Iteration" },
  { id: "secant_method", module: 1, title: "Secant Method" },
  { id: "gauss_jordan_solve", module: 1, title: "Gauss-Jordan Elimination" },
  { id: "lagrange_interpolation", module: 2, title: "Lagrange Interpolation" },
  { id: "cubic_spline_interpolation", module: 2, title: "Cubic Spline (Natural)" },
  { id: "least_squares_fit", module: 2, title: "Least Squares Linear Fit" },
  { id: "newton_forward_difference", module: 3, title: "Newton's Forward Difference" },
  { id: "trapezoidal_rule", module: 3, title: "Trapezoidal Rule" },
  { id: "simpsons_one_third_rule", module: 3, title: "Simpson's 1/3 Rule" },
  { id: "euler_method", module: 4, title: "Euler's Method" },
  { id: "modified_euler_method", module: 4, title: "Modified Euler (Heun)" },
  { id: "runge_kutta_4", module: 4, title: "Runge-Kutta 4th Order (RK4)" },
  { id: "finite_difference_bvp", module: 5, title: "Finite Difference BVP" },
  { id: "heat_equation_explicit", module: 5, title: "1D Heat Equation (FTCS)" },
  { id: "matrix_inversion_gauss_jordan", module: 5, title: "Matrix Inversion" },
];

export default async function HomePage() {
  let topics: Partial<Topic>[] = FALLBACK_TOPICS;
  try {
    const fetched = await getTopics();
    if (fetched && fetched.length > 0) {
      topics = fetched;
    }
  } catch (err) {
    // Graceful fallback to static list
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Hero Section with animated gradient border & background */}
      <div className="relative mb-16 overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-b from-[#131322] via-[#0f0f18] to-[#0a0a0f] p-8 sm:p-14 text-center shadow-2xl">
        <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-4 py-1.5 text-xs font-semibold text-indigo-300">
          <Sparkles className="h-3.5 w-3.5" />
          <span>15 Methods · 5 Modules · Step-by-Step</span>
        </div>

        <h1 className="mt-6 text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
          Numerical Methods with{" "}
          <span className="bg-gradient-to-r from-indigo-400 via-violet-300 to-purple-400 bg-clip-text text-transparent">
            Step-by-Step
          </span>{" "}
          Derivations
        </h1>

        <p className="mx-auto mt-5 max-w-2xl text-base sm:text-lg text-slate-300">
          StepSolve gives textbook-style derivation steps, iteration tables,
          convergence diagnostics, and interactive visual charts for all 5 course modules.
        </p>

        {/* Feature badges */}
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3 text-xs text-slate-400">
          <span className="flex items-center gap-1.5 rounded-md bg-white/5 px-2.5 py-1">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" /> All 15 Solvers Active
          </span>
          <span className="flex items-center gap-1.5 rounded-md bg-white/5 px-2.5 py-1">
            <CheckCircle2 className="h-3.5 w-3.5 text-indigo-400" /> Complete LaTeX Equations
          </span>
          <span className="flex items-center gap-1.5 rounded-md bg-white/5 px-2.5 py-1">
            <CheckCircle2 className="h-3.5 w-3.5 text-teal-400" /> Interactive Charts
          </span>
        </div>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <Link
            href="/calculator"
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-600 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 transition hover:from-indigo-500 hover:to-violet-500 hover:scale-[1.02] cursor-pointer"
          >
            <Calculator className="h-4 w-4" />
            <span>Launch All 15 Solvers</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            href="/calculator/secant_method"
            className="flex items-center gap-2 rounded-xl border border-white/10 bg-slate-900/80 px-5 py-3.5 text-sm font-semibold text-slate-200 transition hover:bg-slate-800 hover:text-white cursor-pointer"
          >
            <BookOpen className="h-4 w-4 text-slate-400" />
            <span>Try Quick Demo (Secant)</span>
          </Link>
        </div>
      </div>

      {/* 5 Modules Overview Grid */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white">
            Course Modules &amp; Topics
          </h2>
          <p className="text-xs text-slate-400">
            3 curated numerical methods per module across all 5 syllabus sections
          </p>
        </div>
        <Link
          href="/calculator"
          className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
        >
          View all 15 <ArrowRight className="h-3 w-3" />
        </Link>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3, 4, 5].map((modNum) => {
          const theme = MODULE_THEMES[modNum];
          const Icon = MODULE_ICONS[modNum];
          const desc = MODULE_DESCRIPTIONS[modNum];
          const moduleTopics = topics.filter((t) => t.module === modNum);

          return (
            <div
              key={modNum}
              className={`flex flex-col justify-between rounded-2xl border ${theme.borderAccent} bg-gradient-to-b ${theme.gradientFrom} via-slate-900/40 to-slate-950 p-6 shadow-lg transition duration-200 hover:scale-[1.02] hover:shadow-xl`}
              style={{
                boxShadow: `0 8px 30px ${theme.glowColor}`,
              }}
            >
              <div>
                <div className="flex items-center justify-between">
                  <span
                    className={`rounded-md border border-white/10 ${theme.badgeBg} px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider ${theme.badgeText}`}
                  >
                    {theme.shortName}
                  </span>
                  <Icon className={`h-5 w-5 ${theme.badgeText} opacity-90`} />
                </div>

                <h3 className="mt-3 text-lg font-bold text-white">
                  {theme.name}
                </h3>
                <p className="mt-1 text-xs text-slate-300/80 leading-relaxed">
                  {desc}
                </p>

                <div className="mt-5 space-y-2 border-t border-white/5 pt-4">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Included Methods:
                  </span>
                  <div className="flex flex-col gap-1.5">
                    {moduleTopics.map((t) => (
                      <Link
                        key={t.id}
                        href={`/calculator/${t.id}`}
                        className="group flex items-center justify-between rounded-lg bg-slate-950/70 px-3 py-2 text-xs font-medium text-slate-300 border border-white/5 transition hover:border-white/20 hover:text-white cursor-pointer"
                      >
                        <span className="truncate">{t.title}</span>
                        <ArrowRight className="h-3 w-3 opacity-0 transition group-hover:opacity-100 group-hover:translate-x-0.5" />
                      </Link>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
