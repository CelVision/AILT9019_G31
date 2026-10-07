"""
Unit tests for Connect Four rules, physics, and win detection engine.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server')))

from app.game_engine import ConnectFourEngine, ROWS, COLS


def test_empty_board():
    engine = ConnectFourEngine()
    assert len(engine.board) == 6
    assert len(engine.board[0]) == 7
    assert engine.get_legal_moves() == [0, 1, 2, 3, 4, 5, 6]
    assert not engine.is_draw()


def test_gravity_drop():
    engine = ConnectFourEngine()
    success, row = engine.drop_token(col=3, player=1)
    assert success is True
    assert row == 5  # Bottom row
    assert engine.board[5][3] == 1

    success, row2 = engine.drop_token(col=3, player=2)
    assert success is True
    assert row2 == 4  # Next row up
    assert engine.board[4][3] == 2


def test_column_overflow():
    engine = ConnectFourEngine()
    for _ in range(6):
        success, _ = engine.drop_token(col=0, player=1)
        assert success is True

    # 7th move in full column should be rejected
    success, row = engine.drop_token(col=0, player=2)
    assert success is False
    assert row is None
    assert 0 not in engine.get_legal_moves()


def test_horizontal_win():
    engine = ConnectFourEngine()
    # Player 1 drops into cols 0, 1, 2, 3
    for col in range(3):
        engine.drop_token(col, player=1)
    
    # 4th token completes horizontal line
    success, row = engine.drop_token(3, player=1)
    is_win, coords = engine.check_win(row, 3)
    assert is_win is True
    assert len(coords) == 4


def test_vertical_win():
    engine = ConnectFourEngine()
    # Player 2 stacks 4 tokens in column 4
    for _ in range(3):
        engine.drop_token(4, player=2)

    success, row = engine.drop_token(4, player=2)
    is_win, coords = engine.check_win(row, 4)
    assert is_win is True
    assert len(coords) == 4


def test_diagonal_down_right_win():
    """
    Construct a diagonal down-right line:
    (2,0), (3,1), (4,2), (5,3)
    """
    engine = ConnectFourEngine()
    # Col 0: 3 tokens (2 dummy, 1 P1 at row 2)
    engine.drop_token(0, 2); engine.drop_token(0, 2); engine.drop_token(0, 2); engine.drop_token(0, 1)
    # Col 1: 3 tokens (2 dummy, 1 P1 at row 3)
    engine.drop_token(1, 2); engine.drop_token(1, 2); engine.drop_token(1, 1)
    # Col 2: 2 tokens (1 dummy, 1 P1 at row 4)
    engine.drop_token(2, 2); engine.drop_token(2, 1)
    # Col 3: 1 token (P1 at row 5)
    success, row = engine.drop_token(3, 1)

    is_win, coords = engine.check_win(row, 3)
    assert is_win is True
    assert len(coords) == 4


def test_diagonal_up_right_win():
    """
    Construct a diagonal up-right line:
    (5,0), (4,1), (3,2), (2,3)
    """
    engine = ConnectFourEngine()
    # Col 0: row 5 is P1
    engine.drop_token(0, 1)
    # Col 1: 1 dummy, row 4 is P1
    engine.drop_token(1, 2); engine.drop_token(1, 1)
    # Col 2: 2 dummy, row 3 is P1
    engine.drop_token(2, 2); engine.drop_token(2, 2); engine.drop_token(2, 1)
    # Col 3: 3 dummy, row 2 is P1
    engine.drop_token(3, 2); engine.drop_token(3, 2); engine.drop_token(3, 2)
    success, row = engine.drop_token(3, 1)

    is_win, coords = engine.check_win(row, 3)
    assert is_win is True
    assert len(coords) == 4


if __name__ == "__main__":
    test_empty_board()
    test_gravity_drop()
    test_column_overflow()
    test_horizontal_win()
    test_vertical_win()
    test_diagonal_down_right_win()
    test_diagonal_up_right_win()
    print("ALL CONNECT FOUR ENGINE TESTS PASSED!")
