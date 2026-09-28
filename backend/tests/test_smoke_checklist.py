import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_smoke_all_edge_cases():
    print("\n--- RUNNING 15 TOPIC SMOKE & EDGE-CASE AUDIT ---")

    # 1. Fixed Point Iteration: g(x) = 2*x (diverges)
    res = client.post("/api/solve/fixed_point_iteration", json={"g_expr": "2*x", "x0": 1.0, "max_iter": 10, "tol": 1e-5})
    assert res.status_code == 200
    assert len(res.json()["warnings"]) > 0
    print("✓ Topic 1 (Fixed Point): Divergence warning verified.")

    # 2. Secant Method: x0 = x1 (near-zero denominator)
    res = client.post("/api/solve/secant_method", json={"f_expr": "x**2 - 4", "x0": 2.0, "x1": 2.0, "tol": 1e-5})
    assert res.status_code == 200
    assert len(res.json()["warnings"]) > 0
    print("✓ Topic 2 (Secant): Near-zero denominator warning verified.")

    # 3. Gauss-Jordan Solve: singular matrix (identical rows)
    res = client.post("/api/solve/gauss_jordan_solve", json={"A": [[1.0, 2.0], [1.0, 2.0]], "B": [3.0, 3.0]})
    assert res.status_code == 200
    assert len(res.json()["warnings"]) > 0
    print("✓ Topic 3 (Gauss-Jordan Solve): Singularity warning verified.")

    # 4. Lagrange: points interpolation
    res = client.post("/api/solve/lagrange_interpolation", json={"points": [[1.0, 2.0], [3.0, 6.0]], "target_x": 2.0})
    assert res.status_code == 200
    assert pytest.approx(res.json()["result"]["interpolated_value"], abs=1e-5) == 4.0
    print("✓ Topic 4 (Lagrange): Points interpolation verified.")

    # 5. Cubic Spline: 3 points minimal boundary
    res = client.post("/api/solve/cubic_spline_interpolation", json={"points": [[0.0, 0.0], [1.0, 1.0], [2.0, 0.0]], "x_eval": 0.5})
    assert res.status_code == 200
    print("✓ Topic 5 (Cubic Spline): Spline interpolation verified.")

    # 6. Least Squares: identical x points (undefined slope warning)
    res = client.post("/api/solve/least_squares_fit", json={"points": [[2.0, 1.0], [2.0, 3.0], [2.0, 5.0]]})
    assert res.status_code == 200
    assert len(res.json()["warnings"]) > 0
    print("✓ Topic 6 (Least Squares): Identical x slope warning verified.")

    # 7. Newton Forward Difference: unequal spacing warning
    res = client.post("/api/solve/newton_forward_difference", json={"points": [[1.0, 1.0], [2.0, 4.0], [4.0, 16.0]], "x_eval": 1.5, "order": 1})
    assert res.status_code == 200
    assert len(res.json()["warnings"]) > 0
    print("✓ Topic 7 (Newton Forward): Spacing warning verified.")

    # 8. Trapezoidal: n=0 validation error
    res = client.post("/api/solve/trapezoidal_rule", json={"f_expr": "x**2", "a": 0.0, "b": 1.0, "n": 0})
    assert res.status_code in [400, 422]
    print("✓ Topic 8 (Trapezoidal): n=0 validation error rejected properly.")

    # 9. Simpson's 1/3: odd n=5 validation error
    res = client.post("/api/solve/simpsons_one_third_rule", json={"f_expr": "x**2", "a": 0.0, "b": 1.0, "n": 5})
    assert res.status_code in [400, 422]
    print("✓ Topic 9 (Simpson's): Odd n validation error rejected properly.")

    # 10. Euler: large h
    res = client.post("/api/solve/euler_method", json={"f_expr": "x + y", "x0": 0.0, "y0": 1.0, "h": 0.5, "x_end": 1.0})
    assert res.status_code == 200
    print("✓ Topic 10 (Euler): Large h handled gracefully.")

    # 11. Modified Euler: large h
    res = client.post("/api/solve/modified_euler_method", json={"f_expr": "x + y", "x0": 0.0, "y0": 1.0, "h": 0.5, "x_end": 1.0})
    assert res.status_code == 200
    print("✓ Topic 11 (Modified Euler): Handled gracefully.")

    # 12. Runge-Kutta 4: large h
    res = client.post("/api/solve/runge_kutta_4", json={"f_expr": "x + y", "x0": 0.0, "y0": 1.0, "h": 0.5, "x_end": 1.0})
    assert res.status_code == 200
    print("✓ Topic 12 (RK4): Handled gracefully.")

    # 13. FD BVP: N=0 validation error
    res = client.post("/api/solve/finite_difference_bvp", json={"p_expr": "0", "q_expr": "0", "r_expr": "0", "a": 0.0, "b": 1.0, "N": 0})
    assert res.status_code in [400, 422] or "at least 1" in res.text
    print("✓ Topic 13 (FD BVP): N=0 rejected properly.")

    # 14. Heat Equation: r > 0.5 stability warning
    res = client.post("/api/solve/heat_equation_explicit", json={"alpha": 1.0, "L": 1.0, "u0_expr": "sin(pi*x)", "u_left": 0.0, "u_right": 0.0, "Nx": 4, "Nt": 2, "T": 0.1})
    assert res.status_code == 200
    assert len(res.json()["warnings"]) > 0
    assert res.json()["result"]["stable"] is False
    print("✓ Topic 14 (Heat Equation): r > 0.5 stability warning verified.")

    # 15. Matrix Inversion: singular matrix warning
    res = client.post("/api/solve/matrix_inversion_gauss_jordan", json={"A": [[1.0, 2.0], [2.0, 4.0]]})
    assert res.status_code == 200
    assert res.json()["result"]["is_invertible"] is False
    assert len(res.json()["warnings"]) > 0
    print("✓ Topic 15 (Matrix Inversion): Singular matrix warning verified.")

    print("\nALL 15 SMOKE CHECKLIST ROWS CONFIRMED!")
