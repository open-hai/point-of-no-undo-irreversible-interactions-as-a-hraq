"""Smoke test for the *Punishable AI* inner loop (paper Section 3.3).

Usage:  python -m src.punishable_ai.run_demo [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import os

from .escalation import LEGS, NoUndo, PunishmentSession
from .spider_sim import MOVEMENT_NAMES, Spider


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    print("=== Punishable AI (paper Section 3.3; firmware from BeatRossmy/PunishableAI) ===")
    bot = Spider(seed=42)
    print(f"legs recovered from the firmware: {sorted(bot.legs)} "
          f"({len(bot.legs)} -- the CHI '23 paper never states the number)")

    bot.press_button()  # switch on -> draws a walking direction at random
    print(f"walking direction after switch-on: "
          f"{MOVEMENT_NAMES[bot.current_movement]} (drawn by random(0,3))")

    for _ in range(300):  # 300 ticks x 10 ms = 3 s of walking
        bot.tick()
    walking_angles = bot.commanded_angles()
    print(f"after 3 s of walking, phase={bot.phase}, "
          f"commanded angles: {walking_angles}")

    # a participant touches leg c while the robot stands still
    bot.press_button()  # switch off -> the touch/light branch becomes live
    bot.tick(touched_pins=(bot.legs['c'].touch_pin,))
    for _ in range(20):
        bot.tick()
    touch_lines = [line for line in bot.serial if line == "TOUCH DETECTED"]
    print(f"touch on pin {bot.legs['c'].touch_pin}: "
          f"{len(touch_lines)} 'TOUCH DETECTED', jiggle_counter now "
          f"{bot.jiggle_counter} (trembling, Section 3.3.2)")

    # flashlight
    bot.jiggle_counter = 0
    bot.tick(light_value=350)
    print(f"flashlight (analogRead=350 <= 400): jiggle_counter="
          f"{bot.jiggle_counter}")

    # --- escalation and irreversibility ------------------------------------
    session = PunishmentSession()
    session.scold("Nein!")
    print(f"\nstage after scolding: {session.stage}")
    session.escalate()
    reacted = session.flashlight(350)
    print(f"stage {session.stage}: firmware reacts to the light = {reacted}")
    session.escalate()
    print(f"stage {session.stage}")

    trace = []
    for leg in LEGS:
        session.break_leg(leg)
        state = session.state()
        trace.append(state)
        print(f"  broke leg {leg}: intact={len(state['intact'])}, "
              f"can_walk={state['can_walk']} (our mobility model)")
        if not state["can_walk"]:
            break

    errors = {}
    for name, fn in (("re-break", lambda: session.break_leg(sorted(session.broken)[0])),
                     ("repair", lambda: session.repair_leg("a")),
                     ("de-escalate", session.de_escalate)):
        try:
            fn()
            errors[name] = None
        except NoUndo as exc:
            errors[name] = str(exc)
            print(f"  {name} refused: {exc}")

    # --- the audit finding --------------------------------------------------
    before = dict(walking_angles)
    bot2 = Spider(seed=42)
    bot2.press_button()
    bot2.broken = {"a", "b", "c"}          # physically broken legs
    for _ in range(300):
        bot2.tick()
    after = bot2.commanded_angles()
    unchanged = before == after
    print(f"\ngait commands with 3 broken legs identical to the intact robot: "
          f"{unchanged}")
    print(f"firmware reads the per-leg switch pins (2..7): "
          f"{bot2.reads_leg_switches()}  <-- Section 3.3.1 says leg state "
          f"'could be sensed'")

    summary = {
        "component": "punishable_ai",
        "legs": len(bot.legs),
        "walking_direction_source": "random(0,3) in the released firmware",
        "touch_detected_lines": len(touch_lines),
        "light_threshold_reaction": reacted,
        "break_trace": trace,
        "no_undo_errors": errors,
        "gait_unchanged_when_legs_broken": unchanged,
        "firmware_reads_leg_switch_pins": bot2.reads_leg_switches(),
    }
    with open(os.path.join(args.out, "punishable_ai.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
