import pytest
import numpy as np
from fastapi.testclient import TestClient
from app.main import app
from app.solvers.module5.matrix_inversion_gauss_jordan import solve

client = TestClient(app)


def test_matrix_inversion_textbook_3x3():
    # A = [[1, 2, 3], [0, 1, 4], [5, 6, 0]]
    # Det(A) = 1(0 - 24) - 2(-20) + 3(-5) = 1
    A = [[1.0, 2.0, 3.0], [0.0, 1.0, 4.0], [5.0, 6.0, 0.0]]
    res = solve({"A": A})

    assert res.topic_id == "matrix_inversion_gauss_jordan"
    assert res.result["is_invertible"] is True
    assert len(res.warnings) == 0

    inv = np.array(res.result["inverse"])
    original = np.array(A)

    # A @ A_inv = I
    prod = original @ inv
    assert np.allclose(prod, np.eye(3), atol=1e-5)

    # Check verification step exists
    last_step = res.steps[-1]
    assert "Verification: A × A⁻¹ = I" in last_step.title
    assert last_step.value is not None


def test_matrix_inversion_identity_2x2():
    I2 = [[1.0, 0.0], [0.0, 1.0]]
    res = solve({"A": I2})
    inv = np.array(res.result["inverse"])
    assert np.allclose(inv, np.eye(2), atol=1e-6)


def test_matrix_inversion_singular_warning():
    # Rows are linearly dependent: [1, 2] and [2, 4]
    singular_A = [[1.0, 2.0], [2.0, 4.0]]
    res = solve({"A": singular_A})

    assert res.result["is_invertible"] is False
    assert any("singular or ill-conditioned" in w.lower() for w in res.warnings)


def test_matrix_inversion_validation_and_api():
    # Non-square matrix
    with pytest.raises(ValueError, match="must be square"):
        solve({"A": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]})

    response = client.post(
        "/api/solve/matrix_inversion_gauss_jordan",
        json={"A": [[2.0, 1.0], [5.0, 3.0]]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == "matrix_inversion_gauss_jordan"
    assert data["result"]["is_invertible"] is True
    # Inverse of [[2, 1], [5, 3]] is [[3, -1], [-5, 2]]
    inv = data["result"]["inverse"]
    assert pytest.approx(inv[0][0], abs=1e-5) == 3.0
    assert pytest.approx(inv[0][1], abs=1e-5) == -1.0
    assert pytest.approx(inv[1][0], abs=1e-5) == -5.0
    assert pytest.approx(inv[1][1], abs=1e-5) == 2.0
