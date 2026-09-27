import numpy as np
from typing import List, Tuple
from app.core.models import Step


def thomas_algorithm(
    a: List[float], b: List[float], c: List[float], d: List[float]
) -> List[float]:
    """
    Solves tridiagonal linear system using the Thomas Algorithm.
    System equations: a[i]*x[i-1] + b[i]*x[i] + c[i]*x[i+1] = d[i] for i = 0 ... n-1
    a: sub-diagonal (length n, a[0] typically 0)
    b: main diagonal (length n)
    c: super-diagonal (length n, c[n-1] typically 0)
    d: right-hand side vector (length n)
    """
    n = len(d)
    if not (len(b) == n and len(a) >= n - 1 and len(c) >= n - 1):
        raise ValueError("Invalid dimension for tridiagonal vectors.")

    # Convert to mutable lists of floats
    a_vec = [float(x) for x in a]
    b_vec = [float(x) for x in b]
    c_vec = [float(x) for x in c]
    d_vec = [float(x) for x in d]

    # Ensure length n
    if len(a_vec) == n - 1:
        a_vec = [0.0] + a_vec
    if len(c_vec) == n - 1:
        c_vec = c_vec + [0.0]

    c_prime = [0.0] * n
    d_prime = [0.0] * n

    # First row
    if abs(b_vec[0]) < 1e-14:
        raise ValueError("Singular matrix encountered in Thomas algorithm: pivot b[0] is zero.")

    c_prime[0] = c_vec[0] / b_vec[0]
    d_prime[0] = d_vec[0] / b_vec[0]

    # Forward elimination
    for i in range(1, n):
        denom = b_vec[i] - a_vec[i] * c_prime[i - 1]
        if abs(denom) < 1e-14:
            raise ValueError(f"Singular matrix encountered in Thomas algorithm at row {i}.")
        c_prime[i] = c_vec[i] / denom if i < n - 1 else 0.0
        d_prime[i] = (d_vec[i] - a_vec[i] * d_prime[i - 1]) / denom

    # Back substitution
    x = [0.0] * n
    x[n - 1] = d_prime[n - 1]
    for i in range(n - 2, -1, -1):
        x[i] = d_prime[i] - c_prime[i] * x[i + 1]

    return x


def gauss_jordan_core(
    augmented: np.ndarray,
) -> Tuple[np.ndarray, List[Step], List[str]]:
    """
    Performs Gauss-Jordan elimination to Reduced Row Echelon Form (RREF).
    Returns (rref_matrix, steps, warnings).
    """
    aug = augmented.astype(float).copy()
    rows, cols = aug.shape
    steps: List[Step] = []
    warnings: List[str] = []

    step_idx = 1
    steps.append(
        Step(
            step_number=step_idx,
            title="Initial Augmented Matrix",
            description=f"Starting augmented matrix of dimension {rows}×{cols}.",
            formula="[A | B]",
            substitution=None,
            value=np.round(aug, 6).tolist(),
        )
    )

    pivot_row = 0
    for col in range(min(rows, cols)):
        if pivot_row >= rows:
            break

        # Partial pivoting: find maximum absolute value in current column from pivot_row down
        max_row = pivot_row + int(np.argmax(np.abs(aug[pivot_row:, col])))
        max_val = abs(aug[max_row, col])

        if max_val < 1e-12:
            warnings.append(f"Near-zero pivot in column {col + 1} (value={max_val:.2e}). Matrix may be singular.")
            continue

        # Row swap if necessary
        if max_row != pivot_row:
            aug[[pivot_row, max_row]] = aug[[max_row, pivot_row]]
            step_idx += 1
            steps.append(
                Step(
                    step_number=step_idx,
                    title=f"Partial Pivoting (R_{pivot_row + 1} ↔ R_{max_row + 1})",
                    description=f"Swap row {pivot_row + 1} with row {max_row + 1} to maximize pivot element.",
                    formula=f"R_{{{pivot_row + 1}}} \\leftrightarrow R_{{{max_row + 1}}}",
                    substitution=f"Pivot element chosen: {aug[pivot_row, col]:.4f}",
                    value=np.round(aug, 6).tolist(),
                )
            )

        # Scale pivot row to make pivot = 1
        pivot_elem = aug[pivot_row, col]
        if abs(pivot_elem - 1.0) > 1e-12:
            aug[pivot_row] = aug[pivot_row] / pivot_elem
            step_idx += 1
            steps.append(
                Step(
                    step_number=step_idx,
                    title=f"Scale Pivot Row R_{pivot_row + 1}",
                    description=f"Divide row {pivot_row + 1} by pivot element {pivot_elem:.4f}.",
                    formula=f"R_{{{pivot_row + 1}}} \\leftarrow R_{{{pivot_row + 1}}} / ({pivot_elem:.4f})",
                    substitution=None,
                    value=np.round(aug, 6).tolist(),
                )
            )

        # Eliminate all other rows in this column (Gauss-Jordan eliminates both above and below)
        eliminated_rows = []
        for r in range(rows):
            if r != pivot_row and abs(aug[r, col]) > 1e-12:
                factor = aug[r, col]
                aug[r] = aug[r] - factor * aug[pivot_row]
                eliminated_rows.append(f"R_{r + 1} - ({factor:.4f})*R_{pivot_row + 1}")

        if eliminated_rows:
            step_idx += 1
            steps.append(
                Step(
                    step_number=step_idx,
                    title=f"Eliminate Column {col + 1} Entries",
                    description=f"Eliminated non-zero entries in column {col + 1} above and below the pivot.",
                    formula="; ".join(eliminated_rows),
                    substitution=None,
                    value=np.round(aug, 6).tolist(),
                )
            )

        pivot_row += 1

    return aug, steps, warnings
