"""
Deterministic Minimax Connect Four Solver with Alpha-Beta Pruning.
Serves as the local fail-safe heuristic engine if GLM times out (>3.5s) or fails.
"""

from typing import List, Tuple, Optional
import time

ROWS = 6
COLS = 7

# Positional bonus values prioritizing center columns
POSITION_WEIGHTS = [
    [3, 4, 5, 7, 5, 4, 3],
    [4, 6, 8, 10, 8, 6, 4],
    [5, 8, 11, 13, 11, 8, 5],
    [5, 8, 11, 13, 11, 8, 5],
    [4, 6, 8, 10, 8, 6, 4],
    [3, 4, 5, 7, 5, 4, 3]
]


def evaluate_window(window: List[int], piece: int) -> int:
    score = 0
    opp_piece = 1 if piece == 2 else 2

    if window.count(piece) == 4:
        score += 100000
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 500
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 50

    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 400
    elif window.count(opp_piece) == 4:
        score -= 80000

    return score


def score_position(board: List[List[int]], piece: int) -> int:
    score = 0

    # Center column preference
    center_col = [board[r][3] for r in range(ROWS)]
    score += center_col.count(piece) * 30

    # Positional table bonus
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == piece:
                score += POSITION_WEIGHTS[r][c]

    # Horizontal windows
    for r in range(ROWS):
        for c in range(COLS - 3):
            window = [board[r][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Vertical windows
    for c in range(COLS):
        for r in range(ROWS - 3):
            window = [board[r + i][c] for i in range(4)]
            score += evaluate_window(window, piece)

    # Positive sloped diagonal
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Negative sloped diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score


def get_legal_moves(board: List[List[int]]) -> List[int]:
    # Order center-out for better alpha-beta cutoffs: [3, 2, 4, 1, 5, 0, 6]
    preferred_order = [3, 2, 4, 1, 5, 0, 6]
    return [c for c in preferred_order if board[0][c] == 0]


def is_winning_move(board: List[List[int]], piece: int) -> bool:
    # Check horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True
    # Check vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True
    # Positive diagonal
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True
    # Negative diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True
    return False


def get_next_open_row(board: List[List[int]], col: int) -> Optional[int]:
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == 0:
            return r
    return None


def minimax(
    board: List[List[int]],
    depth: int,
    alpha: float,
    beta: float,
    maximizing_player: bool,
    bot_piece: int = 2
) -> Tuple[Optional[int], int]:
    legal_moves = get_legal_moves(board)
    opp_piece = 1 if bot_piece == 2 else 2

    # Terminal state checks
    if is_winning_move(board, bot_piece):
        return None, 1000000 + depth
    if is_winning_move(board, opp_piece):
        return None, -1000000 - depth
    if len(legal_moves) == 0 or depth == 0:
        return None, score_position(board, bot_piece)

    if maximizing_player:
        value = -float('inf')
        best_col = legal_moves[0]
        for col in legal_moves:
            row = get_next_open_row(board, col)
            if row is not None:
                board[row][col] = bot_piece
                _, new_score = minimax(board, depth - 1, alpha, beta, False, bot_piece)
                board[row][col] = 0
                if new_score > value:
                    value = new_score
                    best_col = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        return best_col, int(value)
    else:
        value = float('inf')
        best_col = legal_moves[0]
        for col in legal_moves:
            row = get_next_open_row(board, col)
            if row is not None:
                board[row][col] = opp_piece
                _, new_score = minimax(board, depth - 1, alpha, beta, True, bot_piece)
                board[row][col] = 0
                if new_score < value:
                    value = new_score
                    best_col = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
        return best_col, int(value)


def get_minimax_move(board: List[List[int]], depth: int = 4, bot_piece: int = 2) -> int:
    """
    Selects the optimal column for the bot within milliseconds using alpha-beta minimax.
    """
    legal_moves = get_legal_moves(board)
    if not legal_moves:
        return 3

    # Check for immediate win
    for col in legal_moves:
        row = get_next_open_row(board, col)
        if row is not None:
            board[row][col] = bot_piece
            if is_winning_move(board, bot_piece):
                board[row][col] = 0
                return col
            board[row][col] = 0

    # Check for immediate block
    opp_piece = 1 if bot_piece == 2 else 2
    for col in legal_moves:
        row = get_next_open_row(board, col)
        if row is not None:
            board[row][col] = opp_piece
            if is_winning_move(board, opp_piece):
                board[row][col] = 0
                return col
            board[row][col] = 0

    col, _ = minimax(board, depth=depth, alpha=-float('inf'), beta=float('inf'), maximizing_player=True, bot_piece=bot_piece)
    return col if col is not None else legal_moves[0]
