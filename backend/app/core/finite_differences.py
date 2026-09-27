import numpy as np
from typing import List, Optional, Union


def build_forward_difference_table(
    y: List[float],
) -> List[List[Optional[float]]]:
    """
    Constructs the forward difference table for a given list of y-values.
    Returns a 2D table where table[i][j] represents Δ^j y_i.
    Missing / out-of-bound entries in the difference triangle are filled with None.
    """
    n = len(y)
    table: List[List[Optional[float]]] = [[None for _ in range(n)] for _ in range(n)]

    # 0-th difference is y itself
    for i in range(n):
        table[i][0] = float(y[i])

    # Compute higher-order forward differences: Δ^j y_i = Δ^{j-1} y_{i+1} - Δ^{j-1} y_i
    for j in range(1, n):
        for i in range(n - j):
            prev_next = table[i + 1][j - 1]
            prev_curr = table[i][j - 1]
            if prev_next is not None and prev_curr is not None:
                table[i][j] = round(prev_next - prev_curr, 8)

    return table
