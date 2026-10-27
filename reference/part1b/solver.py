"""Sudoku solver: depth-first search with the minimum-remaining-values heuristic.

Design decisions
----------------
Board storage
    A board is a list of nine rows; each row is a list of nine integers.
    Zero marks an empty cell.

Feasibility check
    A digit fits an empty cell when the digit appears in none of the cell's
    twenty peers: the eight other cells of its row, the eight other cells of
    its column and the four remaining cells of its 3x3 box. Candidate sets
    are recomputed from the current board at every search node, so no
    bookkeeping has to be undone on backtracking.

Cell selection (MRV)
    At each node the empty cell with the fewest legal candidates is chosen.
    Ties are broken by scanning order (top row first, leftmost column
    first), which keeps the search deterministic. Values are tried in
    ascending order.

Undo
    An assignment writes a digit into one cell; backtracking resets that
    same cell to zero. Because no propagation is performed, nothing else
    changes and nothing else has to be restored.

Termination
    A board with no empty cells is a solution. An empty cell whose
    candidate set is empty is a dead end. When the whole tree has been
    explored without completing the board, the puzzle has no solution.
"""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

SIZE = 9
BOX = 3
DIGITS = set(range(1, 10))


class PuzzleError(Exception):
    """Raised when the input is malformed or contains conflicting givens."""


@dataclass
class Stats:
    """Search counters for one solve() call.

    nodes       search() invocations: the root, every child state entered,
                every dead end and the terminal state that completes the board
    placements  digits written into empty cells, including ones later undone
    backtracks  placements undone because the subtree below them found no
                completion
    max_depth   largest number of simultaneously filled non-given cells at
                any search state
    """

    nodes: int = 0
    placements: int = 0
    backtracks: int = 0
    max_depth: int = 0


@dataclass
class SolveResult:
    """Outcome of solve(): the completed board (or None) plus the counters."""

    solution: object
    stats: Stats


def parse_puzzle(text, csv=False):
    """Parse 9x9 digit text into a board; raises PuzzleError on bad input.

    Each of the nine rows holds nine single digits, separated by whitespace
    (TXT) or commas (CSV). A row of nine bare digits without separators is
    accepted too. Zero marks an empty cell; 1-9 are givens.
    """
    lines = [line.strip() for line in text.strip().splitlines()]
    if len(lines) != SIZE:
        raise PuzzleError(f"Expected {SIZE} rows, found {len(lines)}.")
    board = []
    for row_no, line in enumerate(lines):
        tokens = line.split(",") if csv else line.split()
        if len(tokens) == 1 and len(tokens[0]) == SIZE:
            tokens = list(tokens[0])  # bare digits, e.g. "530070000"
        if len(tokens) != SIZE:
            raise PuzzleError(f"Row {row_no + 1} must contain {SIZE} digits, found {len(tokens)}.")
        row = []
        for col_no, token in enumerate(tokens):
            if token not in "0123456789":
                raise PuzzleError(
                    f"Row {row_no + 1}, entry {col_no + 1} ({token!r}) is not a single digit.")
            row.append(int(token))
        board.append(row)
    return validate_board(board)


def _units():
    """Yield (kind, label, cells) for every row, column and 3x3 box."""
    for r in range(SIZE):
        yield "row", str(r + 1), [(r, c) for c in range(SIZE)]
    for c in range(SIZE):
        yield "column", str(c + 1), [(r, c) for r in range(SIZE)]
    for br in (0, BOX, 2 * BOX):
        for bc in (0, BOX, 2 * BOX):
            label = f"top-left ({br + 1},{bc + 1})"
            cells = [(r, c) for r in range(br, br + BOX) for c in range(bc, bc + BOX)]
            yield "box", label, cells


def _check_conflicts(board, kind, label, cells):
    seen = {}
    for (r, c) in cells:
        value = board[r][c]
        if not value:
            continue
        if value in seen:
            (pr, pc) = seen[value]
            raise PuzzleError(
                f"Digit {value} appears twice in {kind} {label}: "
                f"cells ({pr + 1},{pc + 1}) and ({r + 1},{c + 1}).")
        seen[value] = (r, c)


def validate_board(board):
    """Check shape, value range and unit conflicts; return an int copy."""
    if not isinstance(board, (list, tuple)) or len(board) != SIZE:
        raise PuzzleError(f"Expected {SIZE} rows, found not a 9-row grid.")
    for r, row in enumerate(board):
        if not isinstance(row, (list, tuple)) or len(row) != SIZE:
            raise PuzzleError(f"Row {r + 1} must contain {SIZE} entries.")
        for c, value in enumerate(row):
            if isinstance(value, bool) or not isinstance(value, int):
                raise PuzzleError(f"Cell ({r + 1},{c + 1}) must be an integer, found {value!r}.")
            if not 0 <= value <= 9:
                raise PuzzleError(
                    f"Cell ({r + 1},{c + 1}) holds {value}; allowed values are the digits 0-9.")
    for kind, label, cells in _units():
        _check_conflicts(board, kind, label, cells)
    return [list(row) for row in board]


