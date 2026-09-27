import pytest
import numpy as np
from app.solvers.module1.gauss_jordan_solve import solve, GaussJordanInput


def test_gauss_jordan_3x3_textbook_system():
    """
    Solve:
      2x + y - z = 8
     -3x - y + 2z = -11
     -2x + y + 2z = -3
    Solution: x = 2, y = 3, z = -1
    """
    payload = GaussJordanInput(
        A=[[2.0, 1.0, -1.0], [-3.0, -1.0, 2.0], [-2.0, 1.0, 2.0]],
        B=[[8.0], [-11.0], [-3.0]],
    )
    res = solve(payload)
    assert res.topic_id == "gauss_jordan_solve"
    assert res.result["is_consistent"] is True
    assert res.result["is_unique"] is True
    sol = res.result["solution"]
    assert len(sol) == 3
    assert np.allclose(sol, [2.0, 3.0, -1.0], atol=1e-5)
    assert len(res.steps) >= 3


def test_gauss_jordan_singular_system():
    """Singular system with proportional rows (infinite solutions / singular)."""
    payload = GaussJordanInput(
        A=[[1.0, 2.0], [2.0, 4.0]],
        B=[[3.0], [6.0]],
    )
    res = solve(payload)
    assert len(res.warnings) > 0
    assert not res.result["is_unique"] or not res.result["is_consistent"]


def test_gauss_jordan_inconsistent_system():
    """Inconsistent system: parallel lines with no solution."""
    payload = GaussJordanInput(
        A=[[1.0, 1.0], [1.0, 1.0]],
        B=[[2.0], [5.0]],
    )
    res = solve(payload)
    assert res.result["is_consistent"] is False
    assert len(res.warnings) > 0
    assert any("inconsistent" in w.lower() or "no solution" in w.lower() for w in res.warnings)
