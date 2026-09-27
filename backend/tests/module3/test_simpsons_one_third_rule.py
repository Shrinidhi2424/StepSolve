import pytest
import math
from fastapi import HTTPException
from app.solvers.module3.simpsons_one_third_rule import solve, SimpsonsInput


def test_simpsons_standard_function():
    """Integral of 1 / (1 + x^2) on [0, 1] with n=6 -> very close to pi/4 ≈ 0.785398."""
    payload = SimpsonsInput(
        f_expr="1 / (1 + x**2)",
        a=0.0,
        b=1.0,
        n=6,
    )
    res = solve(payload)
    assert res.topic_id == "simpsons_one_third_rule"
    assert pytest.approx(res.result["integral"], abs=0.001) == (math.pi / 4.0)
    assert len(res.steps) == 4
    assert len(res.iterations_table) == 7
    assert res.plot_data is not None


def test_simpsons_sin_integral():
    """Integral of sin(x) on [0, pi] with n=6 -> exact is 2.0."""
    payload = SimpsonsInput(
        f_expr="sin(x)",
        a=0.0,
        b=math.pi,
        n=6,
    )
    res = solve(payload)
    assert pytest.approx(res.result["integral"], abs=0.01) == 2.0


def test_simpsons_odd_n_validation_error():
    """Simpson's 1/3 requires an even number of subintervals; odd n must raise HTTP 422 error."""
    with pytest.raises(HTTPException) as exc_info:
        solve(SimpsonsInput(f_expr="x**2", a=0.0, b=1.0, n=5))
    assert exc_info.value.status_code == 422
    assert "even number" in exc_info.value.detail.lower()
