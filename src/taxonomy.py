"""The paper's own classifications, re-derived and checked (Sections 4.3 and 5).

Section 4.3 spans involvement over two dimensions -- closeness (proxy or not)
and time (immediate or delayed) -- and populates the resulting four cells with
projects. Section 5 assigns each of the three speculations to one of the three
design strategies (altering / creating / destructing).

Neither classification needs a participant, so both are inner loop: they are
statements about a fixed set of cited projects, and they can be checked for
completeness and internal consistency. That is all this module does. It does
not re-derive the classification from first principles -- the paper gives no
operational rule that would let anyone do that.

Usage:  python -m src.taxonomy [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import os

# Section 4.3, verbatim assignment of projects to involvement cells.
INVOLVEMENT = {
    ("close", "immediate"): [
        {"project": "Punishable AI", "kind": "own speculation", "citation": "Section 4.3"},
        {"project": "To kill a mockingbird robot [9]", "kind": "HCI project", "citation": "Section 4.3"},
        {"project": "Obscura 1C [112]", "kind": "HCI project", "citation": "Section 4.3"},
    ],
    ("far", "immediate"): [
        {"project": "SocialShredder", "kind": "own speculation", "citation": "Section 4.3"},
        {"project": "DESU 100 [115]", "kind": "HCI project", "citation": "Section 4.3"},
        {"project": "Destructive Games [44]", "kind": "HCI project", "citation": "Section 4.3"},
        {"project": "Scotty [98]", "kind": "HCI project", "citation": "Section 4.3"},
    ],
    ("far", "delayed"): [
        {"project": "PlantDisplay [76]", "kind": "HCI project", "citation": "Section 4.3"},
    ],
    ("close", "delayed"): [
        {"project": "hypothetical robot 'bruise' scenario", "kind": "hypothetical",
         "citation": "Section 4.3"},
        {"project": "The way things go [43]", "kind": "art work", "citation": "Section 4.3"},
        {"project": "curing resins / photographic emulsions", "kind": "material process",
         "citation": "Section 4.3"},
    ],
}

# Section 4.3: "We could not identify related work that presents an actant
# involvement, which uses a direct cause in conjunction with a delayed effect."
PAPER_CLAIM_EMPTY_CELL = ("close", "delayed")

# Section 5 / Figure 6.
DESIGN_STRATEGY = {
    "SocialShredder": {
        "strategy": "altering",
        "citation": "Section 5",
        "note": "the paper itself flags 'a thin line between alteration and "
                "destruction in the SocialShredder'",
    },
    "4 on the Floor": {"strategy": "creating", "citation": "Section 5", "note": ""},
    "Punishable AI": {"strategy": "destructing", "citation": "Section 5", "note": ""},
}

SPECULATIONS = ("4 on the Floor", "SocialShredder", "Punishable AI")


def check() -> dict:
    findings = []

    # 1. all four cells of the 2x2 are named in the text
    cells = sorted(INVOLVEMENT)
    findings.append({
        "check": "all four involvement cells appear in Section 4.3",
        "ok": len(cells) == 4,
        "detail": [f"{c[0]} & {c[1]}" for c in cells],
    })

    # 2. the empty-cell claim, read strictly: no *HCI project* in that cell
    hci_in_claimed_empty = [
        e["project"] for e in INVOLVEMENT[PAPER_CLAIM_EMPTY_CELL]
        if e["kind"] == "HCI project"
    ]
    non_hci = [
        f"{e['project']} ({e['kind']})"
        for e in INVOLVEMENT[PAPER_CLAIM_EMPTY_CELL] if e["kind"] != "HCI project"
    ]
    findings.append({
        "check": "'close & delayed' contains no HCI related work (Section 4.3)",
        "ok": not hci_in_claimed_empty,
        "detail": {
            "hci_projects": hci_in_claimed_empty,
            "non_hci_entries_the_paper_does_give": non_hci,
        },
    })

    # 3. every speculation is placed somewhere in the 2x2
    placed = {e["project"] for entries in INVOLVEMENT.values() for e in entries}
    unplaced = [s for s in SPECULATIONS if s not in placed]
    findings.append({
        "check": "each of the three speculations is placed in the involvement grid",
        "ok": not unplaced,
        "detail": {
            "unplaced": unplaced,
            "note": "Section 5 describes 4 on the Floor as acting 'only by proxy' "
                    "with a 'delayed' change, i.e. far & delayed, but Section 4.3 "
                    "never lists it in a cell",
        },
    })

    # 4. the three design strategies are used exactly once each
    used = sorted(v["strategy"] for v in DESIGN_STRATEGY.values())
    findings.append({
        "check": "altering / creating / destructing each carry one speculation",
        "ok": used == ["altering", "creating", "destructing"],
        "detail": {k: v["strategy"] for k, v in DESIGN_STRATEGY.items()},
    })

    return {"component": "taxonomy", "findings": findings,
            "all_ok": all(f["ok"] for f in findings)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    result = check()
    print("=== Involvement taxonomy and design strategies (Sections 4.3, 5) ===")
    for f in result["findings"]:
        print(f"  [{'ok ' if f['ok'] else 'GAP'}] {f['check']}")
        print(f"        {f['detail']}")
    with open(os.path.join(args.out, "taxonomy.json"), "w") as fh:
        json.dump(result, fh, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
