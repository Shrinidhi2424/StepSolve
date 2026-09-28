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
    Solves first-order IVP dy/dx = f(x, y), y(x0) = y0 using Modified Euler's (Heun's) Method:
        Predictor: y^*_{n+1} = y_n + h * f(x_n, y_n)
        Corrector: y_{n+1} = y_n + (h/2) * [f(x_n, y_n) + f(x_{n+1}, y^*_{n+1})]
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
        f_curr = f(x_curr, y_curr)

        # Predictor (Euler)
        y_pred = y_curr + h * f_curr

        pred_sub = (
            f"y^*_{{{i+1}}} = {y_curr:.6f} + ({h:.4f}) \\times f({x_curr:.4f}, {y_curr:.6f}) = "
            f"{y_curr:.6f} + ({h:.4f}) \\times ({f_curr:.6f}) = {y_pred:.6f}"
        )
        pred_desc = (
            f"Predictor step for interval [x_{{{i}}}, x_{{{i+1}}}] = [{x_curr:.4f}, {x_next:.4f}]. "
            f"Using initial slope f({x_curr:.4f}, {y_curr:.6f}) = {f_curr:.6f}, "
            f"the predicted value is y^*_{{{i+1}}} = {y_pred:.6f}."
        )

        steps.append(
            Step(
                step_number=2 * i + 1,
                title=f"Step {i + 1}a: Predictor (Euler estimate for x = {x_next:.4f})",
                description=pred_desc,
                formula="y^*_{n+1} = y_n + h \\cdot f(x_n, y_n)",
                substitution=pred_sub,
                value=round(y_pred, 6),
            )
        )

        # Slope at predicted end point
        f_pred = f(x_next, y_pred)

        # Corrector (Average slope)
        avg_slope = 0.5 * (f_curr + f_pred)
        y_corr = y_curr + h * avg_slope

        corr_sub = (
            f"y_{{{i+1}}} = {y_curr:.6f} + \\frac{{{h:.4f}}}{{2}} \\left[{f_curr:.6f} + f({x_next:.4f}, {y_pred:.6f})\\right] = "
            f"{y_curr:.6f} + \\frac{{{h:.4f}}}{{2}} \\left[{f_curr:.6f} + {f_pred:.6f}\\right] = {y_corr:.6f}"
        )
        corr_desc = (
            f"Corrector step: evaluate derivative at predicted state f({x_next:.4f}, {y_pred:.6f}) = {f_pred:.6f}. "
            f"Averaging slopes gives {(avg_slope):.6f}. Corrected value is y_{{{i+1}}} = {y_corr:.6f}."
        )

        steps.append(
            Step(
                step_number=2 * i + 2,
                title=f"Step {i + 1}b: Corrector (Average slope for x = {x_next:.4f})",
                description=corr_desc,
                formula="y_{n+1} = y_n + \\frac{h}{2}\\left[f(x_n, y_n) + f(x_{n+1}, y^*_{n+1})\\right]",
                substitution=corr_sub,
                value=round(y_corr, 6),
            )
        )

        iterations_table.append(
            {
                "step": i + 1,
                "x_n": round(x_curr, 4),
                "y_n": round(y_curr, 6),
                "f_xn_yn": round(f_curr, 6),
                "y_predicted": round(y_pred, 6),
                "f_next_predicted": round(f_pred, 6),
                "y_corrected": round(y_corr, 6),
            }
        )

        x_curr = x_next
        y_curr = y_corr
        trajectory.append({"x": round(x_curr, 4), "y": round(y_curr, 6)})

    plot_data = {
        "type": "line",
        "series": [
            {
                "name": "Modified Euler (Heun)",
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
        f"Modified Euler's (Heun's) Method: y({x_curr:.4f}) ≈ {y_curr:.6f} across {n_steps} steps (h = {h})"
    )

    return SolveResponse(
        topic_id="modified_euler_method",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=result_summary,
        iterations_table=iterations_table,
        plot_data=plot_data,
        warnings=warnings,
    )
