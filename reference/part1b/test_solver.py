"""Semantic checks for the Sudoku solver."""

import tempfile
import subprocess
import sys
import unittest
from pathlib import Path

from reference.part1b.solver import PuzzleError, format_board, parse_puzzle, read_puzzle, solve, validate_board

PUZZLES = Path(__file__).with_name("puzzles")
SOLVED = tuple(tuple((r * 3 + r // 3 + c) % 9 + 1 for c in range(9)) for r in range(9))


def assert_valid_completion(testcase, original, solution):
    """Independent oracle: check all units and givens without solver helpers."""
    testcase.assertIsNotNone(solution)
    digits = set(range(1, 10))
    testcase.assertEqual(len(solution), 9)
    for r in range(9):
        testcase.assertEqual(set(solution[r]), digits)
        testcase.assertEqual({solution[c][r] for c in range(9)}, digits)
        for c in range(9):
            if original[r][c]:
                testcase.assertEqual(solution[r][c], original[r][c])
    for br in (0, 3, 6):
        for bc in (0, 3, 6):
            testcase.assertEqual({solution[r][c] for r in range(br, br + 3)
                                 for c in range(bc, bc + 3)}, digits)


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


class SearchTests(unittest.TestCase):
    def test_solved_board_and_single_blank(self):
        completed = solve(SOLVED)
        self.assertEqual(completed.solution, SOLVED)
        self.assertEqual(completed.stats.assignments, 0)
        self.assertEqual(completed.stats.nodes, 1)
        for r, c in [(0, 0), (4, 4), (8, 8)]:
            grid = [list(row) for row in SOLVED]
            grid[r][c] = 0
            with self.subTest(cell=(r, c)):
                result = solve(grid)
                self.assertEqual(result.solution, SOLVED)

    def test_examples_preserve_givens_and_caller_input(self):
        for name in ["standard.txt", "branching.txt"]:
            grid = [list(row) for row in read_puzzle(PUZZLES / name)]
            original = [row[:] for row in grid]
            with self.subTest(name=name):
                result = solve(grid)
                assert_valid_completion(self, original, result.solution)
                self.assertEqual(grid, original)
                self.assertEqual(result.stats.assignments - result.stats.backtracks,
                                 sum(value == 0 for row in grid for value in row))
                if name == "branching.txt":
                    self.assertGreater(result.stats.backtracks, 0)

    def test_unconstrained_board_is_supported_without_uniqueness_claim(self):
        empty = ((0,) * 9,) * 9
        assert_valid_completion(self, empty, solve(empty).solution)

    def test_no_solution_without_duplicate_given_digits(self):
        puzzle = read_puzzle(PUZZLES / "unsatisfiable.txt")
        self.assertIsNone(solve(puzzle).solution)

    def test_conflicting_board_rejected_before_search(self):
        grid = [[0] * 9 for _ in range(9)]
        grid[0][0] = grid[1][1] = 7
        with self.assertRaises(PuzzleError):
            solve(grid)

    def test_repeated_calls_are_independent_and_deterministic(self):
        puzzle = read_puzzle(PUZZLES / "branching.txt")
        first = solve(puzzle)
        solve(read_puzzle(PUZZLES / "unsatisfiable.txt"))
        second = solve(puzzle)
        self.assertEqual(first.solution, second.solution)
        self.assertEqual(first.stats.nodes, second.stats.nodes)
        self.assertEqual(first.stats.backtracks, second.stats.backtracks)

    def test_digit_relabeling_and_transposition(self):
        original = read_puzzle(PUZZLES / "standard.txt")
        variants = [tuple(tuple(original[c][r] for c in range(9)) for r in range(9)),
                    tuple(tuple(10 - value if value else 0 for value in row) for row in original)]
        for grid in variants:
            assert_valid_completion(self, grid, solve(grid).solution)


class CommandTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "reference.part1b.solver", *map(str, args)],
                              capture_output=True, text=True, timeout=15,
                              cwd=Path(__file__).resolve().parents[2])

    def test_solution_stats_and_no_solution_exit_codes(self):
        solved = self.run_cli(PUZZLES / "standard.txt", "--stats")
        self.assertEqual(solved.returncode, 0, solved.stderr)
        self.assertIn("Solution", solved.stdout)
        self.assertIn('"backtracks"', solved.stdout)
        unsolvable = self.run_cli(PUZZLES / "unsatisfiable.txt")
        self.assertEqual(unsolvable.returncode, 1)
        self.assertIn("No solution", unsolvable.stdout)

    def test_missing_invalid_and_non_utf8_files(self):
        missing = self.run_cli(PUZZLES / "does-not-exist.txt")
        self.assertEqual(missing.returncode, 2)
        self.assertIn("Input error", missing.stderr)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.txt"
            for data in [b"1 2 3", b"\xff\xfe"]:
                path.write_bytes(data)
                error = self.run_cli(path)
                self.assertEqual(error.returncode, 2)
                self.assertIn("Input error", error.stderr)

    def test_direct_script_entrypoint(self):
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("solver.py")),
                                 str(PUZZLES / "standard.txt")], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
