# point-of-no-undo — reproduction repository

An independent reproducibility audit of:

> Beat Rossmy, Nađa Terzimehić, Tanja Döring, Daniel Buschek, Alexander Wiethoff.
> **Point of no Undo: Irreversible Interactions as a Design Strategy.**
> CHI '23, article 140, 1–18. [10.1145/3544548.3581433](https://doi.org/10.1145/3544548.3581433)

## What the paper is

A speculative/critical design paper that inverts one of HCI's founding
heuristics. Undo exists to rescue users from irreversibility; this paper asks
what irreversibility is *good for*, and answers with three built artifacts
(Section 3):

- **4 on the Floor** — a Connect-Four-shaped step sequencer. Coloured chips are
  thrown into an 8×8 suspended grid, tracked by webcam, and turned into MIDI.
  Columns are time steps, stacked chips are chords, and in the irreversible
  configuration a thrown chip stays where it lands.
- **SocialShredder** — a mock social-media feed wired over USB to an electric
  shredder loaded with a Polaroid of the participant. Every like consumes a
  little more of the photograph. Un-liking gives the like back and not the
  photograph.
- **Punishable AI** — a six-legged walking robot given feedback by escalation:
  scolding, then a bright flashlight, then snapping a leg at its perforation.
  Each leg breaks once.

From these the authors build a conceptualisation of irreversibility (artifact
value and symbolism, actant context, involvement; Section 4) and three design
strategies — altering, creating, destructing (Section 5).

## What this repository is

Three things, in this order of importance:

1. **[REPRODUCIBILITY.md](REPRODUCIBILITY.md)** — the verdict and the
   per-component reproduction table: every inner-loop component marked
   reproduced / partial / blocked with the evidence or the specific blocker,
   then the inner/outer boundary, the hidden decisions, and the open-science
   scorecard.
2. **`src/`** — a best-effort, runnable reimplementation of the inner loop:
   the grid and sequencer, the shredder controller, a Python port of the
   authors' released robot firmware, and audits of the paper's own
   classifications and counts.
3. **[SOURCES.md](SOURCES.md)** and **[UNVERIFIED.md](UNVERIFIED.md)** — every
   artifact search with its result (30 of them), and everything I could not
   confirm with the reason.

Machine-readable forms of the same content: **[verdict.json](verdict.json)**
(boundary table, mismatches, hidden decisions, scorecard, what was released) and
**[instrument.json](instrument.json)** (the declared study protocol, the
analysis entrypoint contract, the servability assessment).

**Headline:** the verdict is **partial** — 7 of 15 inner-loop components
reproduce, 6 run but cannot be checked against the originals, 2 are blocked.
That ratio depends on how the paper is sliced; read the table, not the ratio.

**What is not here, and never will be:** anything about the three user studies.
20, 16 and 20 participants used these artifacts and talked about them. That work
is the outer loop. It is not attempted, not scored, and not simulated.

## Running it

Requires Python 3.11+, `numpy`, `pillow`, `mido` (`pip install numpy pillow mido`).

```
python -m src.run_all          # every component, writes out/
```

Individual components:

```
python -m src.four_on_the_floor.run_demo   # grid -> webcam frame -> tracking -> MIDI
python -m src.social_shredder.run_demo     # feed -> like -> shred, and the no-undo invariant
python -m src.punishable_ai.run_demo       # gait, touch, flashlight, leg breaking
python -m src.taxonomy                     # Sections 4.3 and 5, checked for consistency
python -m src.consistency                  # do the reported participant counts add up?
python src/analyze.py <input.csv>          # re-analysis entrypoint (see instrument.json)
```

### Real output, from `python -m src.run_all` on 2026-08-09

