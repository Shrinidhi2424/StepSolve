import numpy as np
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from app.core.models import Step, SolveResponse
from app.core.expr_eval import parse_single_var


class TrapezoidalInput(BaseModel):
    f_expr: Optional[str] = Field(default="1 / (1 + x**2)", description="Integrand function f(x)")
    points: Optional[List[List[float]]] = Field(default=None, description="Optional tabulated data points [x, y]")
    a: float = Field(default=0.0, description="Lower integration limit a")
    b: float = Field(default=1.0, description="Upper integration limit b")
    n: int = Field(default=6, description="Number of subintervals n")


def solve(payload: Union[Dict[str, Any], TrapezoidalInput]) -> SolveResponse:
    """
    Computes definite integral using the Composite Trapezoidal Rule:
        I ≈ (h/2) * [ f(x_0) + 2 * sum_{i=1}^{n-1} f(x_i) + f(x_n) ]
    Supports both functional expressions f(x) and tabulated data.
    """
    if isinstance(payload, dict):
        params = TrapezoidalInput(**payload)
    else:
        params = payload

    steps: List[Step] = []
    warnings: List[str] = []
    iterations_table: List[Dict[str, Any]] = []

    # Case 1: Tabulated data mode
    if params.points is not None and len(params.points) >= 2:
        pts = sorted(params.points, key=lambda p: float(p[0]))
        n = len(pts) - 1
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
        if n < 1:
            raise ValueError(f"Number of subintervals n must be at least 1; got n = {n}.")
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

    # Step 1: Subinterval width
    steps.append(
        Step(
            step_number=1,
            title="Step Size Determination",
            description=f"Calculated subinterval width h for [{a:.4f}, {b:.4f}] divided into n = {n} strips.",
            formula="h = \\frac{b - a}{n}",
            substitution=f"h = \\frac{{{b:.4f} - ({a:.4f})}}{{{n}}} = {h:.6f}",
            value=round(h, 6),
        )
    )

    # Step 2: Nodes and function evaluation
    eval_summary = "; ".join([f"f({xs[i]:.4f}) = {ys[i]:.6f}" for i in range(min(5, n + 1))])
    if n + 1 > 5:
        eval_summary += f" ... (+{n + 1 - 5} more)"

    steps.append(
        Step(
            step_number=2,
            title=f"Function Evaluation at {n + 1} Mesh Nodes",
            description="Evaluated integrand at each equidistant node x_i = a + i*h.",
            formula="y_i = f(x_i) = f(a + i \\cdot h)",
            substitution=eval_summary,
            value=[[round(xs[i], 4), round(ys[i], 6)] for i in range(n + 1)],
        )
    )

    # Step 3: Classification of endpoints vs interior nodes
    endpoint_sum = ys[0] + ys[n]
    interior_sum = sum(ys[1:n]) if n > 1 else 0.0

    steps.append(
        Step(
            step_number=3,
            title="Classification of Endpoints and Interior Points",
            description="Multiplied interior nodes by weight 2 and boundary endpoints by weight 1.",
            formula="\\text{Endpoints} = y_0 + y_n ; \\quad \\text{Interior} = 2 \\sum_{i=1}^{n-1} y_i",
            substitution=(
                f"y_0 = {ys[0]:.6f}, y_{{{n}}} = {ys[n]:.6f} \\implies \\text{{Sum}} = {endpoint_sum:.6f} ; "
                f"\\Sigma_{{\\text{{interior}}}} = {interior_sum:.6f} \\implies 2 \\times \\Sigma = {2 * interior_sum:.6f}"
            ),
            value={"endpoint_sum": round(endpoint_sum, 6), "interior_sum": round(interior_sum, 6)},
        )
    )

    # Build iteration table
    for i in range(n + 1):
        weight = 1 if i in (0, n) else 2
        weighted_val = weight * ys[i]
        iterations_table.append(
            {
                "i": i,
                "x_i": round(xs[i], 6),
                "f_x_i": round(ys[i], 6),
                "weight": weight,
                "weighted_value": round(weighted_val, 6),
            }
        )

    # Step 4: Composite Trapezoidal Rule Formula
    integral_val = (h / 2.0) * (endpoint_sum + 2.0 * interior_sum)

    sub_formula = (
        f"I \\approx \\frac{{{h:.6f}}}{{2}} \\left[ ({ys[0]:.6f} + {ys[n]:.6f}) + "
        f"2 \\times ({interior_sum:.6f}) \\right] = {integral_val:.6f}"
    )

    steps.append(
        Step(
            step_number=4,
            title="Composite Trapezoidal Rule Application",
            description="Applied composite quadrature formula to compute final approximation.",
            formula="I = \\frac{h}{2} \\left[ y_0 + y_n + 2 \\sum_{i=1}^{n-1} y_i \\right]",
            substitution=sub_formula,
            value=round(integral_val, 6),
        )
    )

    # Plot data: function curve + trapezoid vertices
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
        f"Trapezoidal Rule: ∫ f(x) dx on [{a:.4f}, {b:.4f}] ≈ {integral_val:.6f} "
        f"(n = {n} subintervals, h = {h:.4f})"
    )

    return SolveResponse(
        topic_id="trapezoidal_rule",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=result_summary,
        iterations_table=iterations_table,
        plot_data=plot_data,
        warnings=warnings,
    )
