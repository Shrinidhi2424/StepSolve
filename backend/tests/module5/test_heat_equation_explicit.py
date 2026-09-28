import pytest
import numpy as np
from fastapi.testclient import TestClient
from app.main import app
from app.solvers.module5.heat_equation_explicit import solve

client = TestClient(app)


def test_heat_equation_uniform_steady():
    # Uniform IC 10.0 with boundary conditions pinned to 10.0
    payload = {
        "alpha": 1.0,
        "L": 1.0,
        "u0_expr": "10.0",
        "u_left": 10.0,
        "u_right": 10.0,
        "Nx": 4,
        "Nt": 10,
        "T": 0.02,  # r = 1.0 * (0.02/10) / (0.25^2) = 0.002 / 0.0625 = 0.032 <= 0.5 (stable)
    }
    res = solve(payload)

    assert res.topic_id == "heat_equation_explicit"
    assert len(res.warnings) == 0
    assert res.result["stable"] is True

    # Profile should remain constant 10.0
    for val in res.result["final_profile"]:
        assert pytest.approx(val, abs=1e-5) == 10.0


def test_heat_equation_stability_warning():
    # Force r > 0.5: dx = 1/4 = 0.25 -> dx^2 = 0.0625. If alpha=1.0, dt = 0.1/2 = 0.05 -> r = 0.8
    payload = {
        "alpha": 1.0,
        "L": 1.0,
        "u0_expr": "sin(pi*x)",
        "u_left": 0.0,
        "u_right": 0.0,
        "Nx": 4,
        "Nt": 2,
        "T": 0.1,
    }
    res = solve(payload)
    assert res.result["stable"] is False
    assert any("conditionally stable only for r ≤ 0.5" in w for w in res.warnings)


def test_heat_equation_plot_data_snapshots():
    payload = {
        "alpha": 1.0,
        "L": 1.0,
        "u0_expr": "sin(pi*x)",
        "u_left": 0.0,
        "u_right": 0.0,
        "Nx": 4,
        "Nt": 10,
        "T": 0.05,
    }
    res = solve(payload)
    assert res.plot_data is not None
    assert res.plot_data["type"] == "multi_line"
    series = res.plot_data["series"]
    assert len(series) >= 3  # Multiple snapshots at distinct times


def test_heat_equation_validation_and_api():
    with pytest.raises(ValueError, match="Nx must be at least 2"):
        solve({"Nx": 1, "Nt": 10, "L": 1.0, "T": 0.1, "alpha": 1.0, "u0_expr": "x"})

    response = client.post(
        "/api/solve/heat_equation_explicit",
        json={
            "alpha": 1.0,
            "L": 1.0,
            "u0_expr": "sin(pi*x)",
            "u_left": 0.0,
            "u_right": 0.0,
            "Nx": 4,
            "Nt": 8,
            "T": 0.04,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == "heat_equation_explicit"
    assert "final_profile" in data["result"]
