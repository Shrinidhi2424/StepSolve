import pytest
from app.solvers.module2.least_squares_fit import solve, LeastSquaresInput


def test_least_squares_known_dataset():
    """Points: (1, 2.1), (2, 3.9), (3, 6.2), (4, 8.1), (5, 9.8)."""
    payload = LeastSquaresInput(
        points=[[1.0, 2.1], [2.0, 3.9], [3.0, 6.2], [4.0, 8.1], [5.0, 9.8]]
    )
    res = solve(payload)
    assert res.topic_id == "least_squares_fit"
    # b should be approx 1.95, a approx 0.17
    assert pytest.approx(res.result["b"], abs=0.05) == 1.95
    assert pytest.approx(res.result["a"], abs=0.05) == 0.17
    assert res.result["r_squared"] > 0.99
    assert len(res.steps) == 5
    assert len(res.iterations_table) == 5
    assert res.plot_data is not None


def test_least_squares_perfect_line():
    """Points exactly on y = 2x + 1 must yield R^2 = 1.0 and b = 2.0."""
    payload = LeastSquaresInput(
        points=[[0.0, 1.0], [1.0, 3.0], [2.0, 5.0], [3.0, 7.0]]
    )
    res = solve(payload)
    assert pytest.approx(res.result["b"], abs=1e-5) == 2.0
    assert pytest.approx(res.result["a"], abs=1e-5) == 1.0
    assert pytest.approx(res.result["r_squared"], abs=1e-5) == 1.0


def test_least_squares_identical_x_warning():
    """All identical x values (vertical line) must add a warning."""
    payload = LeastSquaresInput(
        points=[[2.0, 1.0], [2.0, 3.0], [2.0, 5.0]]
    )
    res = solve(payload)
    assert len(res.warnings) > 0
    assert any("identical" in w.lower() or "undefined" in w.lower() for w in res.warnings)
