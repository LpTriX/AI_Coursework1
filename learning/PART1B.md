# Part 1B: Python Learning and Implementation Roadmap

This is a learning checklist, not report text, solver code, or experimental conclusions. Write submission code independently. Python was selected on 2026-10-22. Use an available Python 3 installation and state the actual version in the run instructions.

## Decisions before implementation

- Input format: start with TXT containing 9 lines of 9 space-separated digits; 0 represents an empty cell. Supporting either TXT or CSV satisfies the format requirement.
- Search method: understand backtracking first, then consider MRV. The task requires one implemented method, not several algorithms.
- Decide how to distinguish invalid input from a correctly formatted but unsatisfiable board.
- Decide how to verify that a completed board preserves all givens and satisfies every row, column, and box constraint.
- Start with readable terminal input and output. The highest assessment band in the PDF mentions a GUI; consider the teaching team's guidance and available time before adding one.

## 1. Read and validate input

Implement these functions independently before adding search:

- Read a board from a file specified on the command line.
- Check that it contains 9 rows of 9 integer values in the range 0–9.
- Check the initial nonzero digits for row, column, and box conflicts.
- Display the board in a consistent, readable layout.

Completion evidence: actually run one valid input and several invalid cases, recording commands and observations. Empty cells containing 0 must not count as duplicate givens.

Questions to resolve:

1. How is the board represented in memory, and how do its indices correspond to rows and columns?
2. What happens with extra spaces, blank lines, non-integer tokens, or a missing file?
3. Are error messages understandable to the user?

## 2. Understand candidates and backtracking

Draw a small example explaining why an empty cell permits some digits and excludes others. Trace one sequence of trying a value, continuing, failing, and undoing the assignment.

Check:

- Do candidates respect the row, column, and 3×3 box together?
- What should happen when an empty cell has no legal candidate?
- Which changes must be undone after a failed attempt? Can the original givens change?
- How is a fully populated board confirmed to be valid?

## 3. Define MRV and measurement counters

If using MRV, explain how it selects the next cell and breaks ties consistently. MRV is a search strategy; it does not establish that the implementation outperforms every alternative.

Before measuring, define exactly which events increment search nodes, assignment attempts, and backtracks. Keep these definitions consistent across puzzles.

## 4. Functional checks

- A solvable board with multiple empty cells: return a correct completion that preserves the givens.
- An already completed valid board: recognise it correctly.
- A nearly completed board: check boundary cases and termination.
- Conflicting initial givens: provide a clear message.
- An initially conflict-free but unsatisfiable board: terminate and report no solution.
- An input with multiple solutions: find one solution without claiming uniqueness.

Malformed input, conflicting givens, and unsatisfiability discovered by search are different outcomes.

## 5. Quantitative evaluation

Use several puzzles and retain their sources, original inputs, execution conditions, and raw measurements. See [EXPERIMENTS.md](EXPERIMENTS.md). A published difficulty label does not necessarily predict the difficulty for this particular algorithm.

Define the timing scope first. Consider repeated measurements for very fast examples and state the summary statistic. Independently validate returned solutions rather than recording success merely because a full board was printed. Leave unmeasured cases marked as not measured.

## 6. Prepare the theoretical A* analysis

An A* implementation is not required. Answer these questions as understanding checks rather than copying this checklist into the report:

- What is a state, what is an action, and when is the goal reached?
- How is path cost defined, and does it match the intended objective?
- What does the proposed heuristic estimate?
- Is it admissible, and why? Does admissibility guarantee useful discrimination?
- Can different assignment orders produce the same board?
- How do A* search and storage requirements compare with the chosen backtracking/CSP approach?

Organise and write the report independently using the actual implementation, real measurements, and reliable references. Do not present an unmeasured claim such as “runs faster” as an experimental result.

## First implementation milestone

Complete the reading, validation, and display tasks in Step 1. Save the implementation in the repository and record actual runs for at least one valid and one invalid input. Review that behaviour before moving on to search.
