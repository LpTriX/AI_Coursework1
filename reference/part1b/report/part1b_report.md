# Part 1B: Sudoku Solver — Implementation, Experiments, and Analysis

## 1. Algorithm choice

We model Sudoku as a constraint satisfaction problem: the 81 cells are the
variables, each empty cell's domain is {1..9}, and the 27 all-different
constraints (9 rows, 9 columns, 9 boxes) restrict which values may coexist.
The full problem and complexity discussion belongs to Part 1A; here we only
need the model to justify the search method.

We solve it with **depth-first search with chronological backtracking and
the minimum-remaining-values (MRV) heuristic**. Three properties drove the
choice. First, the search is **complete**: it finds a completion whenever
one exists, so it can genuinely report "no solution" rather than giving up.
Second, it is **deterministic**: with a fixed tie-break the same puzzle
always produces the same solution and the same search counters, which makes
the experiments reproducible. Third, MRV is cheap to add and usually
shrinks the tree sharply: a cell that admits only one digit must take it in
every completion, so trying such cells first avoids entire subtrees. The
cost is one candidate computation per empty cell per node, and the
experiments in Section 4 quantify when that cost is worth paying.

## 2. Implementation

The solver (`solver.py`, standard library only) follows the four design
decisions below.

**Board storage.** A board is a list of nine rows, each a list of nine
integers; `0` marks an empty cell. The solver copies its input and never
modifies the caller's board.

**Feasibility check.** `candidates(board, r, c)` returns the digits 1-9
minus the values already present in the cell's row, column, and 3x3 box.
Sets are recomputed from the current board at every node, so the code is
simple and there is no bookkeeping to roll back:

```python
used = {v for v in board[r] if v}
used.update(board[i][c] for i in range(9) if board[i][c])
# ... plus the 3x3 box values
return DIGITS - used
```

**Cell selection.** The next cell is the empty cell with the fewest
candidates; ties go to the topmost, then leftmost cell. Digits are tried in
ascending order. A fixed row-major ordering exists as a command-line option
(`--order row-major`) purely for the comparison in Section 4.

**Undo and termination.** An assignment writes one digit into one cell;
backtracking resets that same cell to `0`. Because no propagation is
performed, nothing else changes. A board with no empty cells is a solution;
an empty cell with an empty candidate set is a dead end; when the whole
tree has been explored, the puzzle has no solution. The CLI reports exit
code 0 (solved), 1 (valid but unsolvable), or 2 (input error), and input
checking rejects malformed files and conflicting givens before any search
starts. A separate `count_solutions` routine enumerates completions up to a
limit of two, which is all a uniqueness check needs.

The interface highlights cells involved in repeated row, column or box
values. Selecting an empty cell shows its legal candidates under the current
partial assignment; these do not guarantee a complete solution. Neither
interface feature changes the search algorithm.

## 3. Correctness testing

Seventeen `unittest` cases (saved output in `test_results.txt`, all
passing) cover the required situations. Every solution is checked by an
**independent oracle** that shares no code with the solver: it builds the
set of each row, column, and box from scratch and asserts each is exactly
{1..9}, and verifies every given digit is unchanged. Specifically:

| Situation | Check |
| --- | --- |
| several different puzzles (76, 30, 25 givens) | rows, columns, boxes all {1..9}; givens preserved |
| an already-completed legal board | returned unchanged, 1 node, 0 placements |
| a board with five blanks | completed correctly with 0 backtracks |
| a puzzle with no solution | valid input (no conflicting givens), solver reports no solution for both orderings, completion count is 0 |
| malformed or conflicting input | rejected with a clear message (exit code 2) before search |

Uniqueness deserves one sentence: a puzzle can have a solution without
having a unique one, so `count_solutions` (limit 2) is asserted to return 1
for every solvable practice puzzle. The practice puzzles themselves are
generated locally by `tools/make_puzzles.py`, which blanks cells one at a
time and keeps a blank only if uniqueness survives; random hole-poking
without this check usually produces non-unique puzzles because small
"unavoidable sets" (for example a 2x2 rectangle whose two values can be
swapped) escape it. No external difficulty rating is claimed for any of
these self-generated files.

## 4. Experiments

**Setup.** CPython 3.9.6, macOS (Darwin 27.0.0, arm64), five repetitions
per puzzle per ordering, no warm-up. Timing covers the complete `solve()` call, including its validation and
board copy. File reading, earlier validation, printing and independent
completion verification are excluded. Raw per-run records with input and solver SHA-256 hashes are in
`results/benchmark.json` and `results/benchmark_rowmajor.json`.

**Counter definitions.** `nodes`: search invocations (root, child states,
dead ends, terminal state). `placements`: digits written into empty cells,
including ones later undone. `backtracks`: placements undone after their
subtree failed. `max_depth`: deepest number of simultaneously filled
non-given cells.

**Results** (medians; every run of every puzzle produced identical
counters):

