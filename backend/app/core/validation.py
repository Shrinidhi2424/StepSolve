from typing import List, Tuple, Optional
import numpy as np


def validate_points(
    points: List[Tuple[float, float]],
    min_points: int = 2,
    check_unique_x: bool = True,
    check_equal_spacing: bool = False,
    spacing_tolerance: float = 1e-5,
) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Validates a list of (x, y) coordinate pairs.
    Returns: (is_valid, error_message, step_h)
    """
    if len(points) < min_points:
        return False, f"At least {min_points} data points required, but got {len(points)}.", None

    xs = [p[0] for p in points]

    if check_unique_x:
        if len(set(xs)) != len(xs):
            return False, "Duplicate x-values detected. Each x must be distinct.", None

    step_h = None
    if check_equal_spacing and len(xs) >= 2:
        diffs = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
        step_h = diffs[0]
        if abs(step_h) < 1e-12:
            return False, "Step size h is virtually zero.", None
        for i, d in enumerate(diffs):
            if abs(d - step_h) > spacing_tolerance:
                return (
                    False,
                    f"Points are not equally spaced. Interval {i} has step {d:.6f}, while expected {step_h:.6f}.",
                    step_h,
                )

    return True, None, step_h


def validate_matrix(
    matrix: List[List[float]], expected_rows: Optional[int] = None, expected_cols: Optional[int] = None
) -> Tuple[bool, Optional[str]]:
    """Validates that a 2D list is a proper non-empty rectangular matrix."""
    if not matrix or not isinstance(matrix, list):
        return False, "Matrix must be a non-empty list of rows."

    rows = len(matrix)
    if expected_rows is not None and rows != expected_rows:
        return False, f"Expected {expected_rows} rows, got {rows}."

    cols = len(matrix[0])
    if cols == 0:
        return False, "Matrix columns cannot be empty."

    if expected_cols is not None and cols != expected_cols:
        return False, f"Expected {expected_cols} columns, got {cols}."

    for r_idx, row in enumerate(matrix):
        if len(row) != cols:
            return False, f"Inconsistent row length at row {r_idx}: expected {cols}, got {len(row)}."

    return True, None
