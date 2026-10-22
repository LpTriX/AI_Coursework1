"""Sudoku solver with MRV backtracking.

Command-line input, readable output, and search statistics.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from time import perf_counter_ns
from typing import Sequence

Board = tuple[tuple[int, ...], ...]
ALL_DIGITS = (1 << 9) - 1


@dataclass
class SearchStats:
    """Counters include failed branches; times exclude parsing and validation."""

    nodes: int = 0
    assignments: int = 0
    backtracks: int = 0
    max_depth: int = 0
    elapsed_seconds: float = 0.0


@dataclass
class SolveResult:
    solution: Board | None
    stats: SearchStats


class PuzzleError(ValueError):
    """The input has an invalid shape, value, or conflicting given digits."""


def validate_board(grid: Sequence[Sequence[int]]) -> Board:
    """Copy a 9x9 board and reject malformed or immediately conflicting input."""
    if len(grid) != 9 or any(len(row) != 9 for row in grid):
        raise PuzzleError("Expected exactly 9 rows with 9 values per row.")
    board = tuple(tuple(row) for row in grid)
    for row in board:
        if any(type(value) is not int or not 0 <= value <= 9 for value in row):
            raise PuzzleError("Every value must be an integer from 0 to 9.")
    units = [(f"row {r + 1}", board[r]) for r in range(9)]
    units += [(f"column {c + 1}", tuple(board[r][c] for r in range(9))) for c in range(9)]
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            units.append((f"box ({br // 3 + 1}, {bc // 3 + 1})",
                          tuple(board[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3))))
    for label, values in units:
        given = [value for value in values if value != 0]
        if len(given) != len(set(given)):
            raise PuzzleError(f"Conflicting given digits in {label}.")
    return board


def parse_puzzle(text: str, *, csv: bool = False) -> Board:
    """Parse nine lines; each token must be a single ASCII digit, including 0."""
    lines = text.splitlines()
    if len(lines) != 9:
        raise PuzzleError(f"Expected exactly 9 lines; received {len(lines)}.")
    grid = []
    for number, line in enumerate(lines, 1):
        tokens = [item.strip() for item in line.split(",")] if csv else line.split()
        if len(tokens) != 9:
            raise PuzzleError(f"Line {number}: expected 9 values; received {len(tokens)}.")
        if any(token not in "0123456789" or len(token) != 1 for token in tokens):
            raise PuzzleError(f"Line {number}: values must be single digits from 0 to 9.")
        grid.append([int(token) for token in tokens])
    return validate_board(grid)


def read_puzzle(path: str | Path) -> Board:
    """Read TXT (whitespace) or CSV (commas), allowing a UTF-8 BOM."""
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix not in {".txt", ".csv"}:
        raise PuzzleError("Use a .txt or .csv puzzle file.")
    return parse_puzzle(source.read_text(encoding="utf-8-sig"), csv=suffix == ".csv")


def format_board(board: Sequence[Sequence[int]]) -> str:
    """Render box boundaries; empty cells are displayed as dots."""
    rows = ["+-------+-------+-------+"]
    for index, row in enumerate(board):
        groups = [" ".join(str(value) if value else "." for value in row[start:start + 3])
                  for start in (0, 3, 6)]
        rows.append("| " + " | ".join(groups) + " |")
        if index % 3 == 2:
            rows.append("+-------+-------+-------+")
    return "\n".join(rows)


def solve(grid: Sequence[Sequence[int]]) -> SolveResult:
    """Return the first solution, or None after exhausting the search.

    Choose an unfilled cell with the fewest legal values (MRV). Ties use
    row-major order and values are tried ascending. Every recursive call
    recomputes domains and rejects any empty domain, including those later
    than a singleton in row-major order. Caller-owned input is never modified.

    This finds one solution; it does not prove uniqueness. Search depth is
    bounded by the number of initially empty cells (at most 81).
    """
    original = validate_board(grid)
    started = perf_counter_ns()
    board = [list(row) for row in original]
    rows, columns, boxes = [0] * 9, [0] * 9, [0] * 9
    empty = []
    for r in range(9):
        for c in range(9):
            value = board[r][c]
            if value == 0:
                empty.append((r, c))
            else:
                bit = 1 << (value - 1)
                rows[r] |= bit
                columns[c] |= bit
                boxes[(r // 3) * 3 + c // 3] |= bit
    stats = SearchStats()

    def search(depth: int) -> bool:
        stats.nodes += 1
        stats.max_depth = max(stats.max_depth, depth)
        selected = None
        best_mask = 0
        best_count = 10
        for r, c in empty:
            if board[r][c] != 0:
                continue
            box = (r // 3) * 3 + c // 3
            mask = ALL_DIGITS & ~(rows[r] | columns[c] | boxes[box])
            count = bin(mask).count("1")
            if count == 0:
                return False
            if count < best_count:
                selected, best_mask, best_count = (r, c, box), mask, count
        if selected is None:
            return True
        r, c, box = selected
        while best_mask:
            # Lowest set bit corresponds to the smallest available digit.
            bit = best_mask & -best_mask
            best_mask ^= bit
            board[r][c] = bit.bit_length()
            rows[r] |= bit
            columns[c] |= bit
            boxes[box] |= bit
            stats.assignments += 1
            if search(depth + 1):
                return True
            board[r][c] = 0
            rows[r] &= ~bit
            columns[c] &= ~bit
            boxes[box] &= ~bit
            stats.backtracks += 1
        return False

    found = search(0)
    stats.elapsed_seconds = (perf_counter_ns() - started) / 1_000_000_000
    solution = tuple(tuple(row) for row in board) if found else None
    return SolveResult(solution, stats)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sudoku MRV solver.")
    parser.add_argument("puzzle", type=Path, help="9x9 .txt or .csv file; use 0 for empty cells")
    parser.add_argument("--stats", action="store_true", help="print search counters and elapsed seconds")
    args = parser.parse_args(argv)
    try:
        puzzle = read_puzzle(args.puzzle)
    except (PuzzleError, OSError, UnicodeError) as error:
        print(f"Input error: {error}", file=sys.stderr)
        return 2
    print("Input:")
    print(format_board(puzzle))
    result = solve(puzzle)
    if result.solution is None:
        print("No solution exists.")
    else:
        print("Solution (one valid completion; uniqueness not checked):")
        print(format_board(result.solution))
    if args.stats:
        print("Stats: " + json.dumps(asdict(result.stats), sort_keys=True))
    return 0 if result.solution is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
