# F29AI Coursework 1 — Group Work Log

This repository records task allocation, implementation progress, and validation evidence for the Sudoku solver and lunar planning tasks.

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
[the bilingual contribution draft](reports/gong_contribution_bilingual.md).
At the time of that handoff, Part 2C, the combined report, and video were outstanding.

## Start here

- [Python Sudoku learning reference](reference/part1b/README.md)
- [A* understanding exercise](learning/A_STAR_WALKTHROUGH.md)
- [Task allocation and schedule](docs/WORK_SPLIT.md)
- [Progress log](docs/PROGRESS.md)
- [English writing and evidence review](docs/WRITING_REVIEW.md)
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
