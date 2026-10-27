# English Writing and Evidence Review

Review date: 2026-10-25.

## Scope

No report manuscript or author writing sample is present in the repository. This review covers the existing measurement summary and A* learning exercise. The target voice is concise technical English suitable for undergraduate coursework.

## Audit before revision

| File and location | Observation | Proposed revision |
| --- | --- | --- |
| `reference/part1b/results/README.md`, opening paragraph | The phrase "provide evidence of running" is indirect. | State what the records contain directly. |
| `reference/part1b/results/README.md`, repetition and verification paragraph | Several distinct checks are packed into a long sentence. | Separate repeatability, timing variation, and solution validation. |
| `reference/part1b/results/README.md`, unsatisfiable example | The constraint argument is correct but can be stated more directly. | Split the required digit and conflicting column into short sentences. |
| `reference/part1b/results/README.md`, limitations paragraph | The final sentence combines data selection, implementation, and analysis advice. | Split the advice while retaining every limitation. |
| `learning/A_STAR_WALKTHROUGH.md`, model definition | The action definition can be expressed with fewer subordinate clauses. | State the assignment action and its legality condition separately. |
| `learning/A_STAR_WALKTHROUGH.md`, interpretation of constant f | The discussion can identify the heuristic's limitation more directly. | Explain the lack of discrimination while preserving the modelling assumptions. |

## Claim-evidence checks

| Claim | Evidence inspected | Status |
| --- | --- | --- |
| Five repetitions per input and 15 runs total | `reference/part1b/results/benchmark.json`, repeat count and case records | Supported by the saved records |
| Median times and search counters in the summary table | Per-case summaries and raw run statistics in the same JSON | Supported; values retained |
| Repeated outcomes and counters are identical | All five result/counter tuples for each saved input | Supported by direct comparison |
| Returned completions passed separate validity checks | Saved `solution_verified` flags and the set-based verifier in `reference/part1b/benchmark.py` | Supported within the existing verification procedure; not a uniqueness claim |
| The sample with no solution has an immediate contradiction | First row and first column of `reference/part1b/puzzles/unsatisfiable.txt` | Supported by inspection |
| No algorithm comparison or certified difficulty claim is available | Current benchmark contents and input documentation | Limitations retained |
| Empty-cell h gives constant f under the stated model | The existing equations g = k, h = m - k, and f = g + h = m | Algebraic derivation, not an empirical performance claim |

## Revision record

- Replaced indirect wording and shortened clause-heavy sentences.
- Retained the structure, attribution, mathematical assumptions, and uncertainty statements.
- Added an explicit link to the existing benchmark verifier as an evidence pointer.
- Preserved every existing number, equation, and citation/link target. No results were added or changed.

## Remaining coursework items

The collaborator's base PDDL has not been started, as confirmed on 2026-10-25. No base domain, Mission 1/2 implementation, extended domain, or Mission 3 implementation is currently tracked. The repository also has no report manuscript or video demonstration. The existing Sudoku implementation remains a labelled learning reference.

The next planning step is to agree on the base types, predicates, actions, and Lander 2's landing location before implementing the extension. A complete submission additionally needs the code and report, real validation records, both members' details, and an accessible video link.
