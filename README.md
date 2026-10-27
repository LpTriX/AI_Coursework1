# F29AI Coursework 1 — Group Work Log

This repository records task allocation, learning activities, implementation progress, and validation evidence. It also contains the Python Sudoku implementation with its tests and measurements.

Repository documentation, code comments, program output, and future coursework materials should be written in English.

## Astronaut extension (27 October 2026)

Part 2C is implemented in the existing `PDDL/PartC` files. All three missions
have been planned and independently replayed locally. Mission 3's saved plan
has 24 actions, including four astronaut room changes.

See [the extension interfaces and run instructions](docs/PART2C_IMPLEMENTATION.md),
[validation evidence](evidence/part2c/README.md), and
[the Part 2C progress log](docs/PART2C_PROGRESS.md).
The combined report, video, and final submission package are still outstanding.

## Base-PDDL handoff (25 October 2026)

Chengtian Gong's base domain and Mission 1/2 are implemented and locally validated.
Start with [the implemented interface and run instructions](docs/PDDL_HANDOFF.md),
[actual validation evidence](evidence/base-pddl/README.md), and
[the English contribution draft](reports/gong_contribution_english.md).
The [original bilingual draft](reports/gong_contribution_bilingual.md) is retained
for comparison.
At the time of that handoff, Part 2C, the combined report, and video were outstanding.

## Current Part 1B files

The contents of `reference/part1b/` were replaced with the files supplied by
Pinxin Liu from `Sudoku_Part1B`. Run its commands from that directory; its
README, tests, report draft and measurement files describe the current version.
Earlier progress and review entries refer to earlier versions.

## Start here

- [Python Sudoku solver](reference/part1b/README.md)
- [A* understanding exercise](learning/A_STAR_WALKTHROUGH.md)
- [Task allocation and schedule](docs/WORK_SPLIT.md)
- [Progress log](docs/PROGRESS.md)
- [English writing and evidence review](docs/WRITING_REVIEW.md)
- [Current technical and writing review](docs/FINAL_REVIEW.md)
- [Part 1B learning and implementation roadmap](learning/PART1B.md)
- [Sudoku experiment log template](learning/EXPERIMENTS.md)
- [Part 2C learning and validation roadmap](learning/PART2C.md)
- [PDDL handoff checklist](docs/PDDL_HANDOFF.md)

## Agreed task allocation

| Owner | Responsibility | Marks |
| --- | --- | ---: |
| Pinxin Liu | Part 1B: Sudoku implementation, quantitative evaluation, and theoretical A* analysis | 15 |
| Pinxin Liu | Part 2C: astronaut extension and Mission 3 | 5 |
| Chengtian Gong | Part 1A: CSP formulation and complexity analysis | 5 |
| Chengtian Gong | Parts 2A and 2B: base domain, Mission 1, and Mission 2 | 15 |
| Both | Overall presentation, peer review, video, and final submission | 5 |

## Use and version history

After each real milestone, record the changes, validation, and remaining issues, then create a Git commit and publish it to GitHub. Record failures, unfinished work, and checks that have not been run accurately. Experiment logs must contain actual measurements.

The deadline date is 2026-10-29. Check the OUC Canvas submission page for the exact submission time. These checklists do not replace the full specification.

## Group 38 release preparation

Current checks: `python3 -m unittest discover -s reference/part1b -p 'test_*.py' -v`.
There are 17 solver tests and six interface-state tests. The latter use widget
doubles, so they do not verify native Tk rendering or actual keyboard bindings.
The GUI adds conflict highlighting and candidate inspection; it does not
change the backtracking algorithm or the historical benchmark values.

Member IDs, HWU usernames and the video URL have not been supplied. A final
report or ZIP must not be represented as ready until those details, the
recording and member review are complete.

### Build the review report and package

Install ReportLab for report generation (the Sudoku solver does not require it):

```sh
python3 -m pip install reportlab
python3 tools/build_group_report.py
python3 tools/package_submission.py --draft
python3 tools/package_submission.py
```

The PDF is `output/pdf/OUC_CW_1_38_DRAFT.pdf`; the review ZIP is
`output/F29AI CW1 OUC 38 DRAFT.zip`. Draft names and missing-field notices
are intentional. Edit member details and the video URL in
`reports/group38.json`; the non-draft check reports missing metadata.
Do not upload the review ZIP as a completed submission.

Native Tk 9.0 widget creation, actual KeyRelease handling, conflict highlighting
and Clear were additionally smoke-tested on 28 October. The sandbox could not
access macOS window services; that test ran outside the sandbox. The system
Python/Tk combination failed window startup, while the bundled Python 3.12/Tk 9
worked. Use a Python installation with a working Tk, rather than assuming the
system `python3` can open the GUI. Tests using widget doubles do not replace
a full visual review or the group's recording.
