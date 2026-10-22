# Python Sudoku Learning Reference

This directory contains a Sudoku solver, input handling, correctness tests, and repeatable measurements.

Requirements: Python 3.9 or later. Only the standard library is used; there are no Sudoku, CSP, or constraint-solver dependencies.

## Current implementation

The reference includes input validation, MRV backtracking, a command-line interface, and search statistics. Standard-library unittest checks independently verify rows, columns, boxes, and original givens in returned solutions.

Run from the repository root:

```sh
python3 reference/part1b/solver.py reference/part1b/puzzles/standard.txt --stats
python3 -m reference.part1b.solver reference/part1b/puzzles/branching.txt --stats
```

Exit codes: 0 means a solution was found; 1 means the input is valid but unsatisfiable; 2 means an input error occurred. Finding one solution does not prove uniqueness. There is no default time limit, and worst-case search may take a long time.

Run the tests from the repository root:

```sh
python3 -m unittest reference.part1b.test_solver reference.part1b.test_benchmark -v
```

## Following the code

1. `read_puzzle` / `parse_puzzle`: convert files and text into a board.
2. `validate_board`: check shape, values, and initial conflicts.
3. `solve`: copy the input and build bit masks for digits used in each row, column, and box.
4. The nested `search`: compute legal digits for each empty cell, reject a state with an empty candidate set, and otherwise select a cell using MRV.
5. Try a candidate and recurse. On failure, undo the board assignment and all three mask updates before trying another candidate.
6. `main`: display a solution or no-solution message and optional statistics.

Candidate sets are recomputed at each search call. The reference does not maintain an AC-3 queue or persistent forward-checking domain tables. Do not describe algorithms that are absent from the implementation.

## Measurement definitions

| Field | Definition |
| --- | --- |
| `nodes` | One per recursive search call, including the root, failed states, and the successful terminal state |
| `assignments` | One per candidate digit attempted in the selected cell |
| `backtracks` | One per candidate assignment undone after its child search fails |
| `max_depth` | Maximum number of simultaneously assigned non-given cells; the root has depth 0 |
| `elapsed_seconds` | Starts after initial input validation; includes search setup and recursion, excluding file reading, initial validation, and output |

MRV ties use row-major order, and candidate digits are tried in ascending order. Solutions and counters repeat deterministically for a fixed input; timings depend on the environment.

## Input format

- Exactly 9 lines of 9 single digits; 0 represents an empty cell.
- TXT separates values with whitespace; CSV separates values with commas.
- A normal final newline is accepted. Extra blank lines, missing or additional rows, non-integers, out-of-range values, and conflicting givens are rejected.

## Practice inputs

`standard.txt` and `branching.txt` were transcribed as practice inputs during this session. Their external provenance, uniqueness, and formal difficulty have not been verified. Their names are identifiers, not report-ready difficulty ratings or source citations.

`unsatisfiable.txt` is a counterexample adapted from a rule-generated completed board. Its givens contain no immediate duplicates, but it has no completion. The program must identify unsatisfiability through search or candidate checks rather than treating it as a formatting error.

For formal experiments, independently collect several puzzles with traceable sources and retain actual measurements.

## Repeated measurements

Run from the repository root:

```sh
python3 -m reference.part1b.benchmark --repeats 5
```

Optionally provide one or more TXT/CSV input paths before `--repeats`. The default inputs are the three practice puzzles in this directory.

The default output overwrites `results/benchmark.json`. Use `--output` with a different filename to retain separate experiments. Raw records include each run's counters and time, input/code SHA-256 hashes, the code commit, whether relevant code is uncommitted, and environment details. Timing excludes result verification. Each returned completion is separately checked using sets for rows, columns, boxes, and original givens.

Saved evidence is available in the [measurement summary](results/README.md) and [15 raw run records](results/benchmark.json). These records describe the measured version identified in the raw data.

A no-solution record is the current algorithm's result, not a proof obtained from a second solver. The supplied counterexample can be checked manually: its first row needs 1, but its first column already contains 1, leaving the first cell with no legal value.

## A* understanding exercise

See the [A* derivation and self-check questions](../../learning/A_STAR_WALKTHROUGH.md). The exercise is theoretical; it does not establish unperformed algorithm comparisons.
