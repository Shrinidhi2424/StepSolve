import pytest
from app.solvers.module1.fixed_point_iteration import solve, FixedPointInput


def test_fixed_point_cos_convergence():
    """Solve x = cos(x) starting from x0=0.5 -> root approx 0.7391."""
    payload = FixedPointInput(
        g_expr="cos(x)",
        x0=0.5,
        tolerance=1e-4,
        max_iterations=50,
    )
    res = solve(payload)
    assert res.topic_id == "fixed_point_iteration"
    assert res.result["converged"] is True
    assert pytest.approx(res.result["root"], abs=1e-4) == 0.7391
    assert len(res.steps) >= 5
    assert len(res.iterations_table) == res.result["iterations"]
    assert res.plot_data is not None


def test_fixed_point_divergence_detection():
    """Function with |g'(x)| > 1: g(x) = 2*x + 1 -> error grows strictly; should detect divergence."""
    payload = FixedPointInput(
        g_expr="2*x + 1",
        x0=1.0,
        tolerance=1e-4,
        max_iterations=30,
    )
    res = solve(payload)
    assert res.result["converged"] is False
    assert len(res.warnings) > 0
    assert any("diverg" in w.lower() for w in res.warnings)


def test_fixed_point_max_iterations_cap():
    """Slowly converging iteration with very small max_iterations."""
    payload = FixedPointInput(
        g_expr="cos(x)",
        x0=0.1,
        tolerance=1e-8,
        max_iterations=3,
    )
    res = solve(payload)
    assert res.result["converged"] is False
    assert len(res.steps) == 3
    assert any("maximum iteration" in w.lower() for w in res.warnings)
