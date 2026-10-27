# Progress Log

This is a work log, not report text. Each entry records what changed, how it was checked, and what remains unfinished. Earlier entries describe the state at their respective milestones.

## 2026-10-22 — Stage 1: Collaboration and version tracking

- Read the full specification and starter file list; confirmed that Pinxin Liu owns Parts 1B and 2C.
- Inspected the GitHub repository, which initially contained only a README, and created a local working copy.
- Recorded the task allocation, handoff dependencies, suggested schedule, and version-recording rules.
- Status at this stage: Sudoku code, base PDDL, extended PDDL, measurements, and report were unfinished.
- Selected language: Python, confirmed by Pinxin Liu.
- Validation: checked documentation, links, and version state only. No coursework tests were run or claimed to pass.

## 2026-10-22 — Stage 2: Part 1B learning and experiment roadmap

- Organised the Python learning sequence: reading and validation, candidates, backtracking, optional MRV, functional checks, experiments, and theoretical A* analysis.
- Created blank templates for experimental conditions, raw measurements, and functional checks without fabricated values.
- Defined the first student implementation milestone: read a TXT board, validate it, print it clearly, and retain actual valid/invalid input runs.
- Status at this stage: roadmap and templates prepared; code and experiments unfinished.
- Validation: checked the roadmap against Part 1B. A* requires theoretical analysis only; no runnable coursework implementation existed yet.

## 2026-10-22 — Stage 3: Part 2C handoff and validation roadmap

- Recorded the base files, predicate/action interface, landing-site choice, planner information, and version evidence needed from Chengtian Gong.
- Checked the five PDDL filenames and domain/problem names against the original starter package.
- Prepared astronaut applicability checks and counterexample scenarios, all marked as not run.
- Dependency: Chengtian Gong's implemented base model had not been received. This did not prevent work on the first Python Sudoku step.
- Status at this stage: preparation and learning roadmaps complete; student implementation, measurements, and report unfinished.
- Next step at this stage: independently implement Python reading, validation, and display before reviewing search.

## 2026-10-22 — Stage 4: Python input-layer learning reference

- Following Pinxin Liu's further request, added the input, validation, and display implementation in `reference/part1b/`.
- Added standard-library TXT/CSV reading, format/range/conflict checks, and readable board display.
- Added three practice inputs without claiming certified provenance, uniqueness, or difficulty.
- Actual validation: `python3 -m unittest reference.part1b.test_solver -v`; 7 tests passed.
- Status at this stage: input reference available; search, CLI, and measurements unfinished; Part 2C awaiting the base-model handoff.

## 2026-10-22 — Stage 5: MRV backtracking, CLI, and semantic checks

- Added backtracking implemented without a solver library, MRV cell selection, recomputed candidate sets, dead-end checks, rollback, a CLI, and statistics.
- The first test run found that the local `python3` was Python 3.9 and lacked `int.bit_count()`. Replaced it with compatible bit counting and updated the minimum-version guidance.
- After the fix, ran `python3 -m unittest reference.part1b.test_solver -v`; all 17 tests passed.
- Coverage included unsatisfiability, completed boards, a single blank, an empty board, independent repeated calls, input preservation, digit relabelling, transposition, and CLI exit codes.
- Checked returned completions independently against row, column, box, and given-digit requirements.
- Ran the branching practice input: found a valid completion with 10102 search calls, 10101 assignment attempts, and 10041 failed assignments undone. Repeated timing evidence was saved later.
- Status at this stage: runnable Sudoku reference; repeated measurements not yet saved; Part 2C awaiting the base model.

## 2026-10-22 — Stage 6: Traceable measurement tools and A* exercise

- Added a standard-library benchmark that records each run, repetitions, environment, code commit, code/input hashes, and timing scope.
- Each returned completion is checked independently using sets. A no-solution result from the current search is not presented as a proof from a second method.
- Added an A* understanding exercise covering states, actions, costs, and heuristics. It derives constant f values for the empty-cell heuristic when each unit-cost action fills one cell.
- Actual validation: `python3 -m unittest reference.part1b.test_solver reference.part1b.test_benchmark -v`; 21 tests passed.
- Next step at this stage: measure the three practice inputs five times each on committed code and save raw JSON. The inputs are not a certified difficulty dataset.

## 2026-10-22 — Stage 7: Actual reference measurements

