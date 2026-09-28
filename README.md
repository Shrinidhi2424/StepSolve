# StepSolve — Numerical Methods Multi-Topic Calculator

StepSolve is a high-performance web calculator and pedagogical derivation engine for numerical methods. Developed as a capstone-level course assignment for **Numerical Methods and Applications** (VII Semester CSE, Sahyadri College of Engineering & Management) by **Shrinidhi** (Final-year CSE), the platform bridges computational mathematics and modern web engineering.

Unlike conventional solvers that return single numerical answers without context, StepSolve renders **complete textbook-style step-by-step derivations**, mathematical formulas with LaTeX substitutions, structured iteration history tables, stability and convergence diagnostics, and interactive Recharts visualizations for **all 15 syllabus topics across 5 comprehensive modules**.

---

## 15 Supported Topics & Implementation Status

| Module | # | Topic | Key Technique | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Module I** | 1 | Fixed Point Iteration | Root finding via $x = g(x)$ with divergence detection | Complete ✓ |
| | 2 | Secant Method | Derivative-free root finding, secant chord extrapolation | Complete ✓ |
| | 3 | Gauss-Jordan Elimination | Direct linear system solve ($AX = B$) via RREF with partial pivoting | Complete ✓ |
| **Module II** | 4 | Lagrange Interpolation | Polynomial interpolation for arbitrarily spaced nodes | Complete ✓ |
| | 5 | Cubic Spline Interpolation | Natural cubic spline ($S''(x_0)=S''(x_n)=0$) via Thomas algorithm | Complete ✓ |
| | 6 | Linear Regression (Least Squares) | Best-fit line $y = a + bx$ with normal equations & $R^2$ metric | Complete ✓ |
| **Module III** | 7 | Newton's Forward Difference | Numerical differentiation ($dy/dx, d^2y/dx^2$) via difference table | Complete ✓ |
| | 8 | Trapezoidal Rule | Composite numerical quadrature with step-by-step strip evaluations | Complete ✓ |
| | 9 | Simpson's 1/3 Rule | Parabolic composite numerical quadrature with parity validation | Complete ✓ |
| **Module IV** | 10 | Euler's Method | First-order ODE IVP with forward tangent-line stepping | Complete ✓ |
| | 11 | Modified Euler's Method (Heun) | 2nd-order predictor-corrector with average slope corrections | Complete ✓ |
| | 12 | Runge-Kutta 4th Order (RK4) | 4-stage weighted slope ($k_1, k_2, k_3, k_4$) high-precision ODE solve | Complete ✓ |
| **Module V** | 13 | Finite Difference BVP | Linear 2-point ODE BVP discretization solved via Thomas algorithm | Complete ✓ |
| | 14 | 1D Heat Equation (FTCS) | Explicit forward-time parabolic PDE scheme with stability check | Complete ✓ |
| | 15 | Matrix Inversion | Gauss-Jordan inversion $[A \mid I] \to [I \mid A^{-1}]$ with $A \cdot A^{-1} = I$ check | Complete ✓ |

---

## Tech Stack

| Layer | Technologies & Libraries |
| :--- | :--- |
| **Frontend** | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, Recharts, Lucide Icons, KaTeX/LaTeX rendering |
| **Design System** | Tailored dark mode (`#0a0a0f`), 5-module color coding, Google Fonts (`Outfit`, `Inter`, `JetBrains Mono`) |
| **Backend** | Python 3.12, FastAPI, Uvicorn, NumPy, SymPy (safe AST parsing & restricted expression evaluation) |
| **Testing** | Pytest, FastAPI TestClient, Automated Browser Subagent testing |

---

## Architecture

StepSolve utilizes a **modular-monolith architecture** with declarative metadata schemas:
1. **Dynamic Schema-Driven Forms**: Every topic exports an `input_schema` defining expected inputs (functions, numbers, tables, or matrices). The frontend dynamically renders validated input controls without hardcoded forms.
2. **Unified Step-Logging Contract**: Every solver returns an identical `SolveResponse` payload:
   ```json
   {
     "topic_id": "secant_method",
     "inputs_echo": { ... },
     "steps": [
       {
         "step_number": 1,
         "title": "Iteration 1",
         "description": "...",
         "formula": "x_{n+1} = x_n - ...",
         "substitution": "...",
         "value": 1.5214
       }
     ],
     "result": { ... },
     "result_summary": "Root ≈ 1.5214 after 5 iterations",
     "iterations_table": [ ... ],
     "plot_data": { "type": "line", "series": [ ... ] },
     "warnings": []
   }
   ```
