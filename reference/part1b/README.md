# Sudoku Solver — F29AI Coursework Part 1B

A from-scratch Sudoku solver for Part 1B: depth-first search with
chronological backtracking and the minimum-remaining-values (MRV) heuristic.
The search, the input handling and the validation are all implemented here;
no Sudoku, CSP or constraint-solver library is used.

## Requirements

- Python 3.9 or later (developed and measured on CPython 3.9.6).
- Standard library only; there are no third-party dependencies.

## Files

| Path | What it is |
| --- | --- |
| `solver.py` | the solver: parsing, validation, MRV backtracking, a CLI, and a completion counter |
| `test_solver.py` | 17 correctness tests with an independent set-based oracle |
| `benchmark.py` | repeatable timing and counter measurements, raw JSON output |
| `puzzles/` | five practice puzzles, all constructed locally; see [puzzles/README.md](puzzles/README.md) |
| `results/` | raw benchmark records and the summary; see [results/README.md](results/README.md) |
| `tools/make_puzzles.py` | regenerates every puzzle and verifies uniqueness |
| `report/part1b_report.md` | the Part 1B report text, including the A* analysis |
| `test_results.txt` | saved output of the full test run |
| `video_notes.md` | talking points for the presentation video |

## Input format

A TXT file with exactly 9 lines of 9 single digits each, separated by
whitespace; a row of 9 bare digits (e.g. `530070000`) is also accepted.
`0` marks an empty cell, `1-9` are givens. CSV files are read with the
`--csv` flag. Malformed input and conflicting givens are reported with a
clear message and exit code 2.

## Usage

From this folder:

```sh
# solve a puzzle and show the completed board
python3 solver.py puzzles/p2.txt

# also print search statistics
python3 solver.py puzzles/p2.txt --stats

# comparison mode: fixed row-major cell ordering instead of MRV
python3 solver.py puzzles/p2.txt --order row-major --stats

# CSV input: convert a TXT puzzle first, then read it back with --csv
tr ' ' ',' < puzzles/p1.txt > /tmp/p1.csv
python3 solver.py /tmp/p1.csv --csv

# run all correctness tests (saved output kept in test_results.txt)
python3 -m unittest -v test_solver

# record measurements (5 runs per puzzle, raw JSON in results/)
python3 benchmark.py --order mrv
python3 benchmark.py --order row-major --output results/benchmark_rowmajor.json

# regenerate the practice puzzles
python3 tools/make_puzzles.py
```

Exit codes: `0` a solution was found, `1` the input is valid but has no
solution, `2` an input error occurred.

## The method in one paragraph

The board is a list of nine rows of nine integers; `0` is an empty cell.
At each search node the solver recomputes, for every empty cell, the set of
digits that appear in none of the cell's row, column or 3x3 box. The empty
cell with the fewest such candidates is filled next (ties: topmost, then
leftmost; digits in ascending order). A failed subtree resets only that
cell back to `0`, because no propagation is performed, so there is nothing
else to undo. A full board is a solution; an empty cell with no legal
digit is a dead end; exhausting the tree means the puzzle has no solution.

## Deliverables checklist (Part 1B)

- [x] Python source files: `solver.py`, `test_solver.py`, `benchmark.py`
- [x] English README: this file (Python version, dependencies, input format, run commands)
- [x] Raw experiment data: `results/benchmark.json`, `results/benchmark_rowmajor.json`
- [x] English Part 1B text: `report/part1b_report.md` (algorithm, implementation, testing, experiments, strengths and limitations, alternatives, A* analysis)
- [x] Video material: `video_notes.md`
- [ ] Coordinate the page count with Part 1A (1A + 1B together: 4 pages maximum)
- [ ] Final polish of the report text before submission
