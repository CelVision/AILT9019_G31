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


def test_daily_topics_endpoint():
    topics = asyncio.run(main.get_daily_topics())
    assert "topics" in topics
    assert len(topics["topics"]) >= 4
    assert any("Coffee" in t["label"] for t in topics["topics"])


def test_ai_chat_turn_generates_companion_reply(monkeypatch):
    async def fake_reply(history):
        return "I prefer tea in the morning!"

    monkeypatch.setattr(main, "generate_chat_reply", fake_reply)
    room = {
        "room_id": "chat-test-room",
        "is_pve": True,
        "engine": ConnectFourEngine(),
        "p1": {"ws": None, "session_id": "human", "nickname": "Alex"},
        "p2": {"ws": None, "session_id": "bot", "nickname": "AI Coach"},
        "chat_history": [{"role": "user", "content": "Coffee or tea?"}],
    }
    main.active_rooms.clear()
    main.active_rooms[room["room_id"]] = room

    asyncio.run(main.handle_ai_chat_turn(room))

    assert len(room["chat_history"]) == 2
    assert room["chat_history"][1]["content"] == "I prefer tea in the morning!"
    main.active_rooms.clear()


def test_ai_chat_turn_works_in_finished_room(monkeypatch):
    async def fake_reply(history):
        return "Good game! You played brilliantly!"

    monkeypatch.setattr(main, "generate_chat_reply", fake_reply)
    room = {
        "room_id": "finished-chat-test",
        "is_pve": True,
        "engine": ConnectFourEngine(),
        "p1": {"ws": None, "session_id": "human", "nickname": "Alex"},
        "p2": {"ws": None, "session_id": "bot", "nickname": "AI Coach"},
        "chat_history": [{"role": "user", "content": "GG!"}],
        "ended": True,
    }
    main.active_rooms.clear()
    main.finished_rooms.clear()
    main.finished_rooms[room["room_id"]] = room

    asyncio.run(main.handle_ai_chat_turn(room))

    assert len(room["chat_history"]) == 2
    assert "Good game" in room["chat_history"][1]["content"]
    main.finished_rooms.clear()


def test_find_room_for_chat_selects_latest_finished_room():
    main.active_rooms.clear()
    main.finished_rooms.clear()
    main.finished_rooms["room1"] = {
        "room_id": "room1",
        "is_pve": False,
        "p1": {"session_id": "user1"},
        "p2": {"session_id": "user2"},
        "finished_at": 100.0,
    }
    main.finished_rooms["room2"] = {
        "room_id": "room2",
        "is_pve": False,
        "p1": {"session_id": "user1"},
        "p2": {"session_id": "user3"},
        "finished_at": 200.0,
    }
    r_id, r = main.find_room_for_chat("user1")
    assert r_id == "room2"
    assert r["finished_at"] == 200.0
    main.finished_rooms.clear()


def test_create_pve_match_applies_custom_ai_settings():
    main.active_rooms.clear()
    user = {
        "ws": None,
        "session_id": "cust-user",
        "nickname": "Tester",
        "age": 20,
        "custom_ai": {
            "api_key": "custom-secret-key",
            "model": "deepseek-v4.1-flash",
            "base_url": "https://custom.endpoint.com/v1",
        },
    }
    asyncio.run(main.create_pve_match(user))
    assert len(main.active_rooms) == 1
    room = list(main.active_rooms.values())[0]
    assert "ai_settings" in room
    assert room["ai_settings"].api_key == "custom-secret-key"
    assert room["ai_settings"].default_model == "deepseek-v4.1-flash"
    assert room["ai_settings"].base_url == "https://custom.endpoint.com/v1"
    main.active_rooms.clear()


