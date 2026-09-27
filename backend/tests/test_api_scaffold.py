import pytest
import numpy as np
from fastapi.testclient import TestClient
from app.main import app
from app.registry import TOPICS
from app.core.expr_eval import parse_single_var, parse_two_var, validate_expression
from app.core.linear_algebra import thomas_algorithm, gauss_jordan_core
from app.core.finite_differences import build_forward_difference_table

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_topics_endpoint():
    response = client.get("/api/topics")
    assert response.status_code == 200
    topics = response.json()
    assert len(topics) == 15

    # Check distribution: 3 topics per module
    module_counts = {}
    for t in topics:
        m = t["module"]
        module_counts[m] = module_counts.get(m, 0) + 1
        assert "id" in t
        assert "title" in t
        assert "short_description" in t
        assert "input_schema" in t
        assert len(t["input_schema"]) > 0

    assert module_counts == {1: 3, 2: 3, 3: 3, 4: 3, 5: 3}


def test_single_topic_detail():
    response = client.get("/api/topics/secant_method")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "secant_method"
    assert data["module"] == 1


def test_topic_not_found():
    response = client.get("/api/topics/non_existent_topic")
    assert response.status_code == 404


def test_solve_stub_returns_501():
    # Calling an un-implemented stub (e.g. fixed_point_iteration before Phase 2) returns 501
    response = client.post("/api/solve/fixed_point_iteration", json={})
    assert response.status_code == 501
    assert "not yet implemented" in response.json()["detail"].lower()


def test_expr_eval_safe_functions():
    f = parse_single_var("x**3 - x - 2")
    assert pytest.approx(f(2.0)) == 4.0

    g = parse_single_var("cos(x)")
    assert pytest.approx(g(0.0)) == 1.0

    ode_fn = parse_two_var("x + y")
    assert pytest.approx(ode_fn(1.0, 2.0)) == 3.0


def test_expr_eval_rejects_unsafe():
    is_valid, err = validate_expression("__import__('os').system('ls')")
    assert not is_valid
    assert err is not None

    with pytest.raises(ValueError):
        parse_single_var("__import__('sys')")

    with pytest.raises(ValueError):
        parse_single_var("z + 1")  # z is not allowed when var is x


def test_thomas_algorithm():
    # Solve:
    # 2*x0 - x1 = 1
    # -x0 + 2*x1 - x2 = 0
    # -x1 + 2*x2 = 1
    # Solution is x = [1, 1, 1]
    a = [0.0, -1.0, -1.0]
    b = [2.0, 2.0, 2.0]
    c = [-1.0, -1.0, 0.0]
    d = [1.0, 0.0, 1.0]
    sol = thomas_algorithm(a, b, c, d)
    assert len(sol) == 3
    assert np.allclose(sol, [1.0, 1.0, 1.0], atol=1e-5)


def test_gauss_jordan_core():
    # Augmented matrix for:
    # 2x + y = 5
    # x + 3y = 5
    # Solution: x = 2, y = 1
    aug = np.array([[2.0, 1.0, 5.0], [1.0, 3.0, 5.0]])
    rref, steps, warnings = gauss_jordan_core(aug)
    assert len(steps) >= 2
    assert len(warnings) == 0
    sol = rref[:, -1]
    assert np.allclose(sol, [2.0, 1.0], atol=1e-5)


def test_finite_differences():
    # For y = [1, 4, 9, 16] (y = x^2 for x = 1, 2, 3, 4)
    # Δy = [3, 5, 7]
    # Δ²y = [2, 2]
    # Δ³y = [0]
    y = [1.0, 4.0, 9.0, 16.0]
    table = build_forward_difference_table(y)
    assert table[0][0] == 1.0
    assert table[0][1] == 3.0
    assert table[0][2] == 2.0
    assert table[0][3] == 0.0
