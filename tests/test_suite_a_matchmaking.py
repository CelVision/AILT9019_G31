"""
Test Suite A — age boundary and demographic filtering (WP5-1).

Twenty account cases that mirror the acceptance table in §3 of the revised
proposal: ten valid pairs, five age-gap refusals, and five underage or
malformed profiles. The queue is driven with explicit timestamps so the
15-second expiry is tested without waiting.

The last two tests drive the real WebSocket endpoint to confirm the gateway
surfaces rejections as an `error` frame instead of silently dropping the join.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))

from app.matchmaking import (  # noqa: E402
    QUEUE_TIMEOUT_SECONDS,
    MatchmakingQueue,
    QueueEntry,
    QueueRejected,
    normalize_profile,
)

CURRENT_YEAR = 2026

# (age_a, age_b) — every pair satisfies |ΔAge| <= 3 and age >= 18.
VALID_PAIRS = [
    (18, 18),
    (18, 20),
    (20, 22),
    (22, 20),
    (25, 23),
    (30, 28),
    (19, 21),
    (40, 42),
    (35, 33),
    (60, 58),
]

# (age_a, age_b) — every pair breaks |ΔAge| <= 3.
AGE_GAP_PAIRS = [
    (18, 22),
    (20, 25),
    (21, 30),
    (19, 26),
    (30, 45),
]

# (label, payload, expected error code)
INVALID_PROFILES = [
    ("underage", {"nickname": "Alice", "birth_year": CURRENT_YEAR - 17}, "underage"),
    ("null nickname", {"nickname": None, "birth_year": 2000}, "invalid_nickname"),
    ("nickname too short", {"nickname": "A", "birth_year": 2000}, "invalid_nickname"),
    ("nickname too long", {"nickname": "A" * 17, "birth_year": 2000}, "invalid_nickname"),
    ("birth year as text", {"nickname": "Alice", "birth_year": "2000"}, "invalid_birth_year"),
]


def make_entry(session_id: str, age: int, queued_at: float = 0.0) -> QueueEntry:
    return QueueEntry(
        session_id=session_id,
        nickname=f"user{session_id}",
        birth_year=CURRENT_YEAR - age,
        age=age,
        ws=None,
        queued_at=queued_at,
    )


@pytest.mark.parametrize("age_a,age_b", VALID_PAIRS)
def test_valid_pairs_are_matched(age_a, age_b):
    queue = MatchmakingQueue()
    queue.add(make_entry("a", age_a))
    queue.add(make_entry("b", age_b))

    pairs, expired = queue.tick(now=0.5)

    assert len(pairs) == 1
    assert expired == []
    assert len(queue) == 0
    matched = {pairs[0][0].session_id, pairs[0][1].session_id}
    assert matched == {"a", "b"}


@pytest.mark.parametrize("age_a,age_b", AGE_GAP_PAIRS)
def test_age_gap_pairs_are_never_matched(age_a, age_b):
    queue = MatchmakingQueue()
    queue.add(make_entry("a", age_a))
    queue.add(make_entry("b", age_b))

    pairs, expired = queue.tick(now=0.5)

    assert pairs == []
    assert expired == []
    assert len(queue) == 2

    # Both are still waiting at 14.9 s, then expire on the next tick.
    assert queue.tick(now=QUEUE_TIMEOUT_SECONDS - 0.1)[1] == []
    pairs, expired = queue.tick(now=QUEUE_TIMEOUT_SECONDS)

    assert pairs == []
    assert {e.session_id for e in expired} == {"a", "b"}
    assert len(queue) == 0


@pytest.mark.parametrize("label,payload,code", INVALID_PROFILES)
def test_invalid_profiles_are_rejected(label, payload, code):
    with pytest.raises(QueueRejected) as excinfo:
        normalize_profile(payload, CURRENT_YEAR)

    assert excinfo.value.code == code
    assert excinfo.value.message


def test_duplicate_join_is_rejected():
    queue = MatchmakingQueue()
    queue.add(make_entry("a", 20))

    with pytest.raises(QueueRejected) as excinfo:
        queue.add(make_entry("a", 21))

    assert excinfo.value.code == "already_queued"


def test_queue_capacity_is_enforced():
    queue = MatchmakingQueue(max_size=2)
    queue.add(make_entry("a", 20))
    queue.add(make_entry("b", 21))

    with pytest.raises(QueueRejected) as excinfo:
        queue.add(make_entry("c", 22))

    assert excinfo.value.code == "queue_full"


def test_status_reports_position_and_remaining_time():
    queue = MatchmakingQueue()
    queue.add(make_entry("a", 20, queued_at=0.0))
    queue.add(make_entry("b", 21, queued_at=0.0))

    status = queue.status("b", now=6.0)

    assert status == {
        "elapsed_seconds": 6.0,
        "timeout_seconds": QUEUE_TIMEOUT_SECONDS,
        "remaining_seconds": QUEUE_TIMEOUT_SECONDS - 6.0,
        "position": 2,
        "waiting": 2,
    }
    assert queue.status("missing") is None


def test_remove_takes_a_player_out_of_the_queue():
    queue = MatchmakingQueue()
    queue.add(make_entry("a", 20))

    assert queue.remove("a") is True
    assert queue.remove("a") is False
    assert len(queue) == 0


# --------------------------------------------------------------- WebSocket API
pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

import app.main as main  # noqa: E402


@pytest.fixture(autouse=True)
def clean_queue():
    main.matchmaking._entries.clear()
    yield
    main.matchmaking._entries.clear()


def test_ws_rejects_underage_with_error_frame():
    with TestClient(main.app).websocket_connect("/ws/game") as ws:
        ws.send_json({"type": "queue_join", "payload": {"nickname": "Alice", "birth_year": 2015}})
        message = ws.receive_json()

    assert message["type"] == "error"
    assert message["payload"]["code"] == "underage"
    assert message["payload"]["field"] == "birth_year"
    assert len(main.matchmaking) == 0


def test_ws_accepts_valid_join_and_returns_queue_status():
    with TestClient(main.app).websocket_connect("/ws/game") as ws:
        ws.send_json({"type": "queue_join", "payload": {"nickname": "Alice", "birth_year": 2000}})
        message = ws.receive_json()

    assert message["type"] == "queue_status"
    assert message["payload"]["position"] == 1
    assert message["payload"]["timeout_seconds"] == QUEUE_TIMEOUT_SECONDS


def test_pvp_match_room_uses_plain_player_dicts():
    """Regression: rooms must hold player dicts, not queue entries (main.py:250)."""

    class FakeSocket:
        def __init__(self):
            self.frames = []

        async def send_text(self, raw):
            self.frames.append(json.loads(raw))

    import asyncio

    a = make_entry("a", 20)
    b = make_entry("b", 21)
    a.ws, b.ws = FakeSocket(), FakeSocket()

    asyncio.run(main.create_pvp_match(a, b))

    room = next(iter(main.active_rooms.values()))
    assert isinstance(room["p1"], dict) and isinstance(room["p2"], dict)
    assert {room["p1"]["nickname"], room["p2"]["nickname"]} == {"usera", "userb"}
    assert a.ws.frames[0]["type"] == "match_found"
    assert b.ws.frames[0]["payload"]["assigned_player"] == 2

    main.active_rooms.clear()
