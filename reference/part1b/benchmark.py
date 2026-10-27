"""Measure the solver on every puzzle in puzzles/.

For each puzzle the solver runs `repeats` times in one process. Raw per-run
records (time and search counters) are written as JSON; the console prints
a summary table. Timing measures the complete solve() call, including its validation and
board copy. File reading, earlier input validation, independent verification
and printing are excluded. Run from the folder root:

    python3 benchmark.py --order mrv        # writes results/benchmark.json
    python3 benchmark.py --order row-major --output results/benchmark_rowmajor.json
"""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import statistics
import sys
import time

from solver import PuzzleError, read_puzzle, solve

HERE = Path(__file__).resolve().parent


def verify_completion(original, solution):
    """Set-based check of every row, column, box and given, independent of
    the solver's own logic."""
    if solution is None:
        return None  # an unsolved puzzle has nothing to verify
    if len(solution) != 9 or any(len(row) != 9 for row in solution):
        return False
    digits = set(range(1, 10))
    for r in range(9):
        if set(solution[r]) != digits:
            return False
    for c in range(9):
        if {solution[r][c] for r in range(9)} != digits:
            return False
    for br in (0, 3, 6):
        for bc in (0, 3, 6):
            if {solution[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)} != digits:
                return False
    return all(original[r][c] == 0 or original[r][c] == solution[r][c]
               for r in range(9) for c in range(9))


def run_benchmark(paths, repeats, cell_order):
    cases = []
    for path in paths:
        puzzle = read_puzzle(path)
        runs = []
        for number in range(1, repeats + 1):
            start = time.perf_counter()
            result = solve(puzzle, cell_order=cell_order)
            elapsed = time.perf_counter() - start
            verified = verify_completion(puzzle, result.solution)
            if verified is False:
                raise RuntimeError(f"{path.name}: the solver returned an invalid completion.")
            runs.append({"run": number,
                         "result": "solved" if result.solution is not None else "unsolvable",
                         "solution_verified": verified,
                         "elapsed_seconds": elapsed,
                         "stats": asdict(result.stats)})
        times = [run["elapsed_seconds"] for run in runs]
        counters = {(run["result"], run["stats"]["nodes"], run["stats"]["placements"],
                     run["stats"]["backtracks"], run["stats"]["max_depth"]) for run in runs}
        cases.append({
            "puzzle": path.name,
            "empty_cells": sum(value == 0 for row in puzzle for value in row),
            "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "runs": runs,
            "summary": {
                "median_seconds": statistics.median(times),
                "min_seconds": min(times),
                "max_seconds": max(times),
                "result_and_counters_identical": len(counters) == 1,
            },
        })
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repeats": repeats,
        "cell_order": cell_order,
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "os": platform.system(),
            "os_release": platform.release(),
            "machine": platform.machine(),
        },
        "solver_sha256": hashlib.sha256((HERE / "solver.py").read_bytes()).hexdigest(),
        "timing_scope": "Complete solve() call, including its validation and board copy; excludes file reading, earlier read_puzzle validation, printing and independent verification.",
        "notes": [
            "Puzzles are constructed locally (tools/make_puzzles.py); no external difficulty ratings are claimed.",
            "Every solved run is independently checked; uniqueness was verified with count_solutions.",
            "A no-solution return is recorded, not independently proved with a second solver.",
        ],
        "cases": cases,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Measure the Sudoku solver on the practice puzzles.")
    parser.add_argument("puzzles", nargs="*", type=Path,
                        help="puzzle files (default: all puzzles/*.txt)")
    parser.add_argument("--repeats", type=int, default=5, help="runs per puzzle (default 5)")
    parser.add_argument("--order", choices=("mrv", "row-major"), default="mrv",
                        help="cell ordering to measure (default mrv)")
    parser.add_argument("--output", type=Path, default=HERE / "results" / "benchmark.json")
    args = parser.parse_args(argv)
    if args.repeats < 1:
        print("Benchmark error: --repeats must be at least 1.", file=sys.stderr)
        return 2
    paths = args.puzzles or sorted((HERE / "puzzles").glob("*.txt"))
    try:
        report = run_benchmark(paths, args.repeats, args.order)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except (OSError, UnicodeError, RuntimeError, PuzzleError) as error:
        print(f"Benchmark error: {error}", file=sys.stderr)
        return 2
    print("puzzle | result | median ms | nodes | placements | backtracks")
    for case in report["cases"]:
        first = case["runs"][0]
        print(f"{case['puzzle']} | {first['result']} | "
              f"{case['summary']['median_seconds'] * 1000:.3f} | "
              f"{first['stats']['nodes']} | {first['stats']['placements']} | "
              f"{first['stats']['backtracks']}")
    print(f"Raw records written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
