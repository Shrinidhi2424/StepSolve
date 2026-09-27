import numpy as np
from typing import Any, Dict, List, Union
from pydantic import BaseModel, Field

from app.core.models import Step, SolveResponse


class LagrangeInput(BaseModel):
    points: List[List[float]] = Field(
        default=[[0.0, 1.0], [1.0, 3.0], [2.0, 7.0], [4.0, 21.0]],
        description="Data points as list of [x, y] coordinates",
    )
    target_x: float = Field(default=2.5, description="Target value of x to evaluate P(x)")
    inverse: Union[int, bool] = Field(default=0, description="1/True for inverse interpolation x(y), 0/False for standard y(x)")


def solve(payload: Union[Dict[str, Any], LagrangeInput]) -> SolveResponse:
    """
    Computes Lagrange Polynomial Interpolation for equal or unequal intervals:
        P(x) = sum(y_i * L_i(x)) where L_i(x) = prod_{j != i} (x - x_j) / (x_i - x_j)
    Supports inverse interpolation by swapping roles of x and y.
    """
    if isinstance(payload, dict):
        params = LagrangeInput(**payload)
    else:
        params = payload

    is_inverse = bool(params.inverse)
    raw_points = params.points

    if len(raw_points) < 2:
        raise ValueError("At least 2 data points are required for Lagrange interpolation.")

    # Swap coordinates if inverse interpolation requested
    if is_inverse:
        pts = [[float(p[1]), float(p[0])] for p in raw_points]
        var_indep = "y"
        var_dep = "x"
    else:
        pts = [[float(p[0]), float(p[1])] for p in raw_points]
        var_indep = "x"
        var_dep = "y"

    target = float(params.target_x)
    n = len(pts)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]

    # Validate distinct abscissas
    if len(set(xs)) != n:
        raise ValueError(f"Duplicate {var_indep}-coordinates detected. Abscissas must be strictly distinct.")

    inputs_echo = {
        "points": raw_points,
        "target": target,
        "is_inverse": is_inverse,
        "points_count": n,
    }

    steps: List[Step] = []
    warnings: List[str] = []
    iterations_table: List[Dict[str, Any]] = []

    basis_values: List[float] = []
    terms: List[float] = []

    # Compute each Lagrange basis polynomial L_i(target)
    for i in range(n):
        num_factors = []
        den_factors = []
        num_val = 1.0
        den_val = 1.0

        for j in range(n):
            if i != j:
                diff_num = target - xs[j]
                diff_den = xs[i] - xs[j]
                num_val *= diff_num
                den_val *= diff_den
                num_factors.append(f"({target:.4f} - {xs[j]:.4f})")
                den_factors.append(f"({xs[i]:.4f} - {xs[j]:.4f})")

        L_i = num_val / den_val if abs(den_val) > 1e-14 else 0.0
        basis_values.append(L_i)
        term_val = ys[i] * L_i
        terms.append(term_val)

        formula_str = f"L_{{{i}}}({var_indep}) = \\prod_{{j \\neq {i}}} \\frac{{{var_indep} - {var_indep}_j}}{{{var_indep}_{{{i}}} - {var_indep}_j}}"
        sub_str = f"L_{{{i}}}({target:.4f}) = \\frac{{{' \\times '.join(num_factors)}}}{{{' \\times '.join(den_factors)}}} = \\frac{{{num_val:.6f}}}{{{den_val:.6f}}} = {L_i:.6f}"
        desc = (
            f"Computed basis polynomial L_{{{i}}}({target:.4f}) = {L_i:.6f}. "
            f"Weighted contribution to {var_dep}({target:.4f}) = {ys[i]:.4f} × {L_i:.6f} = {term_val:.6f}."
        )

        steps.append(
            Step(
                step_number=i + 1,
                title=f"Basis Polynomial L_{{{i}}}({var_indep})",
                description=desc,
                formula=formula_str,
                substitution=sub_str,
                value=round(L_i, 6),
            )
        )

        iterations_table.append(
            {
                "i": i,
                f"{var_indep}_i": round(xs[i], 6),
                f"{var_dep}_i": round(ys[i], 6),
                f"L_{i}": round(L_i, 6),
                f"term_{var_dep}i_Li": round(term_val, 6),
            }
        )

    # Sum of all weighted basis polynomials
    interpolated_val = sum(terms)

    steps.append(
        Step(
            step_number=n + 1,
            title=f"Total Interpolated Value {var_dep}({target:.4f})",
            description=f"Summed all {n} weighted basis terms to obtain final interpolated value.",
            formula=f"P_{{{n-1}}}({var_indep}) = \\sum_{{i=0}}^{{{n-1}}} {var_dep}_i L_i({var_indep})",
            substitution=f"P({target:.4f}) = " + " + ".join([f"({t:.6f})" for t in terms]) + f" = {interpolated_val:.6f}",
            value=round(interpolated_val, 6),
        )
    )

    # Dense curve generation for plot
    plot_data = None
    try:
        x_min = min(xs) - 0.5
        x_max = max(xs) + 0.5
        x_samples = np.linspace(x_min, x_max, 100)

        curve_pts = []
        for x_eval in x_samples:
            y_eval = 0.0
            for i in range(n):
                li = 1.0
                for j in range(n):
                    if i != j:
                        li *= (x_eval - xs[j]) / (xs[i] - xs[j])
                y_eval += ys[i] * li
            curve_pts.append({"x": round(float(x_eval), 4), "y": round(float(y_eval), 4)})

        plot_data = {
            "type": "scatter_line",
            "line": curve_pts,
            "scatter": [{"x": round(xs[k], 4), "y": round(ys[k], 4)} for k in range(n)],
            "highlighted": [{"x": round(target, 4), "y": round(interpolated_val, 4)}],
        }
    except Exception:
        plot_data = None

    result = {
        "interpolated_value": round(interpolated_val, 6),
        "target": target,
        "is_inverse": is_inverse,
        "basis_values": [round(v, 6) for v in basis_values],
        "degree": n - 1,
    }

    mode_label = "Inverse" if is_inverse else "Standard"
    result_summary = (
        f"{mode_label} Lagrange Interpolation: {var_dep}({target:.4f}) ≈ {interpolated_val:.6f} "
        f"(degree {n - 1} polynomial across {n} points)"
    )

    return SolveResponse(
        topic_id="lagrange_interpolation",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=result_summary,
        iterations_table=iterations_table,
        plot_data=plot_data,
        warnings=warnings,
    )
