import numpy as np
from typing import Any, Dict, List, Union
from pydantic import BaseModel, Field

from app.core.models import Step, SolveResponse
from app.core.finite_differences import build_forward_difference_table


class NewtonForwardDiffInput(BaseModel):
    points: List[List[float]] = Field(
        default=[[10.0, 0.1736], [20.0, 0.3420], [30.0, 0.5000], [40.0, 0.6428]],
        description="Equally spaced data points [x_i, y_i]",
    )
    target_x: float = Field(default=10.0, description="Abscissa at which to compute derivative")
    order: int = Field(default=1, description="Derivative order: 1 for dy/dx, 2 for d²y/dx²")


def solve(payload: Union[Dict[str, Any], NewtonForwardDiffInput]) -> SolveResponse:
    """
    Computes numerical derivatives using Newton's Forward Difference formula from tabulated data.
    Supports 1st and 2nd derivatives at any point x = x0 + p*h.
    """
    if isinstance(payload, dict):
        params = NewtonForwardDiffInput(**payload)
    else:
        params = payload

    raw_points = params.points
    if len(raw_points) < 3:
        raise ValueError("At least 3 equally spaced data points are required.")

    # Sort points by x
    sorted_pts = sorted(raw_points, key=lambda p: float(p[0]))
    xs = [float(p[0]) for p in sorted_pts]
    ys = [float(p[1]) for p in sorted_pts]
    n = len(xs)
    target = float(params.target_x)
    order = int(params.order)
    if order not in (1, 2):
        raise ValueError("Derivative order must be 1 (dy/dx) or 2 (d²y/dx²).")

    # Verify spacing h
    diffs = [xs[i + 1] - xs[i] for i in range(n - 1)]
    h = diffs[0]
    warnings: List[str] = []

    for idx, d in enumerate(diffs):
        if abs(d - h) > 1e-4:
            warnings.append(
                f"Points may not be strictly equally spaced: interval {idx} step is {d:.4f} vs expected {h:.4f}."
            )

    inputs_echo = {
        "points": sorted_pts,
        "target_x": target,
        "order": order,
        "h": round(h, 6),
    }

    # Build forward difference table
    diff_table = build_forward_difference_table(ys)

    steps: List[Step] = []

    # Step 1: Step size validation
    steps.append(
        Step(
            step_number=1,
            title="Step Size Determination",
            description=f"Verified tabulated data interval: h = x_1 - x_0 = {h:.4f}.",
            formula="h = x_{i+1} - x_i",
            substitution=f"h = {xs[1]:.4f} - {xs[0]:.4f} = {h:.4f}",
            value=round(h, 6),
        )
    )

    # Step 2: Forward Difference Table
    formatted_table = []
    for r in range(n):
        row_vals = []
        for c in range(n - r):
            val = diff_table[r][c]
            row_vals.append(round(val, 6) if val is not None else None)
        formatted_table.append(row_vals)

    steps.append(
        Step(
            step_number=2,
            title="Forward Difference Table Construction",
            description="Constructed table of differences: Δ^j y_i = Δ^{j-1} y_{i+1} - Δ^{j-1} y_i.",
            formula="\\Delta^j y_i = \\Delta^{j-1} y_{i+1} - \\Delta^{j-1} y_i",
            substitution=None,
            value=formatted_table,
        )
    )

    # Find closest node x_0 for forward series (usually first node or closest preceding node)
    base_idx = 0
    for i in range(n - 1):
        if xs[i] <= target <= xs[i + 1]:
            base_idx = i
            break

    x0 = xs[base_idx]
    y0 = ys[base_idx]
    p = (target - x0) / h

    steps.append(
        Step(
            step_number=3,
            title=f"Normalized Variable p (relative to base x_0 = {x0:.4f})",
            description=f"Computed dimensionless offset p = (x - x_0) / h.",
            formula="p = \\frac{x - x_0}{h}",
            substitution=f"p = \\frac{{{target:.4f} - {x0:.4f}}}{{{h:.4f}}} = {p:.6f}",
            value=round(p, 6),
        )
    )

    # Available differences starting at base_idx
    # delta_k = diff_table[base_idx][k] for k = 1, 2, ...
    deltas = []
    max_k = n - base_idx
    for k in range(1, max_k):
        val = diff_table[base_idx][k]
        if val is not None:
            deltas.append(val)

    iterations_table: List[Dict[str, Any]] = []
    series_terms = []
    formula_latex = ""
    sub_terms = []
    derivative_val = 0.0

    if order == 1:
        formula_latex = (
            "\\frac{dy}{dx} = \\frac{1}{h} \\left[ "
            "\\Delta y_0 + \\frac{2p-1}{2} \\Delta^2 y_0 + \\frac{3p^2-6p+2}{6} \\Delta^3 y_0 + "
            "\\frac{4p^3-18p^2+22p-6}{24} \\Delta^4 y_0 + \\dots \\right]"
        )

        # Coefficients for d/dp of binomial coefficients evaluated at p:
        # k=1: 1
        # k=2: (2p - 1) / 2
        # k=3: (3p^2 - 6p + 2) / 6
        # k=4: (4p^3 - 18p^2 + 22p - 6) / 24
        # k=5: (5p^4 - 40p^3 + 105p^2 - 100p + 24) / 120
        coeffs = [
            1.0,
            (2.0 * p - 1.0) / 2.0,
            (3.0 * (p ** 2) - 6.0 * p + 2.0) / 6.0,
            (4.0 * (p ** 3) - 18.0 * (p ** 2) + 22.0 * p - 6.0) / 24.0,
            (5.0 * (p ** 4) - 40.0 * (p ** 3) + 105.0 * (p ** 2) - 100.0 * p + 24.0) / 120.0,
        ]

        bracket_sum = 0.0
        for k_idx, dy_k in enumerate(deltas):
            if k_idx < len(coeffs):
                c = coeffs[k_idx]
                term = c * dy_k
                bracket_sum += term
                sub_terms.append(f"({c:.4f} \\times {dy_k:.6f})")

                iterations_table.append(
                    {
                        "term": f"Δ^{k_idx + 1} y_0",
                        "difference_value": round(dy_k, 6),
                        "polynomial_coeff": round(c, 6),
                        "weighted_term": round(term, 6),
                    }
                )

        derivative_val = (1.0 / h) * bracket_sum

    else:  # order == 2
        formula_latex = (
            "\\frac{d^2y}{dx^2} = \\frac{1}{h^2} \\left[ "
            "\\Delta^2 y_0 + (p-1) \\Delta^3 y_0 + \\frac{6p^2-18p+11}{12} \\Delta^4 y_0 + \\dots \\right]"
        )

        # 2nd derivative coefficients starting at k=2:
        # k=2: 1
        # k=3: p - 1
        # k=4: (6p^2 - 18p + 11) / 12
        # k=5: (2p^3 - 12p^2 + 21p - 10) / 12
        coeffs_2nd = [
            1.0,
            p - 1.0,
            (6.0 * (p ** 2) - 18.0 * p + 11.0) / 12.0,
            (2.0 * (p ** 3) - 12.0 * (p ** 2) + 21.0 * p - 10.0) / 12.0,
        ]

        bracket_sum = 0.0
        # Start at index 1 of deltas (which is Delta^2)
        for k_idx in range(1, len(deltas)):
            c_idx = k_idx - 1
            if c_idx < len(coeffs_2nd):
                dy_k = deltas[k_idx]
                c = coeffs_2nd[c_idx]
                term = c * dy_k
                bracket_sum += term
                sub_terms.append(f"({c:.4f} \\times {dy_k:.6f})")

                iterations_table.append(
                    {
                        "term": f"Δ^{k_idx + 1} y_0",
                        "difference_value": round(dy_k, 6),
                        "polynomial_coeff": round(c, 6),
                        "weighted_term": round(term, 6),
                    }
                )

        derivative_val = (1.0 / (h ** 2)) * bracket_sum

    scale_factor = f"\\frac{{1}}{{{h:.4f}}}" if order == 1 else f"\\frac{{1}}{{{h:.4f}^2}}"
    sub_str = f"{scale_factor} \\left[ {' + '.join(sub_terms)} \\right] = {derivative_val:.6f}"

    deriv_symbol = "\\frac{dy}{dx}" if order == 1 else "\\frac{d^2y}{dx^2}"
    steps.append(
        Step(
            step_number=4,
            title=f"Derivative Series Evaluation ({'1st' if order == 1 else '2nd'} Order)",
            description=f"Applied Newton's Forward Difference differentiation formula at x = {target:.4f}.",
            formula=formula_latex,
            substitution=sub_str,
            value=round(derivative_val, 6),
        )
    )

    # Plot data: scatter of points + tangent line at target_x
    plot_data = None
    try:
        x_min = min(xs) - 0.5
        x_max = max(xs) + 0.5
        tangent_len = 0.5 * (xs[-1] - xs[0])
        # Linear approximation around target point
        y_at_target = ys[base_idx] + p * (deltas[0] if deltas else 0.0)
        t_x1 = target - tangent_len / 2.0
        t_x2 = target + tangent_len / 2.0
        t_y1 = y_at_target - (tangent_len / 2.0) * derivative_val
        t_y2 = y_at_target + (tangent_len / 2.0) * derivative_val

        plot_data = {
            "type": "scatter_line",
            "line": [
                {"x": round(t_x1, 4), "y": round(t_y1, 4)},
                {"x": round(t_x2, 4), "y": round(t_y2, 4)},
            ],
            "scatter": [{"x": round(xs[k], 4), "y": round(ys[k], 4)} for k in range(n)],
            "highlighted": [{"x": round(target, 4), "y": round(y_at_target, 4)}],
        }
    except Exception:
        plot_data = None

    order_str = "dy/dx" if order == 1 else "d²y/dx²"
    result = {
        "derivative": round(derivative_val, 6),
        "order": order,
        "target_x": target,
        "h": round(h, 6),
        "p": round(p, 6),
    }

    result_summary = (
        f"Newton's Forward Difference: {order_str} at x = {target:.4f} ≈ {derivative_val:.6f} (h = {h:.4f}, p = {p:.4f})"
    )

    return SolveResponse(
        topic_id="newton_forward_difference",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=result_summary,
        iterations_table=iterations_table,
        plot_data=plot_data,
        warnings=warnings,
    )
