"""Suite B: ten mocked GLM failure modes must keep the room playable."""

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))

import app.main as main
from app.ai.glm_client import GLMError
from app.game_engine import ConnectFourEngine


@pytest.mark.parametrize(
    "fault",
    [
        "http_500_a", "http_500_b", "http_429_a", "http_429_b",
        "timeout_a", "timeout_b", "malformed_json", "illegal_column",
        "full_column", "socket_reset",
    ],
)
def test_suite_b_faults_fall_back_to_a_legal_move(monkeypatch, fault):
    async def fake_glm(*args, **kwargs):
        if fault.startswith("timeout"):
            raise asyncio.TimeoutError()
        reason = "network_error" if fault == "socket_reset" else fault
        raise GLMError(reason)

    def fake_minimax(board, depth=4, bot_piece=2):
        return 3

    monkeypatch.setattr(main, "request_glm_move", fake_glm)
    monkeypatch.setattr(main, "get_minimax_move", fake_minimax)
    room = {
        "room_id": f"fault-{fault}",
        "is_pve": True,
        "engine": ConnectFourEngine(),
        "p1": {"ws": None, "session_id": "human"},
        "p2": {"ws": None, "session_id": "bot"},
        "current_turn": 2,
        "turn_start": main.time.time(),
        "fallback_notified": False,
    }
    if fault == "full_column":
        for _ in range(6):
            room["engine"].drop_token(3, 1)

    asyncio.run(main.handle_ai_turn(room))

    assert room["fallback_notified"] is True
    assert room["current_turn"] == 1
    assert room["engine"].move_count >= 1
    assert any(cell == 2 for row in room["engine"].board for cell in row)
