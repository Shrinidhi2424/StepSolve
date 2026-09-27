import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.solvers.module1.secant_method import solve, SecantInput

client = TestClient(app)


def test_secant_textbook_example():
    """Textbook example: f(x) = x^3 - x - 2 with x0=1, x1=2 -> root approx 1.5214."""
    payload = SecantInput(
        f_expr="x**3 - x - 2",
        x0=1.0,
        x1=2.0,
        tolerance=1e-4,
        max_iterations=50,
    )
    res = solve(payload)
    assert res.topic_id == "secant_method"
    assert res.result["converged"] is True
    assert pytest.approx(res.result["root"], rel=1e-3) == 1.5214
    assert len(res.steps) >= 3
    assert res.iterations_table is not None
    assert len(res.iterations_table) == res.result["iterations"]
    assert res.plot_data is not None


def test_secant_near_zero_denominator_warning():
    """Near-zero denominator: identical initial guesses generate warning without crashing."""
    payload = {
        "f_expr": "x**2 - 4",
        "x0": 3.0,
        "x1": 3.0,
        "tolerance": 1e-4,
        "max_iterations": 20,
    }
    res = solve(payload)
    assert len(res.warnings) > 0
    assert any("identical" in w.lower() or "denominator" in w.lower() for w in res.warnings)


def test_secant_non_convergence_warning():
    """Capped iterations on slow function trigger non-convergence warning."""
    payload = SecantInput(
        f_expr="x**5 - x - 1",
        x0=1.0,
        x1=2.0,
        tolerance=1e-8,
        max_iterations=2,
    )
    res = solve(payload)
    assert res.result["converged"] is False
    assert len(res.warnings) > 0
    assert any("maximum iteration" in w.lower() for w in res.warnings)


def test_secant_simple_linear_root():
    """Simple linear function f(x) = x - 2 with x0=0, x1=3 -> root = 2.0 exactly in 1 step."""
    payload = SecantInput(
        f_expr="x - 2",
        x0=0.0,
        x1=3.0,
        tolerance=1e-5,
        max_iterations=10,
    )
    res = solve(payload)
    assert res.result["converged"] is True
    assert pytest.approx(res.result["root"], abs=1e-5) == 2.0


def test_secant_transcendental_trig():
    """Trig equation f(x) = cos(x) - x with x0=0, x1=1 -> root approx 0.739085."""
    payload = SecantInput(
        f_expr="cos(x) - x",
        x0=0.0,
        x1=1.0,
        tolerance=1e-5,
        max_iterations=30,
    )
    res = solve(payload)
    assert res.result["converged"] is True
    assert pytest.approx(res.result["root"], abs=1e-4) == 0.7391


def test_secant_api_post_endpoint():
    """Integration test: POST /api/solve/secant_method via FastAPI test client."""
    response = client.post(
        "/api/solve/secant_method",
        json={
            "f_expr": "x**3 - x - 2",
            "x0": 1.0,
            "x1": 2.0,
            "tolerance": 0.0001,
            "max_iterations": 50,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == "secant_method"
    assert "Root ≈ 1.521" in data["result_summary"]
    assert len(data["steps"]) >= 4
    assert len(data["iterations_table"]) >= 4
    assert data["result"]["converged"] is True
    assert pytest.approx(data["result"]["root"], abs=1e-3) == 1.5214
