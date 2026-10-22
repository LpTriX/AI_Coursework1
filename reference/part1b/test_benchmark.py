"""Check measurement integrity and independent result verification."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from reference.part1b.benchmark import run_benchmark, verify_completion

HERE = Path(__file__).resolve().parent
SOLVED = tuple(tuple((r * 3 + r // 3 + c) % 9 + 1 for c in range(9)) for r in range(9))


class BenchmarkTests(unittest.TestCase):
    def test_verifier_rejects_bad_units_and_changed_givens(self):
        self.assertTrue(verify_completion(SOLVED, SOLVED))
        self.assertFalse(verify_completion(SOLVED, None))
        self.assertFalse(verify_completion(SOLVED, ((0,) * 9,) * 9))
        different = tuple(tuple(value % 9 + 1 for value in row) for row in SOLVED)
        self.assertFalse(verify_completion(SOLVED, different))
        self.assertTrue(verify_completion(((0,) * 9,) * 9, different))

    def test_runs_and_no_solution_recorded_without_fabricated_proof(self):
        report = run_benchmark([HERE / "puzzles/standard.txt", HERE / "puzzles/unsatisfiable.txt"], 2)
        self.assertEqual(report["repeats"], 2)
        self.assertEqual(len(report["cases"]), 2)
        for case in report["cases"]:
            self.assertEqual(len(case["runs"]), 2)
            self.assertEqual(len(case["input_sha256"]), 64)
            self.assertGreaterEqual(case["summary"]["median_seconds"], 0)
            self.assertTrue(case["summary"]["result_and_counters_identical"])
        self.assertTrue(report["cases"][0]["runs"][0]["solution_verified"])
        self.assertEqual(report["cases"][1]["runs"][0]["result"], "unsatisfiable")
        self.assertIsNone(report["cases"][1]["runs"][0]["solution_verified"])

    def test_invalid_repeat_count(self):
        with self.assertRaises(ValueError):
            run_benchmark([HERE / "puzzles/standard.txt"], 0)

    def test_command_writes_machine_readable_measurements(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "raw.json"
            result = subprocess.run([sys.executable, "-m", "reference.part1b.benchmark",
                                     str(HERE / "puzzles/standard.txt"), "--repeats", "2",
                                     "--output", str(destination)], cwd=HERE.parents[1],
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(destination.read_text())["repeats"], 2)


if __name__ == "__main__":
    unittest.main()
