"""Tkinter GUI for the Sudoku solver.

A 9x9 grid of entry boxes with bold separators every three rows and
columns, plus Load, Solve, Reset and Clear buttons. The GUI is a thin
layer over solver.py: Load calls read_puzzle, Solve calls solve, and the
cell contents are checked with the same validation code, so the GUI and
the command line share one implementation.

Run from the folder root:  python3 gui.py

Cell colours: digits the user entered stay black; digits the solver added
are blue, so the answer is readable against the original givens.
"""

import copy
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from solver import PuzzleError, candidates, read_puzzle, solve, validate_board

SIZE = 9
BOX = 3
GIVEN_COLOR = "black"
SOLVED_COLOR = "#1a5fb4"
CONFLICT_COLOR = "#ffe1e1"


def conflict_cells(board):
    """Return every filled cell participating in a repeated unit value."""
    units = [[(r, c) for c in range(SIZE)] for r in range(SIZE)]
    units += [[(r, c) for r in range(SIZE)] for c in range(SIZE)]
    units += [[(r, c) for r in range(br, br + BOX)
               for c in range(bc, bc + BOX)]
              for br in range(0, SIZE, BOX) for bc in range(0, SIZE, BOX)]
    conflicts = set()
    for unit in units:
        positions = {}
        for r, c in unit:
            if board[r][c]:
                positions.setdefault(board[r][c], []).append((r, c))
        for group in positions.values():
            if len(group) > 1:
                conflicts.update(group)
    return conflicts