def candidates(board, r, c):
    """Return the set of digits that may legally fill the empty cell (r, c)."""
    used = {value for value in board[r] if value}
    used.update(board[row][c] for row in range(SIZE) if board[row][c])
    br, bc = r - r % BOX, c - c % BOX
    for row in range(br, br + BOX):
        for col in range(bc, bc + BOX):
            if board[row][col]:
                used.add(board[row][col])
    return DIGITS - used


def solve(board, cell_order="mrv"):
    """Solve a validated board with backtracking.

    cell_order selects the next empty cell: "mrv" (the default) picks the
    empty cell with the fewest legal candidates, ties broken in reading
    order; "row-major" picks the first empty cell in reading order. The
    row-major mode exists only for the ordering comparison in the
    experiments; the submitted method is backtracking + MRV.

    The caller's board is never modified; the search works on a copy.
    Returns SolveResult(solution or None, stats). The search is complete:
    a returned None means no solution exists, and exactly one completion is
    returned otherwise (uniqueness is checked separately, see
    count_solutions).
    """
    if cell_order not in ("mrv", "row-major"):
        raise ValueError(f"Unknown cell_order {cell_order!r}; use 'mrv' or 'row-major'.")
    work = validate_board(board)
    stats = Stats()

    def search(depth):
        stats.nodes += 1
        stats.max_depth = max(stats.max_depth, depth)
        if cell_order == "mrv":
            best, best_cands = None, None
            for r in range(SIZE):
                for c in range(SIZE):
                    if work[r][c] == 0:
                        cands = candidates(work, r, c)
                        if not cands:
                            return False  # dead end: no digit fits this empty cell
                        if best_cands is None or len(cands) < len(best_cands):
                            best, best_cands = (r, c), cands
        else:
            best, best_cands = None, None
            for r in range(SIZE):
                for c in range(SIZE):
                    if work[r][c] == 0:
                        best, best_cands = (r, c), candidates(work, r, c)
                        break
                if best is not None:
                    break
            if best is not None and not best_cands:
                return False  # dead end: no digit fits this empty cell
        if best is None:
            return True  # no empty cells: the board is complete
        r, c = best
        for digit in sorted(best_cands):  # ascending order keeps the search deterministic
            work[r][c] = digit
            stats.placements += 1
            if search(depth + 1):
                return True
            work[r][c] = 0  # undo: only this cell changed, so only it is reset
            stats.backtracks += 1
        return False

    found = search(0)
    return SolveResult(work if found else None, stats)


def count_solutions(board, limit=2):
    """Count completions, stopping at `limit` (default 2, enough for uniqueness).

    Do not call this on a nearly empty board: it enumerates completions and
    an empty board has about 6.7e21 of them.
    """
    work = validate_board(board)
    found = 0

    def search():
        nonlocal found
        best, best_cands = None, None
        for r in range(SIZE):
            for c in range(SIZE):
                if work[r][c] == 0:
                    cands = candidates(work, r, c)
                    if not cands:
                        return
                    if best_cands is None or len(cands) < len(best_cands):
                        best, best_cands = (r, c), cands
        if best is None:
            found += 1
            return
        r, c = best
        for digit in sorted(best_cands):
            work[r][c] = digit
            search()
            work[r][c] = 0
            if found >= limit:
                return

    search()
    return found


def read_puzzle(path, csv=False):
    """Read a puzzle file; raises PuzzleError with a clear message on I/O or
    format problems."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        raise PuzzleError(f"Cannot read {path}: {error}") from error
    return parse_puzzle(text, csv=csv)


def format_board(board):
    """Render a board with box separators; empty cells are dots."""
    digits = ["".join(str(value) if value else "." for value in row) for row in board]
    lines = []
    for r in range(SIZE):
        lines.append(" ".join(digits[r][c:c + BOX] for c in range(0, SIZE, BOX)))
        if r in (2, 5):
            lines.append("------+-------+------")
    return "\n".join(lines)


def print_stats(stats):
    print("Search statistics:")
    print(f"  nodes: {stats.nodes}")
    print(f"  placements: {stats.placements}")
    print(f"  backtracks: {stats.backtracks}")
    print(f"  max depth: {stats.max_depth}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Solve a Sudoku puzzle with depth-first search and the MRV heuristic.")
    parser.add_argument("puzzle", help="path to a TXT puzzle: 9 rows of 9 digits, 0 = empty")
    parser.add_argument("--csv", action="store_true",
                        help="read comma-separated values instead of whitespace")
    parser.add_argument("--order", choices=("mrv", "row-major"), default="mrv",
                        help="cell ordering: mrv (default) or row-major, for comparison")
    parser.add_argument("--stats", action="store_true",
                        help="print search statistics after solving")
    args = parser.parse_args(argv)
    try:
        board = read_puzzle(args.puzzle, csv=args.csv)
    except PuzzleError as error:
        print(f"Input error: {error}", file=sys.stderr)
        return 2
    result = solve(board, cell_order=args.order)
    if result.solution is None:
        print("No solution: every candidate assignment was explored without completing the board.")
        if args.stats:
            print_stats(result.stats)
        return 1
    print("Solution:")
    print(format_board(result.solution))
    if args.stats:
        print_stats(result.stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
