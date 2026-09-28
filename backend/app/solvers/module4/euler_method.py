import numpy as np
from typing import Any, Dict, List, Union
from pydantic import BaseModel, Field

from app.core.models import Step, SolveResponse
from app.core.expr_eval import parse_two_var


class ODEInput(BaseModel):
    f_expr: str = Field(default="x + y", description="Derivative function dy/dx = f(x, y)")
    x0: float = Field(default=0.0, description="Initial x₀")
    y0: float = Field(default=1.0, description="Initial y₀ = y(x₀)")
    h: float = Field(default=0.1, description="Step size h")
    x_end: float = Field(default=0.5, description="Final x (target point)")


def solve(payload: Union[Dict[str, Any], ODEInput]) -> SolveResponse:
    """
    Solves first-order IVP dy/dx = f(x, y), y(x0) = y0 using Euler's Method:
        y_{n+1} = y_n + h * f(x_n, y_n)
    """
    if isinstance(payload, dict):
        params = ODEInput(**payload)
    else:
        params = payload

    f = parse_two_var(params.f_expr, var1="x", var2="y")

    x0 = float(params.x0)
    y0 = float(params.y0)
    h = float(params.h)
    x_end = float(params.x_end)

    if abs(h) < 1e-12:
        raise ValueError("Step size h cannot be zero.")

    total_span = x_end - x0
    if total_span * h < 0:
        raise ValueError(f"Step size h={h} sign does not match direction from x0={x0} to x_end={x_end}.")

    n_steps = int(round(total_span / h))
    if n_steps < 1:
        raise ValueError(f"Target x_end={x_end} is too close to x0={x0} for step size h={h}.")
    if n_steps > 500:
        raise ValueError(f"Number of steps ({n_steps}) exceeds limit of 500. Please increase h or reduce interval.")

    inputs_echo = {
        "f_expr": params.f_expr,
        "x0": x0,
        "y0": y0,
        "h": h,
        "x_end": x_end,
        "n_steps": n_steps,
    }

    steps: List[Step] = []
    iterations_table: List[Dict[str, Any]] = []
    warnings: List[str] = []

    trajectory = [{"x": round(x0, 4), "y": round(y0, 6)}]
    x_curr = x0
    y_curr = y0

    for i in range(n_steps):
        f_val = f(x_curr, y_curr)
        y_next = y_curr + h * f_val
        x_next = x0 + (i + 1) * h  # exact grid point avoiding roundoff accumulation

        sub_str = (
            f"y_{{{i+1}}} = {y_curr:.6f} + ({h:.4f}) \\times f({x_curr:.4f}, {y_curr:.6f}) = "
            f"{y_curr:.6f} + ({h:.4f}) \\times ({f_val:.6f}) = {y_next:.6f}"
        )
        desc = (
            f"At node x_{{{i}}} = {x_curr:.4f}, slope dy/dx = f({x_curr:.4f}, {y_curr:.6f}) = {f_val:.6f}. "
            f"Stepping forward to x_{{{i+1}}} = {x_next:.4f} gives y_{{{i+1}}} = {y_next:.6f}."
        )

        steps.append(
            Step(
                step_number=i + 1,
                title=f"Step {i + 1}: x = {x_curr:.4f} → {x_next:.4f}",
                description=desc,
                formula="y_{n+1} = y_n + h \\cdot f(x_n, y_n)",
                substitution=sub_str,
                value=round(y_next, 6),
            )
        )

        iterations_table.append(
            {
                "step": i + 1,
                "x_n": round(x_curr, 4),
                "y_n": round(y_curr, 6),
                "slope_f_xy": round(f_val, 6),
                "x_next": round(x_next, 4),
                "y_next": round(y_next, 6),
            }
        )

        x_curr = x_next
        y_curr = y_next
        trajectory.append({"x": round(x_curr, 4), "y": round(y_curr, 6)})

    plot_data = {
        "type": "line",
        "series": [
            {
                "name": "Euler Approximation",
                "data": trajectory,
            }
        ],
    }

    result = {
        "final_x": round(x_curr, 4),
        "final_y": round(y_curr, 6),
        "steps_count": n_steps,
        "h": h,
    }

    result_summary = (
        f"Euler's Method: y({x_curr:.4f}) ≈ {y_curr:.6f} across {n_steps} steps (h = {h})"
    )

    return SolveResponse(
        topic_id="euler_method",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=result_summary,
        iterations_table=iterations_table,
        plot_data=plot_data,
        warnings=warnings,
    )
