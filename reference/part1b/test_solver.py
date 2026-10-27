"""Correctness tests for the Sudoku solver.

Every solution is checked with an independent set-based oracle that shares
no code with the solver: rows, columns, boxes and the original givens are
all verified separately. Run from the folder root with:

    python3 -m unittest -v test_solver

and keep the saved output as the correctness record.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from solver import (PuzzleError, count_solutions, format_board, parse_puzzle,
                    read_puzzle, solve, validate_board)

HERE = Path(__file__).resolve().parent
PUZZLES = HERE / "puzzles"
SOLVABLE = ["completed.txt", "few_blanks.txt", "p1.txt", "p2.txt"]


def assert_valid_completion(testcase, original, solution):
    """Independent oracle: check every unit and every given, without solver code."""
    testcase.assertIsNotNone(solution)
    testcase.assertEqual(len(solution), 9)
    digits = set(range(1, 10))
    for r in range(9):
        testcase.assertEqual(len(solution[r]), 9)
        testcase.assertEqual(set(solution[r]), digits, f"row {r + 1} invalid")
        testcase.assertEqual({solution[rr][r] for rr in range(9)}, digits,
                              f"column {r + 1} invalid")
        for c in range(9):
            if original[r][c] != 0:
                testcase.assertEqual(solution[r][c], original[r][c],
                                      f"given changed at ({r + 1},{c + 1})")
    for br in (0, 3, 6):
        for bc in (0, 3, 6):
            box = {solution[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)}
            testcase.assertEqual(box, digits, f"box ({br + 1},{bc + 1}) invalid")


class ParsingAndValidationTests(unittest.TestCase):
    def test_txt_csv_and_bare_digit_forms_are_equivalent(self):
        rows = ["5 3 0 0 7 0 0 0 0", "6 0 0 1 9 5 0 0 0", "0 9 8 0 0 0 0 6 0",
                "8 0 0 0 6 0 0 0 3", "4 0 0 8 0 3 0 0 1", "7 0 0 0 2 0 0 0 6",
                "0 6 0 0 0 0 2 8 0", "0 0 0 4 1 9 0 0 5", "0 0 0 0 8 0 0 7 9"]
        bare = ["".join(line.split()) for line in rows]
        csv_rows = [line.replace(" ", ",") for line in rows]
        expected = [list(map(int, line.split())) for line in rows]
        self.assertEqual(parse_puzzle("\n".join(rows)), expected)
        self.assertEqual(parse_puzzle("\n".join(bare)), expected)
        self.assertEqual(parse_puzzle("\n".join(csv_rows), csv=True), expected)

    def test_bom_and_surrounding_whitespace_are_accepted(self):
        rows = ["5 3 0 0 7 0 0 0 0", "6 0 0 1 9 5 0 0 0", "0 9 8 0 0 0 0 6 0",
                "8 0 0 0 6 0 0 0 3", "4 0 0 8 0 3 0 0 1", "7 0 0 0 2 0 0 0 6",
                "0 6 0 0 0 0 2 8 0", "0 0 0 4 1 9 0 0 5", "0 0 0 0 8 0 0 7 9"]
        expected = [list(map(int, line.split())) for line in rows]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "board.txt"
            path.write_text("\ufeff" + "\n".join(rows) + "\n\n", encoding="utf-8")
            self.assertEqual(read_puzzle(path), expected)

    def test_malformed_inputs_are_rejected_with_clear_messages(self):
        rows = ["5 3 0 0 7 0 0 0 0", "6 0 0 1 9 5 0 0 0", "0 9 8 0 0 0 0 6 0",
                "8 0 0 0 6 0 0 0 3", "4 0 0 8 0 3 0 0 1", "7 0 0 0 2 0 0 0 6",
                "0 6 0 0 0 0 2 8 0", "0 0 0 4 1 9 0 0 5", "0 0 0 0 8 0 0 7 9"]
        cases = {
            "too few rows": "\n".join(rows[:8]),
            "too many rows": "\n".join(rows + [rows[0]]),
            "blank line inside": "\n".join(rows[:4] + [""] + rows[5:]),
            "short row": "\n".join(["1 2 3"] + rows[1:]),
            "letter instead of digit": "\n".join([rows[0].replace("5", "x", 1)] + rows[1:]),
            "two-digit number": "\n".join([rows[0].replace("5", "10", 1)] + rows[1:]),
            "negative number": "\n".join([rows[0].replace("5", "-1", 1)] + rows[1:]),
            "trailing comma": "\n".join(line.replace(" ", ",") + "," for line in rows),
        }
        for label, text in cases.items():
            with self.subTest(case=label), self.assertRaises(PuzzleError):
                parse_puzzle(text, csv="comma" in label)

    def test_conflicting_givens_are_rejected(self):
        for positions in [((0, 0), (0, 8)), ((0, 0), (8, 0)), ((0, 0), (1, 1))]:
            grid = [[0] * 9 for _ in range(9)]
            for (r, c) in positions:
                grid[r][c] = 1
            with self.subTest(positions=positions), self.assertRaises(PuzzleError):
                validate_board(grid)

    def test_non_integer_and_out_of_range_api_input(self):
        for value in [True, 1.5, "1", 10, -1]:
            grid = [[0] * 9 for _ in range(9)]
            grid[0][0] = value
            with self.subTest(value=value), self.assertRaises(PuzzleError):
                validate_board(grid)

    def test_formatting_does_not_modify_input(self):
        grid = [[0] * 9 for _ in range(9)]
        rendered = format_board(grid)
        self.assertEqual(rendered.count("."), 81)
        self.assertEqual(grid, [[0] * 9 for _ in range(9)])


class SearchTests(unittest.TestCase):
    def test_solved_board_is_returned_as_is(self):
        original = read_puzzle(PUZZLES / "completed.txt")
        result = solve(original)
        self.assertEqual(result.solution, original)
        self.assertEqual(result.stats.placements, 0)
        self.assertEqual(result.stats.nodes, 1)

    def test_few_blanks_are_completed_correctly(self):
        original = read_puzzle(PUZZLES / "few_blanks.txt")
        result = solve(original)
        assert_valid_completion(self, original, result.solution)
        self.assertEqual(result.stats.backtracks, 0)

    def test_every_solvable_puzzle_yields_a_valid_completion(self):
        for name in SOLVABLE:
            original = read_puzzle(PUZZLES / name)
            with self.subTest(puzzle=name):
                assert_valid_completion(self, original, solve(original).solution)

    def test_both_cell_orderings_find_valid_solutions(self):
        for name in ["few_blanks.txt", "p1.txt"]:
            original = read_puzzle(PUZZLES / name)
            for order in ("mrv", "row-major"):
                with self.subTest(puzzle=name, order=order):
                    assert_valid_completion(self, original, solve(original, cell_order=order).solution)

    def test_unsolvable_puzzle_is_valid_input_but_has_no_solution(self):
        board = read_puzzle(PUZZLES / "unsolvable.txt")
        validate_board(board)  # must NOT raise: no conflicting givens
        self.assertIsNone(solve(board).solution)
        self.assertIsNone(solve(board, cell_order="row-major").solution)
        self.assertEqual(count_solutions(board), 0)

    def test_each_solvable_puzzle_has_exactly_one_completion(self):
        for name in SOLVABLE:
            with self.subTest(puzzle=name):
                self.assertEqual(count_solutions(read_puzzle(PUZZLES / name), limit=2), 1)

    def test_solutions_and_counters_are_deterministic(self):
        original = read_puzzle(PUZZLES / "p2.txt")
        first = solve(original)
        second = solve(original)
        self.assertEqual(first.solution, second.solution)
        self.assertEqual(first.stats, second.stats)

    def test_solving_does_not_modify_the_caller_board(self):
        original = read_puzzle(PUZZLES / "p2.txt")
        snapshot = [row[:] for row in original]
        solve(original)
        self.assertEqual(original, snapshot)


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "solver.py", *map(str, args)],
                              capture_output=True, text=True, timeout=120, cwd=HERE)

    def test_solution_no_solution_and_input_error_exit_codes(self):
        solved = self.run_cli(PUZZLES / "p2.txt", "--stats")
        self.assertEqual(solved.returncode, 0, solved.stderr)
        self.assertIn("Solution", solved.stdout)
        self.assertIn("backtracks", solved.stdout)
        unsolvable = self.run_cli(PUZZLES / "unsolvable.txt")
        self.assertEqual(unsolvable.returncode, 1)
        self.assertIn("No solution", unsolvable.stdout)
        missing = self.run_cli(PUZZLES / "does-not-exist.txt")
        self.assertEqual(missing.returncode, 2)
        self.assertIn("Input error", missing.stderr)

    def test_conflicting_input_is_reported_as_an_input_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "conflict.txt"
            rows = ["1 1 " + " ".join(["0"] * 7)] + [" ".join(["0"] * 9) for _ in range(8)]
            path.write_text("\n".join(rows) + "\n", encoding="utf-8")
            result = self.run_cli(path)
            self.assertEqual(result.returncode, 2)
            self.assertIn("Input error", result.stderr)
            self.assertIn("twice", result.stderr)

    def test_csv_flag_and_row_major_order(self):
        board = read_puzzle(PUZZLES / "p1.txt")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "p1.csv"
            path.write_text("\n".join(",".join(map(str, row)) for row in board), encoding="utf-8")
            result = self.run_cli(path, "--csv", "--order", "row-major")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Solution", result.stdout)


if __name__ == "__main__":
    unittest.main()
