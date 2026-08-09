"""Smoke test for the *SocialShredder* inner loop (paper Section 3.2).

Shows the two conditions and the invariant that makes the artifact what it is:
un-liking removes the like from the interface but never restores the Polaroid.

Usage:  python -m src.social_shredder.run_demo [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import os

from .platform import Irreversible, MockFeed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    print("=== SocialShredder (paper Section 3.2) ===")

    feed_a = MockFeed(condition="A")
    for post in range(5):
        feed_a.like(post, t=post * 3.0)
    print(f"condition A after 5 likes: {feed_a.state()}")

    feed_a.unlike(2, t=20.0)
    print(f"after un-liking one post:  {feed_a.state()}")
    print("  -> the like is gone from the interface, the shredding is not")

    try:
        feed_a.shredder.restore()
        restore_blocked = False
    except Irreversible as exc:
        restore_blocked = True
        print(f"  restore refused: {exc}")

    # keep liking past complete destruction (Section 3.2.2 reports participants
    # who did exactly this)
    for post in range(5, 40):
        feed_a.like(post, t=post * 3.0)
    print(f"condition A after 40 likes: {feed_a.state()}")

    feed_b = MockFeed(condition="B")
    for post in range(40):
        feed_b.like(post, t=post * 3.0)
    print(f"condition B after 40 likes: {feed_b.state()}")

    summary = {
        "component": "social_shredder",
        "condition_A": feed_a.state(),
        "condition_B": feed_b.state(),
        "restore_blocked": restore_blocked,
        "shred_events": len(feed_a.shredder.events),
    }
    with open(os.path.join(args.out, "social_shredder.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    return 0 if restore_blocked and feed_b.shredder.steps == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
