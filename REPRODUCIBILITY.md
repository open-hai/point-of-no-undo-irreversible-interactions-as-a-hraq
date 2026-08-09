# Reproducibility audit — *Point of no Undo: Irreversible Interactions as a Design Strategy*

Rossmy, Terzimehić, Döring, Buschek & Wiethoff. CHI '23, article 140.
[10.1145/3544548.3581433](https://doi.org/10.1145/3544548.3581433). Audited 2026-08-09.

## Verdict: **partial**

This is a speculative/critical design paper. Its argument is carried by three
built artifacts — *4 on the Floor*, *SocialShredder*, *Punishable AI* — and by a
conceptualisation drawn from them. The paper describes each artifact in one or
two paragraphs of prose and releases nothing: no code, no data, no schematics,
no supplementary archive, no preregistration (SOURCES.md, searches 1–30).

What that means for reproduction is asymmetric. The *Punishable AI* robot has a
public firmware repository — published under the earlier DIS '20 paper [119],
never referenced by this one, found by searching GitHub for the artifact's name
— and against that firmware the paper's claims can actually be checked. They
mostly hold, and two do not. The other two artifacts exist only as prose; I could
rebuild their *mechanics* faithfully enough to run, but nothing about my
rebuild can be compared with theirs, so those rows are partial by construction,
not by effort. The paper's single number — median likes 2.5 vs 27.5 — is blocked
outright: no per-participant data exists anywhere public.

Nothing here is a criticism of the paper's contribution, which is conceptual.
It is a statement of what a reader can re-run.

## Per-component reproduction table

Inner-loop components only. `evidence` is what I actually ran and saw, or the
specific thing that stopped me. Outer-loop components are listed further down
and are never scored.

| # | Component | Section | Outcome | Evidence / blocker |
|---|---|---|---|---|
| I1 | *4 on the Floor*: 8×8 gravity grid, and configuration A's rule that a thrown chip cannot be removed | 3.1.1, 3.1.2 | **reproduced** | `src/four_on_the_floor/board.py`. Run: 13 chips dropped, `remove()` raises `IrreversibleActionError` — "configuration A: a chip that has been thrown cannot be removed". The grid size (8×8) and the drop mechanic are stated outright, so this is the one part of this artifact the paper fully determines. |
| I2 | *4 on the Floor*: webcam chip tracking | 3.1.1 | **partial** | `src/four_on_the_floor/vision.py` runs: 64/64 cells classified correctly on a synthetic frame with 2 % sensor noise. But the paper's whole description is "Via a webcam-based image processing approach, the chips were tracked in real time" — no colour space, no thresholds, no calibration, no library, no footage, no rig. My detector works; whether it resembles theirs is unknowable. |
| I3 | *4 on the Floor*: grid → MIDI step sequencer | 3.1.1 | **partial** | `src/four_on_the_floor/sequencer.py` produces `out/four_on_the_floor.mid`: 13 note events, column = time step, stacked chips = simultaneous notes, looped. The *structure* is stated ("columns … represent time increments", "stacking chips forms chords"). The colour→pitch table, tempo, note length and DAW patch are not, so the sounding result cannot be matched. |
| I4 | *4 on the Floor*: configuration B, "removing individual chips at all times" | 3.1.2 | **partial** | Implemented and runs (13 → 12 chips). Blocked from being more than partial by one unanswerable question: does removing a chip let the stack above it fall? I assume yes; the paper does not say, and the two readings are different interfaces. |
| I5 | *SocialShredder*: mock-up social-media feed with likes | 3.2.1 | **partial** | `src/social_shredder/platform.py` implements a headless feed with like/unlike. The paper never states the feed length, the image set, the layout, or whether it scrolled; no screenshot beyond Figure 3 and no code exist. |
| I6 | *SocialShredder*: like → shredder trigger, and the irreversibility invariant | 3.2.1 | **partial** | Runs: 5 likes → 5 shred steps; `unlike` removes the like from the interface and leaves `shred_steps` at 5; `restore()` raises. Condition B produces 0 shred steps for 40 likes. The USB protocol, the strip size per like and the number of likes needed for complete destruction are unstated; my "30 likes destroy it" is invented. |
| I7 | *SocialShredder*: median likes, A: 2.5 vs B: 27.5 | 3.2.2 | **blocked** | No per-participant data was released and none exists in any archive I searched (SOURCES.md 16–21). `src/analyze.py` is the re-analysis, and it runs — but only on `data/EXAMPLE_synthetic_likes.csv`, which I generated and which says nothing about the paper. |
| I8 | *Punishable AI*: hexapod gait controller | 3.3.1 + released firmware | **reproduced** | `src/punishable_ai/spider_sim.py` is a line-by-line port of `spider/spider.ino` from `github.com/BeatRossmy/PunishableAI` (MIT). Runs 3 s of walking; three-phase gait, 500 ms phases, 1°/10 ms servo stepping, `map(angle,0,180,120,550)` all reproduce. The paper never states the leg count; the firmware does — six (legs `a`–`f`). |
| I9 | *Punishable AI*: touch sensing → the robot "trembles" | 3.3.1, 3.3.2 | **reproduced** | Touching leg `c`'s pin emits `TOUCH DETECTED` and sets `jiggleCounter = 100`, producing 100 ticks of random ±10° limb motion — which is what Section 3.3.2 describes as "the robot started trembling upon touch, to depict resistance". |
| I10 | *Punishable AI*: negative stimulus (bright flashlight) | 3.3.1 | **reproduced** | `analogRead(A1) <= 400` triggers the same `jiggle()`. Reproduced exactly, *and* it exposes a mismatch: the paper presents scolding, light and breaking as three escalating feedback channels, but in the released firmware light and touch trigger the identical response and scolding has no code path at all — the escalation is distinguishable to the participant, not to the robot. |
| I11 | *Punishable AI*: sensing leg state through interrupted PCB traces | 3.3.1 | **blocked** | Section 3.3.1: "Through the PCB legs, the state of the legs (interrupted traces) and touches of the participants (capacitive areas) could be sensed." The released `loop()` configures switch pins 2–7 as `INPUT_PULLUP` and then never reads them. My port confirms the consequence: with three legs marked broken the commanded servo angles after 3 s are *identical* to the intact robot. No schematic, no other firmware, no hardware — nothing to build from. |
| I12 | *Punishable AI*: the claim that no learning was implemented | 3.3.1 | **reproduced** | "the learning of the system was not implemented" holds against the code, and the firmware says how the robot "gets off track": `currentMovement = random(0,3)` picks straight/left/right on every switch-on. The deviation the participant corrects is a random draw. |
| I13 | Involvement taxonomy (closeness × time) and its empty cell | 4.3 | **partial** | `src/taxonomy.py`: 3 of 4 checks pass. All four cells are populated in the text; "close & delayed" indeed contains no HCI related work (only a hypothetical, an artwork, and material processes), which is what the paper claims. The failing check: *4 on the Floor* is never placed in the grid at all, although Section 5 describes it as acting "only by proxy" with a "delayed" change — i.e. far & delayed. |
| I14 | Design-strategy mapping: altering / creating / destructing | 5, Fig. 6 | **reproduced** | `src/taxonomy.py`: each of the three speculations carries exactly one strategy (SocialShredder → altering, 4 on the Floor → creating, Punishable AI → destructing), with no strategy unused and none doubled. The paper's own caveat that there is "a thin line between alteration and destruction in the SocialShredder" is carried in the data structure. |
| I15 | Internal arithmetic of the reported participant counts | 3.1.2, 3.2.2 | **reproduced** | `src/consistency.py` recomputes the sums. Two findings: for *4 on the Floor* the three mutually exclusive groups (8 + 6 + 2) account for 16 of 20 participants, leaving 4 unaccounted; for *SocialShredder* the reported theme counts sum to 44 over 16 participants, so participants are multiply coded — normal practice, but the paper never states a denominator or a coding unit. |

**Counts: 7 reproduced, 6 partial, 2 blocked, 15 inner-loop components.**

> *Derived rate (a footnote to the table, not a headline).* On this
> decomposition, 7/15 ≈ 47 % of inner-loop components reproduce fully and a
> further 6/15 run but cannot be checked against the originals. That number is a
> summary of **this** slicing of **this** paper. Slice the three artifacts as
> three components instead of eleven and the same evidence yields a different
> percentage. It is not comparable to another paper, to another auditor, or to
> another run of this audit, and it should never be quoted without the table
> above.

### Mismatches

A mismatch is recorded even where the outcome is *reproduced* — the outcome says
whether I could re-run it, the mismatch says whether the paper's description
survived contact with the artifact.

| Row | Kind | Paper says | I observe | Delta |
|---|---|---|---|---|
| I10 | contradiction | Three escalating feedback methods: scolding, bright flashlight, breaking a leg (§3.3.1) | In the released firmware, the flashlight branch (`analogRead ≤ 400`) and the touch branch call the same `jiggle()`; scolding has no code path at all | The escalation is an escalation for the participant, not a graded response by the robot |
| I11 | contradiction | "the state of the legs (interrupted traces) … could be sensed" (§3.3.1) | `loop()` in the released firmware never reads pins 2–7; gait output with three broken legs is byte-identical to the intact robot | Leg-state sensing is configured but unused in the only released implementation. Caveat: that firmware was published for DIS '20; a later, unreleased revision may differ |
| I15 | numeric | N = 20 for *4 on the Floor* (§3.1.2), split into 8 + 6 in favour and 2 rejecting | The three groups account for 16 participants | 4 participants unaccounted for (20 − 16) |
| I15 | numeric | Theme counts n = 15, 8, 10, 11 for *SocialShredder*, N = 16 (§3.2.2) | Sum = 44 over 16 participants | Multiple coding is implied but never stated; no denominator is given for any count |

## The inner/outer boundary

**Inner loop** — everything above. Grids, image processing, MIDI mapping, a
shredder trigger, robot firmware, and the paper's own classifications and
arithmetic. None of it needs a person.

**Outer loop — not attempted, not scored, not simulated.** Each of these needs
participants; where a row looks merely underspecified rather than human, the
justification says why it is still outer.

| # | Component | Section | Why outer |
|---|---|---|---|
| O1 | *4 on the Floor* lab AB study: 20 participants (11 ♀, 9 ♂, mean 24.2 y), configurations A and B in counterbalanced order, three trials each, ≈30 min | 3.1.2 | Requires participants using a physical instrument. |
| O2 | *4 on the Floor* semi-structured interviews and inductive thematic analysis (creative n=6, thoughtful n=6, challenge n=4, playful n=3; mindset split 8 / 6; 2 rejecting) | 3.1.2 | Themes are constructed from participants' speech by human coders. The arithmetic over the published numbers is inner (I15); the numbers themselves are outer. |
| O3 | Observed behaviour in the irreversible condition: participants pausing and stepping back to get a holistic overview | 3.1.2 | Observation of people. |
| O4 | *SocialShredder* exploration: 16 participants (9 ♀, 7 ♂, mean 27 y), counterbalanced conditions A (shredding) and B (no feedback), Polaroid taken beforehand and loaded into the shredder without telling them | 3.2.2 | Requires participants, a covert manipulation, and an experimenter with a camera. |
| O5 | *SocialShredder* interview reports and ratings: n=15 longer contemplation, n=8 heightened awareness, n=10 felt influenced, n=11 no amusement, 4 continued liking after complete destruction | 3.2.2 | Self-report from participants. |
| O6 | *SocialShredder* observation that shredding pulled attention off the screen, incl. one participant trying to pull the photo back out | 3.2.2 | Observation of people. |
| O7 | *Punishable AI* exploration: 20 participants (9 ♀, 11 ♂, mean 26 y) executing scolding, light stimulus, and leg-breaking; detailed results in DIS '20 [119] | 3.3.2 | Requires participants breaking a physical robot. |
| O8 | Expert colloquium: demonstration to professors and senior researchers, non-directive interviews, observed advocacy and repeat visits | 3.3.2 | Requires the experts, and an experimenter in conversation with them. |
| O9 | Key observations O1–O3 (interruption of interaction flow, interest in the altered object, reasoning beyond the rational) | 3.4 | Generalisations over participant behaviour across all three studies. |
| O10 | The conceptualisation of irreversibility: artifact value and symbolism, actant-dependent context, involvement | 4 | Its evidential base is the participants' behaviour and statements (it is derived from O1–O3 and from comparing the speculations with exemplar projects). The parts of Section 4 that *are* mechanically checkable — the taxonomy's coverage and its empty cell — are split out as I13. |

Two boundary calls worth defending:

- **The three artifacts are inner even though I cannot buy the hardware.** A
  physical shredder or a hexapod is expensive and awkward, not human. The
  control logic, the state machines and the irreversibility invariants are the
  reproducible substance and they are what `src/` contains.
- **The paper's conceptual framework is outer, and its self-consistency is
  inner.** I will not re-derive "value, symbolism, context, involvement" from
  the artifacts — that is interpretive work grounded in what participants did.
  I will check whether every cell of the 2×2 is populated, whether the empty
  cell is really empty, and whether the counts add up. Those need no one.

## Hidden decisions

Choices a reimplementation must make and the paper never states. "Sensitivity"
is how much the result moves if the choice is wrong.

| # | Question | Where the paper leaves it open | What I assumed | Sensitivity |
|---|---|---|---|---|
| D1 | Which colours are the chips, and how many? | §3.1.1 says "colored discs" and "The colors represent pitch or samples" | Four colours: red, yellow, blue, green | Low for the pipeline, total for the music: the colour→sound table *is* the instrument |
| D2 | Does a colour select a pitch or a sample? | §3.1.1 offers both — "pitch or samples" | Pitch: colour picks a MIDI channel and a transposition, row picks a scale degree | High. The two readings give different instruments and different musical tasks |
| D3 | Which pitches do the eight rows carry? | §3.1.1 never gives a scale | C minor pentatonic extended over 8 rows | High for the output, none for the mechanism |
| D4 | Tempo, step length, note duration, velocity | §3.1.1 says only "constantly repeated in a loop" | 120 BPM, one column = one eighth note, 90 % gate, velocity 100 | Medium. Tempo changes how much foresight the irreversible condition demands |
| D5 | Chip-tracking method: colour space, thresholds, calibration | §3.1.1: "a webcam-based image processing approach" and nothing else | Rectified grid, per-cell median HSV of a central disc, S ≥ 0.35 and V ≥ 0.18 for "occupied", nearest reference hue | High for a real rig (lighting, glare through suspended acrylic); nil on synthetic frames |
| D6 | In configuration B, does removing a chip collapse the stack above it? | §3.1.2: "allowed removing individual chips at all times" | Yes, the column collapses (Connect-Four physics) | **High.** Non-collapsing removal is a different instrument: it makes arbitrary holes editable, which is a much stronger undo than the paper's contrast implies |
| D7 | What is a "trial" in the three-trials-each protocol, and how long? | §3.1.2: "three trials each (about 30 minutes)" | Not modelled; ~5 min per trial per condition would fit the total | Medium for the study, none for the code |
| D8 | How long is the mock feed, and what is in it? | §3.2.1 says only "the image feed of the mock-up social media platform" | 60 posts | Medium: a short feed caps the like count and therefore caps the paper's own dependent measure |
| D9 | How much of the Polaroid does one like consume, and how many likes destroy it? | §3.2.1 gives neither; §3.2.2 shows complete destruction is reachable | 30 likes = fully shredded, uniform strips | **High.** It sets the point at which the feedback stops escalating, which is exactly the "tipping point" Section 5 theorises about |
| D10 | How is the shredder driven over USB, and with what latency? | §3.2.1: "Via USB, the shredding action was triggered" | Abstracted to a `shred()` call with a timestamp | Low for the logic, high for the experience (the noise and its timing are the manipulation) |
| D11 | In condition B, was the shredder present and loaded but silent, or absent? | §3.2.2 says condition B is "without any feedback"; §3.2.1 says the Polaroids were placed in the shredder at the start | Present and loaded, inert | **High.** A visible loaded shredder in B is a very different control condition, and the conditions were counterbalanced |
| D12 | How were the A/B orders assigned? | §3.1.2 and §3.2.2 both say "counterbalanced" and stop | Balanced pairs, no seed recorded | Medium; with N=16–20 and a strong order effect (participants learn that likes shred), imbalance would matter |
| D13 | How many legs does the robot have, and where do they break? | Never stated in the paper — "an insect", "gradually breaking the robot's legs", "predetermined perforation" | Six, recovered from the released firmware (`a`–`f`), one perforation each, breakable once | Low, because the firmware settles it — but the paper alone does not |
| D14 | When does the robot stop being able to walk? | §3.4 only reports what participants *believed*: "when most legs … were broken, it would be unable to walk" | My own model: each of the three gait phases needs an intact swing leg and ≥4 of 6 legs must survive | **High and entirely mine.** With this model the robot stops after 3 breaks; the paper asserts nothing testable here |
| D15 | What does the robot do when a leg breaks? | §3.3.1 claims leg state can be sensed but describes no reaction | Nothing — matching the released firmware, which never reads the switch pins | High: it is the difference between a robot that registers punishment and one that only appears to |
| D16 | Photodiode circuit and the meaning of `analogRead ≤ 400`; polarity of the touch inputs | Not in the paper; the threshold is in the firmware | Taken verbatim from the firmware | Medium: with pins 8–13 set `INPUT_PULLUP`, an unconnected touch input reads HIGH and would trigger `TOUCH DETECTED` continuously, so the sensor must actively drive the line — the circuit is not documented anywhere |
| D17 | What was said when "scolding", in which language, and who decided when to escalate? | §3.3.1 gives the order, §3.3.2 calls it "a stringent escalation" | Fixed order scold → light → break, experimenter-paced, no de-escalation | Medium for the study; the code path does not exist either way |
| D18 | What did participants rate, and on what scale? | §3.2.2: "to rate some aspects of their experience" — the ratings are never reported | Not modelled; `src/analyze.py` covers only the like counts | Unknown, and unknowable: an unreported measure cannot be checked against anything |
| D19 | Coding procedure: how many coders, what codebook, what unit, any agreement measure? | §3.1.2 says "clustered and coded by the project researchers using an inductive approach" following Braun & Clarke, in three phases | Not modelled — this is outer-loop work | High for the qualitative claims; unrecoverable without the transcripts |
| D20 | Study language and translation | Footnote 3: "All participants' quotes have been translated into English" | German instruments, translated quotes | Medium: the wording of prompts is unavailable in either language |

## Open-science scorecard

| Criterion | Found | Where |
|---|---|---|
| **Code** | **No** — for this paper | Searched: the paper's full text (no URL, no availability statement), the ACM DL page (403, see UNVERIFIED.md), GitHub search for `rossmy`, `punishable ai`, `socialshredder`, `"4 on the floor" sequencer`, `shredder polaroid social`, `irreversible interactions`, all 28 repositories of `github.com/BeatRossmy`, the first author's portfolio `beatrossmy.com`, three LMU staff pages, `tanjadoering.de`, the Bremen HCI publication list, Buschek's Bayreuth page, ERef Bayreuth, OSF, Zenodo, figshare, Dryad. **Adjacent find, not this paper's:** `https://github.com/BeatRossmy/PunishableAI` (MIT, fetched and cloned) holds the firmware for the robot of Section 3.3, published under the DIS '20 paper [119]. This paper neither references nor releases it, and it covers one of three artifacts. |
| **Data** | **No** | Searched: the paper (no data-availability statement; the only quantitative result, the medians in §3.2.2, is reported inline), OSF nodes (0), OSF registrations (0 related), Zenodo (0 for this paper), figshare (0), Dryad (0), GitHub (as above), all author pages listed in SOURCES.md 22–28. |
| **Licence** | **No** | Crossref returns ACM's copyright policy as the licence; the PDF states "Copyright held by the owner/author(s). Publication rights licensed to ACM" — free to read (OpenAlex: gold) but not openly licensed. No artifact of this paper exists to carry a licence. The adjacent `PunishableAI` repository is MIT. |
| **Preregistration** | **No** | Searched OSF registrations (`filter[title]=irreversible`, 12 unrelated hits) and the paper's own text, which describes exploratory, speculative work — §3 states explicitly "we do not lay focus on empirically testing nor comparing the speculations". A preregistration would be out of keeping with the method; its absence is expected, and recorded here for completeness. |
| **Supplementary artifacts** | **No** (not verifiable from here) | The ACM DL supplementary section is behind a Cloudflare challenge (`HTTP 403`) and the CHI '23 programme site renders client-side only, so I could not enumerate a video figure or supplementary files. Indirect evidence of absence: the published PDF carries no artifact badge and no pointer to supplementary material. A YouTube video titled as this paper's CHI talk appears in search results but could not be fetched; a Vimeo video *was* fetched (`vimeo.com/348646727`, "Punishable AI") and belongs to the DIS '20 project. Recorded as unverified rather than absent — see UNVERIFIED.md. |

## How to re-run this audit's code

```
python -m src.run_all
```

Full expected output is in README.md. `python src/analyze.py <your.csv>` is the
entrypoint that would re-derive the paper's median comparison from a dataset of
the right shape, if one ever appears; `instrument.json` declares its contract.
