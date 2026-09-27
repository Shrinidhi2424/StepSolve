import numpy as np
from typing import Any, Dict, List, Union
from pydantic import BaseModel, Field

from app.core.models import Step, SolveResponse


class LeastSquaresInput(BaseModel):
    points: List[List[float]] = Field(
        default=[[1.0, 2.1], [2.0, 3.9], [3.0, 6.2], [4.0, 8.1], [5.0, 9.8]],
        description="Observed data points [x_i, y_i]",
    )


def solve(payload: Union[Dict[str, Any], LeastSquaresInput]) -> SolveResponse:
    """
    Fits a linear regression model y = a + bx using the Method of Least Squares.
    Solves the 2x2 normal equations and computes R^2 goodness of fit.
    """
    if isinstance(payload, dict):
        params = LeastSquaresInput(**payload)
    else:
        params = payload

    raw_points = params.points
    if len(raw_points) < 2:
        raise ValueError("At least 2 data points are required for linear regression fitting.")

    xs = [float(p[0]) for p in raw_points]
    ys = [float(p[1]) for p in raw_points]
    n = len(xs)

    inputs_echo = {
        "points": raw_points,
        "n": n,
    }

    steps: List[Step] = []
    warnings: List[str] = []
    iterations_table: List[Dict[str, Any]] = []

    # Step 1: Compute summations
    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_xx = sum(x * x for x in xs)
    sum_xy = sum(x * y for x, y in zip(xs, ys))
    sum_yy = sum(y * y for y in ys)

    steps.append(
        Step(
            step_number=1,
            title="Statistical Summations",
            description=f"Calculated necessary summation quantities for n = {n} data points.",
            formula="\\Sigma x, \\Sigma y, \\Sigma x^2, \\Sigma xy",
            substitution=(
                f"n = {n}; "
                f"\\Sigma x = {sum_x:.4f}; "
                f"\\Sigma y = {sum_y:.4f}; "
                f"\\Sigma x^2 = {sum_xx:.4f}; "
                f"\\Sigma xy = {sum_xy:.4f}"
            ),
            value={
                "n": n,
                "sum_x": round(sum_x, 4),
                "sum_y": round(sum_y, 4),
                "sum_xx": round(sum_xx, 4),
                "sum_xy": round(sum_xy, 4),
            },
        )
    )

    # Step 2: Formulate normal equations
    denom = n * sum_xx - (sum_x ** 2)

    steps.append(
        Step(
            step_number=2,
            title="Normal Equations System",
            description="Constructed 2×2 linear system of normal equations minimizing squared error.",
            formula=(
                "\\begin{cases} "
                "n \\cdot a + (\\Sigma x) b = \\Sigma y \\\\ "
                "(\\Sigma x) a + (\\Sigma x^2) b = \\Sigma xy "
                "\\end{cases}"
            ),
            substitution=(
                f"[{n} a + ({sum_x:.4f}) b = {sum_y:.4f}] ; "
                f"[({sum_x:.4f}) a + ({sum_xx:.4f}) b = {sum_xy:.4f}] ; "
                f"Determinant D = {denom:.4f}"
            ),
            value=[[n, round(sum_x, 4)], [round(sum_x, 4), round(sum_xx, 4)]],
        )
    )

    if abs(denom) < 1e-12:
        warnings.append("All x values are identical (vertical line). Slope b is mathematically undefined.")
        b = 0.0
        a = sum_y / n
        r_squared = 0.0
    else:
        # Step 3: Solve slope b
        b = (n * sum_xy - sum_x * sum_y) / denom
        sub_b = f"b = \\frac{{{n} \\times ({sum_xy:.4f}) - ({sum_x:.4f}) \\times ({sum_y:.4f})}}{{{denom:.4f}}} = {b:.6f}"
        steps.append(
            Step(
                step_number=3,
                title="Solve Slope Parameter b",
                description="Computed regression line slope b via normal equations determinant.",
                formula="b = \\frac{n \\Sigma xy - (\\Sigma x)(\\Sigma y)}{n \\Sigma x^2 - (\\Sigma x)^2}",
                substitution=sub_b,
                value=round(b, 6),
            )
        )

        # Step 4: Solve intercept a
        a = (sum_y - b * sum_x) / n
        sub_a = f"a = \\frac{{{sum_y:.4f} - ({b:.6f}) \\times ({sum_x:.4f})}}{{{n}}} = {a:.6f}"
        steps.append(
            Step(
                step_number=4,
                title="Solve Intercept Parameter a",
                description="Computed regression line intercept a using calculated slope.",
                formula="a = \\frac{\\Sigma y - b \\Sigma x}{n}",
                substitution=sub_a,
                value=round(a, 6),
            )
        )

        # Step 5: Compute R^2 goodness of fit
        y_mean = sum_y / n
        ss_tot = sum((y - y_mean) ** 2 for y in ys)
        ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
        r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-12 else 1.0
        r_squared = max(0.0, min(1.0, r_squared))  # bound between 0 and 1

        steps.append(
            Step(
                step_number=5,
                title="Goodness of Fit (Coefficient of Determination R²)",
                description="Evaluated quality of linear fit through total and residual sum of squares.",
                formula="R^2 = 1 - \\frac{SS_{res}}{SS_{tot}}",
                substitution=f"R^2 = 1 - \\frac{{{ss_res:.4f}}}{{{ss_tot:.4f}}} = {r_squared:.4f}",
                value=round(r_squared, 4),
            )
        )

    # Build iteration table with individual point residuals
    for i in range(n):
        y_pred = a + b * xs[i]
        residual = ys[i] - y_pred
        iterations_table.append(
            {
                "point": i + 1,
                "x_i": round(xs[i], 4),
                "y_i": round(ys[i], 4),
                "x_squared": round(xs[i] ** 2, 4),
                "xy": round(xs[i] * ys[i], 4),
                "y_predicted": round(y_pred, 4),
                "residual": round(residual, 4),
            }
        )

    # Plot data: scatter of points + fitted line
    plot_data = None
    try:
        x_min = min(xs) - 0.5
        x_max = max(xs) + 0.5
        line_pts = [
            {"x": round(x_min, 4), "y": round(a + b * x_min, 4)},
            {"x": round(x_max, 4), "y": round(a + b * x_max, 4)},
        ]
        plot_data = {
            "type": "scatter_line",
            "line": line_pts,
            "scatter": [{"x": round(xs[k], 4), "y": round(ys[k], 4)} for k in range(n)],
        }
    except Exception:
        plot_data = None

    sign_str = "+" if b >= 0 else "-"
    equation_str = f"y = {a:.4f} {sign_str} {abs(b):.4f}x"

    result = {
        "a": round(a, 6),
        "b": round(b, 6),
        "equation": equation_str,
        "r_squared": round(r_squared, 4),
        "n": n,
    }

    result_summary = f"Fitted Line: {equation_str} with R² = {r_squared:.4f} (n = {n})"

    return SolveResponse(
        topic_id="least_squares_fit",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=result_summary,
        iterations_table=iterations_table,
        plot_data=plot_data,
        warnings=warnings,
    )