```
$ python -m src.four_on_the_floor.run_demo
=== 4 on the Floor (paper Section 3.1) ===

grid state (configuration A, 8x8, row 0 = bottom):
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . Y
B . G . Y . . R
R Y R B Y G R B

configuration A refuses removal: configuration A: a chip that has been thrown cannot be removed (paper Section 3.1.2)

chip tracking on a synthetic frame (320, 320, 3): 64/64 cells correct, 0 mismatched
13 note events; step = 0.250 s at 120 BPM
  step 0  row 0  red    pitch 60  ch 0
  ...
wrote out/four_on_the_floor.mid

configuration B allows removal: 13 -> 12 chips (collapse_on_remove=True, our assumption)

$ python -m src.social_shredder.run_demo
=== SocialShredder (paper Section 3.2) ===
condition A after 5 likes: {'condition': 'A', 'likes_visible': 5, 'likes_given': 5, 'shred_steps': 5, 'destroyed_fraction': 0.167, 'fully_destroyed': False}
after un-liking one post:  {'condition': 'A', 'likes_visible': 4, 'likes_given': 5, 'shred_steps': 5, 'destroyed_fraction': 0.167, 'fully_destroyed': False}
  -> the like is gone from the interface, the shredding is not
  restore refused: the Polaroid cannot be un-shredded: ... (Section 3.2.1)
condition A after 40 likes: {..., 'shred_steps': 40, 'destroyed_fraction': 1.0, 'fully_destroyed': True}
condition B after 40 likes: {..., 'shred_steps': 0, 'destroyed_fraction': 0.0, 'fully_destroyed': False}

$ python -m src.punishable_ai.run_demo
=== Punishable AI (paper Section 3.3; firmware from BeatRossmy/PunishableAI) ===
legs recovered from the firmware: ['a', 'b', 'c', 'd', 'e', 'f'] (6 -- the CHI '23 paper never states the number)
walking direction after switch-on: right (drawn by random(0,3))
after 3 s of walking, phase=2, commanded angles: {'a': (90, 90), 'b': (60, 70), 'c': (120, 90), 'd': (60, 90), 'e': (90, 90), 'f': (110, 70)}
touch on pin 10: 1 'TOUCH DETECTED', jiggle_counter now 79 (trembling, Section 3.3.2)
flashlight (analogRead=350 <= 400): jiggle_counter=99
  broke leg a: intact=5, can_walk=True (our mobility model)
  broke leg b: intact=4, can_walk=True (our mobility model)
  broke leg c: intact=3, can_walk=False (our mobility model)
  re-break refused: leg a is already broken; the breaking interaction 'could only be repeated once per leg' (Section 3.3.1)
  repair refused: there is no undo: a broken PCB leg cannot be restored
gait commands with 3 broken legs identical to the intact robot: True
firmware reads the per-leg switch pins (2..7): False  <-- Section 3.3.1 says leg state 'could be sensed'

$ python -m src.taxonomy
  [ok ] all four involvement cells appear in Section 4.3
  [ok ] 'close & delayed' contains no HCI related work (Section 4.3)
  [GAP] each of the three speculations is placed in the involvement grid
        {'unplaced': ['4 on the Floor'], ...}
  [ok ] altering / creating / destructing each carry one speculation

$ python -m src.consistency
  4 on the Floor (Section 3.1.2): N=20, theme mentions=19, subgroups=16
      - the mutually exclusive subgroups account for 16 of 20 participants; 4 are unaccounted for
  SocialShredder (Section 3.2.2): N=16, theme mentions=44, subgroups=4
      - theme mentions sum to 44 > n=16, so participants must be counted under more than one theme (the paper does not say so)
  Punishable AI (Section 3.3.2): N=20, theme mentions=0, subgroups=0
      - no counts are reported in this paper; the detailed results are in the DIS '20 paper [119]

$ python src/analyze.py data/EXAMPLE_synthetic_likes.csv
input: data/EXAMPLE_synthetic_likes.csv  (32 rows, 16 participants)
  condition A (irreversible feedback): n=16  median=3.5  mean=4.062  range=[0,9]
  condition B (no feedback          ): n=16  median=22.5  mean=24.5  range=[5,45]
  median difference A-B: -19.0
  paper (Section 3.2.2) reports A: 2.5, B: 27.5; delta vs reported: {'A': 1.0, 'B': -5.0}
```

## About that last block

`data/EXAMPLE_synthetic_likes.csv` is **synthetic filler I generated** to
exercise `src/analyze.py`. It is not the paper's data, it was not drawn to match
the paper's numbers, and its medians say nothing whatsoever about the paper's
finding. The paper's own like counts have never been released; that is why row
I7 of the reproduction table is **blocked**.

## Provenance of `src/punishable_ai/`

`src/punishable_ai/spider_sim.py` is my Python port of `spider/spider.ino` from
[github.com/BeatRossmy/PunishableAI](https://github.com/BeatRossmy/PunishableAI)
(MIT licence, by the paper's first author, published for the DIS '20 predecessor
paper). The upstream repository was cloned to `/tmp` and is not vendored here.
It is the only executable artifact by the authors that touches this paper's
material, and this paper does not cite it.

## Layout

```
README.md              this file
REPRODUCIBILITY.md     verdict, per-component table, boundary, hidden decisions, scorecard
SOURCES.md             paper identity; 30 artifact searches with results
UNVERIFIED.md          everything unconfirmed, with the blocker
verdict.json           the above as data
instrument.json        study protocol, analysis contract, servability
src/                   the inner-loop implementation
data/                  synthetic example input for src/analyze.py
```
