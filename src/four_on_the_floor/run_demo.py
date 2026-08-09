"""Smoke test for the *4 on the Floor* inner loop (paper Section 3.1).

Runs the whole chain the paper describes in one sentence:
    chips in an 8x8 grid -> webcam frame -> chip tracking -> MIDI -> (DAW).
The DAW is out of scope: we stop at a standard MIDI file.

Usage:  python -m src.four_on_the_floor.run_demo [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import os

from .board import Board, IrreversibleActionError
from .sequencer import board_to_events, write_midi, step_seconds
from .vision import detect_board, render_board

# A deterministic sequence of (column, colour) throws, so the demo is
# reproducible. This is our own test input, not data from the paper.
THROWS = [
    (0, "red"), (0, "blue"), (1, "yellow"), (2, "red"), (2, "green"),
    (3, "blue"), (4, "yellow"), (4, "yellow"), (5, "green"), (6, "red"),
    (7, "blue"), (7, "red"), (7, "yellow"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out")
    ap.add_argument("--noise", type=float, default=0.02,
                    help="sensor noise added to the synthetic frame")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    print("=== 4 on the Floor (paper Section 3.1) ===")

    # --- configuration A: the irreversible condition -----------------------
    board_a = Board(config="A")
    for col, color in THROWS:
        board_a.drop(col, color)
    print("\ngrid state (configuration A, 8x8, row 0 = bottom):")
    print(board_a.as_text())

    try:
        board_a.remove(0, 0)
        removal_blocked = False
    except IrreversibleActionError as exc:
        removal_blocked = True
        print(f"\nconfiguration A refuses removal: {exc}")

    # --- webcam-style detection -------------------------------------------
    frame = render_board(board_a, noise=args.noise, seed=1)
    detected = detect_board(frame, config="A")
    cells_total = board_a.rows * board_a.cols
    wrong = [
        (r, c, board_a.cells[r][c], detected.cells[r][c])
        for r in range(board_a.rows)
        for c in range(board_a.cols)
        if board_a.cells[r][c] != detected.cells[r][c]
    ]
    print(f"\nchip tracking on a synthetic frame {frame.shape}: "
          f"{cells_total - len(wrong)}/{cells_total} cells correct, "
          f"{len(wrong)} mismatched")

    # --- MIDI ---------------------------------------------------------------
    events = board_to_events(detected)
    midi_path = os.path.join(args.out, "four_on_the_floor.mid")
    write_midi(events, midi_path, n_loops=2)
    print(f"{len(events)} note events; step = {step_seconds():.3f} s at 120 BPM")
    for ev in events[:6]:
        print(f"  step {ev.step}  row {ev.row}  {ev.color:<6} "
              f"pitch {ev.pitch}  ch {ev.channel}")
    if len(events) > 6:
        print(f"  ... ({len(events) - 6} more)")
    print(f"wrote {midi_path}")

    # --- configuration B: chips removable at all times ----------------------
    board_b = Board(config="B")
    for col, color in THROWS:
        board_b.drop(col, color)
    before = len(board_b.occupied())
    board_b.remove(0, 0)
    after = len(board_b.occupied())
    print(f"\nconfiguration B allows removal: {before} -> {after} chips "
          f"(collapse_on_remove={board_b.collapse_on_remove}, our assumption)")

    summary = {
        "component": "four_on_the_floor",
        "grid": [board_a.rows, board_a.cols],
        "throws": len(THROWS),
        "config_A_removal_blocked": removal_blocked,
        "detection_cells_total": cells_total,
        "detection_cells_correct": cells_total - len(wrong),
        "detection_mismatches": wrong,
        "note_events": len(events),
        "midi_file": midi_path,
        "config_B_chips_before_after": [before, after],
    }
    with open(os.path.join(args.out, "four_on_the_floor.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    return 0 if not wrong and removal_blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
