import pytest
import math
from fastapi.testclient import TestClient
from app.main import app
from app.solvers.module4.modified_euler_method import solve

client = TestClient(app)


def test_modified_euler_manual_calculation():
    # dy/dx = x + y, y(0) = 1, h = 0.1, x_end = 0.2
    payload = {
        "f_expr": "x + y",
        "x0": 0.0,
        "y0": 1.0,
        "h": 0.1,
        "x_end": 0.2,
    }
    res = solve(payload)

    assert res.topic_id == "modified_euler_method"
    # 2 intervals -> 2 predictor steps + 2 corrector steps = 4 steps total
    assert len(res.steps) == 4
    assert len(res.iterations_table) == 2

    # Step 1a: Predictor
    assert res.steps[0].title.startswith("Step 1a: Predictor")
    assert pytest.approx(res.steps[0].value, abs=1e-5) == 1.1

    # Step 1b: Corrector
    assert res.steps[1].title.startswith("Step 1b: Corrector")
    assert pytest.approx(res.steps[1].value, abs=1e-5) == 1.11

    # Step 2a: Predictor
    assert res.steps[2].title.startswith("Step 2a: Predictor")
    assert pytest.approx(res.steps[2].value, abs=1e-5) == 1.231

    # Step 2b: Corrector
    assert res.steps[3].title.startswith("Step 2b: Corrector")
    assert pytest.approx(res.steps[3].value, abs=1e-5) == 1.24205

    assert pytest.approx(res.result["final_y"], abs=1e-4) == 1.24205
    assert res.result["steps_count"] == 2


def test_modified_euler_superior_to_standard_euler():
    # Exact solution of dy/dx = y, y(0) = 1 is y(x) = e^x
    # At x = 0.5, exact = e^0.5 ≈ 1.64872127
    exact = math.exp(0.5)

    res_euler = client.post(
        "/api/solve/euler_method",
        json={"f_expr": "y", "x0": 0.0, "y0": 1.0, "h": 0.1, "x_end": 0.5},
    ).json()

    res_mod = client.post(
        "/api/solve/modified_euler_method",
        json={"f_expr": "y", "x0": 0.0, "y0": 1.0, "h": 0.1, "x_end": 0.5},
    ).json()

    err_euler = abs(res_euler["result"]["final_y"] - exact)
    err_mod = abs(res_mod["result"]["final_y"] - exact)

    # 2nd order Modified Euler must be substantially more accurate than 1st order Euler
    assert err_mod < err_euler / 5.0


def test_modified_euler_validation_and_api():
    # Incompatible direction
    with pytest.raises(ValueError, match="sign does not match direction"):
        solve({"f_expr": "x + y", "x0": 0.0, "y0": 1.0, "h": -0.1, "x_end": 0.5})

    # Valid API call
    response = client.post(
        "/api/solve/modified_euler_method",
        json={"f_expr": "x - y", "x0": 0.0, "y0": 1.0, "h": 0.1, "x_end": 0.3},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["steps"]) == 6  # 3 * 2
    assert len(data["iterations_table"]) == 3
