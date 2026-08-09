"""Grid -> MIDI step sequencer for *4 on the Floor* (paper Section 3.1.1).

Paper: "The colors represent pitch or samples and the columns along the x-axis
represent time increments. By throwing chips into the grid, a sequence of notes
is created and stacking chips forms chords or layers sounds. This sequence is
constantly repeated in a loop, as known from step sequencers."

Unstated, and therefore assumed here: tempo, step length, note duration,
velocity, the concrete colour->pitch table, and whether a colour selects a pitch
or a sample. See REPRODUCIBILITY.md, "Hidden decisions".
"""

from __future__ import annotations

from dataclasses import dataclass

import mido

from .board import Board

# ASSUMPTION: the paper says colours represent "pitch or samples". We take the
# pitch reading: chip colour selects a MIDI channel/voice and the row selects a
# degree of an 8-note scale (C minor pentatonic extended to 8 rows).
SCALE = [60, 62, 63, 65, 67, 68, 70, 72]  # row 0 (bottom) .. row 7 (top)
COLOR_CHANNEL = {"red": 0, "yellow": 1, "blue": 2, "green": 3}
COLOR_TRANSPOSE = {"red": 0, "yellow": -12, "blue": 12, "green": 0}

BPM = 120.0            # ASSUMPTION
STEPS_PER_BEAT = 2     # ASSUMPTION: one column = one eighth note
VELOCITY = 100         # ASSUMPTION
GATE = 0.9             # ASSUMPTION: note length as a fraction of one step


@dataclass(frozen=True)
class NoteEvent:
    step: int
    pitch: int
    channel: int
    color: str
    row: int


def board_to_events(board: Board) -> list[NoteEvent]:
    """One column = one time increment; stacked chips = simultaneous notes."""
    events: list[NoteEvent] = []
    for col in range(board.cols):
        for row in range(board.rows):
            color = board.cells[row][col]
            if color is None:
                continue
            pitch = SCALE[row % len(SCALE)] + COLOR_TRANSPOSE[color]
            events.append(
                NoteEvent(step=col, pitch=pitch, channel=COLOR_CHANNEL[color],
                          color=color, row=row)
            )
    return sorted(events, key=lambda e: (e.step, e.pitch))


def loop(events: list[NoteEvent], n_loops: int, n_steps: int = 8):
    """Yield (absolute_step, event) for a repeating pattern."""
    for i in range(n_loops):
        for ev in events:
            yield i * n_steps + ev.step, ev


def step_seconds(bpm: float = BPM, steps_per_beat: int = STEPS_PER_BEAT) -> float:
    return 60.0 / bpm / steps_per_beat


def write_midi(events: list[NoteEvent], path: str, n_loops: int = 2,
               n_steps: int = 8, ticks_per_beat: int = 480) -> str:
    """Write the looped pattern to a standard MIDI file."""
    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(int(BPM))))
    ticks_per_step = ticks_per_beat // STEPS_PER_BEAT
    gate_ticks = max(1, int(ticks_per_step * GATE))

    timeline: dict[int, list[tuple[str, NoteEvent]]] = {}
    for abs_step, ev in loop(events, n_loops, n_steps):
        on = abs_step * ticks_per_step
        timeline.setdefault(on, []).append(("on", ev))
        timeline.setdefault(on + gate_ticks, []).append(("off", ev))

    prev = 0
    for tick in sorted(timeline):
        for kind, ev in timeline[tick]:
            track.append(
                mido.Message(
                    "note_on" if kind == "on" else "note_off",
                    note=ev.pitch, channel=ev.channel,
                    velocity=VELOCITY if kind == "on" else 0,
                    time=tick - prev,
                )
            )
            prev = tick
    mid.save(path)
    return path
