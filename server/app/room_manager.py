"""
In-memory room manager for ConnectFour Connect (WP2-3).
Encapsulates active room sessions, finished room retention, and thread-safe lookups.
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple


class RoomManager:
    """Manages active and finished Connect Four game rooms."""

    def __init__(self) -> None:
        self.active_rooms: Dict[str, dict] = {}
        self.finished_rooms: Dict[str, dict] = {}

    def add_active_room(self, room: dict) -> None:
        """Register a new active game room."""
        self.active_rooms[room["room_id"]] = room

    def get_active_room(self, room_id: str) -> Optional[dict]:
        """Fetch active room by ID."""
        return self.active_rooms.get(room_id)

    def remove_active_room(self, room_id: str) -> Optional[dict]:
        """Remove and return active room."""
        return self.active_rooms.pop(room_id, None)

    def remember_finished_room(self, room: dict, max_records: int = 100) -> None:
        """Retain completed match metadata for post-game banter and rematches."""
        if len(self.finished_rooms) >= max_records:
            oldest = min(self.finished_rooms.keys(), key=lambda k: self.finished_rooms[k].get("finished_at", 0))
            self.finished_rooms.pop(oldest, None)

        self.finished_rooms[room["room_id"]] = {
            "room_id": room["room_id"],
            "is_pve": room["is_pve"],
            "p1": room["p1"],
            "p2": room["p2"],
            "rematch_requests": set(),
            "finished_at": time.time(),
            "chat_history": room.get("chat_history", []),
            "last_chat_time": room.get("last_chat_time", {}),
            "ended": True,
            "ai_settings": room.get("ai_settings"),
        }

    def find_room_for_session(self, session_id: str) -> Tuple[Optional[str], Optional[dict]]:
        """Find active room containing the session ID."""
        for room_id, room in self.active_rooms.items():
            if room["p1"]["session_id"] == session_id:
                return room_id, room
            if not room["is_pve"] and room["p2"]["session_id"] == session_id:
                return room_id, room
        return None, None

    def find_room_for_chat(self, session_id: str) -> Tuple[Optional[str], Optional[dict]]:
        """Find active or newest finished room so players can chat during and after match."""
        room_id, room = self.find_room_for_session(session_id)
        if room:
            return room_id, room

        candidates = [
            (r_id, r)
            for r_id, r in self.finished_rooms.items()
            if r["p1"]["session_id"] == session_id
            or (not r["is_pve"] and r["p2"]["session_id"] == session_id)
        ]
        if candidates:
            candidates.sort(key=lambda item: item[1].get("finished_at", 0), reverse=True)
            return candidates[0]
        return None, None

    def cleanup_stale_finished(self, max_age_seconds: float = 600.0) -> int:
        """Evict finished matches older than max_age_seconds."""
        now = time.time()
        stale = [
            r_id
            for r_id, r in self.finished_rooms.items()
            if now - r.get("finished_at", 0) > max_age_seconds
        ]
        for r_id in stale:
            self.finished_rooms.pop(r_id, None)
        return len(stale)

    def clear(self) -> None:
        """Clear all active and finished rooms."""
        self.active_rooms.clear()
        self.finished_rooms.clear()
