# Technical and Writing Review

Review date: 27 October 2026.
Reviewed implementation: `96f1e93fd4dff0084ff2c8a663f6b631abc80c09`.

## Scope and result

Reviewed the Sudoku solver and benchmark, the five PDDL files, the validation
tools, the saved measurements, the contribution draft, and the run instructions.
No new functional defect was found in the reviewed scope. This is not a claim
that testing proves correctness for every possible input.

The working code was retained. Changes focus on clearer English and a separate
English version of the collaborator's contribution.

## Checks performed

| Check | Actual outcome |
| --- | --- |
| Sudoku solver, parser, CLI, and benchmark tests | All 21 tests passed |
| Mission 1 planning and independent replay | All goals achieved, 10 actions |
| Mission 2 planning and independent replay | All goals achieved, 20 actions |
| Mission 3 planning and independent replay | All six goals achieved, 24 actions, four astronaut movements |
| Astronaut and inherited-rule checks | 24,380 typed instances in 23 states: 180 allowed with correct effects, 24,200 forbidden |
| Base initial setup, directed roads, and Mission 3 goals | Match Mission 2 as required |
| Base source files | Match the collaborator's recorded SHA-256 hashes |

Commands used from the repository root:

```sh
.venv/bin/python -m unittest reference.part1b.test_solver reference.part1b.test_benchmark -v
.venv/bin/python tools/validate_extension.py --output /private/tmp/f29ai-review-part2c
```

The new planning summary is retained in
`evidence/review-2026-10-27/planning-validation.json`. The original measurements
and planning evidence were not overwritten. The fresh run is a regression
check, not a new performance comparison.

## Writing audit before revision

| Location | Observation | Revision |
| --- | --- | --- |
| Contribution draft, CSP introduction | Several definitions share one sentence. | Keep the formal definitions and split the explanations. |
| Contribution draft, complexity section | The fixed-board caveat is correct but dense. | Separate the search-tree calculation from its assumptions. |
| Contribution draft, capacity section | One sentence describes several action effects. | State each capacity change in a shorter sentence. |
| Contribution draft, validation section | Long lists mix evidence with its limitations. | Separate what was tested from what the tests do not establish. |
| Contribution draft, headings and discussion paragraphs | English and Chinese are interleaved. | Retain the original and provide a separate English draft. |
| Part 2C instructions | Terms such as "gated action" and "initial facts" can be made more direct. | Use "affected action" and explain the starting setup plainly. |

No promotional claims or invented results need to be added. Keep equations,
references, measured counts, uncertainty, and the distinction between a valid
plan and a shortest plan. Use ordinary technical English rather than inserting
errors or informal language to imitate a particular student.

## Evidence and references

- Numerical claims were checked against the Sudoku and PDDL JSON records.
- The A* derivation remains conditional on a unit-cost action filling one cell.
- The CSP and backtracking references in the draft were reopened at their
  official Berkeley and AIMA addresses. They support the concepts; the Sudoku
  search-tree calculation remains the draft's stated derivation.
- Pyperplan's official repository describes its STRIPS support. The actual
  local planner version is recorded separately in the evidence.

Existing citation identifiers and URLs are retained in the English draft.
Numbers and formal definitions are not changed during editing.

## Remaining work before submission

- The group report still needs Part 1B and Part 2C prose, a cover page, actual
  member details, the video link, and a consistent reference list.
- Part 1 must fit within four pages and Part 2 within three pages; the cover
  page and references are outside those limits.
- The Sudoku practice inputs have no verified external provenance or certified
  difficulty ratings. Do not describe them as an established benchmark dataset.
- The Sudoku interface is command-line only. Do not claim a GUI exists.
- The pair still needs to record a video of at most eight minutes, with both
  members explaining substantial parts of the work and all three missions shown.
- The final ZIP must be assembled and checked. The feature branch has not been
  merged into `main`.

## Change report

The English contribution draft uses shorter sentences, consistent predicate and
capacity terms, and direct explanations of the implementation. The Part 2C
instructions use plainer wording. No code, measured value, equation, citation,
or original attribution is changed. The bilingual source is retained for
comparison, and the contribution is not presented as a completed group report.