| Puzzle (givens) | Order | Median time | nodes | backtracks |
| --- | --- | ---: | ---: | ---: |
| completed (81) | mrv | 0.042 ms | 1 | 0 |
| few blanks (76) | mrv | 0.086 ms | 6 | 0 |
| p1 (30) | mrv | 2.213 ms | 52 | 0 |
| p1 (30) | row-major | 1.103 ms | 353 | 301 |
| p2 (25) | mrv | 27.353 ms | 594 | 537 |
| p2 (25) | row-major | 1008.228 ms | 349,303 | 349,246 |
| unsolvable (79) | mrv | 0.040 ms | 1 | 0 |

**Interpretation.** The completed and unsolvable boards are decided in one
node each — the latter has an empty cell with no legal digit, which the
search finds immediately; a format checker could not, because no givens
conflict. The interesting rows are p1 and p2. On p2, MRV visits **about 588
times fewer nodes** (594 against 349,303) and finishes **about 37 times
faster** than fixed row-major order — the heuristic repeatedly selects the
cell that is effectively forced, so the tree stays tiny. On p1 the story
reverses: row-major is faster (1.1 ms against 2.2 ms) despite 301
backtracks, because MRV recomputes the candidate sets of *every* empty cell
at *every* node, and p1 barely branches, so the per-node overhead never
pays for itself. The lesson we take from the data: MRV's value grows with
the amount of real branching in the puzzle, and for nearly-constrained
boards the simpler ordering wins. Counters were identical across all five
repetitions of every puzzle; timings varied with machine load, so the node
counts are the reliable comparison.

## 5. Strengths and limitations

**Strengths.** Complete and deterministic; finds one solution or proves
none exists; simple enough that every design decision can be explained from
the code; no dependencies; robust input checking with clear messages;
search behavior is measurable through four well-defined counters.

**Limitations.** Worst-case time is exponential in the number of empty
cells (roughly 9^m for m blanks) — completeness and speed are different
things. There is no constraint propagation: no forward checking, no AC-3,
so a dead end is noticed only when a candidate set is computed and comes
up empty. Under MRV that happens while scanning every empty cell to pick
the next one (the scan gives up as soon as any cell has no legal digit);
under row-major it happens only when the chosen cell itself has none. No
digit is pruned from a peer's candidates ahead of time. The solver returns
one solution and does not by itself certify uniqueness.
Finally, all five measured inputs are self-generated, so the results are
evidence about this implementation, not a claim about certified-difficulty
puzzles; for the final submission we will re-measure on puzzles with
traceable sources if the page budget allows the extra table.

## 6. Alternative techniques

**Forward checking.** After each assignment, delete the assigned digit
from the domains of the cell's 20 peers; fail as soon as some peer's domain
empties. This is the cheapest propagation beyond plain backtracking and
would likely cut the row-major tree on p2 substantially, at a small
per-node cost.

**Arc consistency (AC-3).** Enforce binary consistency across all
row/column/box pairs after each assignment. Stronger pruning, heavier
per-node work; on hard puzzles AC-3 often pays, on easy ones (like our p1)
its overhead might outweigh its pruning benefit. AC-3 was not measured
here, so this remains a hypothesis.

**Exact cover / dancing links (DLX).** Sudoku is an exact-cover problem
(cells x digits x units), and DLX is the standard fast method, especially
for counting all solutions or finding the hardest instances. It is a data
structure exercise rather than a conceptual change; we did not implement
it because MRV backtracking already solves our inputs in tens of
milliseconds.

**Stochastic local search (min-conflicts).** Very fast on many CSPs but
**incomplete**: it cannot certify "no solution", which our test set
requires of the method, so we rejected it.

## 7. A* analysis (theoretical, as required)

**State representation.** A partial board: which of the 81 cells are still
empty and which digits the others hold (a valid partial assignment).

**Actions and costs.** Assign one legal digit to one empty cell; the MRV
rule could pick the cell, or any empty cell could be allowed. Every action
costs 1 — Sudoku has no geometric path, so cost accumulates one step per
filled cell.

**Initial state and goal test.** The initial state is the puzzle with only
its givens; the goal is any board with no empty cells (all 27 constraints
then hold by construction of the legal moves).

**A heuristic.** h = number of remaining empty cells. It is **admissible**
(each action fills exactly one cell, so at least h actions remain) and
**consistent** (every action decreases h by exactly 1).

**Would A* be suitable here?** Not in practice, for a revealing reason.
With uniform step costs, g = cells filled so far, so

    f = g + h = (filled − givens) + (81 − filled) = 81 − givens,

a **constant** for every node in the tree. The heuristic is correct but
gives the search no gradient at all: f cannot separate promising states
from dead ends, so the order in which A* expands nodes is set entirely by
its tie-breaking rule. A first-in-first-out tie-break degenerates to
breadth-first behaviour and retains the unexpanded search frontier.
That frontier can require exponential memory in the worst case, while
depth-first backtracking keeps only the path it is currently on. A
last-in-first-out rule would avoid that memory blow-up, but then the
search is depth-first anyway and A* contributes nothing beyond plain DFS.
A stronger admissible heuristic is hard to find because Sudoku's
constraints interact globally; that is exactly the structure MRV exploits
cheaply. We therefore conclude
that DFS + MRV is a reasonable choice for this implementation. Section 4
compares MRV with row-major backtracking; neither was measured against A*.
