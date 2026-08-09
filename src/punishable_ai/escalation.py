"""Escalating feedback and leg-break irreversibility (paper Section 3.3.1).

Paper: "Feedback to the robot is provided first by scolding, second by a
negative stimulus (bright flashlight), and last by gradually breaking the
robot's legs [...] The breaking interaction was limited by design and could
only be repeated once per leg."

Scolding leaves no trace in the released firmware -- it is speech, administered
by the participant and observed by the experimenter, so nothing in the robot
reacts to it. The flashlight maps onto the firmware's analogRead(A1) <= 400
branch. Breaking a leg is a physical act that the released firmware does not
sense at all (the per-leg switch pins are configured but never read).

Whether the robot can still walk after k broken legs is OUR model, not the
paper's: the paper only reports that participants "knew that when most legs of
the Punishable AI robot were broken, it would be unable to walk" (Section 3.4).
"""

from __future__ import annotations

from dataclasses import dataclass, field

LEGS = ("a", "b", "c", "d", "e", "f")

# The firmware's 3-phase gait swings these leg pairs in each phase.
PHASE_GROUPS = {0: ("a", "e"), 1: ("b", "f"), 2: ("c", "d")}


class NoUndo(RuntimeError):
    """Raised on any attempt to reverse an irreversible act."""


@dataclass
class PunishmentSession:
    """Order of escalation is fixed by the paper: scold -> light -> break."""

    stages: tuple[str, ...] = ("scold", "light", "break")
    stage_index: int = 0
    broken: set[str] = field(default_factory=set)
    log: list[tuple[str, str]] = field(default_factory=list)

    @property
    def stage(self) -> str:
        return self.stages[min(self.stage_index, len(self.stages) - 1)]

    def escalate(self) -> str:
        if self.stage_index < len(self.stages) - 1:
            self.stage_index += 1
        self.log.append(("escalate", self.stage))
        return self.stage

    def de_escalate(self) -> None:
        raise NoUndo(
            "the paper defines a 'stringent escalation' (Section 3.3.2); "
            "no de-escalation is defined"
        )

    def scold(self, utterance: str) -> None:
        # No robot-side effect exists: nothing in the released firmware listens.
        self.log.append(("scold", utterance))

    def flashlight(self, analog_value: int) -> bool:
        """Returns whether the firmware would react (jiggle)."""
        from .spider_sim import LIGHT_THRESHOLD

        reacted = analog_value <= LIGHT_THRESHOLD
        self.log.append(("light", f"analog={analog_value} reacted={reacted}"))
        return reacted

    def break_leg(self, leg: str) -> None:
        if leg not in LEGS:
            raise ValueError(f"unknown leg {leg!r}")
        if leg in self.broken:
            raise NoUndo(
                f"leg {leg} is already broken; the breaking interaction "
                "'could only be repeated once per leg' (Section 3.3.1)"
            )
        self.broken.add(leg)
        self.log.append(("break", leg))

    def repair_leg(self, leg: str) -> None:
        raise NoUndo("there is no undo: a broken PCB leg cannot be restored")

    # --- our mobility model (ASSUMPTION) -----------------------------------
    def can_walk(self) -> bool:
        """Tripod-style assumption: each gait phase needs at least one intact
        swing leg, and at least four of six legs must be intact for support."""
        intact = set(LEGS) - self.broken
        if len(intact) < 4:
            return False
        return all(set(group) & intact for group in PHASE_GROUPS.values())

    def state(self) -> dict:
        return {
            "stage": self.stage,
            "broken": sorted(self.broken),
            "intact": sorted(set(LEGS) - self.broken),
            "can_walk": self.can_walk(),
        }
