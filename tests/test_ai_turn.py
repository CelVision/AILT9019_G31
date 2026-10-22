"""
Tests for the GLM-first PvE turn handler and the temporary safe-move fallback.

The gateway's WebSocket is set to None, so manager.send_json swallows the
send attempt; these tests focus on board mutation and fallback state.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))

from app.ai.glm_client import GLMError, GLMMove, safe_legal_column
from app.game_engine import ConnectFourEngine
import app.main as main


def make_room() -> dict:
    return {
        "room_id": "test-room",
        "is_pve": True,
        "engine": ConnectFourEngine(),
        "p1": {"ws": None, "session_id": "human"},
        "p2": {"ws": None, "session_id": "bot"},
        "current_turn": 2,
        "fallback_notified": False,
    }


def test_safe_legal_column_prefers_center():
    board = [[0 for _ in range(7)] for _ in range(6)]
    assert safe_legal_column(board) == 3

    for row in range(6):
        board[row][3] = 1
    assert safe_legal_column(board) == 2


def test_safe_legal_column_returns_none_when_full():
    board = [[1 for _ in range(7)] for _ in range(6)]
    assert safe_legal_column(board) is None


def test_ai_turn_uses_glm_move(monkeypatch):
    async def fake_move(*args, **kwargs):
        return GLMMove(column=0, canned_reaction_id=0, latency_ms=1.0)

    monkeypatch.setattr(main, "request_glm_move", fake_move)
    room = make_room()

    asyncio.run(main.handle_ai_turn(room))

    assert room["engine"].board[5][0] == 2
    assert room["current_turn"] == 1
    assert room["fallback_notified"] is False


def test_ai_turn_falls_back_to_safe_move(monkeypatch):
    async def fake_move(*args, **kwargs):
        raise GLMError("missing_api_key")

    monkeypatch.setattr(main, "request_glm_move", fake_move)
    room = make_room()

    asyncio.run(main.handle_ai_turn(room))

    assert room["engine"].board[5][3] == 2
    assert room["current_turn"] == 1
    assert room["fallback_notified"] is True


def test_ai_turn_handles_wait_for_timeout(monkeypatch):
    async def fake_move(*args, **kwargs):
        raise asyncio.TimeoutError()

    monkeypatch.setattr(main, "request_glm_move", fake_move)
    room = make_room()

    asyncio.run(main.handle_ai_turn(room))

    assert room["engine"].board[5][3] == 2
    assert room["fallback_notified"] is True
