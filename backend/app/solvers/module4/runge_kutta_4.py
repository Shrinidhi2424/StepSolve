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
    Solves first-order IVP dy/dx = f(x, y), y(x0) = y0 using Runge-Kutta 4th Order (RK4):
        k1 = h * f(x_n, y_n)
        k2 = h * f(x_n + h/2, y_n + k1/2)
        k3 = h * f(x_n + h/2, y_n + k2/2)
        k4 = h * f(x_n + h, y_n + k3)
        y_{n+1} = y_n + (1/6) * (k1 + 2k2 + 2k3 + k4)
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
        x_next = x0 + (i + 1) * h
        x_mid = x_curr + 0.5 * h

        # k1
        f_k1 = f(x_curr, y_curr)
        k1 = h * f_k1

        k1_sub = (
            f"k_1 = ({h:.4f}) \\times f({x_curr:.4f}, {y_curr:.6f}) = "
            f"({h:.4f}) \\times ({f_k1:.6f}) = {k1:.6f}"
        )
        steps.append(
            Step(
                step_number=5 * i + 1,
                title=f"Step {i + 1}.1: Compute slope k₁ at x = {x_curr:.4f}",
                description=f"Initial slope increment at node (x_{{{i}}}, y_{{{i}}}) = ({x_curr:.4f}, {y_curr:.6f}).",
                formula="k_1 = h \\cdot f(x_n, y_n)",
                substitution=k1_sub,
                value=round(k1, 6),
            )
        )

        # k2
        y_k1 = y_curr + 0.5 * k1
        f_k2 = f(x_mid, y_k1)
        k2 = h * f_k2

        k2_sub = (
            f"k_2 = ({h:.4f}) \\times f\\left({x_curr:.4f} + \\frac{{{h:.4f}}}{{2}}, {y_curr:.6f} + \\frac{{{k1:.6f}}}{{2}}\\right) = "
            f"({h:.4f}) \\times f({x_mid:.4f}, {y_k1:.6f}) = ({h:.4f}) \\times ({f_k2:.6f}) = {k2:.6f}"
        )
        steps.append(
            Step(
                step_number=5 * i + 2,
                title=f"Step {i + 1}.2: Compute midpoint slope k₂ at x = {x_mid:.4f}",
                description=f"Midpoint slope estimated using half-step advance from k₁: ({x_mid:.4f}, {y_k1:.6f}).",
                formula="k_2 = h \\cdot f\\left(x_n + \\frac{h}{2}, y_n + \\frac{k_1}{2}\\right)",
                substitution=k2_sub,
                value=round(k2, 6),
            )
        )

        # k3
        y_k2 = y_curr + 0.5 * k2
        f_k3 = f(x_mid, y_k2)
        k3 = h * f_k3

        k3_sub = (
            f"k_3 = ({h:.4f}) \\times f\\left({x_curr:.4f} + \\frac{{{h:.4f}}}{{2}}, {y_curr:.6f} + \\frac{{{k2:.6f}}}{{2}}\\right) = "
            f"({h:.4f}) \\times f({x_mid:.4f}, {y_k2:.6f}) = ({h:.4f}) \\times ({f_k3:.6f}) = {k3:.6f}"
        )
        steps.append(
            Step(
                step_number=5 * i + 3,
                title=f"Step {i + 1}.3: Compute refined midpoint slope k₃ at x = {x_mid:.4f}",
                description=f"Refined midpoint slope estimated using half-step advance from k₂: ({x_mid:.4f}, {y_k2:.6f}).",
                formula="k_3 = h \\cdot f\\left(x_n + \\frac{h}{2}, y_n + \\frac{k_2}{2}\\right)",
                substitution=k3_sub,
                value=round(k3, 6),
            )
        )

        # k4
        y_k3 = y_curr + k3
        f_k4 = f(x_next, y_k3)
        k4 = h * f_k4

        k4_sub = (
            f"k_4 = ({h:.4f}) \\times f\\left({x_curr:.4f} + {h:.4f}, {y_curr:.6f} + {k3:.6f}\\right) = "
            f"({h:.4f}) \\times f({x_next:.4f}, {y_k3:.6f}) = ({h:.4f}) \\times ({f_k4:.6f}) = {k4:.6f}"
        )
        steps.append(
            Step(
                step_number=5 * i + 4,
                title=f"Step {i + 1}.4: Compute full-step slope k₄ at x = {x_next:.4f}",
                description=f"Endpoint slope estimated using full-step advance from k₃: ({x_next:.4f}, {y_k3:.6f}).",
                formula="k_4 = h \\cdot f(x_n + h, y_n + k_3)",
                substitution=k4_sub,
                value=round(k4, 6),
            )
        )

        # Weighted combination
        delta_y = (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        y_next = y_curr + delta_y

        update_sub = (
            f"y_{{{i+1}}} = {y_curr:.6f} + \\frac{1}{6}\\left[{k1:.6f} + 2({k2:.6f}) + 2({k3:.6f}) + {k4:.6f}\\right] = "
            f"{y_curr:.6f} + {delta_y:.6f} = {y_next:.6f}"
        )
        steps.append(
            Step(
                step_number=5 * i + 5,
                title=f"Step {i + 1}.5: Update y to x_{{{i+1}}} = {x_next:.4f}",
                description=f"Weighted Simpson-type average of slopes yields displacement Δy = {delta_y:.6f}. New value y({x_next:.4f}) = {y_next:.6f}.",
                formula="y_{n+1} = y_n + \\frac{1}{6}\\left(k_1 + 2k_2 + 2k_3 + k_4\\right)",
                substitution=update_sub,
                value=round(y_next, 6),
            )
        )

        iterations_table.append(
            {
                "step": i + 1,
                "x_n": round(x_curr, 4),
                "y_n": round(y_curr, 6),
                "k1": round(k1, 6),
                "k2": round(k2, 6),
                "k3": round(k3, 6),
                "k4": round(k4, 6),
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
                "name": "Runge-Kutta 4th Order",
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
        f"Runge-Kutta 4th Order: y({x_curr:.4f}) ≈ {y_curr:.6f} across {n_steps} steps (h = {h})"
    )

    return SolveResponse(
        topic_id="runge_kutta_4",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=result_summary,
        iterations_table=iterations_table,
        plot_data=plot_data,
        warnings=warnings,
    )
