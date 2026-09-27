import pytest
from app.solvers.module2.lagrange_interpolation import solve, LagrangeInput


def test_lagrange_polynomial_interpolation():
    """Points: (0, 1), (1, 3), (2, 7), (4, 21) from y = x^2 + x + 1. Evaluate at x = 2.5 -> y = 9.75."""
    payload = LagrangeInput(
        points=[[0.0, 1.0], [1.0, 3.0], [2.0, 7.0], [4.0, 21.0]],
        target_x=2.5,
        inverse=0,
    )
    res = solve(payload)
    assert res.topic_id == "lagrange_interpolation"
    assert pytest.approx(res.result["interpolated_value"], abs=1e-4) == 9.75
    assert len(res.steps) == 5  # 4 basis polynomials + 1 sum step
    assert len(res.iterations_table) == 4
    assert res.plot_data is not None


def test_lagrange_inverse_interpolation():
    """Inverse interpolation: find x for which y = 7 -> expected x = 2.0."""
    payload = LagrangeInput(
        points=[[0.0, 1.0], [1.0, 3.0], [2.0, 7.0], [4.0, 21.0]],
        target_x=7.0,
        inverse=1,
    )
    res = solve(payload)
    assert res.result["is_inverse"] is True
    assert pytest.approx(res.result["interpolated_value"], abs=1e-3) == 2.0


def test_lagrange_duplicate_abscissa_error():
    """Duplicate x points should trigger ValueError."""
    with pytest.raises(ValueError, match="Duplicate"):
        solve(LagrangeInput(points=[[1.0, 2.0], [1.0, 4.0]], target_x=1.5))
