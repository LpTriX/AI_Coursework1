# Sudoku Experiment Log Template

Use this template to record experimental conditions, measurements, and observations. Existing [practice measurements](../reference/part1b/results/README.md) are recorded separately.

## Experimental conditions

| Item | Actual record |
| --- | --- |
| Operating system and hardware | Not measured |
| Python version | To be confirmed |
| Implementation version / commit | Not implemented |
| Selected search strategy | To be decided |
| Whether timing includes reading and printing | To be defined |
| Repeat count and summary statistic | To be defined |
| Definition of a search step | To be defined |
| Definition of a backtrack | To be defined |
| Correctness verification method | Not implemented |

## Raw measurements

Append rows from real runs. Retain failures and timeouts rather than reporting only successful inputs.

| Date | Puzzle identifier / input file | Source | Empty cells | Commit | Run number | Time and unit | Search steps | Backtracks | Outcome | Independent verification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Functional checks

| Scenario | Actual input | Command | Observed result | Matches expectation? |
| --- | --- | --- | --- | --- |
| Ordinary solvable puzzle | Not run | Not run | Not run | Unknown |
| Completed valid puzzle | Not run | Not run | Not run | Unknown |
| Nearly completed puzzle | Not run | Not run | Not run | Unknown |
| Malformed input | Not run | Not run | Not run | Unknown |
| Conflicting givens | Not run | Not run | Not run | Unknown |
| Initially conflict-free but unsatisfiable | Not run | Not run | Not run | Unknown |

## Questions before interpreting results

- Are the original inputs and raw measurements retained so the runs can be repeated?
- Are counter definitions and timing scopes consistent across puzzles?
- Are observed timing differences larger than execution noise?
- Do the results describe these inputs, or is there evidence for a more general conclusion?
- Does the discussion distinguish theoretical expectations from alternatives that were actually tested?
