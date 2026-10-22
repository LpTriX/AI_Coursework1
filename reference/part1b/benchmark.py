"""Record repeatable measurements for the AI-generated Sudoku reference."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys

from reference.part1b.solver import PuzzleError, read_puzzle, solve

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def verify_completion(original, solution) -> bool:
    """Validate results with sets, separately from the solver's mask logic."""
    if solution is None or len(solution) != 9 or any(len(row) != 9 for row in solution):
        return False
    digits = set(range(1, 10))
    if any(set(row) != digits for row in solution):
        return False
    if any({solution[r][c] for r in range(9)} != digits for c in range(9)):
        return False
    for br in (0, 3, 6):
        for bc in (0, 3, 6):
            if {solution[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)} != digits:
                return False
    return all(not original[r][c] or original[r][c] == solution[r][c]
               for r in range(9) for c in range(9))


def git_metadata() -> dict:
    try:
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                           text=True, stderr=subprocess.DEVNULL).strip()
        status = subprocess.check_output(["git", "status", "--porcelain", "--",
                                          "reference/part1b/solver.py", "reference/part1b/benchmark.py",
                                          "reference/part1b/puzzles"], cwd=ROOT,
                                         text=True, stderr=subprocess.DEVNULL)
        return {"commit": revision, "benchmark_inputs_or_code_dirty": bool(status.strip())}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "benchmark_inputs_or_code_dirty": None}


def run_benchmark(paths: list[Path], repeats: int) -> dict:
    if repeats < 1:
        raise ValueError("Repeats must be at least 1.")
    if not paths:
        raise ValueError("At least one puzzle is required.")
    cases = []
    for path in paths:
        puzzle = read_puzzle(path)
        runs = []
        for number in range(1, repeats + 1):
            result = solve(puzzle)
            verified = verify_completion(puzzle, result.solution) if result.solution is not None else None
            if verified is False:
                raise RuntimeError(f"Invalid completion returned for {path.name}.")
            runs.append({"run": number, "result": "solved" if result.solution is not None else "unsatisfiable",
                         "solution_verified": verified, "stats": asdict(result.stats)})
        times = [sample["stats"]["elapsed_seconds"] for sample in runs]
        signatures = {(sample["result"], sample["stats"]["nodes"], sample["stats"]["assignments"],
                       sample["stats"]["backtracks"], sample["stats"]["max_depth"]) for sample in runs}
        cases.append({"puzzle": path.name, "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "empty_cells": sum(value == 0 for row in puzzle for value in row),
                      "runs": runs, "summary": {"median_seconds": statistics.median(times),
                      "min_seconds": min(times), "max_seconds": max(times),
                      "result_and_counters_identical": len(signatures) == 1}})
    return {"created_at_utc": datetime.now(timezone.utc).isoformat(), "repeats": repeats,
            "environment": {"python": platform.python_version(), "implementation": platform.python_implementation(),
                            "os": platform.system(), "os_release": platform.release(), "machine": platform.machine()},
            "version": git_metadata(), "solver_sha256": hashlib.sha256((HERE / "solver.py").read_bytes()).hexdigest(),
            "timing_scope": "Search initialization and recursion; excludes parsing, initial validation, output and verification.",
            "notes": ["Practice inputs are not an externally sourced or difficulty-certified dataset.",
                      "Solved results are independently checked; no uniqueness test is performed.",
                      "A no-solution return is recorded, not independently proved by a second solver."],
            "cases": cases}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Measure the AI-generated Sudoku learning reference.")
    parser.add_argument("puzzles", nargs="*", type=Path)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", type=Path, default=HERE / "results" / "benchmark.json")
    args = parser.parse_args(argv)
    paths = args.puzzles or sorted((HERE / "puzzles").glob("*.txt"))
    try:
        report = run_benchmark(paths, args.repeats)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except (ValueError, OSError, UnicodeError, RuntimeError) as error:
        print(f"Benchmark error: {error}", file=sys.stderr)
        return 2
    print("puzzle | result | median ms | nodes | backtracks")
    for case in report["cases"]:
        first = case["runs"][0]
        print(f"{case['puzzle']} | {first['result']} | {case['summary']['median_seconds'] * 1000:.3f} | "
              f"{first['stats']['nodes']} | {first['stats']['backtracks']}")
    print(f"Raw measurements saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
