"""Unit tests for the extracted RoomManager (WP2-3)."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))

from app.room_manager import RoomManager


def test_room_manager_lifecycle():
    rm = RoomManager()
    room = {
        "room_id": "rm-123",
        "is_pve": False,
        "p1": {"session_id": "s1", "nickname": "Alice"},
        "p2": {"session_id": "s2", "nickname": "Bob"},
        "chat_history": [{"role": "user", "content": "hi"}],
    }

    rm.add_active_room(room)
    assert rm.get_active_room("rm-123") is room

    rid, found = rm.find_room_for_session("s1")
    assert rid == "rm-123"
    assert found is room

    rid2, found2 = rm.find_room_for_session("s2")
    assert rid2 == "rm-123"

    # Remember finished room
    rm.remember_finished_room(room)
    rm.remove_active_room("rm-123")
    assert rm.get_active_room("rm-123") is None

    # Chat lookup finds latest finished room
    chat_rid, chat_room = rm.find_room_for_chat("s1")
    assert chat_rid == "rm-123"
    assert chat_room["ended"] is True
    assert len(chat_room["chat_history"]) == 1

    # Cleanup stale
    rm.cleanup_stale_finished(max_age_seconds=0.0)
    assert len(rm.finished_rooms) == 0
