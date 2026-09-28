import pytest
import math
import numpy as np
from fastapi.testclient import TestClient
from app.main import app
from app.solvers.module5.finite_difference_bvp import solve

client = TestClient(app)


def test_bvp_sinh_analytical():
    # y'' - y = 0, y(0) = 0, y(1) = sinh(1) ≈ 1.17520119
    # Exact solution: y(x) = sinh(x)
    sinh1 = math.sinh(1.0)
    payload = {
        "p_expr": "0",
        "q_expr": "-1",
        "r_expr": "0",
        "a": 0.0,
        "b": 1.0,
        "alpha": 0.0,
        "beta": sinh1,
        "N": 4,
    }
    res = solve(payload)

    assert res.topic_id == "finite_difference_bvp"
    assert len(res.steps) == 3
    assert len(res.iterations_table) == 6  # 4 interior + 2 boundary

    mesh = res.result["mesh"]
    solution = res.result["solution"]
    assert len(mesh) == 6
    assert len(solution) == 6

    # Compare interior points against exact sinh(x)
    for x_val, y_val in zip(mesh, solution):
        exact_y = math.sinh(x_val)
        # O(h^2) truncation error for h = 0.2 is ~ 0.005
        assert pytest.approx(y_val, abs=5e-3) == exact_y

    assert res.plot_data is not None
    assert res.plot_data["type"] == "line"


def test_bvp_exact_linear():
    # y'' = 0, y(0) = 1, y(2) = 5 -> exact y(x) = 1 + 2x
    # Central difference has 0 truncation error for polynomials of degree <= 3
    payload = {
        "p_expr": "0",
        "q_expr": "0",
        "r_expr": "0",
        "a": 0.0,
        "b": 2.0,
        "alpha": 1.0,
        "beta": 5.0,
        "N": 3,
    }
    res = solve(payload)
    mesh = res.result["mesh"]
    solution = res.result["solution"]

    for x_val, y_val in zip(mesh, solution):
        exact_y = 1.0 + 2.0 * x_val
        assert pytest.approx(y_val, abs=1e-5) == exact_y


def test_bvp_validation_errors():
    with pytest.raises(ValueError, match="strictly greater than left boundary"):
        solve({"p_expr": "0", "q_expr": "0", "r_expr": "0", "a": 2.0, "b": 1.0, "N": 4})

    with pytest.raises(ValueError, match="at least 1"):
        solve({"p_expr": "0", "q_expr": "0", "r_expr": "0", "a": 0.0, "b": 1.0, "N": 0})


def test_bvp_api_endpoint():
    payload = {
        "p_expr": "0",
        "q_expr": "-1",
        "r_expr": "0",
        "a": 0.0,
        "b": 1.0,
        "alpha": 0.0,
        "beta": 1.1752,
        "N": 4,
    }
    response = client.post("/api/solve/finite_difference_bvp", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == "finite_difference_bvp"
    assert len(data["steps"]) == 3
    assert len(data["result"]["solution"]) == 6
