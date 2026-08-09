"""Re-analysis entrypoint for the one quantitative result in the paper.

Section 3.2.2 reports: "the participants provided less likes for images in the
condition with irreversible feedback provided (Median of likes. A: 2.5;
B: 27.5)". That is the whole of the paper's numeric reporting: no test
statistic, no interval, no per-participant data. The authors released no data,
so this script cannot be run on the paper's own measurements; it is the
contract by which the finding could be re-derived from a dataset of the same
shape.

Usage:
    python src/analyze.py <input.csv> [--out out/analysis.json]

Input CSV columns:
    participant_id  str    identifier, one row per participant per condition
    condition       str    "A" (irreversible feedback) or "B" (no feedback)
    likes           int    number of likes given in that condition

The exact sign test at the end is OURS, not the paper's: the paper declares no
statistical model (Section 3.2.2).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys

REPORTED_MEDIANS = {"A": 2.5, "B": 27.5}  # Section 3.2.2
REQUIRED_COLUMNS = ("participant_id", "condition", "likes")


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("median of an empty sample")
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return float(s[mid]) if n % 2 else (s[mid - 1] + s[mid]) / 2.0


def binom_two_sided(k: int, n: int) -> float:
    """Exact two-sided p for a sign test with p=0.5."""
    if n == 0:
        return float("nan")
    pmf = [math.comb(n, i) * 0.5 ** n for i in range(n + 1)]
    obs = pmf[k]
    return min(1.0, sum(p for p in pmf if p <= obs + 1e-12))


def load(path: str) -> list[dict]:
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(
                f"input {path} is missing required column(s): {', '.join(missing)}; "
                f"expected {', '.join(REQUIRED_COLUMNS)}"
            )
        rows = []
        for i, row in enumerate(reader, start=2):
            cond = (row["condition"] or "").strip().upper()
            if cond not in ("A", "B"):
                raise SystemExit(f"{path} line {i}: condition must be A or B, got {row['condition']!r}")
            try:
                likes = int(row["likes"])
            except (TypeError, ValueError):
                raise SystemExit(f"{path} line {i}: likes must be an integer, got {row['likes']!r}")
            if likes < 0:
                raise SystemExit(f"{path} line {i}: likes must be non-negative")
            rows.append({"participant_id": row["participant_id"].strip(),
                         "condition": cond, "likes": likes})
    if not rows:
        raise SystemExit(f"{path} contains no data rows")
    return rows


def analyse(rows: list[dict]) -> dict:
    by_cond = {"A": [], "B": []}
    by_pid: dict[str, dict[str, int]] = {}
    for r in rows:
        by_cond[r["condition"]].append(r["likes"])
        by_pid.setdefault(r["participant_id"], {})[r["condition"]] = r["likes"]

    result: dict = {
        "n_rows": len(rows),
        "n_participants": len(by_pid),
        "per_condition": {},
        "paper_reported_medians": REPORTED_MEDIANS,
    }
    for cond in ("A", "B"):
        vals = by_cond[cond]
        result["per_condition"][cond] = {
            "n": len(vals),
            "median": median(vals) if vals else None,
            "min": min(vals) if vals else None,
            "max": max(vals) if vals else None,
            "mean": round(sum(vals) / len(vals), 3) if vals else None,
        }
    ma = result["per_condition"]["A"]["median"]
    mb = result["per_condition"]["B"]["median"]
    if ma is not None and mb is not None:
        result["median_difference_A_minus_B"] = ma - mb
        result["direction_matches_paper"] = ma < mb
        result["delta_vs_reported"] = {
            "A": round(ma - REPORTED_MEDIANS["A"], 3),
            "B": round(mb - REPORTED_MEDIANS["B"], 3),
        }

    paired = [(v["A"], v["B"]) for v in by_pid.values() if "A" in v and "B" in v]
    lower = sum(1 for a, b in paired if a < b)
    higher = sum(1 for a, b in paired if a > b)
    n_eff = lower + higher
    result["sign_test_not_declared_by_paper"] = {
        "n_paired": len(paired),
        "n_nonzero": n_eff,
        "n_A_lower_than_B": lower,
        "p_two_sided": round(binom_two_sided(min(lower, higher), n_eff), 5) if n_eff else None,
    }
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="CSV with columns participant_id,condition,likes")
    ap.add_argument("--out", default="out/analysis.json")
    args = ap.parse_args(argv)

    rows = load(args.input)
    result = analyse(rows)
    result["input"] = os.path.abspath(args.input)

    print(f"input: {args.input}  ({result['n_rows']} rows, "
          f"{result['n_participants']} participants)")
    for cond in ("A", "B"):
        c = result["per_condition"][cond]
        label = "irreversible feedback" if cond == "A" else "no feedback"
        print(f"  condition {cond} ({label:<21}): n={c['n']:<3} "
              f"median={c['median']}  mean={c['mean']}  range=[{c['min']},{c['max']}]")
    if "median_difference_A_minus_B" in result:
        print(f"  median difference A-B: {result['median_difference_A_minus_B']}")
        print(f"  paper (Section 3.2.2) reports A: {REPORTED_MEDIANS['A']}, "
              f"B: {REPORTED_MEDIANS['B']}; delta vs reported: "
              f"{result['delta_vs_reported']}")
        print(f"  direction (A < B) matches the paper: "
              f"{result['direction_matches_paper']}")
    st = result["sign_test_not_declared_by_paper"]
    print(f"  sign test (ours, the paper declares none): "
          f"{st['n_A_lower_than_B']}/{st['n_nonzero']} pairs lower in A, "
          f"p={st['p_two_sided']}")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(result, fh, indent=2)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
