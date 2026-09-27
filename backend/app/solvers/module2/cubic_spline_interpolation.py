import numpy as np
from typing import Any, Dict, List, Union
from pydantic import BaseModel, Field

from app.core.models import Step, SolveResponse
from app.core.linear_algebra import thomas_algorithm


class CubicSplineInput(BaseModel):
    points: List[List[float]] = Field(
        default=[[1.0, 1.0], [2.0, 5.0], [3.0, 11.0], [4.0, 8.0]],
        description="Tabulated data points [x_i, y_i]",
    )
    target_x: float = Field(default=2.5, description="Target value x to evaluate S(x)")


def solve(payload: Union[Dict[str, Any], CubicSplineInput]) -> SolveResponse:
    """
    Constructs a Natural Cubic Spline S(x) passing through given points.
    Boundary Conditions: S''(x_0) = M_0 = 0 and S''(x_n) = M_n = 0.
    Solves the tridiagonal system for second derivatives M_i using Thomas Algorithm.
    """
    if isinstance(payload, dict):
        params = CubicSplineInput(**payload)
    else:
        params = payload

    raw_points = params.points
    if len(raw_points) < 3:
        raise ValueError("At least 3 data points are required to construct a cubic spline.")

    # Sort points by x
    sorted_pts = sorted(raw_points, key=lambda p: float(p[0]))
    xs = [float(p[0]) for p in sorted_pts]
    ys = [float(p[1]) for p in sorted_pts]
    n_intervals = len(xs) - 1
    target = float(params.target_x)

    # Check for strictly increasing x
    for i in range(n_intervals):
        if xs[i + 1] <= xs[i]:
            raise ValueError(f"Abscissa values must be strictly increasing. Duplicate or unsorted x={xs[i]}.")

    inputs_echo = {
        "points": sorted_pts,
        "target_x": target,
        "intervals_count": n_intervals,
    }

    steps: List[Step] = []
    warnings: List[str] = []
    iterations_table: List[Dict[str, Any]] = []

    # Step 1: Compute interval widths h_i
    h = [xs[i + 1] - xs[i] for i in range(n_intervals)]
    steps.append(
        Step(
            step_number=1,
            title="Step Sizes (Interval Widths h_i)",
            description="Computed step sizes between successive nodes: h_i = x_{i+1} - x_i.",
            formula="h_i = x_{i+1} - x_i",
            substitution="; ".join([f"h_{{{i}}} = {xs[i+1]:.4f} - {xs[i]:.4f} = {h[i]:.4f}" for i in range(n_intervals)]),
            value=[round(val, 6) for val in h],
        )
    )

    # Step 2: Assemble tridiagonal system for M_1 ... M_{n-1}
    # For natural spline, M_0 = 0 and M_n = 0
    num_interior = n_intervals - 1
    sub_diag = []
    main_diag = []
    sup_diag = []
    rhs = []

    for i in range(1, n_intervals):
        hi_prev = h[i - 1]
        hi = h[i]
        sub_diag.append(hi_prev)
        main_diag.append(2.0 * (hi_prev + hi))
        sup_diag.append(hi)

        d_i = 6.0 * ((ys[i + 1] - ys[i]) / hi - (ys[i] - ys[i - 1]) / hi_prev)
        rhs.append(d_i)

    system_desc = (
        f"Assembled {num_interior}×{num_interior} tridiagonal system for interior second derivatives "
        f"M_1 ... M_{{{num_interior}}} with Natural Boundary Conditions M_0 = M_{{{n_intervals}}} = 0."
    )
    system_sub = (
        f"Main diagonal: {np.round(main_diag, 4).tolist()}; "
        f"RHS vector d: {np.round(rhs, 4).tolist()}"
    )

    steps.append(
        Step(
            step_number=2,
            title="Tridiagonal System Assembly",
            description=system_desc,
            formula="h_{i-1} M_{i-1} + 2(h_{i-1} + h_i) M_i + h_i M_{i+1} = 6 \\left( \\frac{y_{i+1}-y_i}{h_i} - \\frac{y_i-y_{i-1}}{h_{i-1}} \\right)",
            substitution=system_sub,
            value={"main_diag": np.round(main_diag, 4).tolist(), "rhs": np.round(rhs, 4).tolist()},
        )
    )

    # Step 3: Solve via Thomas Algorithm
    if num_interior == 1:
        # Single interior equation: main_diag[0] * M_1 = rhs[0]
        interior_M = [rhs[0] / main_diag[0]]
    else:
        # Format vectors for thomas_algorithm
        a_vec = [0.0] + sub_diag[1:]
        b_vec = main_diag
        c_vec = sup_diag[:-1] + [0.0]
        interior_M = thomas_algorithm(a_vec, b_vec, c_vec, rhs)

    M = [0.0] + [float(m) for m in interior_M] + [0.0]

    steps.append(
        Step(
            step_number=3,
            title="Second Derivatives Vector M",
            description="Solved tridiagonal system via Thomas algorithm. Boundary values M_0 = 0 and M_n = 0 enforced.",
            formula="M = [M_0, M_1, \\dots, M_n]^T",
            substitution="; ".join([f"M_{{{k}}} = {M[k]:.6f}" for k in range(len(M))]),
            value=[round(val, 6) for val in M],
        )
    )

    # Fill iterations table with interval details
    for i in range(n_intervals):
        iterations_table.append(
            {
                "interval": f"[{xs[i]:.2f}, {xs[i+1]:.2f}]",
                "h_i": round(h[i], 6),
                "M_i": round(M[i], 6),
                "M_next": round(M[i + 1], 6),
                "y_i": round(ys[i], 6),
                "y_next": round(ys[i + 1], 6),
            }
        )

    # Step 4: Determine which interval target_x belongs to
    interval_idx = -1
    if target < xs[0]:
        interval_idx = 0
        warnings.append(f"Target x={target} is to the left of domain [{xs[0]}, {xs[-1]}]. Extrapolating on first piece.")
    elif target > xs[-1]:
        interval_idx = n_intervals - 1
        warnings.append(f"Target x={target} is to the right of domain [{xs[0]}, {xs[-1]}]. Extrapolating on last piece.")
    else:
        for i in range(n_intervals):
            if xs[i] <= target <= xs[i + 1]:
                interval_idx = i
                break

    steps.append(
        Step(
            step_number=4,
            title=f"Interval Selection for x = {target:.4f}",
            description=f"Identified interval [{xs[interval_idx]:.4f}, {xs[interval_idx + 1]:.4f}] containing target point.",
            formula="x \\in [x_i, x_{i+1}]",
            substitution=f"{xs[interval_idx]:.4f} \\le {target:.4f} \\le {xs[interval_idx + 1]:.4f}",
            value=interval_idx,
        )
    )

    # Step 5: Evaluate cubic piece formula
    idx = interval_idx
    x_i = xs[idx]
    x_ip1 = xs[idx + 1]
    y_i = ys[idx]
    y_ip1 = ys[idx + 1]
    M_i = M[idx]
    M_ip1 = M[idx + 1]
    h_i = h[idx]

    term1 = M_i * ((x_ip1 - target) ** 3) / (6.0 * h_i)
    term2 = M_ip1 * ((target - x_i) ** 3) / (6.0 * h_i)
    term3 = (y_i - (M_i * (h_i ** 2)) / 6.0) * ((x_ip1 - target) / h_i)
    term4 = (y_ip1 - (M_ip1 * (h_i ** 2)) / 6.0) * ((target - x_i) / h_i)

    spline_value = term1 + term2 + term3 + term4

    eval_formula = (
        "S_i(x) = \\frac{M_i(x_{i+1}-x)^3}{6h_i} + \\frac{M_{i+1}(x-x_i)^3}{6h_i} + "
        "\\left(y_i - \\frac{M_i h_i^2}{6}\\right)\\frac{x_{i+1}-x}{h_i} + "
        "\\left(y_{i+1} - \\frac{M_{i+1} h_i^2}{6}\\right)\\frac{x-x_i}{h_i}"
    )

    eval_sub = (
        f"S_{{{idx}}}({target:.4f}) = {term1:.6f} + {term2:.6f} + {term3:.6f} + {term4:.6f} = {spline_value:.6f}"
    )

    steps.append(
        Step(
            step_number=5,
            title=f"Spline Evaluation S({target:.4f})",
            description=f"Evaluated piece {idx + 1} at target x = {target:.4f}.",
            formula=eval_formula,
            substitution=eval_sub,
            value=round(spline_value, 6),
        )
    )

    # Dense spline plot data across all intervals
    plot_data = None
    try:
        curve_pts = []
        for i in range(n_intervals):
            x_left = xs[i]
            x_right = xs[i + 1]
            seg_x = np.linspace(x_left, x_right, 30)
            h_seg = h[i]
            for xx in seg_x:
                t1 = M[i] * ((x_right - xx) ** 3) / (6.0 * h_seg)
                t2 = M[i + 1] * ((xx - x_left) ** 3) / (6.0 * h_seg)
                t3 = (ys[i] - (M[i] * (h_seg ** 2)) / 6.0) * ((x_right - xx) / h_seg)
                t4 = (ys[i + 1] - (M[i + 1] * (h_seg ** 2)) / 6.0) * ((xx - x_left) / h_seg)
                yy = t1 + t2 + t3 + t4
                curve_pts.append({"x": round(float(xx), 4), "y": round(float(yy), 4)})

        plot_data = {
            "type": "scatter_line",
            "line": curve_pts,
            "scatter": [{"x": round(xs[k], 4), "y": round(ys[k], 4)} for k in range(len(xs))],
            "highlighted": [{"x": round(target, 4), "y": round(spline_value, 4)}],
        }
    except Exception:
        plot_data = None

    result = {
        "interpolated_value": round(spline_value, 6),
        "target_x": target,
        "interval_used": f"[{x_i:.4f}, {x_ip1:.4f}]",
        "second_derivatives": [round(m, 6) for m in M],
    }

    result_summary = (
        f"Natural Cubic Spline S({target:.4f}) ≈ {spline_value:.6f} "
        f"(evaluated on interval [{x_i:.4f}, {x_ip1:.4f}] across {n_intervals} pieces)"
    )

    return SolveResponse(
        topic_id="cubic_spline_interpolation",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=result_summary,
        iterations_table=iterations_table,
        plot_data=plot_data,
        warnings=warnings,
    )
