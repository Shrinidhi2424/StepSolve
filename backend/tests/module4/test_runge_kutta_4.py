import pytest
import math
from fastapi.testclient import TestClient
from app.main import app
from app.solvers.module4.runge_kutta_4 import solve

client = TestClient(app)


def test_rk4_manual_one_step():
    # dy/dx = x + y, y(0) = 1, h = 0.1, x_end = 0.1
    payload = {
        "f_expr": "x + y",
        "x0": 0.0,
        "y0": 1.0,
        "h": 0.1,
        "x_end": 0.1,
    }
    res = solve(payload)

    assert res.topic_id == "runge_kutta_4"
    # 1 interval -> 5 sub-steps: k1, k2, k3, k4, and y update
    assert len(res.steps) == 5
    assert len(res.iterations_table) == 1

    # Check k1, k2, k3, k4
    assert pytest.approx(res.steps[0].value, abs=1e-5) == 0.1
    assert pytest.approx(res.steps[1].value, abs=1e-5) == 0.11
    assert pytest.approx(res.steps[2].value, abs=1e-5) == 0.1105
    assert pytest.approx(res.steps[3].value, abs=1e-5) == 0.12105

    # Check final y1 = 1.110342
    assert pytest.approx(res.result["final_y"], abs=1e-5) == 1.110342
    assert pytest.approx(res.steps[4].value, abs=1e-5) == 1.110342

    # Check table
    row = res.iterations_table[0]
    assert row["step"] == 1
    assert pytest.approx(row["k1"], abs=1e-5) == 0.1
    assert pytest.approx(row["k2"], abs=1e-5) == 0.11
    assert pytest.approx(row["k3"], abs=1e-5) == 0.1105
    assert pytest.approx(row["k4"], abs=1e-5) == 0.12105
    assert pytest.approx(row["y_next"], abs=1e-5) == 1.110342


def test_rk4_high_order_accuracy():
    # dy/dx = y, y(0) = 1 -> exact y(1) = e ≈ 2.718281828459
    exact = math.e

    res_rk4 = solve({"f_expr": "y", "x0": 0.0, "y0": 1.0, "h": 0.1, "x_end": 1.0})
    err_rk4 = abs(res_rk4.result["final_y"] - exact)

    # 4th order error with h=0.1 should be <= 1e-4
    assert err_rk4 < 1e-4

    # Compare against Euler and Modified Euler
    res_euler = client.post(
        "/api/solve/euler_method",
        json={"f_expr": "y", "x0": 0.0, "y0": 1.0, "h": 0.1, "x_end": 1.0},
    ).json()
    res_mod = client.post(
        "/api/solve/modified_euler_method",
        json={"f_expr": "y", "x0": 0.0, "y0": 1.0, "h": 0.1, "x_end": 1.0},
    ).json()

    err_euler = abs(res_euler["result"]["final_y"] - exact)
    err_mod = abs(res_mod["result"]["final_y"] - exact)

    assert err_rk4 < err_mod < err_euler


def test_rk4_validation_and_api():
    # Incompatible direction
    with pytest.raises(ValueError, match="sign does not match direction"):
        solve({"f_expr": "x + y", "x0": 1.0, "y0": 1.0, "h": 0.1, "x_end": 0.5})

    # Valid API call with 2 steps
    response = client.post(
        "/api/solve/runge_kutta_4",
        json={"f_expr": "x**2 - y", "x0": 0.0, "y0": 1.0, "h": 0.1, "x_end": 0.2},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["steps"]) == 10  # 2 intervals * 5 steps
    assert len(data["iterations_table"]) == 2
    assert "plot_data" in data
