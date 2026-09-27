import numpy as np
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from app.core.models import Step, SolveResponse
from app.core.expr_eval import parse_single_var


class SecantInput(BaseModel):
    f_expr: str = Field(default="x**3 - x - 2", description="Function f(x)")
    x0: float = Field(default=1.0, description="First initial guess")
    x1: float = Field(default=2.0, description="Second initial guess")
    tolerance: float = Field(default=1e-4, description="Convergence tolerance")
    max_iterations: int = Field(default=50, description="Maximum iterations")


def solve(payload: Union[Dict[str, Any], SecantInput]) -> SolveResponse:
    """
    Executes the Secant Method to find a root of f(x) = 0.
    Iteratively computes:
        x_{n+1} = x_n - f(x_n) * (x_n - x_{n-1}) / (f(x_n) - f(x_{n-1}))
    Logs all textbook steps, iteration rows, and curve plot data.
    """
    if isinstance(payload, dict):
        params = SecantInput(**payload)
    else:
        params = payload

    f = parse_single_var(params.f_expr, var="x")

    inputs_echo = {
        "f_expr": params.f_expr,
        "x0": params.x0,
        "x1": params.x1,
        "tolerance": params.tolerance,
        "max_iterations": params.max_iterations,
    }

    x_prev = float(params.x0)
    x_curr = float(params.x1)
    tol = float(params.tolerance)
    max_iter = int(params.max_iterations)

    steps: List[Step] = []
    iterations_table: List[Dict[str, Any]] = []
    warnings: List[str] = []

    f_prev = f(x_prev)
    f_curr = f(x_curr)

    # Check for identical initial points
    if abs(x_curr - x_prev) < 1e-14:
        warnings.append("Initial guesses x0 and x1 are identical. Secant method requires two distinct points.")

    converged = False
    root = x_curr
    f_at_root = f_curr

    # Handle immediate root at initial guesses
    if abs(f_prev) <= tol:
        converged = True
        root = x_prev
        f_at_root = f_prev
        steps.append(
            Step(
                step_number=1,
                title="Immediate Root at x₀",
                description=f"Initial guess x₀ = {x_prev} already satisfies |f(x₀)| ≤ {tol}.",
                formula="f(x_0) \\approx 0",
                substitution=f"f({x_prev}) = {f_prev:.6e}",
                value=round(root, 6),
            )
        )
    elif abs(f_curr) <= tol:
        converged = True
        root = x_curr
        f_at_root = f_curr
        steps.append(
            Step(
                step_number=1,
                title="Immediate Root at x₁",
                description=f"Initial guess x₁ = {x_curr} already satisfies |f(x₁)| ≤ {tol}.",
                formula="f(x_1) \\approx 0",
                substitution=f"f({x_curr}) = {f_curr:.6e}",
                value=round(root, 6),
            )
        )
    else:
        for n in range(1, max_iter + 1):
            denom = f_curr - f_prev

            if abs(denom) < 1e-12:
                warnings.append(
                    f"Near-zero denominator |f(x_{n}) - f(x_{n-1})| = {abs(denom):.2e} at iteration {n}. "
                    "Secant line is nearly horizontal; stopping iteration to avoid division by zero."
                )
                break

            x_next = x_curr - f_curr * (x_curr - x_prev) / denom
            error = abs(x_next - x_curr)
            f_next = f(x_next)

            sub_str = (
                f"x_{{{n+1}}} = {x_curr:.6f} - "
                f"\\frac{{{f_curr:.6f} \\times ({x_curr:.6f} - {x_prev:.6f})}}"
                f"{{{f_curr:.6f} - ({f_prev:.6f})}} = {x_next:.6f}"
            )

            desc = (
                f"Applied secant interpolation between x_{{{n-1}}} = {x_prev:.6f} (f = {f_prev:.6f}) "
                f"and x_{{{n}}} = {x_curr:.6f} (f = {f_curr:.6f}). "
                f"Computed x_{{{n+1}}} = {x_next:.6f} with step error = {error:.6e}."
            )

            steps.append(
                Step(
                    step_number=n,
                    title=f"Iteration {n}",
                    description=desc,
                    formula="x_{n+1} = x_n - \\frac{f(x_n)(x_n - x_{n-1})}{f(x_n) - f(x_{n-1})}",
                    substitution=sub_str,
                    value=round(x_next, 6),
                )
            )

            iterations_table.append(
                {
                    "iteration": n,
                    "x_prev": round(x_prev, 6),
                    "x_curr": round(x_curr, 6),
                    "f_x_prev": round(f_prev, 6),
                    "f_x_curr": round(f_curr, 6),
                    "x_next": round(x_next, 6),
                    "error": round(error, 6),
                }
            )

            root = x_next
            f_at_root = f_next

            if error < tol or abs(f_next) < tol:
                converged = True
                break

            x_prev, x_curr = x_curr, x_next
            f_prev, f_curr = f_curr, f_next

        if not converged and len(warnings) == 0:
            warnings.append(
                f"Method reached maximum iteration limit ({max_iter}) without reaching tolerance ({tol})."
            )

    # Prepare plot data for visualization
    plot_data = None
    try:
        x_min = min(params.x0, params.x1, root) - 1.0
        x_max = max(params.x0, params.x1, root) + 1.0
        x_samples = np.linspace(x_min, x_max, 100)
        curve_pts = []
        for xs in x_samples:
            try:
                curve_pts.append({"x": round(float(xs), 4), "y": round(float(f(xs)), 4)})
            except Exception:
                pass

        plot_data = {
            "type": "scatter_line",
            "line": curve_pts,
            "scatter": [
                {"x": round(params.x0, 4), "y": round(float(f(params.x0)), 4)},
                {"x": round(params.x1, 4), "y": round(float(f(params.x1)), 4)},
            ],
            "highlighted": [
                {"x": round(root, 4), "y": round(float(f_at_root), 4)},
            ],
        }
    except Exception:
        plot_data = None

    result = {
        "root": round(root, 6),
        "iterations": len(iterations_table),
        "converged": converged,
        "f_at_root": round(f_at_root, 8),
    }

    result_summary = (
        f"Root ≈ {root:.6f} found after {len(iterations_table)} iterations "
        f"(|f(root)| = {abs(f_at_root):.2e})"
    )

    return SolveResponse(
        topic_id="secant_method",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=result_summary,
        iterations_table=iterations_table,
        plot_data=plot_data,
        warnings=warnings,
    )
