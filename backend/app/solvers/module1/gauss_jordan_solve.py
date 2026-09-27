import numpy as np
from typing import Any, Dict, List, Union
from pydantic import BaseModel, Field

from app.core.models import Step, SolveResponse
from app.core.linear_algebra import gauss_jordan_core


class GaussJordanInput(BaseModel):
    A: List[List[float]] = Field(
        default=[[2.0, 1.0, -1.0], [-3.0, -1.0, 2.0], [-2.0, 1.0, 2.0]],
        description="Square coefficient matrix A (n × n)",
    )
    B: Union[List[float], List[List[float]]] = Field(
        default=[[8.0], [-11.0], [-3.0]],
        description="Constant vector or column matrix B",
    )


def solve(payload: Union[Dict[str, Any], GaussJordanInput]) -> SolveResponse:
    """
    Solves AX = B using Gauss-Jordan Elimination.
    Forms augmented matrix [A | B] and reduces to Reduced Row Echelon Form (RREF).
    """
    if isinstance(payload, dict):
        params = GaussJordanInput(**payload)
    else:
        params = payload

    A_mat = np.array(params.A, dtype=float)
    if A_mat.ndim != 2 or A_mat.shape[0] != A_mat.shape[1]:
        raise ValueError(f"Coefficient matrix A must be square (n × n). Received shape {A_mat.shape}.")

    n = A_mat.shape[0]

    # Handle B as 1D list or 2D column list
    B_raw = params.B
    if isinstance(B_raw, list) and len(B_raw) > 0 and isinstance(B_raw[0], list):
        B_vec = np.array(B_raw, dtype=float).reshape(n, -1)
    else:
        B_vec = np.array(B_raw, dtype=float).reshape(n, 1)

    if B_vec.shape[0] != n:
        raise ValueError(f"Vector B rows ({B_vec.shape[0]}) do not match matrix A dimension ({n}).")

    inputs_echo = {
        "A": np.round(A_mat, 6).tolist(),
        "B": np.round(B_vec, 6).tolist(),
        "dimension_n": n,
    }

    # Form augmented matrix [A | B]
    aug = np.hstack([A_mat, B_vec])

    # Perform Gauss-Jordan elimination to RREF
    rref, steps, warnings = gauss_jordan_core(aug)

    # Check for consistency and singularity
    solution: List[float] = []
    is_consistent = True
    is_unique = True

    for r in range(n):
        coeff_row = rref[r, :n]
        rhs_val = rref[r, n]
        if np.all(np.abs(coeff_row) < 1e-9):
            if abs(rhs_val) > 1e-6:
                is_consistent = False
                warnings.append(f"Row {r + 1} has zero coefficients but non-zero constant ({rhs_val:.4f}). System has NO solution (inconsistent).")
            else:
                is_unique = False
                warnings.append(f"Row {r + 1} is entirely zero. System has INFINITELY many solutions.")

    if is_consistent and is_unique:
        for r in range(n):
            solution.append(round(float(rref[r, n]), 6))

        # Add final solution extraction step
        sol_str = ", ".join([f"x_{{{i+1}}} = {solution[i]}" for i in range(n)])
        steps.append(
            Step(
                step_number=len(steps) + 1,
                title="Solution Vector Extraction",
                description=f"Read off the unique solution directly from the reduced row-echelon constants column.",
                formula="X = [x_1, x_2, \\dots, x_n]^T",
                substitution=sol_str,
                value=solution,
            )
        )
        result_summary = f"Unique solution: X = [{', '.join(map(str, solution))}]"
    elif not is_consistent:
        result_summary = "System of equations is inconsistent (no solution exists)."
    else:
        result_summary = "System is dependent (infinitely many solutions exist)."

    # Iteration table showing row variables and solved values
    iterations_table = []
    for i in range(n):
        iterations_table.append(
            {
                "variable": f"x_{i + 1}",
                "solved_value": solution[i] if i < len(solution) else None,
                "pivot_status": "Pivoted (RREF = 1.0)" if is_consistent and is_unique else "Dependent / Singular",
            }
        )

    result = {
        "solution": solution,
        "is_consistent": is_consistent,
        "is_unique": is_unique,
        "dimension": n,
        "rref_matrix": np.round(rref, 6).tolist(),
    }

    return SolveResponse(
        topic_id="gauss_jordan_solve",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=result_summary,
        iterations_table=iterations_table,
        plot_data=None,
        warnings=warnings,
    )
