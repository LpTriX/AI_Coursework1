# Chengtian Gong: Part 1A and Parts 2A/2B

English contribution draft

This is an English revision of the [original bilingual contribution](gong_contribution_bilingual.md). It covers the same contribution and retains its author attribution. It is not the complete group report. The pair still needs to review and combine the remaining sections, cover details and video link.

## Part 1A: Sudoku as a CSP

### Variables and domains

A CSP consists of variables, their allowed values, and constraints on combinations
of values [2, 3]. For Sudoku, let X = {X_rc | r,c in {1,...,9}}, where X_rc is the
digit in row r and column c. There are 81 variables. For a blank cell,
D_rc = {1,...,9}; for a given clue g_rc, D_rc = {g_rc}. The clues stay fixed,
and the input marker 0 is not a solution value.

### Constraints

Impose AllDifferent(X_r1,...,X_r9) for each r in {1,...,9}, and
AllDifferent(X_1c,...,X_9c) for each c in {1,...,9}. For every a,b in {0,1,2},
impose AllDifferent({X_(3a+i,3b+j) | i,j in {1,2,3}}) on the corresponding
3-by-3 box. These 27 AllDifferent constraints and the domains require each digit
1–9 to appear exactly once in every row, column and box. A solution assigns every
variable, satisfies all constraints and preserves the clues.

### Search complexity and pruning

Let m be the number of blank cells. Enumerating all assignments tries 9^m complete
candidates. If checking a candidate takes fixed time on this fixed 9-by-9 board,
the upper bound is O(9^m). Backtracking assigns one blank at a time and checks
consistency before continuing [2, 4]. Without pruning, its search tree has at most
1 + 9 + ... + 9^m nodes, so O(9^m) is also a coarse worst-case upper bound.
This is not a tight bound for every Sudoku instance. If constraint checking is
counted separately, its cost multiplies the search-node bound. Here m describes
the work within the fixed board size. It does not assert an asymptotic hardness
result for fixed 9-by-9 Sudoku.

Pruning stops a partial assignment when it repeats a digit in a row, column or
box. Filling other cells cannot repair that conflict. The search can therefore
skip all descendants of the assignment without losing a valid solution. With k
blanks remaining, a conflict can avoid up to 9^k complete extensions. This often
reduces practical work, but does not give a polynomial worst-case bound. MRV,
forward checking and propagation can reduce exploration further [2]. A description
of the actual solver should name only the techniques it implements.

## Parts 2A and 2B: Lunar planning

### Representation and assumptions

The `lunar` domain uses only `:strips` and `:typing`, with types `rover`, `lander`
and `waypoint`. `belongs-to` records ownership, `lander-at` fixes each landing
site, and `connected` records directed roads. `aboard` identifies an undeployed
rover, while `rover-at` gives a deployed rover's location. Deployment removes the
aboard fact and places the rover at its own lander. Movement removes the previous
location. Every action uses parameters rather than mission-specific object names.
The initial state must be well formed: each rover has one owner and either one
location or an aboard state, and each lander has one fixed landing site.

### Capacity and completion

`memory-free` is a single token shared by images and scans. Acquiring either kind
consumes the token. Transmitting held data restores it and records `image-saved`
or `scan-saved` at the receiving lander. Transmission checks ownership but does
not require the rover to be at the lander or to have visited it. The source
waypoint records where the data was acquired. The current waypoint records the
rover's present location. Acquiring data alone does not satisfy a saved-data goal.

Samples use a separate `sample-free` token. A rover can therefore carry one sample
and one unsent data item at the same time. Collection consumes the sample token.
`store-sample` requires the rover and its own lander to share a waypoint. It
restores the rover's sample token, consumes the lander's `storage-free` token,
and records the sample's origin in `sample-stored`. No action restores lander
storage, so each lander can store at most one sample. The specification does not
limit the stock of samples at a waypoint, so the domain does not add a
source-exhaustion rule. It also adds no sample-type or data-size distinctions.

### Mission configuration

Mission 1 fixes Lander 1 at WP1 and starts Rover 1 aboard it. Figure 2 is encoded
with six directed edges. The goals require an image from WP5 and a scan from WP3
saved at Lander 1, plus a WP1 sample stored there. Mission 2 keeps Lander 1 and
the already deployed Rover 1 at WP2, as required. Lander 2 is fixed at WP1 with
Rover 2 initially aboard. This permitted choice simplifies storage of the WP1
sample and must be retained in Mission 3. Figure 3 has nine directed edges.
All six goals specify a receiving lander, so ownership assigns three goals to
each rover. Both missions use the same domain without changes [1].

### Validation and limitations

In the saved run, Pyperplan 2.1 [5] used greedy best-first search with hFF and
found a 10-action plan for Mission 1 and a 20-action plan for Mission 2. A separate
implementation of the specification's rules replayed every action. It compared
PDDL effects with expected state changes and checked location and capacity
invariants after each step. All goals held at the end. The checks covered wireless
transmission after leaving a data source and the physical return of samples.
The plans are valid solutions; they are not claimed to be shortest plans.

A further check compared 2,496 typed action instances in 16 constructed, coherent
states. All 63 allowed instances had the expected effects, and all 2,433 forbidden
instances were rejected. Cases covered reverse roads, sending unacquired data,
full memory, separate sample/data slots, remote sample storage, full lander
storage, and incorrect ownership even when landers share a location. Another
instance renamed every rover, lander and waypoint. It added a third rover and
lander with an extra image goal. The unchanged domain found a valid 23-action
plan. These are targeted checks, not an exhaustive test of every reachable state.
Raw plans, state traces, logs, file hashes and environment details are saved in
`evidence/base-pddl/`. Mission 3 and its astronaut tests are the partner's separate work.

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
explicit search-tree derivation; the references support CSP and backtracking concepts.

## Review notes

The English paragraphs above preserve the source contribution's numbers, formal definitions and citation identifiers. The five reference entries are unchanged. The bilingual source remains available for comparison.

Part 2C is documented separately in [the extension implementation](../docs/PART2C_IMPLEMENTATION.md) and [its validation evidence](../evidence/part2c/README.md). The current group-level status is listed in [the final review](../docs/FINAL_REVIEW.md). 
