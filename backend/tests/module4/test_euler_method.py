import pytest
import math
from fastapi.testclient import TestClient
from app.main import app
from app.solvers.module4.euler_method import solve, ODEInput

client = TestClient(app)


def test_euler_method_standard_case():
    # dy/dx = x + y, y(0) = 1, h = 0.1, x_end = 0.5
    payload = {
        "f_expr": "x + y",
        "x0": 0.0,
        "y0": 1.0,
        "h": 0.1,
        "x_end": 0.5,
    }
    res = solve(payload)

    assert res.topic_id == "euler_method"
    assert len(res.steps) == 5
    assert len(res.iterations_table) == 5

    # Check first step
    step1 = res.steps[0]
    assert step1.step_number == 1
    assert pytest.approx(step1.value, abs=1e-5) == 1.1

    # Check final result (1.72102)
    assert pytest.approx(res.result["final_y"], abs=1e-4) == 1.72102
    assert res.result["steps_count"] == 5

    # Check plot data
    assert res.plot_data is not None
    assert res.plot_data["type"] == "line"
    series = res.plot_data["series"][0]
    assert len(series["data"]) == 6  # initial point + 5 steps


def test_euler_convergence_with_step_size():
    # dy/dx = y, y(0) = 1 -> exact solution y(x) = e^x, at x=1 y(1) = e ≈ 2.71828
    e_exact = math.e

    res_coarse = solve({"f_expr": "y", "x0": 0.0, "y0": 1.0, "h": 0.1, "x_end": 1.0})
    err_coarse = abs(res_coarse.result["final_y"] - e_exact)

    res_fine = solve({"f_expr": "y", "x0": 0.0, "y0": 1.0, "h": 0.01, "x_end": 1.0})
    err_fine = abs(res_fine.result["final_y"] - e_exact)

    # Smaller step size must yield smaller error
    assert err_fine < err_coarse


def test_euler_validation_errors():
    # Zero step size
    with pytest.raises(ValueError, match="Step size h cannot be zero"):
        solve({"f_expr": "x + y", "x0": 0.0, "y0": 1.0, "h": 0.0, "x_end": 1.0})

    # Incompatible direction
    with pytest.raises(ValueError, match="sign does not match direction"):
        solve({"f_expr": "x + y", "x0": 1.0, "y0": 1.0, "h": 0.1, "x_end": 0.0})

    # Too many steps (> 500)
    with pytest.raises(ValueError, match="exceeds limit"):
        solve({"f_expr": "x + y", "x0": 0.0, "y0": 1.0, "h": 0.001, "x_end": 1.0})


def test_euler_endpoint_via_api():
    payload = {
        "f_expr": "x + y",
        "x0": 0.0,
        "y0": 1.0,
        "h": 0.1,
        "x_end": 0.2,
    }
    response = client.post("/api/solve/euler_method", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == "euler_method"
    assert len(data["steps"]) == 2
    assert pytest.approx(data["result"]["final_y"], abs=1e-4) == 1.22
