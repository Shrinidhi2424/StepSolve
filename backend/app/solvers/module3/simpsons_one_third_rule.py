import numpy as np
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from fastapi import HTTPException, status

from app.core.models import Step, SolveResponse
from app.core.expr_eval import parse_single_var


class SimpsonsInput(BaseModel):
    f_expr: Optional[str] = Field(default="1 / (1 + x**2)", description="Integrand function f(x)")
    points: Optional[List[List[float]]] = Field(default=None, description="Optional tabulated data points [x, y]")
    a: float = Field(default=0.0, description="Lower integration limit a")
    b: float = Field(default=1.0, description="Upper integration limit b")
    n: int = Field(default=6, description="Number of subintervals n (must be an even integer)")


def solve(payload: Union[Dict[str, Any], SimpsonsInput]) -> SolveResponse:
    """
    Computes definite integral using Composite Simpson's 1/3 Rule:
        I ≈ (h/3) * [ y_0 + 4 * sum(y_odd) + 2 * sum(y_even) + y_n ]
    Requires an even number of subintervals (n % 2 == 0).
    """
    if isinstance(payload, dict):
        params = SimpsonsInput(**payload)
    else:
        params = payload

    steps: List[Step] = []
    warnings: List[str] = []
    iterations_table: List[Dict[str, Any]] = []

    # Case 1: Tabulated data mode
    if params.points is not None and len(params.points) >= 3:
        pts = sorted(params.points, key=lambda p: float(p[0]))
        n = len(pts) - 1
        if n % 2 != 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Simpson's 1/3 rule requires an even number of subintervals. Tabulated data has {len(pts)} points ({n} subintervals).",
            )
        a = float(pts[0][0])
        b = float(pts[-1][0])
        h = (b - a) / n
        xs = [float(p[0]) for p in pts]
        ys = [float(p[1]) for p in pts]
        f_callable = None
    # Case 2: Function expression mode
    else:
        if not params.f_expr:
            raise ValueError("Either a function expression f(x) or tabulated points must be provided.")
        a = float(params.a)
        b = float(params.b)
        n = int(params.n)

        # Validate even parity
        if n % 2 != 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Simpson's 1/3 rule requires an even number of subintervals; got n = {n}. Try n = {n - 1} or n = {n + 1}.",
            )
        if n < 2:
            raise ValueError(f"Number of subintervals n must be at least 2; got n = {n}.")
        if abs(b - a) < 1e-12:
            raise ValueError("Lower limit a and upper limit b cannot be identical.")

        h = (b - a) / n
        f_callable = parse_single_var(params.f_expr, var="x")
        xs = [a + i * h for i in range(n + 1)]
        ys = [f_callable(x) for x in xs]

    inputs_echo = {
        "f_expr": params.f_expr,
        "a": a,
        "b": b,
        "n": n,
        "h": round(h, 6),
    }

    # Step 1: Subinterval width & Parity Validation
    steps.append(
        Step(
            step_number=1,
            title="Step Size Determination & Parity Validation",
            description=f"Verified n = {n} is an even integer. Computed strip width h = (b - a) / n = {h:.6f}.",
            formula="h = \\frac{b - a}{n}, \\quad n \\pmod 2 = 0",
            substitution=f"h = \\frac{{{b:.4f} - ({a:.4f})}}{{{n}}} = {h:.6f} \\quad (\\text{{even}} \\checkmark)",
            value=round(h, 6),
        )
    )

    # Step 2: Mesh Nodes Evaluation
    eval_summary = "; ".join([f"f({xs[i]:.4f}) = {ys[i]:.6f}" for i in range(min(5, n + 1))])
    if n + 1 > 5:
        eval_summary += f" ... (+{n + 1 - 5} more)"

    steps.append(
        Step(
            step_number=2,
            title=f"Function Evaluation at {n + 1} Nodes",
            description="Evaluated integrand at each node across the integration interval.",
            formula="y_i = f(x_i), \\quad i = 0, \\dots, n",
            substitution=eval_summary,
            value=[[round(xs[i], 4), round(ys[i], 6)] for i in range(n + 1)],
        )
    )

    # Step 3: Odd/Even Node Classification
    y_endpoints = ys[0] + ys[n]
    odd_indices = [i for i in range(1, n) if i % 2 != 0]
    even_indices = [i for i in range(1, n) if i % 2 == 0]

    sum_odd = sum(ys[i] for i in odd_indices)
    sum_even = sum(ys[i] for i in even_indices)

    classification_desc = (
        f"Endpoints (y_0, y_{{{n}}}) carry coefficient 1. "
        f"Odd interior nodes ({len(odd_indices)} nodes) carry coefficient 4 (parabolic apex). "
        f"Even interior nodes ({len(even_indices)} nodes) carry coefficient 2 (parabolic interface)."
    )

    classification_sub = (
        f"Endpoints: y_0 + y_{{{n}}} = {ys[0]:.6f} + {ys[n]:.6f} = {y_endpoints:.6f} ; "
        f"4 \\times \\Sigma_{{\\text{{odd}}}} = 4 \\times ({sum_odd:.6f}) = {4 * sum_odd:.6f} ; "
        f"2 \\times \\Sigma_{{\\text{{even}}}} = 2 \\times ({sum_even:.6f}) = {2 * sum_even:.6f}"
    )

    steps.append(
        Step(
            step_number=3,
            title="Classification into Odd and Even Weighted Groups",
            description=classification_desc,
            formula="\\Sigma_0 = y_0 + y_n, \\quad \\Sigma_1 = 4 \\sum_{i \\text{ odd}} y_i, \\quad \\Sigma_2 = 2 \\sum_{i \\text{ even}} y_i",
            substitution=classification_sub,
            value={
                "endpoints_sum": round(y_endpoints, 6),
                "odd_sum": round(sum_odd, 6),
                "even_sum": round(sum_even, 6),
            },
        )
    )

    # Build iteration table
    for i in range(n + 1):
        if i in (0, n):
            coeff = 1
        elif i % 2 != 0:
            coeff = 4
        else:
            coeff = 2

        weighted_val = coeff * ys[i]
        iterations_table.append(
            {
                "i": i,
                "x_i": round(xs[i], 6),
                "f_x_i": round(ys[i], 6),
                "coefficient": coeff,
                "weighted_value": round(weighted_val, 6),
            }
        )

    # Step 4: Final Simpson's 1/3 Formula Evaluation
    integral_val = (h / 3.0) * (y_endpoints + 4.0 * sum_odd + 2.0 * sum_even)

    sub_integral = (
        f"I \\approx \\frac{{{h:.6f}}}{{3}} \\left[ ({y_endpoints:.6f}) + "
        f"4 \\times ({sum_odd:.6f}) + 2 \\times ({sum_even:.6f}) \\right] = {integral_val:.6f}"
    )

    steps.append(
        Step(
            step_number=4,
            title="Composite Simpson's 1/3 Rule Computation",
            description="Applied Simpson's 1/3 quadratic formula to compute high-accuracy approximation.",
            formula="I = \\frac{h}{3} \\left[ y_0 + y_n + 4 \\sum_{i \\text{ odd}} y_i + 2 \\sum_{i \\text{ even}} y_i \\right]",
            substitution=sub_integral,
            value=round(integral_val, 6),
        )
    )

    # Plot data: curve + sample nodes
    plot_data = None
    try:
        if f_callable is not None:
            curve_x = np.linspace(a, b, 100)
            curve_pts = []
            for cx in curve_x:
                try:
                    curve_pts.append({"x": round(float(cx), 4), "y": round(float(f_callable(cx)), 4)})
                except Exception:
                    pass
        else:
            curve_pts = [{"x": round(xs[i], 4), "y": round(ys[i], 4)} for i in range(n + 1)]

        plot_data = {
            "type": "scatter_line",
            "line": curve_pts,
            "scatter": [{"x": round(xs[i], 4), "y": round(ys[i], 4)} for i in range(n + 1)],
        }
    except Exception:
        plot_data = None

    result = {
        "integral": round(integral_val, 6),
        "h": round(h, 6),
        "n": n,
        "a": round(a, 4),
        "b": round(b, 4),
    }

    result_summary = (
        f"Simpson's 1/3 Rule: ∫ f(x) dx on [{a:.4f}, {b:.4f}] ≈ {integral_val:.6f} "
        f"(n = {n} subintervals, h = {h:.4f})"
    )

    return SolveResponse(
        topic_id="simpsons_one_third_rule",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=result_summary,
        iterations_table=iterations_table,
        plot_data=plot_data,
        warnings=warnings,
    )
