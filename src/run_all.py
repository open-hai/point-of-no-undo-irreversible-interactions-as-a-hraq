"""Run every inner-loop component and write the artifacts to out/.

Usage:  python -m src.run_all
"""

from __future__ import annotations

import subprocess
import sys

STEPS = [
    ["python", "-m", "src.four_on_the_floor.run_demo"],
    ["python", "-m", "src.social_shredder.run_demo"],
    ["python", "-m", "src.punishable_ai.run_demo"],
    ["python", "-m", "src.taxonomy"],
    ["python", "-m", "src.consistency"],
    ["python", "src/analyze.py", "data/EXAMPLE_synthetic_likes.csv"],
]


def main() -> int:
    failed = []
    for cmd in STEPS:
        print("\n" + "=" * 72)
        print("$ " + " ".join(cmd))
        print("=" * 72)
        rc = subprocess.call([sys.executable] + cmd[1:])
        if rc != 0:
            failed.append((cmd, rc))
    print("\n" + "=" * 72)
    if failed:
        for cmd, rc in failed:
            print(f"FAILED (exit {rc}): {' '.join(cmd)}")
        return 1
    print("all inner-loop components ran")
    print("NOTE: data/EXAMPLE_synthetic_likes.csv is synthetic filler generated "
          "by us to exercise src/analyze.py. It is not the paper's data and its "
          "numbers mean nothing about the paper's findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
