import pytest
import math
from app.solvers.module3.trapezoidal_rule import solve, TrapezoidalInput


def test_trapezoidal_standard_function():
    """Integral of 1 / (1 + x^2) from 0 to 1 -> exact is pi/4 ≈ 0.785398."""
    payload = TrapezoidalInput(
        f_expr="1 / (1 + x**2)",
        a=0.0,
        b=1.0,
        n=6,
    )
    res = solve(payload)
    assert res.topic_id == "trapezoidal_rule"
    assert pytest.approx(res.result["integral"], abs=0.01) == (math.pi / 4.0)
    assert len(res.steps) == 4
    assert len(res.iterations_table) == 7
    assert res.plot_data is not None


def test_trapezoidal_polynomial():
    """Integral of x^2 from 0 to 1 with n=4: h=0.25; nodes=0, 0.25, 0.5, 0.75, 1 -> I = 0.34375 vs 0.33333."""
    payload = TrapezoidalInput(
        f_expr="x**2",
        a=0.0,
        b=1.0,
        n=4,
    )
    res = solve(payload)
    assert pytest.approx(res.result["integral"], abs=1e-4) == 0.34375


def test_trapezoidal_tabulated_points():
    """Tabulated points mode."""
    payload = TrapezoidalInput(
        points=[[0.0, 0.0], [0.5, 0.25], [1.0, 1.0]],
    )
    res = solve(payload)
    assert res.result["n"] == 2
    assert res.result["integral"] > 0
