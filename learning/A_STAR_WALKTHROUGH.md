# A* Understanding Exercise: Check the Heuristic Against the Model

This note explains Sudoku as an A* search problem and relates the heuristic to the implemented solver.

## Fix the model before discussing h

Consider a model in which a state is a legal partial board preserving the original givens. An action fills one empty cell with a digit that does not violate the current row, column, or box constraints. Every action costs 1. Let the initial board contain m empty cells.

Check these equations:

- After k assignments, path cost g = k.
- If h is the number of remaining empty cells, then h = m - k.
- Therefore f = g + h = m for every reachable partial board in this state space.

A heuristic that resembles the remaining work does not necessarily distinguish promising branches. This derivation applies specifically to actions that fill exactly one cell at unit cost. If an action propagates several assignments, analyse the costs again.

## Questions to answer independently

1. How many further actions are necessary from a solvable state? How should optimal remaining cost be understood for an unsatisfiable state?
2. Can the number of empty cells overestimate the optimal remaining cost? How does it change along a legal edge?
3. Can different assignment orders reach the same state? What must be stored for duplicate detection?
4. If all f values are equal, what determines the search order? Can tie-breaking affect practical behaviour?
5. What memory does A* need for its frontier? What information does the chosen backtracking implementation retain?
6. Is MRV a variable-selection strategy or an already defined A* path-cost heuristic? Keep these concepts distinct.
7. If proposing the number of conflicts as h, why must its relationship to the remaining number of actions be checked rather than assumed?

An A* implementation is not required. Understand the relationship between states, actions, costs, and h, then explain its suitability and limitations.
