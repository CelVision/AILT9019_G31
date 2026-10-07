"""
Connect Four Game Engine (7 columns x 6 rows)
Pure Python implementation with gravity physics, win condition detection, and legal move validation.
"""

from typing import List, Optional, Tuple


ROWS = 6
COLS = 7


class ConnectFourEngine:
    def __init__(self, board: Optional[List[List[int]]] = None):
        if board:
            self.board = [row[:] for row in board]
        else:
            self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.move_count = sum(1 for r in range(ROWS) for c in range(COLS) if self.board[r][c] != 0)

    def is_legal_move(self, col: int) -> bool:
        """A move is legal if the column is within bounds and the top cell is empty."""
        if not (0 <= col < COLS):
            return False
        return self.board[0][col] == 0

    def get_legal_moves(self) -> List[int]:
        """Returns list of column indices that are not full."""
        return [c for c in range(COLS) if self.board[0][c] == 0]

    def drop_token(self, col: int, player: int) -> Tuple[bool, Optional[int]]:
        """
        Drops a token for `player` (1 or 2) into column `col`.
        Returns (success: bool, target_row: Optional[int]).
        """
        if not self.is_legal_move(col):
            return False, None

        # Fall from row 5 (bottom) up to row 0 (top)
        for row in range(ROWS - 1, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = player
                self.move_count += 1
                return True, row

        return False, None

    def check_win(self, last_row: int, last_col: int) -> Tuple[bool, Optional[List[List[int]]]]:
        """
        Checks if the last placed token at (last_row, last_col) created a 4-in-a-row.
        Returns (is_win: bool, winning_coordinates: Optional[List[[r, c]]]).
        """
        player = self.board[last_row][last_col]
        if player == 0:
            return False, None

        # Check all 4 directions: (d_row, d_col)
        directions = [
            (0, 1),   # Horizontal
            (1, 0),   # Vertical
            (1, 1),   # Diagonal down-right (\)
            (-1, 1),  # Diagonal up-right (/)
        ]

        for dr, dc in directions:
            coords = [[last_row, last_col]]

            # Forward check
            r, c = last_row + dr, last_col + dc
            while 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == player:
                coords.append([r, c])
                r += dr
                c += dc

            # Backward check
            r, c = last_row - dr, last_col - dc
            while 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == player:
                coords.append([r, c])
                r -= dr
                c -= dc

            if len(coords) >= 4:
                return True, coords[:4]

        return False, None

    def is_draw(self) -> bool:
        """Returns True if all cells are filled and there is no legal move."""
        return len(self.get_legal_moves()) == 0

    def get_board(self) -> List[List[int]]:
        """Returns a deep copy of the 7x6 board matrix."""
        return [row[:] for row in self.board]

    def reset(self):
        """Resets the board to an empty state."""
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.move_count = 0
