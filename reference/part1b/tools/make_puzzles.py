"""Build the practice puzzles in ../puzzles.

Every puzzle here is constructed locally from a completed board generated
by a closed formula, optionally shuffled with a fixed seed. Nothing is
copied from an external puzzle collection, so no external difficulty rating
is claimed for any of these files.

Construction rules
- completed.txt: the full formula-generated board (81 givens).
- few_blanks.txt: the same board with five cells blanked.
- p1.txt / p2.txt: a shuffled copy of the board, dug cell by cell in a
  seeded pseudo-random order; a cell stays blank only when the puzzle still
  has exactly one completion afterwards (checked with
  solver.count_solutions). Digging targets 30 and 24 givens and stops
  earlier if no further cell can be removed without breaking uniqueness.
- unsolvable.txt: the board with the corner digit blanked and a 1 moved
  into column 0, so cell (0,0) sees every digit 1-9 in its row, column or
  box while no two givens conflict anywhere. The solver must reject it by
  search, not by format checking.

Run from the folder root:  python3 tools/make_puzzles.py
"""

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from solver import candidates, count_solutions, solve, validate_board  # noqa: E402


def completed_board():
    """A valid board from a closed formula; every row, column and box holds
    each digit 1-9 exactly once."""
    return [[(r * 3 + r // 3 + c) % 9 + 1 for c in range(9)] for r in range(9)]


def shuffled_board(seed=20261027):
    """A deterministic shuffle of the formula board: relabel the digits and
    permute rows within bands and columns within stacks, which preserves
    validity."""
    randomizer = random.Random(seed)
    board = completed_board()
    label = list(range(1, 10))
    randomizer.shuffle(label)
    board = [[label[value - 1] for value in row] for row in board]
    for band in (0, 3, 6):
        rows = board[band:band + 3]
        randomizer.shuffle(rows)
        board[band:band + 3] = rows
    for stack in (0, 3, 6):
        order = list(range(3))
        randomizer.shuffle(order)
        for row in board:
            cols = [row[stack + i] for i in order]
            row[stack:stack + 3] = cols
    return board


def dig_unique(board, seed, target_givens):
    """Remove cells one at a time in a seeded pseudo-random order, keeping
    only removals that preserve uniqueness.

    Random subsets of a completed board are usually non-unique because they
    miss small unavoidable sets (for example a 2x2 rectangle whose two
    values can be swapped), so cells are blanked and checked one by one
    instead. Digging stops at `target_givens` or earlier, when no further
    cell can be removed without creating a second completion.
    """
    randomizer = random.Random(seed)
    puzzle = [row[:] for row in board]
    cells = [(r, c) for r in range(9) for c in range(9)]
    randomizer.shuffle(cells)
    removed = 0
    for (r, c) in cells:
        if removed >= 81 - target_givens:
            break
        saved = puzzle[r][c]
        puzzle[r][c] = 0
        if count_solutions(puzzle, limit=2) == 1:
            removed += 1
        else:
            puzzle[r][c] = saved
    return puzzle


def few_blanks(base):
    """Blank five scattered cells; the result must still be unique."""
    blank_sets = [
        [(0, 0), (4, 4), (8, 8), (1, 7), (6, 2)],
        [(0, 8), (3, 3), (5, 5), (7, 1), (2, 4)],
        [(1, 1), (4, 7), (6, 0), (8, 4), (2, 6)],
    ]
    for blanks in blank_sets:
        puzzle = [row[:] for row in base]
        for (r, c) in blanks:
            puzzle[r][c] = 0
        if count_solutions(puzzle, limit=2) == 1:
            return puzzle
    raise RuntimeError("No blank set produced a uniquely completable puzzle.")


def unsolvable():
    """A board with no completion and no conflicting givens.

    The formula board's first row is 1-9 and its first column starts with 1.
    Blanking (0,0) leaves row 0 holding 2-9, so only a 1 could fill the
    corner. Moving row 1's 1 into (1,0) and blanking its old home (1,6)
    puts a 1 into column 0 while keeping every unit conflict-free. The
    corner therefore sees all nine digits, but the puzzle looks like any
    other valid input.
    """
    board = completed_board()
    board[0][0] = 0  # row 0 now holds 2-9
    board[1][0] = 1  # column 0 now contains a 1 at row 1
    board[1][6] = 0  # row 1 must not hold two 1s
    return board


def write_puzzle(path, board):
    path.write_text("\n".join(" ".join(map(str, row)) for row in board) + "\n", encoding="utf-8")


def main():
    base = completed_board()
    puzzles = {
        "completed.txt": base,
        "few_blanks.txt": few_blanks(base),
        "unsolvable.txt": unsolvable(),
    }
    shuffled = shuffled_board()
    puzzles["p1.txt"] = dig_unique(shuffled, seed=1, target_givens=30)
    puzzles["p2.txt"] = dig_unique(shuffled, seed=7, target_givens=17)

    out_dir = ROOT / "puzzles"
    out_dir.mkdir(exist_ok=True)
    for name, board in puzzles.items():
        write_puzzle(out_dir / name, board)
        givens = sum(value != 0 for row in board for value in row)
        expected = 0 if name == "unsolvable.txt" else 1
        assert count_solutions(board, limit=2) == expected, f"{name} failed its count check"
        print(f"{name}: {givens} givens, count check passed (expected {expected})")

    validate_board(puzzles["unsolvable.txt"])
    assert candidates(puzzles["unsolvable.txt"], 0, 0) == set()
    assert solve(puzzles["unsolvable.txt"]).solution is None
    assert count_solutions(puzzles["unsolvable.txt"]) == 0
    print("unsolvable.txt: valid input, cell (0,0) has no legal digit, no completion.")


if __name__ == "__main__":
    main()
