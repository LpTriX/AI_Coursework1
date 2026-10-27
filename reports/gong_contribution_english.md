# Chengtian Gong: Part 1A and Parts 2A/2B

English contribution draft

This is an English version of the original bilingual contribution. It covers the same material and keeps the same author attribution. It is not the complete group report: the pair still has to review it and merge in the remaining sections, the cover details and the video link.

## Part 1A: Sudoku as a CSP

### Variables and domains

A CSP is a set of variables, a domain of allowed values for each variable, and constraints over combinations of values [2, 3]. Sudoku's variables are its 81 cells. Let X_rc be the digit in row r, column c, with r, c in {1,...,9}. A blank cell can end up as any digit, so D_rc = {1,...,9}. A cell that starts with a clue g_rc is fixed: D_rc = {g_rc}. The clues never change, and the input marker 0 is not a solution value.

### Constraints

Every row imposes AllDifferent(X_r1, ..., X_r9), for r in {1,...,9}, and every column imposes AllDifferent(X_1c, ..., X_9c), for c in {1,...,9}. Every 3x3 box imposes AllDifferent over its nine cells: AllDifferent({X_(3a+i,3b+j) : i,j in {1,2,3}}), for a,b in {0,1,2}. That gives 27 constraints in total. Together with the domains they force each digit 1-9 to appear exactly once in every row, column and box. A solution is a complete assignment that satisfies all of them and keeps every clue.

### Search complexity and pruning

Let m be the number of blank cells. Enumerating all assignments means checking 9^m complete candidates. If checking one candidate costs fixed time on this fixed 9x9 board, the upper bound is O(9^m). Backtracking fills one blank at a time and checks consistency before moving on [2, 4]. Without pruning its tree has at most 1 + 9 + ... + 9^m nodes, so O(9^m) is also a coarse worst-case upper bound for backtracking — not a tight bound for every Sudoku instance. If constraint checking is counted separately, its cost multiplies the node bound. Here m measures the work on the fixed board size; this is not an asymptotic hardness claim for fixed 9x9 Sudoku.

Pruning stops a partial assignment as soon as it repeats a digit in a row, column or box. Filling the remaining cells cannot fix that, so the whole subtree below the bad assignment can be skipped without losing any solution. A conflict found with k blanks left avoids up to 9^k complete extensions. In practice this usually cuts the search a lot, but it does not give a polynomial worst-case bound. MRV, forward checking and constraint propagation can cut it further [2]. When we describe the actual solver, we should only name techniques it really implements.

## Parts 2A and 2B: Lunar planning

### Representation and assumptions

The `lunar` domain uses only `:strips` and `:typing`. The types are `rover`, `lander` and `waypoint`. `belongs-to` records which lander owns each rover, `lander-at` fixes each landing site, and `connected` gives the directed roads. `aboard` marks an undeployed rover; `rover-at` gives a deployed rover's current waypoint. Deployment deletes the aboard fact and puts the rover at its own lander's site; movement deletes the old location. Every action is parameterised — no action rule names a particular mission object. We assume the initial state is well formed: each rover has exactly one owner and exactly one aboard/location state, and each lander has one fixed site.

### Capacity and completion

`memory-free` is a single token shared by images and scans. Capturing either kind of data consumes it. Transmitting held data restores it and records `image-saved` or `scan-saved` at the receiving lander. Transmission requires ownership, the rover’s current location and the corresponding held data: the rover does not have to be at the lander or to have visited it before. The source waypoint records where the data came from; the current waypoint records where the rover is now. So acquiring data on its own never satisfies a saved-data goal.

Samples use a separate `sample-free` token, so a rover can carry one sample and one unsent data item at the same time. Collection consumes the token. `store-sample` requires the rover and its own lander to share a waypoint; it restores the rover's sample token, consumes the lander's `storage-free` token, and records the sample's origin in `sample-stored`. No action restores lander storage, so each lander stores at most one sample. The specification puts no limit on the sample stock at a waypoint, so the domain adds no source-exhaustion rule. We also add no sample-type or data-size distinctions.

### Mission configuration

Mission 1 fixes Lander 1 at WP1 and starts Rover 1 aboard it. Figure 2 is encoded as six directed edges. The goals require an image from WP5 and a scan from WP3 saved at Lander 1, plus a WP1 sample stored there. Mission 2 keeps Lander 1 and the already deployed Rover 1 at WP2, as required. Lander 2 is fixed at WP1 with Rover 2 aboard at the start. This choice (which the spec permits) makes storing the WP1 sample straightforward, and Mission 3 must keep it. Figure 3 has nine directed edges. All six goals name their receiving lander, so ownership splits them three per rover. Both missions run on the same domain with no changes [1].

### Validation and limitations

In the saved run, Pyperplan 2.1 [5] with greedy best-first search and hFF found a 10-action plan for Mission 1 and a 20-action plan for Mission 2. We then replayed each plan step by step against a separate implementation of the specification's rules: every PDDL effect was compared with the expected state change, and location and capacity invariants were checked after every step. All goals held at the end. The checks included wireless transmission after leaving the data source, and samples physically returning to the lander. The plans are valid solutions; we did not check whether they are shortest.

A further check compared 2,496 typed action instances in 16 constructed, coherent states. All 63 allowed instances produced the expected effects, and all 2,433 forbidden instances were rejected. The cases covered reverse roads, sending data that was never acquired, full memory, independent sample/data slots, remote sample storage, full lander storage, and wrong ownership even when two landers share a waypoint. Another instance renamed every rover, lander and waypoint and added a third rover/lander pair with one extra image goal; the unchanged domain found a valid 23-action plan. These are targeted checks, not an exhaustive test of every reachable state. Raw plans, state traces, logs, file hashes and environment details are saved in `evidence/base-pddl/`. Mission 3 and its astronaut tests are the partner's separate work.

## References

[1] F29AI teaching team. *Coursework 1: Search and Automated Planning*, 2026,
pp. 2, 4–10, 13, 15. Local file: F29AI_2026_cw1.pdf.

[2] Russell, S. and Norvig, P. *Constraint Satisfaction Problems*, official AIMA
teaching slides, slides 3, 7, 11–13 and 18–21. The public slide file labels this
material Chapter 5; do not confuse that label with textbook edition chapter numbers.
https://aima.cs.berkeley.edu/4th-ed/slides-pdf/chapter05.pdf

[3] UC Berkeley CS188. *2.1 Constraint Satisfaction Problems*.
https://inst.eecs.berkeley.edu/~cs188/textbook/csp/csps.html

[4] UC Berkeley CS188. *2.2 Solving Constraint Satisfaction Problems*.
https://inst.eecs.berkeley.edu/~cs188/textbook/csp/solving.html

[5] Pyperplan contributors. *Pyperplan*, version 2.1.
https://github.com/aibasel/pyperplan

Web sources checked on 25 October 2026. The complexity calculation above is our
explicit search-tree derivation; the references support the CSP and backtracking concepts.

## Review notes

The English above keeps the source contribution's numbers, formal definitions and citation identifiers. The five reference entries are unchanged. The bilingual source is still available for comparison.

Part 2C is documented separately in [the extension implementation](../docs/PART2C_IMPLEMENTATION.md) and [its validation evidence](../evidence/part2c/README.md). The current group-level status is in [the final review](../docs/FINAL_REVIEW.md).
