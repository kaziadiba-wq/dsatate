"""Local math checks. The tutor must call these before it states any math fact.

Everything runs on this machine with SymPy, so results are exact, not model guesses.
Note: SymPy parses expressions with eval, so only feed it expressions, not untrusted code.
"""
import random

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

_T = standard_transformations + (implicit_multiplication_application, convert_xor)


def _p(s: str):
    return parse_expr(str(s), transformations=_T, evaluate=True)


def check_identity(lhs: str, rhs: str) -> dict:
    """Is lhs == rhs for all values? Symbolic check plus 20 random numeric spot checks."""
    a, b = _p(lhs), _p(rhs)
    diff = sp.simplify(a - b)
    symbolic = diff == 0
    syms = sorted(diff.free_symbols | a.free_symbols | b.free_symbols, key=str)
    counter = None
    for _ in range(20):
        sub = {s: sp.Rational(random.randint(-50, 50), random.randint(1, 9)) for s in syms}
        try:
            val = sp.N(diff.subs(sub), 30)
        except Exception:
            continue
        if val.is_finite and abs(val) > 1e-20:
            counter = {str(k): str(v) for k, v in sub.items()}
            break
    return {
        "holds": bool(symbolic) and counter is None,
        "symbolic_difference": str(diff),
        "counterexample": counter,
    }


def solve(equation: str, variable: str = "x") -> dict:
    """Solve 'lhs = rhs' (or 'expr', meaning expr = 0) for one variable."""
    if "=" in equation:
        l, r = equation.split("=", 1)
        expr = _p(l) - _p(r)
    else:
        expr = _p(equation)
    return {"solutions": [str(s) for s in sp.solve(expr, sp.Symbol(variable))]}


def evaluate(expression: str) -> dict:
    """Exact value plus a 30-digit decimal."""
    v = sp.nsimplify(_p(expression)) if "." in expression else sp.simplify(_p(expression))
    return {"exact": str(v), "decimal": str(sp.N(v, 30))}


def integer_scan(expression: str, variable: str = "n", start: int = 1, end: int = 50,
                 divisor: int | None = None) -> dict:
    """Brute-force a number theory claim: values, primality, divisibility for n in [start, end]."""
    end = min(end, start + 10_000)
    n = sp.Symbol(variable)
    e = _p(expression)
    rows, fails = [], []
    for k in range(start, end + 1):
        v = sp.Integer(e.subs(n, k))
        row = {variable: k, "value": str(v), "prime": bool(sp.isprime(v)) if v > 1 else False}
        if divisor:
            row["divisible"] = v % divisor == 0
            if not row["divisible"]:
                fails.append(k)
        rows.append(row)
    return {"rows": rows[:60], "not_divisible_at": fails[:20] if divisor else None,
            "checked": f"{start}..{end}"}


def factor(expression: str) -> dict:
    e = _p(expression)
    if e.is_Integer:
        return {"factorization": {str(p): m for p, m in sp.factorint(e).items()}}
    return {"factored": str(sp.factor(e))}


TOOLS = {
    "check_identity": check_identity,
    "solve": solve,
    "evaluate": evaluate,
    "integer_scan": integer_scan,
    "factor": factor,
}
