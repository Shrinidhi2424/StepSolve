import pytest
from app.solvers.module3.newton_forward_difference import solve, NewtonForwardDiffInput


def test_newton_forward_diff_1st_order():
    """
    Given tabulated points for y = x^2:
    x = 1, 2, 3, 4, 5 -> y = 1, 4, 9, 16, 25.
    At x = 1.0, dy/dx of x^2 is 2*x = 2.0.
    """
    payload = NewtonForwardDiffInput(
        points=[[1.0, 1.0], [2.0, 4.0], [3.0, 9.0], [4.0, 16.0], [5.0, 25.0]],
        target_x=1.0,
        order=1,
    )
    res = solve(payload)
    assert res.topic_id == "newton_forward_difference"
    assert pytest.approx(res.result["derivative"], abs=1e-4) == 2.0
    assert len(res.steps) == 4
    assert res.plot_data is not None


def test_newton_forward_diff_2nd_order():
    """
    For y = x^2:
    Second derivative d²y/dx² is 2.0 everywhere.
    """
    payload = NewtonForwardDiffInput(
        points=[[1.0, 1.0], [2.0, 4.0], [3.0, 9.0], [4.0, 16.0], [5.0, 25.0]],
        target_x=1.0,
        order=2,
    )
    res = solve(payload)
    assert pytest.approx(res.result["derivative"], abs=1e-4) == 2.0


def test_newton_forward_diff_unequal_spacing_warning():
    """Points with non-constant gap should trigger a warning."""
    payload = NewtonForwardDiffInput(
        points=[[1.0, 1.0], [2.0, 4.0], [3.5, 12.25]],
        target_x=1.0,
        order=1,
    )
    res = solve(payload)
    assert len(res.warnings) > 0
    assert any("equally spaced" in w.lower() for w in res.warnings)
