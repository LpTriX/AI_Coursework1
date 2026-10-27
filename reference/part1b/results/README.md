# Measured results

Raw records: [benchmark.json](benchmark.json) (MRV ordering) and
[benchmark_rowmajor.json](benchmark_rowmajor.json) (row-major comparison).
The JSON files are authoritative; the tables below show medians rounded to
the nearest microsecond.

- Date: 2026-10-27, 13:36 UTC.
- Environment: CPython 3.9.6, macOS / Darwin 27.0.0, arm64.
- Five repetitions per puzzle, per ordering, in one process; no warm-up run.
- Every run of every puzzle produced the same result and the same search
  counters (`result_and_counters_identical: true`); timings varied.
- Timing starts after the puzzle has been read and validated and stops when
  the search returns. Independent solution verification, printing and file
  reading are excluded.
- Solver file measured: SHA-256 `7eed993d133f22a47d3858794d5d196a2c0fce9b7663c5f01d6beb024540d281`.

## Counter definitions

| Counter | Meaning |
| --- | --- |
| `nodes` | search invocations: the root, every child state entered, every dead end, and the terminal state that completes the board |
| `placements` | digits written into empty cells, including ones later undone |
| `backtracks` | placements undone because the subtree below them found no completion |
| `max_depth` | largest number of simultaneously filled non-given cells at any search state |

## MRV ordering (`--order mrv`, the submitted method)

| Puzzle | Outcome | Median time (ms) | nodes | placements | backtracks | max depth |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| completed.txt | solved | 0.042 | 1 | 0 | 0 | 0 |
| few_blanks.txt | solved | 0.086 | 6 | 5 | 0 | 5 |
| p1.txt | solved | 2.213 | 52 | 51 | 0 | 51 |
| p2.txt | solved | 27.353 | 594 | 593 | 537 | 56 |
| unsolvable.txt | no solution | 0.040 | 1 | 0 | 0 | 0 |

## Row-major comparison (`--order row-major`)

| Puzzle | Outcome | Median time (ms) | nodes | placements | backtracks | max depth |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| completed.txt | solved | 0.040 | 1 | 0 | 0 | 0 |
| few_blanks.txt | solved | 0.056 | 6 | 5 | 0 | 5 |
| p1.txt | solved | 1.103 | 353 | 352 | 301 | 51 |
| p2.txt | solved | 1008.228 | 349303 | 349302 | 349246 | 56 |
| unsolvable.txt | no solution | 0.041 | 1 | 0 | 0 | 0 |

## Reading the numbers

- The completed board and the unsolvable board are decided in one node: the
  first has no empty cell, the second has an empty cell with no legal digit.
- `p2.txt` is where the orderings separate: MRV visits 594 nodes and
  finishes in about 27 ms; row-major visits about 588 times as many nodes
  (349,303) and finishes in about 37 times the time (1008 ms).
- `p1.txt` is the opposite: row-major is *faster* there (1.1 ms against
  2.2 ms) even though it backtracks 301 times. MRV pays a fixed per-node
  price — it recomputes the candidates of every empty cell before each
  assignment — and that price only pays off when the puzzle actually
  branches. On `p1.txt` the first row-major choices happen to be right.
- The counters are deterministic; the timings are not. All measurements
  were taken on a shared desktop machine with other processes running, so
  small timing differences between orderings are noise; the node counts are
  the reliable comparison.

## Honest limitations

- The puzzles are self-generated (see [puzzles/README.md](../puzzles/README.md));
  no certified difficulty ratings or external sources are claimed.
- One solver was used throughout; a "no solution" result is this search's
  verdict, not a proof from a second solver. Uniqueness was, however,
  verified separately with `count_solutions`.
- These results describe this implementation on these five inputs. They do
  not establish performance on other puzzles or superiority over untested
  alternatives.
