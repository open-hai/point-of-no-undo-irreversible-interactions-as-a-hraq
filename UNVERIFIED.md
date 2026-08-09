# Unverified

Everything I could not confirm, each with the specific thing that stopped me.
Nothing on this list is claimed anywhere else in this repository as established.

## Access

| # | Claim I could not verify | Blocker |
|---|---|---|
| U1 | Whether the ACM Digital Library lists **supplementary material** (a video figure, a talk recording, attached files) for this paper | `dl.acm.org` returns `HTTP/2 403` with `cf-mitigated: challenge` to `curl`, and `web_fetch` returns `url_not_accessible`. I never loaded the article page. The scorecard's "no supplement" is therefore inference from the published PDF (no artifact badge, no pointer in the text), not observation. |
| U2 | Whether the YouTube video `https://www.youtube.com/watch?v=gyhH74Ymw4I` is this paper's CHI 2023 talk | Web search returns it with a matching title and author list, but `web_fetch` gives `url_not_accessible` and `curl` gives a 302 to a consent interstitial. I did not retrieve the page, so I do not count it as a found artifact. |
| U3 | Whether the CHI '23 programme entry lists materials for this paper | `programs.sigchi.org` is a client-rendered SPA; every URL and every API path I tried returns the same shell HTML with no content. |
| U4 | Whether the paper has an ACM artifact badge | Follows from U1. The author copy of the PDF shows none, which is good but indirect evidence. |

## The artifacts

| # | Claim I could not verify | Blocker |
|---|---|---|
| U5 | That my chip tracker resembles the authors' | Section 3.1.1 describes it in twelve words. No code, no footage, no photographs of the rig beyond Figure 2, no camera model. My 64/64 cells correct is a statement about my own synthetic frames and nothing else. |
| U6 | The colour→sound mapping, the scale, the tempo, and the DAW patch of *4 on the Floor* | Unstated (D1–D4). The MIDI file this repo produces is structurally faithful and sonically arbitrary. |
| U7 | Whether removal in configuration B collapses the column | Unstated (D6). Both readings are consistent with "allowed removing individual chips at all times", and they are different instruments. |
| U8 | The shredder's mechanics: strip size per like, motor run time, USB command set, latency, and the number of likes that destroy a Polaroid | Unstated (D9, D10). Section 3.2.2 establishes only that complete destruction was reachable within a session. |
| U9 | What condition B of *SocialShredder* physically looked like — whether the loaded shredder sat there silently | Unstated (D11). This matters because the conditions were counterbalanced, so half the participants met condition B after learning what the machine does. |
| U10 | Whether the released `spider.ino` is the firmware that ran during the CHI '23 study | The repository was published for the DIS '20 paper; the CHI '23 paper does not reference it. The robot is described identically in both, but a later revision could exist. Every *Punishable AI* row in the reproduction table inherits this caveat, including the two mismatches. |
| U11 | Whether the physical robot's leg-break sensing worked despite the firmware never reading the switch pins | Possible in principle — a different sketch, a companion program, or a wired indicator. Nothing public shows one. I record the mismatch as being with the released code, not with the physical artifact. |
| U12 | How many broken legs actually stopped the robot walking | The paper only reports participants' belief (§3.4). My tripod model (D14) is mine. It is not a reproduction of anything. |
| U13 | The photodiode and capacitive-touch circuits | Not in the paper, not in the repository. The `INPUT_PULLUP` configuration of pins 8–13 is in tension with a HIGH-means-touched test (D16); with the sensor board undocumented I cannot say whether that is a quirk of the hardware or a latent bug. |

## The studies

| # | Claim I could not verify | Blocker |
|---|---|---|
| U14 | Any of the reported human results | Outer loop. Not attempted, by design. |
| U15 | Where the 4 participants missing from the *4 on the Floor* mindset split went (20 reported, 8 + 6 + 2 accounted for) | The paper's counts are all I have; no coded data was released. Possible innocuous readings: participants who endorsed both mindsets, or who said nothing on the topic. The paper does not say which. |
| U16 | Whether the theme counts (n=6, 6, 4, 3 and n=15, 8, 10, 11) count participants or statements | The prose says "participants" for some counts and is ambiguous for others; no denominator or coding unit is given (D19). |
| U17 | What the "rate some aspects of their experience" ratings in §3.2.2 were, and what they showed | The measure is mentioned once and never reported (D18). |
| U18 | Whether the medians 2.5 and 27.5 are medians of a per-condition count over all 16 participants | The most natural reading, but the paper gives no n per condition, no range, no test, and no data. |
| U19 | The colloquium in §3.3.2: how many experts, what was asked, how it was recorded | The paper says the discussions were "non-directive interviews" and that the setting was "due to the general structure and nature of the event". No count, no protocol. |
| U20 | Ethics review status | The paper's footnote 3 states consent, anonymisation and fair compensation. No ethics board or approval number is named. |
