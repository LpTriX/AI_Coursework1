"""Semantic checks for Sudoku solving."""

import tempfile
import unittest
from pathlib import Path

from reference.part1b.solver import PuzzleError, format_board, parse_puzzle, read_puzzle, validate_board

PUZZLES = Path(__file__).with_name("puzzles")
SOLVED = tuple(tuple((r * 3 + r // 3 + c) % 9 + 1 for c in range(9)) for r in range(9))


class InputTests(unittest.TestCase):
    def test_txt_and_csv_are_equivalent(self):
        txt = "\n".join(" ".join(map(str, row)) for row in SOLVED)
        csv = "\n".join(",".join(map(str, row)) for row in SOLVED)
        self.assertEqual(parse_puzzle(txt), SOLVED)
        self.assertEqual(parse_puzzle(csv, csv=True), SOLVED)

    def test_empty_grid_is_valid_input(self):
        self.assertEqual(parse_puzzle(("0 " * 8 + "0\n") * 9), ((0,) * 9,) * 9)

    def test_invalid_rows_columns_and_tokens(self):
        rows = [" ".join(map(str, row)) for row in SOLVED]
        cases = ["\n".join(rows[:8]), "\n".join(rows + [rows[0]]),
                 "\n".join(["1 2 3"] + rows[1:]),
                 "\n".join([rows[0].replace("1", "x", 1)] + rows[1:]),
                 "\n".join([rows[0].replace("1", "10", 1)] + rows[1:]),
                 "\n".join([rows[0].replace("1", "-1", 1)] + rows[1:])]
        for text in cases:
            with self.subTest(text=text[:20]), self.assertRaises(PuzzleError):
                parse_puzzle(text)
        with self.assertRaises(PuzzleError):
            parse_puzzle("\n".join(",".join(map(str, row)) for row in SOLVED) + ",", csv=True)

    def test_row_column_and_box_conflicts(self):
        for positions in [((0, 0), (0, 8)), ((0, 0), (8, 0)), ((0, 0), (1, 1))]:
            grid = [[0] * 9 for _ in range(9)]
            for r, c in positions:
                grid[r][c] = 1
            with self.subTest(positions=positions), self.assertRaises(PuzzleError):
                validate_board(grid)

    def test_non_integer_and_out_of_range_api_input(self):
        for value in [True, 1.5, "1", 10, -1]:
            grid = [[0] * 9 for _ in range(9)]
            grid[0][0] = value
            with self.subTest(value=value), self.assertRaises(PuzzleError):
                validate_board(grid)

    def test_file_format_bom_and_io_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "board.CSV"
            file.write_text("\ufeff" + "\n".join(",".join(map(str, row)) for row in SOLVED), encoding="utf-8")
            self.assertEqual(read_puzzle(file), SOLVED)
            with self.assertRaises(PuzzleError):
                read_puzzle(Path(directory) / "board.json")
            with self.assertRaises(FileNotFoundError):
                read_puzzle(Path(directory) / "missing.txt")

    def test_formatting_does_not_modify_input(self):
        grid = [[0] * 9 for _ in range(9)]
        rendered = format_board(grid)
        self.assertEqual(rendered.count("."), 81)
        self.assertEqual(grid, [[0] * 9 for _ in range(9)])


if __name__ == "__main__":
    unittest.main()
