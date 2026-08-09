# Sources

## The paper

| Field | Value |
|---|---|
| Title | Point of no Undo: Irreversible Interactions as a Design Strategy |
| Authors | Beat Rossmy (LMU Munich), Nađa Terzimehić (LMU Munich), Tanja Döring (University of Bremen), Daniel Buschek (University of Bayreuth), Alexander Wiethoff (LMU Munich) |
| Venue | CHI '23 — Proceedings of the 2023 CHI Conference on Human Factors in Computing Systems, Hamburg, Germany, 23–28 April 2023. Article 140, 1–18 |
| DOI | [10.1145/3544548.3581433](https://doi.org/10.1145/3544548.3581433) |
| Publisher | ACM. Crossref records the licence as ACM's copyright policy (`https://www.acm.org/publications/policies/copyright_policy#Background`), i.e. not an open licence; the PDF's first page reads "Copyright held by the owner/author(s). Publication rights licensed to ACM." |
| Open access | OpenAlex and Semantic Scholar both record `oa_status: gold` with the ACM PDF as the OA location |
| Award | CHI 2023 Honorable Mention, per Tanja Döring's page (https://www.tanjadoering.de/, fetched 2026-08-09) |
| Full text used here | Author copy at `https://www.medien.ifi.lmu.de/pubdb/publications/pub/rossmy2023chi/rossmy2023chi.pdf` — HTTP 200, 2,483,615 bytes, 18 pages, SHA-256 `094410b844d1e0054c2d73ca88ba7f48f86604669229c169c4f4a92ee5e6e2ee`, fetched 2026-08-09. Text extracted with `pypdf` 3.17.4. The file was kept in `/tmp`, never in this repository. |

All section numbers used in this repository refer to that PDF.

## Every artifact search performed (2026-08-09)

"Result" is what the fetch actually returned, not what I expected.

### The paper's own record

| # | Where | What I looked for | Result |
|---|---|---|---|
| 1 | Full text of the PDF: data-availability statement, footnotes, acknowledgements, all 142 references | any URL to code, data, a repository or supplementary files | **none**. `grep -i "github\|gitlab\|osf.io\|zenodo\|supplement\|available at\|data availability\|open source\|repository"` over the extracted text returns nothing. The paper carries no data-availability statement, no artifact badge on its first page, and no footnote pointing at materials. The only URLs in the body are `www.nngroup.com/articles/ten-usability-heuristics` (footnote 2) and `artelectronicmedia.com/.../helena-by-marco-evaristti/` (footnote 5), both citations of other people's work. |
| 2 | `https://dl.acm.org/doi/10.1145/3544548.3581433` (DL landing page, supplementary-material section) | supplementary files, artifact badges, video figure | **blocked**, not "absent". `web_fetch` → `url_not_accessible`; `curl -I https://dl.acm.org/doi/pdf/10.1145/3544548.3581433` → `HTTP/2 403` with `cf-mitigated: challenge`. I could not inspect the DL's supplementary tab from this environment. See UNVERIFIED.md. |
| 3 | `https://api.crossref.org/works/10.1145/3544548.3581433` | licence, related identifiers | HTTP 200. Licence URL is ACM's copyright policy; no CC licence; no related-identifier links to data or code. |
| 4 | `https://api.openalex.org/works/doi:10.1145/3544548.3581433` | repository copies, OA locations | HTTP 200. One location only (the ACM DL); `any_repository_has_fulltext: null`; 10 citing works. |
| 5 | `https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3544548.3581433` | open-access PDF, linked artifacts | HTTP 200. `openAccessPdf` points back at the ACM DL. No artifact links. |
| 6 | `https://programs.sigchi.org/chi/2023/...` (CHI '23 programme, incl. `/api/...` guesses) | the paper's programme entry, talk video, materials | **not retrievable**. The site is a client-rendered SPA; every URL returns the same shell HTML with no content. |

### Repositories and archives

| # | Where | Query | Result |
|---|---|---|---|
| 7 | GitHub search API, repositories | `rossmy` | 0 repositories |
| 8 | GitHub search API, repositories | `punishable ai` | 3; one relevant: `BeatRossmy/PunishableAI` |
| 9 | GitHub search API, repositories | `socialshredder` | 0 |
| 10 | GitHub search API, repositories | `"4 on the floor" sequencer` | 0 |
| 11 | GitHub search API, repositories | `shredder polaroid social` | 0 |
| 12 | GitHub search API, repositories | `irreversible interactions` | 4, none by these authors or about this work |
| 13 | GitHub user `BeatRossmy`, all 28 public repositories enumerated from `https://github.com/BeatRossmy?tab=repositories` (pages 1–2) | a repository for this paper, for *4 on the Floor*, or for *SocialShredder* | **none**. The 28 repos are: COMB, CreativeCoding, EYESY_OS_for_RasPi, InternetRadio, LightInstallation, MidiBrainModule, MidiFoot, MidiRuler, MuBu, Musical-Grid-Interfaces, NeuralNorns, NeuralNorns_Project, NornsTakt, P5_GRID, P5_grid_ui, PunishableAI, StringTouch, SuperBrain, SuperBrainGrid, TeensyMultiSamplePlayer, TouchGrid, ZORNS, code_scribbles, ii_dodeca, midi_cv_pal, midigrid, model_reader, norns-community. Only `PunishableAI` relates to this paper. |
| 14 | `https://github.com/BeatRossmy/PunishableAI` | firmware for the robot of Section 3.3 | **found**. Public, MIT licence, 3 commits, `README.md` + `LICENSE` + `spider/spider.ino`. Cloned to `/tmp` (216 KB). The README describes the DIS '20 study, not the CHI '23 paper. |
| 15 | `https://vimeo.com/348646727` (linked from that README) | project video | **found**, HTTP 200, page title "Punishable AI". This is the DIS '20 project video. |
| 16 | Zenodo API, `q="irreversible interactions" Rossmy` | a deposit for this paper | **none** for this paper. Note: `https://zenodo.org/api/records/3672988` (fetched, HTTP 200) is "The Modular Backward Evolution — Why to Use Outdated Technologies" by Rossmy & Wiethoff, 2019 — the first author does deposit on Zenodo for other work, just not for this paper. |
| 17 | OSF API, `nodes?filter[title]=irreversible interactions` and `=point of no undo` | project or materials | **none** (0 hits each) |
| 18 | OSF API, `registrations?filter[title]=irreversible` | a preregistration | **none related** (12 hits, all unrelated medical/physics registrations) |
| 19 | figshare API search, `irreversible interactions design strategy Rossmy` | deposit | **none** (0 hits) |
| 20 | Dryad API search, `Rossmy` | dataset | **none** (0 hits) |
| 21 | GitLab | searched via the general web searches below; no GitLab project by these authors surfaced | **none** |

### Author and institution pages

| # | Where | Result |
|---|---|---|
| 22 | `https://beatrossmy.com/` (first author's portfolio, linked from his LMU page), fetched HTTP 200 | **none for this paper.** The portfolio links code for COMB, StringTouch, SuperBrain, TouchGrid and PunishableAI. It does not mention "Point of no Undo", "irreversible", "4 on the Floor" or "SocialShredder" anywhere (case-insensitive grep of the page: only "Punishable" matches). |
| 23 | `https://www.medien.ifi.lmu.de/pubdb/publications/pub/rossmy2023chi/` (the directory holding the author copy of the PDF) | HTTP 200 but "Verzeichnisanzeige nicht möglich" — no directory listing, so no ancillary files are exposed. Only the PDF itself is reachable. |
| 24 | `https://www.medien.ifi.lmu.de/team/beat.rossmy/`, `.../nadja.terzimehic/`, `.../alexander.wiethoff/` | HTTP 200 each. No links to GitHub, OSF, Zenodo, Vimeo or YouTube on any of the three. |
| 25 | `https://www.tanjadoering.de/` | HTTP 200. Lists the paper and the CHI 2023 Honorable Mention. No artifact link. |
| 26 | `https://www.uni-bremen.de/en/human-computer-interaction/publications` | HTTP 200. Lists the paper. No artifact link. |
| 27 | `https://www.hciai.uni-bayreuth.de/en/team/daniel_buschek/index.php` | HTTP 200. Lists the paper. No GitHub/OSF/Zenodo link for it. |
| 28 | `https://eref.uni-bayreuth.de/id/eprint/76605/` (institutional repository record) | HTTP 200. Metadata only — no deposited full text, no supplementary files. |
| 29 | ResearchGate record `.../370180372_Point_of_no_Undo_...` | "Request full-text PDF" — no public deposit, no artifacts. |
| 30 | YouTube `https://www.youtube.com/watch?v=gyhH74Ymw4I`, titled as the CHI 2023 talk for this paper in web search results | **unverified.** `web_fetch` → `url_not_accessible`; `curl` → 302 to a consent interstitial. I never successfully retrieved the page, so I do not count it as an artifact. See UNVERIFIED.md. |

### What the searches add up to

- No code, data, preregistration, or supplementary archive was released **for this paper**.
- One artifact exists for one of the three speculations, published under the *predecessor* paper: `BeatRossmy/PunishableAI` (MIT). This paper does not reference it; I found it by searching GitHub for the artifact's name. It is the reason the *Punishable AI* rows of the reproduction table are the strongest ones in this audit.
- Nothing was found and then lost: there are no dead links. Every "none" above is an absence, not a rot.

## Third-party material used, and where it lives

| Item | Location | Note |
|---|---|---|
| Paper PDF | `/tmp/rossmy2023chi.pdf` | not committed |
| Extracted text | `/tmp/paper.txt` | not committed |
| `BeatRossmy/PunishableAI` clone | `/tmp/punishable_ai_upstream/` | not committed; `src/punishable_ai/spider_sim.py` is my own Python port, written from that firmware and attributed in its docstring |

## Prior publication reused by the paper

Reference [119]: Beat Rossmy, Sarah Theres Völkel, Elias Naphausen, Patricia Kimm, Alexander Wiethoff, Andreas Muxel. 2020. *Punishable AI: Examining Users' Attitude Towards Robot Punishment.* DIS '20, 179–191. [10.1145/3357236.3395542](https://doi.org/10.1145/3357236.3395542). Section 3.3.2 of the CHI '23 paper says the detailed results of that N=20 exploration "have been published in [119]".
