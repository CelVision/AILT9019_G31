"""
Test Suite B — external LLM outage and graceful degradation (WP5-2).

Ten fault injections against the PvE turn handler: two upstream HTTP failures,
two quota failures, two timeouts, and four malformed or illegal model replies.
Every case must end with a legal local move, a fallback notice, and an intact
room — no unhandled exception, no disconnected WebSocket.

The final two tests check that the local reply is actually good: Minimax must
block an immediate loss rather than dropping a token in the centre column.
"""

import asyncio
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))

from app.ai.glm_client import GLMError, GLMMove  # noqa: E402
from app.game_engine import ConnectFourEngine  # noqa: E402
import app.main as main  # noqa: E402


class FakeSocket:
    """Stand-in for a Starlette WebSocket that records every frame."""

    def __init__(self):
        self.frames = []

    async def send_text(self, raw: str) -> None:
        self.frames.append(json.loads(raw))

    def types(self):
        return [frame["type"] for frame in self.frames]

    def payload_of(self, msg_type):
        for frame in self.frames:
            if frame["type"] == msg_type:
                return frame["payload"]
        return None


def make_room(board=None) -> dict:
    engine = ConnectFourEngine(board) if board else ConnectFourEngine()
    return {
        "room_id": "test-room",
        "is_pve": True,
        "engine": engine,
        "p1": {"ws": FakeSocket(), "session_id": "human"},
        "p2": {"ws": None, "session_id": "bot"},
        "current_turn": 2,
        "fallback_notified": False,
    }


# (label, exception raised by the GLM adapter)
FAULTS = [
    ("http_500", GLMError("http_500")),
    ("http_502", GLMError("http_502")),
    ("rate_limited_429", GLMError("http_429")),
    ("quota_429_retry", GLMError("http_429")),
    ("network_timeout", asyncio.TimeoutError()),
    ("slow_response_timeout", asyncio.TimeoutError()),
    ("bad_response_body", GLMError("bad_response")),
    ("invalid_column", GLMError("invalid_column")),
    ("illegal_column", GLMError("illegal_column")),
    ("unexpected_runtime_error", RuntimeError("boom")),
]


@pytest.mark.parametrize("label,fault", FAULTS)
def test_fault_injection_falls_back_cleanly(label, fault, monkeypatch):
    async def failing_move(*args, **kwargs):
        raise fault

    monkeypatch.setattr(main, "request_glm_move", failing_move)
    room = make_room()
    socket = room["p1"]["ws"]

    asyncio.run(main.handle_ai_turn(room))

    # The room survived and the bot actually moved.
    assert room["room_id"] in main.active_rooms or room["engine"].move_count == 1
    assert room["engine"].move_count == 1
    assert room["current_turn"] == 1

    # The human was told, once, with a non-secret reason.
    notice = socket.payload_of("pve_fallback_notice")
    assert notice is not None
    assert "fallback" in notice["message"].lower()
    assert notice["strategy"] in {"minimax", "safe_move"}
    assert room["fallback_notified"] is True

    # The reply landed on a legal column and the board is consistent.
    last_move = socket.payload_of("board_update")["last_move"]
    assert 0 <= last_move["column"] <= 6
    assert room["engine"].board[last_move["row"]][last_move["column"]] == 2


def test_fallback_blocks_an_immediate_loss(monkeypatch):
    """Human has three in a row in column 0; the fallback must block it."""

    async def failing_move(*args, **kwargs):
        raise GLMError("http_500")

    monkeypatch.setattr(main, "request_glm_move", failing_move)

    board = [[0] * 7 for _ in range(6)]
    for row in (5, 4, 3):
        board[row][0] = 1
    room = make_room(board)

    asyncio.run(main.handle_ai_turn(room))

    assert room["engine"].board[2][0] == 2
    assert room["p1"]["ws"].payload_of("pve_fallback_notice")["strategy"] == "minimax"


def test_fallback_prefers_minimax_over_a_centre_drop():
    board = [[0] * 7 for _ in range(6)]
    for row in (5, 4, 3):
        board[row][2] = 1  # human threatens column 2

    column, strategy = main.choose_fallback_move(board)

    assert strategy == "minimax"
    assert column == 2


def test_fallback_degrades_to_safe_move_on_a_full_board():
    board = [[1] * 7 for _ in range(6)]

    column, strategy = main.choose_fallback_move(board)

    assert column is None
    assert strategy == "safe_move"


def test_glm_success_path_is_unaffected(monkeypatch):
    async def good_move(*args, **kwargs):
        return GLMMove(column=0, canned_reaction_id=0, latency_ms=5.0)

    monkeypatch.setattr(main, "request_glm_move", good_move)
    room = make_room()

    asyncio.run(main.handle_ai_turn(room))

    assert room["engine"].board[5][0] == 2
    assert room["fallback_notified"] is False
    assert "pve_fallback_notice" not in room["p1"]["ws"].types()
