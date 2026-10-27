# Video talking points (Part 1B)

A suggested order for the recording. The five sections below total about
4 minutes, leaving roughly 4 of the group's 8-minute budget for the PDDL
parts. Every item has a runnable command you can show live.

## 1. The problem and the approach (30 seconds)

- Sudoku as a constraint satisfaction problem: 81 variables, domains
  1-9, 27 all-different constraints (9 rows, 9 columns, 9 boxes).
- The chosen method: depth-first search with chronological backtracking
  plus MRV. Complete (finds a solution iff one exists) and deterministic.

## 2. Live demos: solve and no solution (1 minute 30 seconds)

- `python3 solver.py puzzles/p2.txt --stats` — point at the output: the
  completed board keeps every given, and the statistics line shows how
  much search happened (594 nodes, 537 backtracks on p2).
- The four design decisions, in your own words: board stored as a list
  of lists (`0` = empty); a digit fits when it is absent from the row,
  column and box (candidates recomputed at each node); the next cell is
  the one with the fewest candidates (ties topmost-leftmost, digits
  ascending); undo resets exactly the one cell the assignment changed.
- `python3 solver.py puzzles/unsolvable.txt` — no conflicting givens,
  yet "No solution" in one node: the first row holds 2-9 and the first
  column holds a 1, so the corner has no legal digit. Found by search,
  not by an input check.

## 3. Experiments (1 minute)

- Show `results/README.md` and the two tables.
- The key comparison: on p2, fixed row-major order takes 349,303 nodes
  and ~1 s; MRV takes 594 nodes and ~27 ms — about 588 times fewer
  nodes.
- The honest caveat: on p1 row-major is actually slightly faster,
  because MRV recomputes every empty cell's candidates at every node.
  MRV pays when the puzzle branches, and p1 hardly branches.
- One line on the counters (nodes, placements, backtracks, max_depth)
  and that five repeats gave identical counters.

## 4. Correctness and the A* comparison (45 seconds)

- `python3 -m unittest -v test_solver` (or show `test_results.txt`):
  17 tests, every solution checked by an independent oracle for rows,
  columns, boxes and untouched givens; uniqueness verified separately
  with the completion counter.
- A* in one breath: h = number of empty cells is admissible and
  consistent, but f = g + h = 81 - givens is constant for every state,
  so the heuristic gives no guidance — expansion order falls to the
  tie-break rule, and the usual first-in-first-out rule stores every
  partial board (exponential memory) while DFS keeps one path. That is
  why the submitted method is DFS + MRV, not A*.

## 5. Close (15 seconds)

- Strengths: complete, deterministic, no external libraries, clear
  input checking. Limitations: no constraint propagation, worst-case
  exponential, puzzles are self-generated with no difficulty ratings.
  What we would try next: forward checking or an exact-cover (DLX)
  formulation.
