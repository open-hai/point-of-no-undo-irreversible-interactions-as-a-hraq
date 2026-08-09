"""Python port of the released *Punishable AI* robot firmware.

Source of truth: spider/spider.ino in https://github.com/BeatRossmy/PunishableAI
(MIT licensed, fetched 2026-08-09). That repository accompanies the DIS '20
paper [119] whose robot is reused as material speculation 3 of the CHI '23
paper (Section 3.3). The CHI '23 paper itself links to no code.

This port keeps the firmware's numbers verbatim (SERVOMIN/SERVOMAX, the 3x9
movement table, the 500 ms phase length, the 10 ms servo step, the light
threshold of 400, jiggleCounter = 100) so that the behaviour the paper describes
in prose can be inspected without the hardware.

Two facts recovered from the firmware that the CHI '23 paper never states:
  1. the robot has six legs (a..f), i.e. it is a hexapod;
  2. the walking direction is picked with random(0, 3) each time the robot is
     switched on -- the "getting off track" the paper describes (Section 3.3.1)
     is a random draw, consistent with "the learning of the system was not
     implemented".
And one thing the firmware does *not* do: it never reads the per-leg switch pins
(2..7), so the "state of the legs (interrupted traces)" that Section 3.3.1
claims can be sensed is not sensed anywhere in the released code.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

SERVOMIN = 120
SERVOMAX = 550

# mid, upR, upRB, upL, upLB, fwdR, fwdL, bwdR, bwdL
MOVEMENT = [
    [90, 110, 70, 70, 110, 125, 60, 65, 120],  # straight
    [90, 110, 70, 70, 110, 130, 60, 70, 120],  # left
    [90, 110, 70, 70, 110, 120, 60, 60, 120],  # right
]
MOVEMENT_NAMES = ["straight", "left", "right"]

TICK_MS = 10          # delay(10) in loop()
PHASE_MS = 500        # if (t > 500)
JIGGLE_TICKS = 100    # jiggleCounter = 100
LIGHT_THRESHOLD = 400  # if (lightValue <= 400)


def servo_map(angle: int) -> int:
    """Arduino map(angle, 0, 180, SERVOMIN, SERVOMAX), integer division."""
    return (angle - 0) * (SERVOMAX - SERVOMIN) // (180 - 0) + SERVOMIN


@dataclass
class Leg:
    name: str
    s_pin: int
    r_pin: int
    switch_pin: int   # leg-break sensing: declared in the firmware, never read
    touch_pin: int
    pos_a: int = 90
    pos_b: int = 90
    target_a: int = 90
    target_b: int = 90
    pwm: dict[int, int] = field(default_factory=dict)

    def set_target(self, a: int, b: int) -> None:
        self.target_a, self.target_b = a, b

    def move(self) -> None:
        """One servo step, exactly as LEG::move() in spider.ino."""
        if self.target_a != self.pos_a:
            self.pos_a += 1 if self.target_a > self.pos_a else -1
            self.pwm[self.s_pin] = servo_map(self.pos_a)
        if self.target_b != self.pos_b:
            self.pos_b += 1 if self.target_b > self.pos_b else -1
            self.pwm[self.r_pin] = servo_map(self.pos_b)


class Spider:
    """The firmware's loop(), one call to `tick()` per 10 ms."""

    def __init__(self, seed: int = 0) -> None:
        self._rng = random.Random(seed)
        self.legs = {
            "a": Leg("a", 0, 1, 2, 8),
            "b": Leg("b", 2, 3, 3, 9),
            "c": Leg("c", 4, 5, 4, 10),
            "d": Leg("d", 6, 7, 5, 11),
            "e": Leg("e", 8, 9, 6, 12),
            "f": Leg("f", 10, 11, 7, 13),
        }
        self.on = False
        self.current_movement = 0
        self.phase = 0
        self.t_ms = 0
        self.jiggle_counter = 0
        self.millis = 0
        self.serial: list[str] = []
        self.broken: set[str] = set()   # physical state, invisible to the firmware
        self.stand()

    # --- firmware helpers ---------------------------------------------------
    def stand(self) -> None:
        mid = MOVEMENT[self.current_movement][0]
        for leg in self.legs.values():
            leg.set_target(mid, mid)

    def jiggle(self) -> None:
        for leg in self.legs.values():
            leg.set_target(self._rng.randrange(80, 100), self._rng.randrange(80, 100))

    def press_button(self) -> None:
        """The on/off button on A0; also re-draws the walking direction."""
        self.on = not self.on
        self.current_movement = self._rng.randrange(0, 3)
        self.serial.append(
            f"BUTTON -> on={self.on} movement={MOVEMENT_NAMES[self.current_movement]}"
        )

    # --- loop() -------------------------------------------------------------
    def tick(self, touched_pins: tuple[int, ...] = (), light_value: int = 1023) -> None:
        for leg in self.legs.values():
            leg.move()
        self.millis += TICK_MS
        self.t_ms += TICK_MS

        if not self.on:
            self.stand()
            for pin in range(8, 14):
                if pin in touched_pins:
                    self.serial.append("TOUCH DETECTED")
                    self.jiggle_counter = JIGGLE_TICKS
            if light_value <= LIGHT_THRESHOLD:
                self.jiggle_counter = JIGGLE_TICKS
            if self.jiggle_counter > 0:
                self.jiggle_counter -= 1
                self.jiggle()
            return

        if self.t_ms > PHASE_MS:
            self.t_ms = 0
            m = MOVEMENT[self.current_movement]
            a, b, c, d, e, f = (self.legs[k] for k in "abcdef")
            if self.phase == 0:
                a.set_target(m[6], m[3]); e.set_target(m[5], m[1])
                b.set_target(m[8], m[0]); f.set_target(m[7], m[0])
                c.set_target(m[0], m[0]); d.set_target(m[0], m[0])
            elif self.phase == 1:
                a.set_target(m[0], m[0]); e.set_target(m[0], m[0])
                b.set_target(m[6], m[3]); f.set_target(m[4], m[2])
                c.set_target(m[8], m[0]); d.set_target(m[7], m[0])
            else:
                a.set_target(m[8], m[0]); e.set_target(m[7], m[0])
                b.set_target(m[0], m[0]); f.set_target(m[0], m[0])
                c.set_target(m[6], m[4]); d.set_target(m[5], m[1])
            self.phase = (self.phase + 1) % 3

    # --- what the firmware does *not* do ------------------------------------
    def reads_leg_switches(self) -> bool:
        """The released loop() never calls digitalRead on pins 2..7."""
        return False

    def commanded_angles(self) -> dict[str, tuple[int, int]]:
        return {k: (leg.target_a, leg.target_b) for k, leg in self.legs.items()}
