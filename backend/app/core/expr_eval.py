import sympy
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)
from typing import Callable, Set, Optional, Tuple

# Whitelist allowed functions and constants
SAFE_LOCALS = {
    "sin": sympy.sin,
    "cos": sympy.cos,
    "tan": sympy.tan,
    "asin": sympy.asin,
    "acos": sympy.acos,
    "atan": sympy.atan,
    "sinh": sympy.sinh,
    "cosh": sympy.cosh,
    "tanh": sympy.tanh,
    "exp": sympy.exp,
    "log": sympy.log,
    "ln": sympy.log,
    "sqrt": sympy.sqrt,
    "abs": sympy.Abs,
    "Abs": sympy.Abs,
    "pi": sympy.pi,
    "e": sympy.E,
    "E": sympy.E,
}

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def _check_symbols(expr: sympy.Expr, allowed_vars: Set[str]) -> None:
    """Check that the expression only uses allowed symbols."""
    for symbol in expr.free_symbols:
        if symbol.name not in allowed_vars:
            raise ValueError(
                f"Unauthorized variable or symbol: '{symbol.name}'. "
                f"Allowed variables are: {sorted(list(allowed_vars))}"
            )


def parse_symbolic(expr_str: str, allowed_vars: Set[str]) -> sympy.Expr:
    """Parse expression string into a SymPy expression safely with a locked namespace."""
    if not expr_str or not expr_str.strip():
        raise ValueError("Expression string cannot be empty.")

    # Disallow dangerous patterns using word boundaries and token checks
    import re
    if "__" in expr_str:
        raise ValueError("Disallowed dunder in expression.")

    dangerous_keywords = ["import", "exec", "eval", "compile", "open", "os", "sys", "builtins"]
    for kw in dangerous_keywords:
        if re.search(r"\b" + re.escape(kw) + r"\b", expr_str, re.IGNORECASE):
            raise ValueError(f"Disallowed keyword in expression: '{kw}'")

    local_dict = dict(SAFE_LOCALS)
    for v in allowed_vars:
        local_dict[v] = sympy.Symbol(v)

    try:
        parsed = parse_expr(
            expr_str.strip(),
            local_dict=local_dict,
            transformations=TRANSFORMATIONS,
            evaluate=True,
        )
    except Exception as e:
        raise ValueError(f"Invalid mathematical expression '{expr_str}': {str(e)}")

    _check_symbols(parsed, allowed_vars)
    return parsed


def parse_single_var(expr_str: str, var: str = "x") -> Callable[[float], float]:
    """Parse a single-variable expression and return a fast callable f(x)."""
    sym = sympy.Symbol(var)
    parsed = parse_symbolic(expr_str, allowed_vars={var})
    fn = sympy.lambdify(sym, parsed, modules=["numpy", "math"])

    def wrapped(val: float) -> float:
        try:
            res = fn(val)
            if isinstance(res, complex):
                if abs(res.imag) < 1e-9:
                    return float(res.real)
                raise ValueError("Evaluation produced complex result.")
            return float(res)
        except Exception as e:
            raise ValueError(f"Error evaluating '{expr_str}' at {var}={val}: {str(e)}")

    return wrapped


def parse_two_var(expr_str: str, var1: str = "x", var2: str = "y") -> Callable[[float, float], float]:
    """Parse a two-variable expression (e.g., dy/dx = f(x, y)) and return a fast callable f(x, y)."""
    sym1 = sympy.Symbol(var1)
    sym2 = sympy.Symbol(var2)
    parsed = parse_symbolic(expr_str, allowed_vars={var1, var2})
    fn = sympy.lambdify((sym1, sym2), parsed, modules=["numpy", "math"])

    def wrapped(val1: float, val2: float) -> float:
        try:
            res = fn(val1, val2)
            if isinstance(res, complex):
                if abs(res.imag) < 1e-9:
                    return float(res.real)
                raise ValueError("Evaluation produced complex result.")
            return float(res)
        except Exception as e:
            raise ValueError(f"Error evaluating '{expr_str}' at ({var1}={val1}, {var2}={val2}): {str(e)}")

    return wrapped


def expr_to_latex(expr_str: str, allowed_vars: Optional[Set[str]] = None) -> str:
    """Convert expression string to LaTeX formatted string."""
    if allowed_vars is None:
        allowed_vars = {"x", "y", "t"}
    try:
        parsed = parse_symbolic(expr_str, allowed_vars=allowed_vars)
        return sympy.latex(parsed)
    except Exception:
        return expr_str


def validate_expression(expr_str: str, allowed_vars: Tuple[str, ...] = ("x",)) -> Tuple[bool, Optional[str]]:
    """Validate expression and return (is_valid, error_message)."""
    try:
        parse_symbolic(expr_str, allowed_vars=set(allowed_vars))
        return True, None
    except Exception as e:
        return False, str(e)
