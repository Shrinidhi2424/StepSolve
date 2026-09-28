import numpy as np
from typing import Any, Dict, List, Union
from pydantic import BaseModel, Field

from app.core.models import Step, SolveResponse
from app.core.expr_eval import parse_single_var
from app.core.linear_algebra import thomas_algorithm


class BVPInput(BaseModel):
    p_expr: str = Field(default="0", description="p(x) coefficient for y'")
    q_expr: str = Field(default="-1", description="q(x) coefficient for y")
    r_expr: str = Field(default="0", description="r(x) RHS term")
    a: float = Field(default=0.0, description="Left boundary x = a")
    b: float = Field(default=1.0, description="Right boundary x = b")
    alpha: float = Field(default=0.0, description="Boundary condition y(a)")
    beta: float = Field(default=1.1752, description="Boundary condition y(b)")
    N: int = Field(default=4, description="Number of interior mesh points")


def solve(payload: Union[Dict[str, Any], BVPInput]) -> SolveResponse:
    """
    Solves linear 2nd-order ODE BVP:
        y'' + p(x)y' + q(x)y = r(x),   y(a) = alpha, y(b) = beta
    using central finite difference discretization and Thomas algorithm.
    """
    if isinstance(payload, dict):
        params = BVPInput(**payload)
    else:
        params = payload

    p_fn = parse_single_var(params.p_expr, var="x")
    q_fn = parse_single_var(params.q_expr, var="x")
    r_fn = parse_single_var(params.r_expr, var="x")

    a = float(params.a)
    b = float(params.b)
    alpha = float(params.alpha)
    beta = float(params.beta)
    N = int(params.N)

    if b <= a:
        raise ValueError("Right boundary b must be strictly greater than left boundary a.")
    if N < 1:
        raise ValueError("Number of interior points N must be at least 1.")
    if N > 200:
        raise ValueError("Number of interior points N cannot exceed 200.")

    h = (b - a) / (N + 1)
    h2 = h * h

    inputs_echo = {
        "p_expr": params.p_expr,
        "q_expr": params.q_expr,
        "r_expr": params.r_expr,
        "a": a,
        "b": b,
        "alpha": alpha,
        "beta": beta,
        "N": N,
        "h": round(h, 6),
    }

    steps: List[Step] = []
    warnings: List[str] = []

    # Step 1: Mesh and Central Difference Discretization
    mesh_points = [a + i * h for i in range(N + 2)]
    steps.append(
        Step(
            step_number=1,
            title="Mesh Discretization & Finite Difference Scheme",
            description=(
                f"Interval [{a:.4f}, {b:.4f}] is divided into {N + 1} subintervals with step size "
                f"h = (b - a) / (N + 1) = {h:.4f}. There are {N} interior nodes: "
                f"{', '.join(f'x_{i}={mesh_points[i]:.4f}' for i in range(1, min(N + 1, 6)))}"
                f"{'...' if N > 5 else ''}."
            ),
            formula=(
                "y''_i \\approx \\frac{y_{i-1} - 2y_i + y_{i+1}}{h^2}, \\quad "
                "y'_i \\approx \\frac{y_{i+1} - y_{i-1}}{2h}"
            ),
            substitution=(
                f"\\left(1 - \\frac{{{h:.4f}}}{{2}}p(x_i)\\right)y_{{i-1}} + "
                f"\\left(-2 + {h2:.6f}q(x_i)\\right)y_i + "
                f"\\left(1 + \\frac{{{h:.4f}}}{{2}}p(x_i)\\right)y_{{i+1}} = {h2:.6f}r(x_i)"
            ),
            value=round(h, 6),
        )
    )

    # Step 2: Assemble Tridiagonal Matrix
    # Coefficients for interior nodes i = 1 .. N
    sub_diag: List[float] = []    # a_coeff (length N, sub_diag[0] = 0)
    main_diag: List[float] = []   # b_coeff (length N)
    super_diag: List[float] = []  # c_coeff (length N, super_diag[N-1] = 0)
    rhs_vec: List[float] = []     # d_vec (length N)

    for idx, i in enumerate(range(1, N + 1)):
        xi = mesh_points[i]
        pi = p_fn(xi)
        qi = q_fn(xi)
        ri = r_fn(xi)

        ai = 1.0 - 0.5 * h * pi
        bi = -2.0 + h2 * qi
        ci = 1.0 + 0.5 * h * pi
        di = h2 * ri

        sub_val = 0.0 if idx == 0 else ai
        sup_val = 0.0 if idx == N - 1 else ci

        # Adjust RHS for boundary conditions
        if idx == 0:
            di -= ai * alpha
        if idx == N - 1:
            di -= ci * beta

        sub_diag.append(sub_val)
        main_diag.append(bi)
        super_diag.append(sup_val)
        rhs_vec.append(di)

    sample_eqns = []
    for idx in range(min(N, 3)):
        sample_eqns.append(
            f"Row {idx+1}: {sub_diag[idx]:.4f}y_{{{idx}}} + {main_diag[idx]:.4f}y_{{{idx+1}}} + {super_diag[idx]:.4f}y_{{{idx+2}}} = {rhs_vec[idx]:.4f}"
        )

    steps.append(
        Step(
            step_number=2,
            title="Assemble Tridiagonal System & Apply Boundary Conditions",
            description=(
                f"Applying boundary conditions y(a) = y({a:.4f}) = {alpha:.4f} and "
                f"y(b) = y({b:.4f}) = {beta:.4f} modifies rows 1 and {N} of the {N}×{N} system. "
                f"Sample assembled equations:\n" + "\n".join(sample_eqns)
            ),
            formula="A_i y_{i-1} + B_i y_i + C_i y_{i+1} = D_i",
            substitution=(
                f"Row 1: B_1 y_1 + C_1 y_2 = D_1 - A_1\\alpha = {rhs_vec[0]:.4f}; "
                f"Row {N}: A_N y_{{{N-1}}} + B_N y_N = D_N - C_N\\beta = {rhs_vec[-1]:.4f}"
            ),
            value=N,
        )
    )

    # Step 3: Solve via Thomas Algorithm
    try:
        interior_y = thomas_algorithm(sub_diag, main_diag, super_diag, rhs_vec)
    except Exception as e:
        raise ValueError(f"Failed to solve tridiagonal BVP system: {str(e)}")

    full_solution = [alpha] + [float(y) for y in interior_y] + [beta]

    steps.append(
        Step(
            step_number=3,
            title="Solve Tridiagonal System via Thomas Algorithm",
            description=(
                f"Using forward elimination and back substitution, the {N} interior nodal values "
                f"are resolved with O(N) complexity."
            ),
            formula="\\mathbf{T} \\mathbf{y}_{\\text{interior}} = \\mathbf{d}",
            substitution=(
                f"y_1={interior_y[0]:.6f}, "
                f"{f'y_{N}={interior_y[-1]:.6f}' if N > 1 else ''}"
            ),
            value=round(interior_y[0], 6),
        )
    )

    # Format Iteration Table
    iterations_table: List[Dict[str, Any]] = []
    for idx, (x_val, y_val) in enumerate(zip(mesh_points, full_solution)):
        node_type = "Boundary (Left)" if idx == 0 else ("Boundary (Right)" if idx == N + 1 else "Interior")
        iterations_table.append(
            {
                "node": idx,
                "x_i": round(x_val, 4),
                "y_i": round(y_val, 6),
                "node_type": node_type,
            }
        )

    # Plot data
    trajectory = [{"x": round(x_val, 4), "y": round(y_val, 6)} for x_val, y_val in zip(mesh_points, full_solution)]
    plot_data = {
        "type": "line",
        "series": [
            {
                "name": "BVP Solution Curve",
                "data": trajectory,
            }
        ],
    }

    result = {
        "mesh": [round(x, 4) for x in mesh_points],
        "solution": [round(y, 6) for y in full_solution],
        "h": round(h, 6),
        "N": N,
        "a": a,
        "b": b,
    }

    result_summary = (
        f"Finite Difference BVP: Computed solution across {N} interior points on [{a:.2f}, {b:.2f}] (h = {h:.4f})"
    )

    return SolveResponse(
        topic_id="finite_difference_bvp",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=result_summary,
        iterations_table=iterations_table,
        plot_data=plot_data,
        warnings=warnings,
    )
