import numpy as np
from typing import Any, Dict, List, Union
from pydantic import BaseModel, Field

from app.core.models import Step, SolveResponse
from app.core.expr_eval import parse_single_var


class HeatInput(BaseModel):
    alpha: float = Field(default=1.0, description="Thermal diffusivity α")
    L: float = Field(default=1.0, description="Domain length L")
    u0_expr: str = Field(default="sin(pi*x)", description="Initial temperature profile u(x, 0)")
    u_left: float = Field(default=0.0, description="Left boundary temperature u(0, t)")
    u_right: float = Field(default=0.0, description="Right boundary temperature u(L, t)")
    Nx: int = Field(default=4, description="Number of spatial intervals")
    Nt: int = Field(default=10, description="Number of time intervals")
    T: float = Field(default=0.1, description="Total simulation duration T")


def solve(payload: Union[Dict[str, Any], HeatInput]) -> SolveResponse:
    """
    Solves 1D parabolic heat equation:
        ∂u/∂t = α · ∂²u/∂x²,   0 < x < L, 0 < t ≤ T
        u(x, 0) = u₀(x), u(0, t) = u_left, u(L, t) = u_right
    using Forward-Time Central-Space (FTCS) explicit scheme.
    """
    if isinstance(payload, dict):
        params = HeatInput(**payload)
    else:
        params = payload

    alpha = float(params.alpha)
    L = float(params.L)
    u_left = float(params.u_left)
    u_right = float(params.u_right)
    Nx = int(params.Nx)
    Nt = int(params.Nt)
    T = float(params.T)

    if L <= 0:
        raise ValueError("Domain length L must be strictly positive.")
    if T <= 0:
        raise ValueError("Duration T must be strictly positive.")
    if alpha <= 0:
        raise ValueError("Thermal diffusivity alpha must be strictly positive.")
    if Nx < 2:
        raise ValueError("Number of spatial intervals Nx must be at least 2.")
    if Nx > 100:
        raise ValueError("Nx cannot exceed 100.")
    if Nt < 1:
        raise ValueError("Number of time intervals Nt must be at least 1.")
    if Nt > 500:
        raise ValueError("Nt cannot exceed 500.")

    u0_fn = parse_single_var(params.u0_expr, var="x")

    dx = L / Nx
    dt = T / Nt
    r = alpha * dt / (dx * dx)

    inputs_echo = {
        "alpha": alpha,
        "L": L,
        "u0_expr": params.u0_expr,
        "u_left": u_left,
        "u_right": u_right,
        "Nx": Nx,
        "Nt": Nt,
        "T": T,
        "dx": round(dx, 4),
        "dt": round(dt, 4),
        "r": round(r, 6),
    }

    steps: List[Step] = []
    warnings: List[str] = []

    # Stability check
    if r > 0.5:
        warn_msg = (
            f"Explicit FTCS scheme is conditionally stable only for r ≤ 0.5; current r = {r:.4f}. "
            f"Numerical oscillations or divergence may occur. Consider increasing Nx, decreasing Nt, or reducing T."
        )
        warnings.append(warn_msg)

    # Step 1: Discretization & Stability Criterion
    steps.append(
        Step(
            step_number=1,
            title="Spatial/Temporal Grid & Stability Criterion",
            description=(
                f"Grid spacing Δx = L / Nx = {L} / {Nx} = {dx:.4f}, time step Δt = T / Nt = {T} / {Nt} = {dt:.4f}. "
                f"Mesh ratio parameter r = α·Δt / (Δx)² = {r:.4f}. "
                f"Stability status: {'STABLE (r ≤ 0.5)' if r <= 0.5 else 'UNSTABLE (r > 0.5) — oscillatory divergence expected'}."
            ),
            formula="r = \\frac{\\alpha \\Delta t}{(\\Delta x)^2} \\le 0.5",
            substitution=(
                f"r = \\frac{{{alpha:.4f} \\times {dt:.4f}}}{{({dx:.4f})^2}} = "
                f"\\frac{{{alpha * dt:.6f}}}{{{dx * dx:.6f}}} = {r:.6f}"
            ),
            value=round(r, 6),
        )
    )

    # Initialize 2D grid
    x_mesh = [i * dx for i in range(Nx + 1)]
    u = np.zeros((Nt + 1, Nx + 1), dtype=float)

    # Initial condition at t = 0
    for j in range(Nx + 1):
        u[0, j] = float(u0_fn(x_mesh[j]))
    u[0, 0] = u_left
    u[0, Nx] = u_right

    steps.append(
        Step(
            step_number=2,
            title="Initial Condition & Boundary Enforcement (t = 0)",
            description=(
                f"Profile sampled at {Nx + 1} spatial points using u(x, 0) = {params.u0_expr}. "
                f"Boundaries pinned: u(0, t) = {u_left:.4f}, u(L, t) = {u_right:.4f}."
            ),
            formula="u_i^0 = u_0(x_i), \\quad u_0^n = u_{\\text{left}}, \\quad u_{N_x}^n = u_{\\text{right}}",
            substitution=(
                f"u(0) = [{', '.join(f'{u[0, j]:.4f}' for j in range(Nx + 1))}]"
            ),
            value=round(float(u[0, Nx // 2]), 6),
        )
    )

    # FTCS time-stepping loop
    for n in range(Nt):
        for i in range(1, Nx):
            u[n + 1, i] = u[n, i] + r * (u[n, i + 1] - 2.0 * u[n, i] + u[n, i - 1])
        u[n + 1, 0] = u_left
        u[n + 1, Nx] = u_right

    # Step logging: log first 5 time levels and final time level if Nt > 5
    logged_levels = [n for n in range(1, min(6, Nt + 1))]
    if Nt > 5 and Nt not in logged_levels:
        logged_levels.append(Nt)

    current_step_num = 3
    for lvl in logged_levels:
        t_curr = lvl * dt
        mid_val = float(u[lvl, Nx // 2])
        profile_str = ", ".join(f"{u[lvl, j]:.4f}" for j in range(Nx + 1))
        steps.append(
            Step(
                step_number=current_step_num,
                title=f"Time Level n = {lvl}: t = {t_curr:.4f}s",
                description=(
                    f"Profile advanced via explicit FTCS stencil. "
                    f"Center point temperature u({x_mesh[Nx//2]:.2f}, {t_curr:.4f}) = {mid_val:.6f}. "
                    f"Spatial profile: [{profile_str}]."
                ),
                formula="u_i^{n+1} = u_i^n + r\\left(u_{i+1}^n - 2u_i^n + u_{i-1}^n\\right)",
                substitution=(
                    f"u_{{{Nx//2}}}^{{{lvl}}} = {u[lvl-1, Nx//2]:.4f} + {r:.4f}\\left("
                    f"{u[lvl-1, Nx//2 + 1]:.4f} - 2({u[lvl-1, Nx//2]:.4f}) + {u[lvl-1, Nx//2 - 1]:.4f}\\right) = {mid_val:.6f}"
                ),
                value=round(mid_val, 6),
            )
        )
        current_step_num += 1

    # Format Iterations Table (Summary per time level)
    iterations_table: List[Dict[str, Any]] = []
    for n in range(Nt + 1):
        iterations_table.append(
            {
                "time_step": n,
                "t": round(n * dt, 4),
                "u_mid": round(float(u[n, Nx // 2]), 6),
                "u_min": round(float(np.min(u[n])), 6),
                "u_max": round(float(np.max(u[n])), 6),
            }
        )

    # Snapshots for multi_line plot (5 snapshots: t=0, t=T/4, t=T/2, t=3T/4, t=T)
    snapshot_indices = [0, Nt // 4, Nt // 2, (3 * Nt) // 4, Nt]
    # Ensure uniqueness and sorted order
    snapshot_indices = sorted(list(set(snapshot_indices)))

    plot_series = []
    for s_idx in snapshot_indices:
        t_val = s_idx * dt
        data_pts = [
            {"x": round(x_mesh[j], 4), "y": round(float(u[s_idx, j]), 6)}
            for j in range(Nx + 1)
        ]
        plot_series.append(
            {
                "name": f"t = {t_val:.3f}s",
                "data": data_pts,
            }
        )

    plot_data = {
        "type": "multi_line",
        "series": plot_series,
    }

    result = {
        "dx": round(dx, 4),
        "dt": round(dt, 4),
        "r": round(r, 6),
        "stable": bool(r <= 0.5),
        "x_mesh": [round(x, 4) for x in x_mesh],
        "final_profile": [round(float(v), 6) for v in u[Nt]],
    }

    result_summary = (
        f"1D Heat Equation (FTCS): Simulated to T = {T:.2f}s across {Nt} time levels "
        f"(r = {r:.4f}, {'STABLE' if r <= 0.5 else 'UNSTABLE'})"
    )

    return SolveResponse(
        topic_id="heat_equation_explicit",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=result_summary,
        iterations_table=iterations_table,
        plot_data=plot_data,
        warnings=warnings,
    )