3. **Safe Mathematical Evaluation**: User expressions are verified via an AST visitor in `backend/app/core/expr_eval.py` that disallows arbitrary code execution while supporting standard arithmetic, trigonometric, exponential, and logarithmic functions.

---

## Project Structure

```
StepSolve/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── router.py                 # REST endpoints: /api/topics, /api/solve/{topic_id}
│   │   ├── core/
│   │   │   ├── expr_eval.py              # Safe single- and multi-variable SymPy parser
│   │   │   ├── finite_differences.py     # Forward difference table construction
│   │   │   ├── linear_algebra.py         # Thomas algorithm and Gauss-Jordan RREF
│   │   │   └── models.py                 # Pydantic schemas (Step, SolveResponse)
│   │   ├── solvers/
│   │   │   ├── module1/                  # Topics 1, 2, 3
│   │   │   ├── module2/                  # Topics 4, 5, 6
│   │   │   ├── module3/                  # Topics 7, 8, 9
│   │   │   ├── module4/                  # Topics 10, 11, 12
│   │   │   └── module5/                  # Topics 13, 14, 15
│   │   ├── main.py                       # FastAPI initialization and CORS setup
│   │   └── registry.py                   # Declarative schema registry for all 15 topics
│   ├── tests/
│   │   ├── module1/ ... module5/         # 62 unit tests across all 5 modules
│   │   └── test_api_scaffold.py          # Scaffold, safety, and 15-topic live tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── calculator/
│   │   │   │   ├── [topicId]/page.tsx    # Interactive solver workspace
│   │   │   │   └── page.tsx              # Topic catalog with module tabs
│   │   │   ├── globals.css               # Design system tokens and micro-animations
│   │   │   ├── layout.tsx                # App shell, fonts, and footer
│   │   │   └── page.tsx                  # Landing page with hero and module cards
│   │   ├── components/
│   │   │   ├── forms/                    # Dynamic form fields (function, matrix, table, number)
│   │   │   ├── layout/                   # Navbar, ModuleTabs, and branding
│   │   │   └── results/                  # StepList, ResultSummary, IterationTable, SolverChart
│   │   └── lib/                          # API client, types, and moduleTheme
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

---

## Local Setup

### 1. Backend (FastAPI)

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (cmd):
.\venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload --port 8000
```
Interactive API documentation (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs).

### 2. Frontend (Next.js)

Open a second terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Open your browser at [http://localhost:3000](http://localhost:3000).

---

## API Endpoints

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health-check endpoint returning system status |
| `GET` | `/api/topics` | Returns metadata and `input_schema` for all 15 topics |
| `GET` | `/api/topics/{topic_id}` | Returns metadata and configuration for a specific topic |
| `POST` | `/api/solve/{topic_id}` | Solves a method given parameters, returning derivation steps |

---

## Automated Testing

Execute the comprehensive Pytest suite (62 tests across all 5 modules):

```bash
cd backend
pytest -v
```

All 62 tests validate:
- Convergence to analytical solutions ($e^x, \sinh(x)$, known roots).
- Step-logging correctness and schema adherence.
- Edge case handling (singular matrices, step sizes, odd $n$ in Simpson's, divergence detection).
- End-to-end HTTP responses for all 15 topics.

---

## Known Considerations & Tech Debt

- **TypeScript Type Sharing**: TypeScript types in `frontend/src/lib/types.ts` are cleanly maintained alongside Pydantic models. For multi-team scale, `openapi-typescript-codegen` could be added to generate them automatically from `/openapi.json`.
- **High-Dimension ODE Meshes**: For performance and UX readability, ODE iterations and finite difference grids are capped at 500 steps to prevent browser lag.
