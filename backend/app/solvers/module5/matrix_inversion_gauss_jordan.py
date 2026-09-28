import numpy as np
from typing import Any, Dict, List, Union
from pydantic import BaseModel, Field

from app.core.models import Step, SolveResponse
from app.core.linear_algebra import gauss_jordan_core


class MatrixInversionInput(BaseModel):
    A: List[List[float]] = Field(
        default=[[1.0, 2.0, 3.0], [0.0, 1.0, 4.0], [5.0, 6.0, 0.0]],
        description="Square n × n matrix A to invert",
    )


def solve(payload: Union[Dict[str, Any], MatrixInversionInput]) -> SolveResponse:
    """
    Computes matrix inverse A⁻¹ using Gauss-Jordan elimination on [A | I_n] -> [I_n | A⁻¹].
    Includes verification step A @ A⁻¹ = I.
    """
    if isinstance(payload, dict):
        params = MatrixInversionInput(**payload)
    else:
        params = payload

    raw_A = params.A
    if not raw_A or not isinstance(raw_A, list) or len(raw_A) == 0:
        raise ValueError("Matrix A cannot be empty.")

    n = len(raw_A)
    for i, row in enumerate(raw_A):
        if not isinstance(row, list) or len(row) != n:
            raise ValueError(f"Matrix A must be square (n × n). Row {i + 1} has length {len(row)} but expected {n}.")
        for j, val in enumerate(row):
            if not isinstance(val, (int, float)) or np.isnan(val) or np.isinf(val):
                raise ValueError(f"Matrix A entry at ({i+1}, {j+1}) must be a finite real number.")

    if n > 10:
        raise ValueError("Matrix dimension cannot exceed 10 × 10.")

    A_mat = np.array(raw_A, dtype=float)
    I_mat = np.eye(n, dtype=float)

    # Build augmented matrix [A | I_n] of size n x 2n
    augmented = np.hstack([A_mat, I_mat])

    inputs_echo = {
        "A": A_mat.tolist(),
        "dimension": n,
    }

    # Execute Gauss-Jordan core
    rref, steps, gj_warnings = gauss_jordan_core(augmented)
    warnings: List[str] = list(gj_warnings)

    left_half = rref[:, :n]
    right_half = rref[:, n:]

    is_invertible = np.allclose(left_half, np.eye(n), atol=1e-5)

    if not is_invertible:
        warnings.append("Matrix A is singular or ill-conditioned; full inverse does not exist.")
        A_inv = right_half
        prod = A_mat @ A_inv
        max_err = float(np.max(np.abs(prod - np.eye(n))))
        summary = f"Matrix Inversion (Gauss-Jordan): Matrix is singular. RREF failed to produce identity on left half."
    else:
        A_inv = right_half
        prod = A_mat @ A_inv
        max_err = float(np.max(np.abs(prod - np.eye(n))))

        # Verification step
        steps.append(
            Step(
                step_number=len(steps) + 1,
                title="Verification: A × A⁻¹ = I ✓",
                description=(
                    f"Multiplying original matrix A by computed inverse A⁻¹ produces identity matrix I "
                    f"with maximum absolute element discrepancy ||A·A⁻¹ - I||_inf = {max_err:.2e}."
                ),
                formula="A \\cdot A^{-1} = \\mathbf{I}_n",
                substitution=f"\\|A \\cdot A^{{-1}} - \\mathbf{{I}}_{{{n}}}\\|_\\infty = {max_err:.2e}",
                value=np.round(prod, 6).tolist(),
            )
        )
        summary = f"Matrix Inversion (Gauss-Jordan): Successfully inverted {n}×{n} matrix (||A·A⁻¹ - I||_inf = {max_err:.2e})"

    # Iteration Table: Tabulate inverse matrix rows
    iterations_table: List[Dict[str, Any]] = []
    for i in range(n):
        row_dict: Dict[str, Any] = {"row": i + 1}
        for j in range(n):
            row_dict[f"col_{j + 1}"] = round(float(A_inv[i, j]), 6)
        iterations_table.append(row_dict)

    result = {
        "dimension": n,
        "is_invertible": is_invertible,
        "inverse": np.round(A_inv, 6).tolist(),
        "original": np.round(A_mat, 6).tolist(),
        "verification": np.round(prod, 6).tolist(),
        "max_verification_error": round(max_err, 8),
    }

    return SolveResponse(
        topic_id="matrix_inversion_gauss_jordan",
        inputs_echo=inputs_echo,
        steps=steps,
        result=result,
        result_summary=summary,
        iterations_table=iterations_table,
        plot_data=None,
        warnings=warnings,
    )
