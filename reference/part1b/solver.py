"""Sudoku input and validation.

"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

Board = tuple[tuple[int, ...], ...]


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
