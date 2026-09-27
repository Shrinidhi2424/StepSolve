from typing import Dict, Any, List

TOPICS: Dict[str, Dict[str, Any]] = {
    # MODULE 1
    "fixed_point_iteration": {
        "id": "fixed_point_iteration",
        "module": 1,
        "title": "Fixed Point Iteration Method",
        "short_description": "Find real roots of f(x) = 0 by rewriting into x = g(x) and computing successive approximations.",
        "input_schema": [
            {"name": "g_expr", "type": "function", "label": "Iteration formula g(x)", "default": "cos(x)"},
            {"name": "x0", "type": "number", "label": "Initial guess x₀", "default": 0.5},
            {"name": "tolerance", "type": "number", "label": "Convergence tolerance (ε)", "default": 0.0001},
            {"name": "max_iterations", "type": "number", "label": "Maximum iterations", "default": 50},
        ],
        "solve_fn": "app.solvers.module1.fixed_point_iteration.solve",
    },
    "secant_method": {
        "id": "secant_method",
        "module": 1,
        "title": "Secant Method",
        "short_description": "Determine roots of f(x) = 0 using two initial approximations without requiring derivative evaluation.",
        "input_schema": [
            {"name": "f_expr", "type": "function", "label": "Function f(x)", "default": "x**3 - x - 2"},
            {"name": "x0", "type": "number", "label": "Initial guess x₀", "default": 1.0},
            {"name": "x1", "type": "number", "label": "Second guess x₁", "default": 2.0},
            {"name": "tolerance", "type": "number", "label": "Convergence tolerance (ε)", "default": 0.0001},
            {"name": "max_iterations", "type": "number", "label": "Maximum iterations", "default": 50},
        ],
        "solve_fn": "app.solvers.module1.secant_method.solve",
    },
    "gauss_jordan_solve": {
        "id": "gauss_jordan_solve",
        "module": 1,
        "title": "Gauss-Jordan Elimination (AX = B)",
        "short_description": "Directly solve a system of n linear equations with n unknowns using full reduced row-echelon form.",
        "input_schema": [
            {
                "name": "A",
                "type": "matrix",
                "label": "Coefficient matrix A (n × n)",
                "default": [[2.0, 1.0, -1.0], [-3.0, -1.0, 2.0], [-2.0, 1.0, 2.0]],
            },
            {
                "name": "B",
                "type": "matrix",
                "label": "Constant column vector B (n × 1)",
                "default": [[8.0], [-11.0], [-3.0]],
            },
        ],
        "solve_fn": "app.solvers.module1.gauss_jordan_solve.solve",
    },
    # MODULE 2
    "lagrange_interpolation": {
        "id": "lagrange_interpolation",
        "module": 2,
        "title": "Lagrange Interpolation",
        "short_description": "Construct an interpolating polynomial through unequal interval data points with optional inverse interpolation.",
        "input_schema": [
            {
                "name": "points",
                "type": "table",
                "label": "Data points (x, y)",
                "default": [[0.0, 1.0], [1.0, 3.0], [2.0, 7.0], [4.0, 21.0]],
            },
            {"name": "target_x", "type": "number", "label": "Target x to evaluate", "default": 2.5},
            {"name": "inverse", "type": "number", "label": "Inverse mode (1 for x(y), 0 for y(x))", "default": 0},
        ],
        "solve_fn": "app.solvers.module2.lagrange_interpolation.solve",
    },
    "cubic_spline_interpolation": {
        "id": "cubic_spline_interpolation",
        "module": 2,
        "title": "Cubic Spline Interpolation (Natural Spline)",
        "short_description": "Fit smooth piecewise cubic polynomials across data points with natural boundary conditions S''(x₀) = S''(xₙ) = 0.",
        "input_schema": [
            {
                "name": "points",
                "type": "table",
                "label": "Data points (x, y)",
                "default": [[1.0, 1.0], [2.0, 5.0], [3.0, 11.0], [4.0, 8.0]],
            },
            {"name": "target_x", "type": "number", "label": "Target x to evaluate", "default": 2.5},
        ],
        "solve_fn": "app.solvers.module2.cubic_spline_interpolation.solve",
    },
    "least_squares_fit": {
        "id": "least_squares_fit",
        "module": 2,
        "title": "Curve Fitting — Least Squares (y = a + bx)",
        "short_description": "Determine best-fit linear regression parameters a and b by minimizing sum of squared residuals.",
        "input_schema": [
            {
                "name": "points",
                "type": "table",
                "label": "Observed data points (x, y)",
                "default": [[1.0, 2.1], [2.0, 3.9], [3.0, 6.2], [4.0, 8.1], [5.0, 9.8]],
            }
        ],
        "solve_fn": "app.solvers.module2.least_squares_fit.solve",
    },
    # MODULE 3
    "newton_forward_difference": {
        "id": "newton_forward_difference",
        "module": 3,
        "title": "Numerical Differentiation (Newton's Forward Difference)",
        "short_description": "Estimate first and second order derivatives from equally spaced tabulated values using forward difference series.",
        "input_schema": [
            {
                "name": "points",
                "type": "table",
                "label": "Equally spaced data points (x, y)",
                "default": [[10.0, 0.1736], [20.0, 0.3420], [30.0, 0.5000], [40.0, 0.6428]],
            },
            {"name": "target_x", "type": "number", "label": "Value of x at which to differentiate", "default": 10.0},
            {"name": "order", "type": "number", "label": "Derivative order (1 or 2)", "default": 1},
        ],
        "solve_fn": "app.solvers.module3.newton_forward_difference.solve",
    },
    "trapezoidal_rule": {
        "id": "trapezoidal_rule",
        "module": 3,
        "title": "Trapezoidal Rule (Integration)",
        "short_description": "Approximate definite integral ∫ f(x) dx by approximating area under curve with trapezoids.",
        "input_schema": [
            {"name": "f_expr", "type": "function", "label": "Integrand function f(x)", "default": "1 / (1 + x**2)"},
            {"name": "a", "type": "number", "label": "Lower limit a", "default": 0.0},
            {"name": "b", "type": "number", "label": "Upper limit b", "default": 1.0},
            {"name": "n", "type": "number", "label": "Subintervals count n", "default": 6},
        ],
        "solve_fn": "app.solvers.module3.trapezoidal_rule.solve",
    },
    "simpsons_one_third_rule": {
        "id": "simpsons_one_third_rule",
        "module": 3,
        "title": "Simpson's 1/3 Rule (Integration)",
        "short_description": "Evaluate definite integral using parabolic segments across even number of subintervals.",
        "input_schema": [
            {"name": "f_expr", "type": "function", "label": "Integrand function f(x)", "default": "1 / (1 + x**2)"},
            {"name": "a", "type": "number", "label": "Lower limit a", "default": 0.0},
            {"name": "b", "type": "number", "label": "Upper limit b", "default": 1.0},
            {"name": "n", "type": "number", "label": "Subintervals count n (even)", "default": 6},
        ],
        "solve_fn": "app.solvers.module3.simpsons_one_third_rule.solve",
    },
    # MODULE 4
    "euler_method": {
        "id": "euler_method",
        "module": 4,
        "title": "Euler's Method (ODE IVP)",
        "short_description": "Solve first-order initial value problem dy/dx = f(x, y) with tangent-line step progression.",
        "input_schema": [
            {"name": "f_expr", "type": "function", "label": "Derivative f(x, y) = dy/dx", "default": "x + y"},
            {"name": "x0", "type": "number", "label": "Initial x₀", "default": 0.0},
            {"name": "y0", "type": "number", "label": "Initial y₀ = y(x₀)", "default": 1.0},
            {"name": "h", "type": "number", "label": "Step size h", "default": 0.1},
            {"name": "x_end", "type": "number", "label": "Target x (terminal)", "default": 0.5},
        ],
        "solve_fn": "app.solvers.module4.euler_method.solve",
    },
    "modified_euler_method": {
        "id": "modified_euler_method",
        "module": 4,
        "title": "Modified Euler's Method (Heun's Predictor-Corrector)",
        "short_description": "Second-order predictor-corrector method averaging slopes at beginning and predicted end of step.",
        "input_schema": [
            {"name": "f_expr", "type": "function", "label": "Derivative f(x, y) = dy/dx", "default": "x + y"},
            {"name": "x0", "type": "number", "label": "Initial x₀", "default": 0.0},
            {"name": "y0", "type": "number", "label": "Initial y₀ = y(x₀)", "default": 1.0},
            {"name": "h", "type": "number", "label": "Step size h", "default": 0.1},
            {"name": "x_end", "type": "number", "label": "Target x (terminal)", "default": 0.5},
        ],
        "solve_fn": "app.solvers.module4.modified_euler_method.solve",
    },
    "runge_kutta_4": {
        "id": "runge_kutta_4",
        "module": 4,
        "title": "Runge-Kutta 4th Order (RK4)",
        "short_description": "Fourth-order ODE solver computing four weighted slope increments (k₁, k₂, k₃, k₄) per step.",
        "input_schema": [
            {"name": "f_expr", "type": "function", "label": "Derivative f(x, y) = dy/dx", "default": "x + y"},
            {"name": "x0", "type": "number", "label": "Initial x₀", "default": 0.0},
            {"name": "y0", "type": "number", "label": "Initial y₀ = y(x₀)", "default": 1.0},
            {"name": "h", "type": "number", "label": "Step size h", "default": 0.1},
            {"name": "x_end", "type": "number", "label": "Target x (terminal)", "default": 0.5},
        ],
        "solve_fn": "app.solvers.module4.runge_kutta_4.solve",
    },
    # MODULE 5
    "finite_difference_bvp": {
        "id": "finite_difference_bvp",
        "module": 5,
        "title": "Finite Difference Method (2nd-Order Linear ODE BVP)",
        "short_description": "Solve two-point boundary value problem y'' + p(x)y' + q(x)y = r(x) using central difference discretization.",
        "input_schema": [
            {"name": "p_expr", "type": "function", "label": "p(x) coefficient for y'", "default": "0"},
            {"name": "q_expr", "type": "function", "label": "q(x) coefficient for y", "default": "-1"},
            {"name": "r_expr", "type": "function", "label": "r(x) RHS term", "default": "0"},
            {"name": "a", "type": "number", "label": "Left boundary x = a", "default": 0.0},
            {"name": "b", "type": "number", "label": "Right boundary x = b", "default": 1.0},
            {"name": "alpha", "type": "number", "label": "Boundary value y(a)", "default": 0.0},
            {"name": "beta", "type": "number", "label": "Boundary value y(b)", "default": 1.1752},
            {"name": "N", "type": "number", "label": "Number of interior mesh points N", "default": 4},
        ],
        "solve_fn": "app.solvers.module5.finite_difference_bvp.solve",
    },
    "heat_equation_explicit": {
        "id": "heat_equation_explicit",
        "module": 5,
        "title": "1D Heat Equation (Explicit FTCS Method)",
        "short_description": "Solve parabolic PDE ∂u/∂t = α·∂²u/∂x² with forward time and central space explicit scheme.",
        "input_schema": [
            {"name": "alpha", "type": "number", "label": "Thermal diffusivity α", "default": 1.0},
            {"name": "L", "type": "number", "label": "Domain length L", "default": 1.0},
            {"name": "u0_expr", "type": "function", "label": "Initial temperature profile u(x, 0)", "default": "sin(pi*x)"},
            {"name": "u_left", "type": "number", "label": "Left boundary u(0, t)", "default": 0.0},
            {"name": "u_right", "type": "number", "label": "Right boundary u(L, t)", "default": 0.0},
            {"name": "Nx", "type": "number", "label": "Spatial intervals Nx", "default": 4},
            {"name": "Nt", "type": "number", "label": "Time intervals Nt", "default": 10},
            {"name": "T", "type": "number", "label": "Total duration T", "default": 0.1},
        ],
        "solve_fn": "app.solvers.module5.heat_equation_explicit.solve",
    },
    "matrix_inversion_gauss_jordan": {
        "id": "matrix_inversion_gauss_jordan",
        "module": 5,
        "title": "Matrix Inversion by Gauss-Jordan Method",
        "short_description": "Invert an n × n non-singular square matrix by augmenting with the identity matrix [A | I] → [I | A⁻¹].",
        "input_schema": [
            {
                "name": "A",
                "type": "matrix",
                "label": "Square matrix A (n × n)",
                "default": [[1.0, 2.0, 3.0], [0.0, 1.0, 4.0], [5.0, 6.0, 0.0]],
            }
        ],
        "solve_fn": "app.solvers.module5.matrix_inversion_gauss_jordan.solve",
    },
}


def get_all_topics_metadata() -> List[Dict[str, Any]]:
    """Returns public topic metadata without internal implementation details."""
    result = []
    for topic_id, item in TOPICS.items():
        result.append(
            {
                "id": item["id"],
                "module": item["module"],
                "title": item["title"],
                "short_description": item["short_description"],
                "input_schema": item["input_schema"],
            }
        )
    return result
