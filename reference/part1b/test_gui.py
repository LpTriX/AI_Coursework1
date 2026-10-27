"""Interface state checks that do not require a window server."""
import unittest
from unittest.mock import patch
from pathlib import Path
from gui import CONFLICT_COLOR, SudokuApp, conflict_cells
from solver import read_puzzle

class Widget:
    def __init__(self): self.text = ''; self.options = {}
    def get(self): return self.text
    def config(self, **options): self.options.update(options)
    def delete(self, *_): self.text = ''
    def insert(self, _, text): self.text = str(text)

def app():
    ui = SudokuApp.__new__(SudokuApp)
    ui.original = None
    ui.cells = [[Widget() for _ in range(9)] for _ in range(9)]
    ui.status = Widget(); ui.reset_button = Widget(); ui.clear_button = Widget()
    return ui

class InterfaceTests(unittest.TestCase):
    def test_row_column_and_box_conflicts(self):
        for pair in (((0,0),(0,8)), ((0,0),(8,0)), ((0,0),(1,1))):
            board = [[0]*9 for _ in range(9)]
            for r,c in pair: board[r][c] = 5
            self.assertEqual(conflict_cells(board), set(pair))
    def test_zeros_and_separate_units_are_not_conflicts(self):
        board = [[0]*9 for _ in range(9)]
        board[0][0] = board[4][4] = 5
        self.assertEqual(conflict_cells(board), set())
    def test_edit_enables_clear_and_clearing_disables_it(self):
        ui = app(); ui._refresh_buttons()
        self.assertEqual(ui.clear_button.options['state'], 'disabled')
        ui.cells[0][0].text = '5'; ui._on_edit(0,0)
        self.assertEqual(ui.clear_button.options['state'], 'normal')
        ui.clear_grid()
        self.assertEqual(ui.clear_button.options['state'], 'disabled')
        self.assertTrue(all(not c.get() for row in ui.cells for c in row))
    def test_correcting_conflict_removes_highlight(self):
        ui = app(); ui.cells[0][0].text = ui.cells[0][1].text = '5'
        ui._on_edit(0,1)
        self.assertEqual(ui.cells[0][0].options['background'], CONFLICT_COLOR)
        ui.cells[0][1].text = '6'; ui._on_edit(0,1)
        self.assertEqual(ui.cells[0][0].options['background'], 'white')
    def test_reset_restores_loaded_puzzle_after_solve(self):
        ui = app(); board = read_puzzle(Path(__file__).parent/'puzzles/p1.txt')
        ui.original = [row[:] for row in board]; ui._fill_grid(board)
        with patch('gui.messagebox.showinfo') as message:
            ui.solve_puzzle(); message.assert_not_called()
        self.assertTrue(all(c.get() for row in ui.cells for c in row))
        ui.reset_puzzle(); self.assertEqual(ui._read_grid(),board)
    def test_candidates_and_conflict_message(self):
        ui = app(); ui.cells[0][1].text='5'; ui._inspect_cell(0,0)
        self.assertNotIn('5',ui.status.options['text'].split('candidates ')[1])
        ui.cells[0][0].text='5'; ui._on_edit(0,0)
        self.assertIn('2 cells',ui.status.options['text'])

if __name__ == '__main__': unittest.main()