class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.original = None  # the most recently loaded board, or None
        self.cells = [[None] * SIZE for _ in range(SIZE)]
        self._build_board()
        self._build_controls()

    # ---------- layout ----------

    def _build_board(self):
        """Nine 3x3 box frames inside one grid; the box borders form the
        bold lines every three rows and columns, and each cell is an entry
        box with a thin outline."""
        frame = tk.Frame(self.root)
        frame.pack(padx=12, pady=(12, 6))
        for br in range(0, SIZE, BOX):
            for bc in range(0, SIZE, BOX):
                box = tk.Frame(frame, borderwidth=2, relief="solid")
                box.grid(row=br // BOX, column=bc // BOX)
                for r in range(br, br + BOX):
                    for c in range(bc, bc + BOX):
                        cell = tk.Entry(box, width=2, font=("Menlo", 22),
                                        justify="center", relief="flat",
                                        highlightthickness=1,
                                        highlightbackground="#cccccc",
                                        highlightcolor=SOLVED_COLOR,
                                        foreground=GIVEN_COLOR,
                                        validate="key",
                                        validatecommand=(self.root.register(self._valid_digit), "%P"))
                        cell.grid(row=r - br, column=c - bc, padx=1, pady=1)
                        cell.bind("<Up>", lambda event, r=r, c=c: self._move(r, c, -1, 0))
                        cell.bind("<Down>", lambda event, r=r, c=c: self._move(r, c, 1, 0))
                        cell.bind("<Left>", lambda event, r=r, c=c: self._move(r, c, 0, -1))
                        cell.bind("<Right>", lambda event, r=r, c=c: self._move(r, c, 0, 1))
                        cell.bind("<<Paste>>", lambda event: "break")
                        cell.bind("<KeyRelease>", lambda event, r=r, c=c: self._on_edit(r, c))
                        cell.bind("<FocusIn>", lambda event, r=r, c=c: self._inspect_cell(r, c))
                        self.cells[r][c] = cell

    def _build_controls(self):
        bar = tk.Frame(self.root)
        bar.pack(pady=6)
        tk.Button(bar, text="Load", width=8, command=self.load_puzzle).pack(side="left", padx=4)
        tk.Button(bar, text="Solve", width=8, command=self.solve_puzzle).pack(side="left", padx=4)
        self.reset_button = tk.Button(bar, text="Reset", width=8, command=self.reset_puzzle)
        self.reset_button.pack(side="left", padx=4)
        self.clear_button = tk.Button(bar, text="Clear", width=8, command=self.clear_grid)
        self.clear_button.pack(side="left", padx=4)
        self.status = tk.Label(self.root, anchor="w", justify="left",
                               text="Load a puzzle or type digits, then press Solve.")
        self.status.pack(fill="x", padx=12, pady=(0, 12))
        self._refresh_buttons()

    # ---------- helpers ----------

    @staticmethod
    def _valid_digit(text):
        """Entry validation: accept an empty cell or a single digit 1-9."""
        return text == "" or (len(text) == 1 and text in "123456789")

    def _move(self, r, c, dr, dc):
        """Move focus one cell up/down/left/right, staying on the board."""
        r = max(0, min(SIZE - 1, r + dr))
        c = max(0, min(SIZE - 1, c + dc))
        self.cells[r][c].focus_set()
        return "break"

    def _read_grid(self):
        """Collect the entry texts into a board and validate it.

        Blank cells become 0. The solver's validate_board then checks the
        shape and rejects conflicting digits with its usual messages, so
        the GUI and the command line share one validation path.
        """
        board = []
        for r in range(SIZE):
            row = []
            for c in range(SIZE):
                text = self.cells[r][c].get().strip()
                if text == "":
                    row.append(0)
                elif len(text) == 1 and text in "123456789":
                    row.append(int(text))
                else:
                    raise PuzzleError(
                        f"Cell ({r + 1},{c + 1}) holds {text!r}; "
                        f"enter a digit 1-9 or leave it blank.")
            board.append(row)
        return validate_board(board)

    def _current_values(self):
        return [[int(cell.get()) if len(cell.get()) == 1 and
                 cell.get() in "123456789" else 0 for cell in row]
                for row in self.cells]

    def _mark_conflicts(self):
        conflicts = conflict_cells(self._current_values())
        for r in range(SIZE):
            for c in range(SIZE):
                self.cells[r][c].config(
                    background=CONFLICT_COLOR if (r, c) in conflicts else "white")
        return conflicts

    def _inspect_cell(self, r, c):
        conflicts = self._mark_conflicts()
        if conflicts:
            self.status.config(text=f"Conflicting digits in {len(conflicts)} cells (highlighted red).")
            return
        board = self._current_values()
        if board[r][c]:
            text = f"Row {r + 1}, column {c + 1}: {board[r][c]}."
        else:
            legal = sorted(candidates(board, r, c))
            text = f"Row {r + 1}, column {c + 1}: candidates " + (
                ", ".join(map(str, legal)) if legal else "none (dead end)") + "."
        self.status.config(text=text)

    def _on_edit(self, r, c):
        self.cells[r][c].config(foreground=GIVEN_COLOR)
        self._refresh_buttons()
        self._inspect_cell(r, c)

    def _write_cell(self, cell, text, color):
        """Write text into an entry, bypassing the key validation.

        Entry validation also applies to programmatic inserts, so without
        this switch a programmatic write of an invalid key (for example a
        '0' during tests or future paste support) would be silently
        dropped.
        """
        cell.config(validate="none")
        cell.config(foreground=color)
        cell.delete(0, "end")
        if text:
            cell.insert(0, text)
        cell.config(validate="key")

    def _fill_grid(self, board, color=GIVEN_COLOR):
        for r in range(SIZE):
            for c in range(SIZE):
                self._write_cell(self.cells[r][c], str(board[r][c]) if board[r][c] else "", color)
        self._mark_conflicts()

    def _fill_solution(self, given, solution):
        """Show the completed board: user digits black, solver digits blue."""
        for r in range(SIZE):
            for c in range(SIZE):
                color = GIVEN_COLOR if given[r][c] else SOLVED_COLOR
                self._write_cell(self.cells[r][c], str(solution[r][c]), color)

    def _set_status(self, text):
        self.status.config(text=text)
        self._refresh_buttons()

    def _refresh_buttons(self):
        any_digit = any(self.cells[r][c].get().strip()
                        for r in range(SIZE) for c in range(SIZE))
        self.reset_button.config(state="normal" if self.original is not None else "disabled")
        self.clear_button.config(state="normal" if self.original is not None or any_digit
                                 else "disabled")

    # ---------- button handlers ----------

    def load_puzzle(self):
        path = filedialog.askopenfilename(
            title="Load a Sudoku puzzle",
            filetypes=[("Sudoku files", "*.txt *.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            board = read_puzzle(path, csv=Path(path).suffix.lower() == ".csv")
        except PuzzleError as error:
            messagebox.showerror("Input error", str(error))
            return
        givens = sum(value != 0 for row in board for value in row)
        self.original = copy.deepcopy(board)
        self._fill_grid(board)
        self._set_status(f"Loaded {Path(path).name}: {givens} givens. Press Solve.")

    def solve_puzzle(self):
        self._mark_conflicts()
        try:
            given = self._read_grid()
        except PuzzleError as error:
            messagebox.showerror("Input error", str(error))
            return
        if not any(value for row in given for value in row):
            messagebox.showinfo("Sudoku", "Enter at least one digit before solving.")
            return
        start = time.perf_counter()
        result = solve(given)
        elapsed = time.perf_counter() - start
        if result.solution is None:
            messagebox.showinfo("Sudoku", "No solution exists for these digits.")
            self._set_status(f"No solution ({result.stats.nodes} nodes).")
            return
        self._fill_solution(given, result.solution)
        self._set_status(f"Solved: {result.stats.nodes} nodes, {result.stats.placements} "
                         f"placements, {result.stats.backtracks} backtracks "
                         f"in {elapsed * 1000:.1f} ms.")

    def reset_puzzle(self):
        """Restore the most recently loaded original and clear the result."""
        if self.original is None:
            messagebox.showinfo("Sudoku", "No puzzle has been loaded yet.")
            return
        self._fill_grid(self.original)
        self._set_status("Reset to the loaded puzzle.")

    def clear_grid(self):
        for r in range(SIZE):
            for c in range(SIZE):
                self._write_cell(self.cells[r][c], "", GIVEN_COLOR)
        self.original = None
        self._mark_conflicts()
        self._set_status("Cleared. Load a puzzle or type digits.")


def main():
    root = tk.Tk()
    root.title("Sudoku Solver")
    root.resizable(False, False)
    SudokuApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
