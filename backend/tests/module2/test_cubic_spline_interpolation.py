import pytest
from app.solvers.module2.cubic_spline_interpolation import solve, CubicSplineInput


def test_cubic_spline_natural_boundary_conditions():
    """Verify that M_0 = 0 and M_n = 0 are strictly enforced for natural cubic spline."""
    payload = CubicSplineInput(
        points=[[1.0, 1.0], [2.0, 5.0], [3.0, 11.0], [4.0, 8.0]],
        target_x=2.5,
    )
    res = solve(payload)
    assert res.topic_id == "cubic_spline_interpolation"
    M = res.result["second_derivatives"]
    assert M[0] == 0.0
    assert M[-1] == 0.0
    assert len(M) == 4
    assert len(res.steps) == 5
    assert res.plot_data is not None
    # S(2.5) should be between S(2)=5 and S(3)=11
    val = res.result["interpolated_value"]
    assert 5.0 < val < 11.0


def test_cubic_spline_node_evaluation():
    """At an exact node x = 2.0, spline value should match y_node = 5.0."""
    payload = CubicSplineInput(
        points=[[1.0, 1.0], [2.0, 5.0], [3.0, 11.0], [4.0, 8.0]],
        target_x=2.0,
    )
    res = solve(payload)
    assert pytest.approx(res.result["interpolated_value"], abs=1e-5) == 5.0


def test_cubic_spline_min_points_error():
    """Less than 3 points must raise ValueError."""
    with pytest.raises(ValueError, match="At least 3 data points"):
        solve(CubicSplineInput(points=[[1.0, 2.0], [2.0, 3.0]], target_x=1.5))