- Ran `python3 -m reference.part1b.benchmark --repeats 5` on committed version `a431cc1eddeea8f7a47bc8a792a31e1d3b8428a0`.
- Saved all 15 runs across three inputs, including counters, timings, environment, and hashes, to `reference/part1b/results/benchmark.json`, with a summary.
- Verified five records per input, consistent counters across repetitions, independent validation of every returned completion, and no uncommitted measured code or input changes.
- Median times: branching 85.508 ms, standard 0.342 ms, and the immediately contradictory unsatisfiable input 0.016 ms. These measurements describe this machine and this run only.
- Left the experiment template blank; the measured reference results are recorded separately.
- Status at this stage: the Part 1B learning reference, tests, measurement tools, and A* exercise were available. Implementation/report, GUI, and Part 2C remained unfinished. Part 2C depends on Chengtian Gong's base domain and Mission 2.

## 2026-10-22 — Stage 8: English-language repository

- Applied the requirement that coursework and GitHub repository content use English.
- Translated the root README, collaboration documents, learning notes, experiment template, reference run instructions, measurement summary, historical progress entries, and ignore-file comments.
- Used the English names Pinxin Liu and Chengtian Gong consistently in the collaboration documents.
- Code comments, program output, filenames, and raw measurement records were already in English. Executable code, practice inputs, and measurement values were not edited.
- Validation: scanned tracked text for remaining Chinese characters, checked relative Markdown links and whitespace, and compared executable code, inputs, and raw measurements with their preceding versions. No new solver tests or performance measurements were needed for this documentation-only change.

## 2026-10-25: English writing and evidence review

- Audited the existing measurement summary and A* exercise before editing.
- No report manuscript or author writing sample was present. Used concise technical English for the existing learning materials rather than claiming a finished coursework report.
- Checked empirical statements against the saved benchmark records and recorded their evidence status in `docs/WRITING_REVIEW.md`.
- Shortened long sentences, replaced indirect wording, and linked the existing independent verifier. Preserved numeric values, equations, existing references, attribution, and limitations.
- Confirmed that the collaborator has not yet started the base PDDL. Part 2C has no implemented base model to extend.
- No solver code, inputs, raw measurements, or test results were changed or regenerated during this review. The report, PDDL implementations, and video remain outstanding.

## Format for future entries

Record the date, owner and objective, actual changes, commands and results, remaining issues, and next step. Use real commit identifiers when referring to code; do not invent implementation history or test outcomes. Write future entries in English.

## 2026-10-25 — Chengtian Gong: base PDDL and contribution draft

- Confirmed remote main matched downloaded snapshot 907128310be91d417e7c8c5aca2b5e71134e02cb.
- Preserved the original five PDDL paths and names. Implemented only the three
  Part A/B files; the two Part C files remain unchanged starter templates.
- Added a generic STRIPS/typing domain, capacity tokens, ownership checks,
  directed roads, provenance-aware wireless data sends and physical sample storage.
- Fixed permitted landing choices: Mission 1 lander1=wp1; Mission 2 lander2=wp1.
- Ran Pyperplan 2.1 (greedy best-first, hFF): Mission 1 found 10 actions, Mission 2
  found 20. Replayed all steps against independent specification rules.
- Checked 2,496 action instances in 16 coherent states and a renamed three-rover,
  seven-goal instance (23 actions). All checks passed; this is targeted validation.
- Prepared a bilingual Part 1A and Part 2A/2B contribution draft with references,
  implementation interface, reproducible validation command and Chinese handoff guide.
- Remaining: partner accepts interface, implements Part 2C, completes own Part 1B;
  pair reviews drafts, merges report, records video and confirms OUC deadline.

## 2026-10-27 — Pinxin Liu: Sudoku optimisation, Part 2C comments, prose revision

- Optimised `reference/part1b/solver.py`: candidate sets are kept as bitmasks
  and updated only for the 20 peers of the assigned cell, instead of recomputing
  every domain on every node. Search order and the node/assignment/backtrack
  counts are unchanged.
- The tests caught a real bug in the first version of this change: with two
  assignments of the same digit in different units of a peer, a naive undo
  restored a digit that was still in use. Each assignment now records the peers
  it actually cleared and restores exactly those.
- Actual validation: `python3 -m unittest reference.part1b.test_solver
  reference.part1b.test_benchmark -v`; all 21 tests passed. Rerun of the local
  benchmark: branching median 43.0 ms, down from 89.2 ms measured on this machine
  immediately before the change, with identical counters (10102/10101/10041).
  The saved historical measurement records were not regenerated.
- Part C PDDL: added short file headers and plainer comments only; no predicate,
  action, effect or fact changed. Revalidated with
  `.venv/bin/python tools/validate_extension.py --output /tmp/f29ai-part2c-opt`:
  Mission 1/2/3 plans 10/20/24 actions, both astronauts move, all gated actions
  verified. The saved `evidence/part2c/` files were left untouched.
- Rewrote the report-facing prose (English contribution draft, bilingual draft,
  Part 2C implementation notes) in plainer, less formulaic English and Chinese.
  Numbers, equations, citations, and limitations are unchanged.
