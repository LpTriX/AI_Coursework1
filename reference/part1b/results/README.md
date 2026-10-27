# Actual Measurements of the Reference Implementation

These records document local runs of the Sudoku solver on the three practice inputs.

Raw data: [benchmark.json](benchmark.json). The JSON is authoritative; the table presents median times rounded to the nearest microsecond.

- Run date: 2026-10-22, Beijing time (UTC+8).
- Environment: CPython 3.9.6, macOS / Darwin 27.0.0, arm64.
- Measured code commit: `a431cc1eddeea8f7a47bc8a792a31e1d3b8428a0`.
- The measured code and inputs had no uncommitted changes. File hashes are included in the raw data.
- Five repetitions per input, 15 runs in total, with no additional warm-up run.
- Timing includes search setup and recursion, excluding input reading/validation, printing, and independent solution verification.

| Practice input | Outcome | Median time (ms) | Search calls | Assignment attempts | Failed assignments undone |
| --- | --- | ---: | ---: | ---: | ---: |
| branching.txt | One valid solution found | 85.508 | 10102 | 10101 | 10041 |
| standard.txt | One valid solution found | 0.342 | 52 | 51 | 0 |
| unsatisfiable.txt | No solution | 0.016 | 1 | 0 | 0 |

Each input produced the same outcome and search counters across all five repetitions. Timings varied. Every returned completion passed the separate [row, column, box, and given-digit checks](../benchmark.py). Uniqueness was not tested.

The unsatisfiable example can be checked manually. The first row requires 1, but the first column already contains 1. The first cell therefore has no legal value. This example covers an immediate contradiction, not the performance of every unsatisfiable puzzle.

These three examples have no certified difficulty ratings or verified external provenance. Other search methods were not benchmarked. These results do not establish performance on other inputs or superiority to untested alternatives. For the report, use puzzles with traceable sources and re-measure the current committed code if exact timings are needed.
