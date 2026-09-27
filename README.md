# StepSolve — Numerical Methods Multi-Topic Calculator

StepSolve is a modern web calculator and textbook-style derivation engine for numerical methods. Built for the **Numerical Methods and Applications** course (VII Semester CSE, Sahyadri College of Engineering & Management).

Unlike ordinary calculators that only produce final numerical answers, StepSolve renders **comprehensive step-by-step working**, formula derivations, iteration tables, convergence warnings, and interactive function curves across **all 15 syllabus topics** spanning 5 modules.

---

## 15 Supported Topics

| Module | # | Topic | Key Technique |
| :--- | :--- | :--- | :--- |
| **Module I** | 1 | Fixed Point Iteration | Root finding via $x = g(x)$ |
| | 2 | Secant Method | Root finding, derivative-free |
| | 3 | Gauss-Jordan Elimination | Direct linear system solve ($AX = B$) |
| **Module II** | 4 | Lagrange Interpolation | Unequal-interval interpolation |
| | 5 | Cubic Spline Interpolation | Natural spline with Thomas algorithm |
| | 6 | Curve Fitting (Least Squares) | Linear regression $y = a + bx$ |
| **Module III** | 7 | Newton's Forward Difference | Finite difference differentiation |
| | 8 | Trapezoidal Rule | Composite numerical quadrature |
| | 9 | Simpson's 1/3 Rule | Parabolic composite numerical quadrature |
| **Module IV** | 10 | Euler's Method | First-order ODE initial value problem |
| | 11 | Modified Euler's Method | Heun's predictor-corrector ODE solve |
| | 12 | Runge-Kutta 4th Order (RK4) | 4-stage high accuracy ODE solve |
| **Module V** | 13 | Finite Difference BVP | 2-point second-order linear ODE BVP |
| | 14 | 1D Heat Equation (FTCS) | Explicit forward-time PDE scheme |
| | 15 | Matrix Inversion | Gauss-Jordan inversion $[A \mid I] \to [I \mid A^{-1}]$ |

---

## Tech Stack

- **Frontend**: Next.js (App Router), React, TypeScript, Tailwind CSS, Recharts, Lucide Icons.
- **Backend**: Python 3.12, FastAPI, NumPy, SymPy (safe restricted AST parsing & evaluation).
- **Architecture**: Modular monolith with shared `Step` and `SolveResponse` data models.

---

## Local Setup

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your web browser.

---

## Running Backend Tests

```bash
cd backend
.\venv\Scripts\pytest -v
```
