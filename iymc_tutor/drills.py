"""Tier 1: arithmetic/algebra speed runs. Python makes and grades every question, no model needed.

Run: python -m iymc_tutor.drills [count] [seconds_per_question]
"""
import random
import sys
import time
from fractions import Fraction

from . import progress


def _q():
    r = random.randint
    kind = random.choice(["mult", "square", "linear", "fraction", "percent", "power_mod", "quadratic"])
    if kind == "mult":
        a, b = r(12, 99), r(12, 99)
        return kind, f"{a} × {b}", str(a * b)
    if kind == "square":
        a = r(21, 129)
        return kind, f"{a}²", str(a * a)
    if kind == "linear":
        x, a, b = r(-12, 12), r(2, 9), r(-30, 30)
        return kind, f"Solve {a}x {'-' if b < 0 else '+'} {abs(b)} = {a * x + b}", str(x)
    if kind == "fraction":
        a, b = Fraction(r(1, 9), r(2, 12)), Fraction(r(1, 9), r(2, 12))
        f = a + b
        return kind, f"{a} + {b} (lowest terms)", str(f)
    if kind == "percent":
        p, n = random.choice([5, 12, 15, 25, 35, 40, 75, 120]), r(2, 40) * 20
        return kind, f"{p}% of {n}", str(Fraction(p * n, 100))
    if kind == "power_mod":
        a, e, m = r(2, 9), r(10, 60), random.choice([5, 7, 9, 10, 11, 13])
        return kind, f"{a}^{e} mod {m}", str(pow(a, e, m))
    s, t = r(-9, 9), r(-9, 9)
    return kind, f"Sum of roots of x² {'-' if s + t >= 0 else '+'} {abs(s + t)}x + ({s * t}) = 0", str(s + t)


def run(count: int = 15, limit: float = 20.0) -> None:
    weak = progress.weak_points(tier=1, top=3)
    if weak:
        print("Your weakest Tier 1 topics:", ", ".join(w["topic"] for w in weak))
    score = 0
    for i in range(1, count + 1):
        topic, prompt, answer = _q()
        t0 = time.monotonic()
        given = input(f"[{i}/{count}] {prompt} = ").strip().replace(" ", "")
        dt = time.monotonic() - t0
        ok = given == answer and dt <= limit
        why = "" if ok else ("too slow" if given == answer else f"answered {given}, correct {answer}")
        print(("✓" if ok else "✗ " + why) + f"  ({dt:.1f}s)")
        progress.record(1, topic, ok, why, round(dt, 1))
        score += ok
    print(f"\nScore {score}/{count}. Weakest now:", progress.weak_points(tier=1, top=3))


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 15, float(sys.argv[2]) if len(sys.argv) > 2 else 20.0)
