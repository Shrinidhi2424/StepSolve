import numpy as np
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from app.core.models import Step, SolveResponse
from app.core.expr_eval import parse_single_var


class FixedPointInput(BaseModel):
    g_expr: str = Field(default="cos(x)", description="Iteration function g(x) such that x = g(x)")
    x0: float = Field(default=0.5, description="Initial approximation x₀")
    tolerance: float = Field(default=1e-4, description="Convergence tolerance ε")
    max_iterations: int = Field(default=50, description="Maximum iterations allowed")


def solve(payload: Union[Dict[str, Any], FixedPointInput]) -> SolveResponse:
    """
    Executes Fixed Point Iteration Method:
        x_{n+1} = g(x_n)
    Solves f(x) = 0 by transforming it into the fixed point form x = g(x).
    """
    if isinstance(payload, dict):
        params = FixedPointInput(**payload)
    else:
        params = payload

    g = parse_single_var(params.g_expr, var="x")

    inputs_echo = {
        "g_expr": params.g_expr,
        "x0": params.x0,
        "tolerance": params.tolerance,
        "max_iterations": params.max_iterations,
    }

    x_curr = float(params.x0)
    tol = float(params.tolerance)
    max_iter = int(params.max_iterations)

    steps: List[Step] = []
    iterations_table: List[Dict[str, Any]] = []
    warnings: List[str] = []
    errors: List[float] = []

    converged = False
    root = x_curr
    final_error = float("inf")

    for n in range(1, max_iter + 1):
        try:
            x_next = g(x_curr)
        except Exception as e:
            warnings.append(f"Evaluation error at iteration {n} with x = {x_curr:.6f}: {str(e)}")
            break

        if np.isnan(x_next) or np.isinf(x_next) or abs(x_next) > 1e12:
            warnings.append(
                f"Numerical overflow/divergence at iteration {n}: value reached {x_next}. "
                "The iteration function diverges; ensure |g'(x)| < 1 in the neighborhood of the root."
            )
            break

        error = abs(x_next - x_curr)
        errors.append(error)
        final_error = error

        sub_str = f"x_{{{n}}} = g({x_curr:.6f}) = {x_next:.6f}"
        desc = (
            f"Evaluated iteration function at x_{{{n-1}}} = {x_curr:.6f} to obtain "
            f"x_{{{n}}} = {x_next:.6f}. Step difference |x_{{{n}}} - x_{{{n-1}}}| = {error:.6e}."
        )

        steps.append(
            Step(
                step_number=n,
                title=f"Iteration {n}",
                description=desc,
                formula="x_{n+1} = g(x_n)",
                substitution=sub_str,
                value=round(x_next, 6),
            )
        )

        iterations_table.append(
            {
                "iteration": n,
                "x_n": round(x_curr, 6),
                "g_x_n": round(x_next, 6),
                "error": round(error, 6),
            }
        )

        root = x_next

        # Convergence test
        if error < tol:
            converged = True
            break

        # Divergence test: check if error is strictly increasing over 3 consecutive steps
        if len(errors) >= 3 and errors[-1] > errors[-2] > errors[-3]:
            warnings.append(
                "Sequence appears to be diverging — error is increasing (|g'(x)| ≥ 1). "
                "Try reformulating x = g(x) or choosing a closer initial guess."
            )
            break

        x_curr = x_next

    if not converged and len(warnings) == 0:
        warnings.append(
            f"Maximum iterations ({max_iter}) reached without meeting convergence tolerance ({tol})."
        )

    # Plot data: curve of g(x) vs y = x line
    plot_data = None
    try:
        margin = max(abs(root - params.x0) * 1.5, 1.5)
        x_min = min(params.x0, root) - margin
        x_max = max(params.x0, root) + margin
        x_samples = np.linspace(x_min, x_max, 100)

        curve_pts = []
        for xs in x_samples:
            try:
                curve_pts.append({"x": round(float(xs), 4), "y": round(float(g(xs)), 4)})
            except Exception:
                pass

        plot_data = {
            "type": "scatter_line",
            "line": curve_pts,
            "scatter": [{"x": round(params.x0, 4), "y": round(float(g(params.x0)), 4)}],
            "highlighted": [{"x": round(root, 4), "y": round(float(root), 4)}],
        }
    except Exception:
        plot_data = None

    result = {
        "root": round(root, 6),
        "iterations": len(iterations_table),
        "converged": converged,
        "final_error": round(final_error, 8) if final_error != float("inf") else None,
    }

    if converged:
        result_summary = (
            f"Fixed point x* ≈ {root:.6f} found after {len(iterations_table)} iterations "
            f"(error = {final_error:.2e})"
        )
    else:
        result_summary = (
            f"Iteration terminated after {len(iterations_table)} steps. "
            f"Last value x ≈ {root:.6f} (did not converge to tolerance {tol})"
        )

    return SolveResponse(
        topic_id="fixed_point_iteration",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=result_summary,
        iterations_table=iterations_table,
        plot_data=plot_data,
        warnings=warnings,
    )
