"""Regression tests for the registration, timeout, and fallback requirements."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))

import app.main as main
from app.game_engine import ConnectFourEngine
from app.ai.glm_client import GLMError


def test_registration_validation_rejects_invalid_profiles():
    valid, error = main.validate_registration({"nickname": "Alex", "birth_year": 2003})
    assert error is None
    assert valid["age"] >= 18

    for payload, field in (
        ({"nickname": "A", "birth_year": 2003}, "nickname"),
        ({"nickname": "Alex", "birth_year": 2010}, "birth_year"),
        ({"nickname": "Alex"}, "birth_year"),
        ({"nickname": "Alex", "birth_year": "not-a-year"}, "birth_year"),
    ):
        value, error = main.validate_registration(payload)
        assert value is None
        assert error["field"] == field


def test_glm_failure_uses_minimax(monkeypatch):
    async def fake_glm(*args, **kwargs):
        raise GLMError("http_429")

    called = []

    def fake_minimax(board, depth=4, bot_piece=2):
        called.append((board, depth, bot_piece))
        return 2

    monkeypatch.setattr(main, "request_glm_move", fake_glm)
    monkeypatch.setattr(main, "get_minimax_move", fake_minimax)
    room = {
        "room_id": "minimax-test",
        "is_pve": True,
        "engine": ConnectFourEngine(),
        "p1": {"ws": None, "session_id": "human"},
        "p2": {"ws": None, "session_id": "bot"},
        "current_turn": 2,
        "turn_start": main.time.time(),
        "fallback_notified": False,
    }

    asyncio.run(main.handle_ai_turn(room))

    assert called and called[0][1:] == (4, 2)
    assert room["engine"].board[5][2] == 2
    assert room["fallback_notified"] is True


def test_expired_turn_finishes_room(monkeypatch):
    room = {
        "room_id": "timeout-test",
        "is_pve": True,
        "engine": ConnectFourEngine(),
        "p1": {"ws": None, "session_id": "human"},
        "p2": {"ws": None, "session_id": "bot"},
        "current_turn": 1,
        "turn_start": main.time.time() - main.TURN_DURATION_SECONDS - 1,
    }
    main.active_rooms.clear()
    main.finished_rooms.clear()
    main.active_rooms[room["room_id"]] = room

    asyncio.run(main.expire_turn(room))

    assert room["room_id"] not in main.active_rooms
    assert main.finished_rooms[room["room_id"]]["p1"]["session_id"] == "human"
    main.finished_rooms.clear()
