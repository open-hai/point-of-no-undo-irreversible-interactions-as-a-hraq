"""Arithmetic audit of the counts the paper reports (Sections 3.1.2 - 3.3.2).

Checking whether reported subgroup counts add up to the reported sample size
needs no participants, so this is inner loop. It is the only handle a reader has
on qualitative counts when neither the coded data nor a codebook is released.

Usage:  python -m src.consistency [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import os

STUDIES = {
    "4 on the Floor": {
        "citation": "Section 3.1.2",
        "n": 20,
        "themes": {"creative aspects": 6, "thoughtful process": 6,
                   "challenge": 4, "playful qualities": 3},
        "groups": {"playful/creative mindset (exclusively)": 8,
                   "challenging/thoughtful mindset": 6,
                   "completely rejected the concept": 2},
        # the paper divides participants "in favor" into two mindsets and names
        # the two who rejected the concept, so these three groups read as a
        # partition of the sample
        "groups_are_partition": True,
    },
    "SocialShredder": {
        "citation": "Section 3.2.2",
        "n": 16,
        "themes": {"longer contemplation": 15, "heightened awareness": 8,
                   "felt influenced": 10, "no amusement": 11},
        "groups": {"continued liking after complete destruction": 4},
        "groups_are_partition": False,
    },
    "Punishable AI": {
        "citation": "Section 3.3.2",
        "n": 20,
        "themes": {},
        "groups": {},
        "groups_are_partition": False,
    },
}


def audit() -> dict:
    out = []
    for name, s in STUDIES.items():
        theme_total = sum(s["themes"].values())
        group_total = sum(s["groups"].values())
        entry = {
            "study": name,
            "citation": s["citation"],
            "n_reported": s["n"],
            "theme_mentions_total": theme_total,
            "largest_theme_count": max(s["themes"].values()) if s["themes"] else 0,
            "subgroup_total": group_total,
            "groups_are_partition": s["groups_are_partition"],
            "participants_unaccounted_for": (
                s["n"] - group_total if s["groups"] and s["groups_are_partition"] else None
            ),
            "any_count_exceeds_n": any(v > s["n"] for v in
                                       list(s["themes"].values()) + list(s["groups"].values())),
            "denominator_stated_in_paper": False,
        }
        notes = []
        if s["groups"] and s["groups_are_partition"] and group_total < s["n"]:
            notes.append(
                f"the mutually exclusive subgroups account for {group_total} of "
                f"{s['n']} participants; {s['n'] - group_total} are unaccounted for"
            )
        if s["themes"] and theme_total > s["n"]:
            notes.append(
                f"theme mentions sum to {theme_total} > n={s['n']}, so participants "
                "must be counted under more than one theme (the paper does not say so)"
            )
        if not s["themes"] and not s["groups"]:
            notes.append("no counts are reported in this paper; "
                         "the detailed results are in the DIS '20 paper [119]")
        entry["notes"] = notes
        out.append(entry)
    return {"component": "consistency", "studies": out}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    result = audit()
    print("=== Reported-count audit ===")
    for e in result["studies"]:
        print(f"  {e['study']} ({e['citation']}): N={e['n_reported']}, "
              f"theme mentions={e['theme_mentions_total']}, "
              f"subgroups={e['subgroup_total']}")
        for note in e["notes"]:
            print(f"      - {note}")
    with open(os.path.join(args.out, "consistency.json"), "w") as fh:
        json.dump(result, fh, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
