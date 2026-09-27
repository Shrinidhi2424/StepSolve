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
} from "lucide-react";
import { getTopics } from "@/lib/api";
import { Topic } from "@/lib/types";

const MODULE_META = [
  {
    module: 1,
    title: "Module I: Equations & Systems",
    icon: FunctionSquare,
    badge: "Module 1",
    accent: "from-indigo-500/20 via-indigo-600/5 to-transparent border-indigo-500/30 text-indigo-400",
    description: "Fixed point iteration, Secant method, and Gauss-Jordan direct linear system elimination.",
  },
  {
    module: 2,
    title: "Module II: Interpolation & Fit",
    icon: Spline,
    badge: "Module 2",
    accent: "from-teal-500/20 via-teal-600/5 to-transparent border-teal-500/30 text-teal-400",
    description: "Lagrange polynomials (unequal intervals), Natural Cubic Splines, and Least Squares linear regression.",
  },
  {
    module: 3,
    title: "Module III: Calculus & Quadrature",
    icon: Sigma,
    badge: "Module 3",
    accent: "from-amber-500/20 via-amber-600/5 to-transparent border-amber-500/30 text-amber-400",
    description: "Newton forward differences differentiation, Trapezoidal rule, and Simpson's 1/3 integration.",
  },
  {
    module: 4,
    title: "Module IV: ODE Initial Value",
    icon: Activity,
    badge: "Module 4",
    accent: "from-rose-500/20 via-rose-600/5 to-transparent border-rose-500/30 text-rose-400",
    description: "First-order ODE solutions via Euler, Modified Euler (Heun), and 4th-Order Runge-Kutta (RK4).",
  },
  {
    module: 5,
    title: "Module V: BVP & Inversion",
    icon: Layers,
    badge: "Module 5",
    accent: "from-emerald-500/20 via-emerald-600/5 to-transparent border-emerald-500/30 text-emerald-400",
    description: "Finite difference for 2-point ODE BVPs, 1D Heat Equation (FTCS), and Gauss-Jordan matrix inversion.",
  },
];

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
      {/* Hero Section */}
      <div className="relative mb-16 overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-b from-indigo-950/40 via-slate-900/60 to-slate-950 p-8 sm:p-14 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-4 py-1.5 text-xs font-semibold text-indigo-300">
          <Sparkles className="h-3.5 w-3.5" />
          <span>Complete 15-Topic Syllabus Calculator</span>
        </div>

        <h1 className="mt-6 text-4xl sm:text-6xl font-black tracking-tight text-white">
          Numerical Methods with{" "}
          <span className="bg-gradient-to-r from-indigo-400 via-violet-300 to-purple-400 bg-clip-text text-transparent">
            Step-by-Step
          </span>{" "}
          Derivations
        </h1>

        <p className="mx-auto mt-5 max-w-2xl text-base sm:text-lg text-slate-300">
          StepSolve gives textbook-style derivation steps, iteration tables,
          convergence checks, and interactive visual charts for all 5 course modules.
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <Link
            href="/calculator"
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 transition hover:from-indigo-500 hover:to-violet-500 cursor-pointer"
          >
            <Calculator className="h-4 w-4" />
            <span>Launch All 15 Solvers</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            href="/calculator/secant_method"
            className="flex items-center gap-2 rounded-xl border border-white/10 bg-slate-900/80 px-5 py-3.5 text-sm font-semibold text-slate-200 transition hover:bg-slate-800 hover:text-white cursor-pointer"
          >
            <span>Try Quick Demo (Secant)</span>
          </Link>
        </div>
      </div>

      {/* 5 Modules Overview Grid */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white">
            Course Modules & Topics
          </h2>
          <p className="text-xs text-slate-400">
            3 curated methods per module across all 5 syllabus sections
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
        {MODULE_META.map((meta) => {
          const moduleTopics = topics.filter((t) => t.module === meta.module);
          const Icon = meta.icon;

          return (
            <div
              key={meta.module}
              className={`flex flex-col justify-between rounded-2xl border bg-gradient-to-b ${meta.accent} p-6 transition hover:scale-[1.01]`}
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="rounded-md border border-white/10 bg-slate-950/60 px-2 py-0.5 text-[11px] font-bold uppercase tracking-wider text-slate-300">
                    {meta.badge}
                  </span>
                  <Icon className="h-5 w-5 opacity-80" />
                </div>

                <h3 className="mt-3 text-lg font-bold text-white">
                  {meta.title}
                </h3>
                <p className="mt-1 text-xs text-slate-300/80 leading-relaxed">
                  {meta.description}
                </p>

                <div className="mt-4 space-y-2 border-t border-white/5 pt-4">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Included Methods:
                  </span>
                  <div className="flex flex-col gap-1.5">
                    {moduleTopics.map((t) => (
                      <Link
                        key={t.id}
                        href={`/calculator/${t.id}`}
                        className="group flex items-center justify-between rounded-lg bg-slate-950/60 px-3 py-2 text-xs font-medium text-slate-300 border border-white/5 transition hover:border-white/20 hover:text-white"
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
