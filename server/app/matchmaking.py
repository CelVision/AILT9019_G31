"""
In-memory FIFO matchmaking queue for ConnectFour Connect.

Extracted from the WebSocket gateway so the pairing rules can be exercised
directly by Test Suite A: age gating, the three-year age gap, the 15-second
queue timeout, duplicate joins and the queue capacity limit.

The queue holds no FastAPI objects of its own apart from an opaque `ws` handle,
so it can be driven with a fake clock in tests.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

MIN_AGE = 18
MAX_AGE_GAP = 3
QUEUE_TIMEOUT_SECONDS = 15.0
MAX_QUEUE_SIZE = 200

MIN_NICKNAME_LENGTH = 2
MAX_NICKNAME_LENGTH = 16
EARLIEST_BIRTH_YEAR = 1920


class QueueRejected(Exception):
    """A queue_join request the server will not accept.

    `code` is a short machine-readable token the client can switch on;
    `message` is safe to show to the player; `field` names the offending
    form input when there is one.
    """

    def __init__(self, code: str, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field

    def as_payload(self) -> Dict[str, object]:
        return {"code": self.code, "message": self.message, "field": self.field}


@dataclass
class QueueEntry:
    session_id: str
    nickname: str
    birth_year: int
    age: int
    ws: object = None
    queued_at: float = field(default_factory=time.time)

    def as_player(self) -> Dict[str, object]:
        """A room-side copy of this entry (rooms never share the queue row)."""
        return {
            "ws": self.ws,
            "session_id": self.session_id,
            "nickname": self.nickname,
            "age": self.age,
        }


def normalize_profile(payload: Dict[str, object], current_year: int) -> Tuple[str, int, int]:
    """Validate a raw queue_join payload and return (nickname, birth_year, age)."""

    nickname = payload.get("nickname")
    if not isinstance(nickname, str):
        raise QueueRejected("invalid_nickname", "Please enter a nickname.", "nickname")
    nickname = nickname.strip()
    if not (MIN_NICKNAME_LENGTH <= len(nickname) <= MAX_NICKNAME_LENGTH):
        raise QueueRejected(
            "invalid_nickname",
            f"Nickname must be {MIN_NICKNAME_LENGTH}-{MAX_NICKNAME_LENGTH} characters.",
            "nickname",
        )

    birth_year = payload.get("birth_year")
    if isinstance(birth_year, bool) or not isinstance(birth_year, int):
        raise QueueRejected("invalid_birth_year", "Birth year must be a whole number.", "birth_year")
    if birth_year < EARLIEST_BIRTH_YEAR or birth_year > current_year:
        raise QueueRejected("invalid_birth_year", "That birth year is not plausible.", "birth_year")

    age = current_year - birth_year
    if age < MIN_AGE:
        raise QueueRejected(
            "underage",
            f"Users must be {MIN_AGE}+ to enter.",
            "birth_year",
        )

    return nickname, birth_year, age


class MatchmakingQueue:
    """FIFO pool with age filtering, expiry and a hard capacity limit."""

    def __init__(
        self,
        *,
        timeout_seconds: float = QUEUE_TIMEOUT_SECONDS,
        max_age_gap: int = MAX_AGE_GAP,
        max_size: int = MAX_QUEUE_SIZE,
        clock: Callable[[], float] = time.time,
    ):
        self.timeout_seconds = timeout_seconds
        self.max_age_gap = max_age_gap
        self.max_size = max_size
        self._clock = clock
        self._entries: List[QueueEntry] = []

    def __len__(self) -> int:
        return len(self._entries)

    def entries(self) -> List[QueueEntry]:
        return list(self._entries)

    def build_entry(
        self,
        payload: Dict[str, object],
        session_id: str,
        ws: object,
        current_year: int,
    ) -> QueueEntry:
        nickname, birth_year, age = normalize_profile(payload, current_year)
        return QueueEntry(
            session_id=session_id,
            nickname=nickname,
            birth_year=birth_year,
            age=age,
            ws=ws,
            queued_at=self._clock(),
        )

    def add(self, entry: QueueEntry) -> QueueEntry:
        if any(existing.session_id == entry.session_id for existing in self._entries):
            raise QueueRejected("already_queued", "You are already in the queue.")
        if len(self._entries) >= self.max_size:
            raise QueueRejected(
                "queue_full",
                "The queue is full right now. Please try again in a moment.",
            )
        self._entries.append(entry)
        return entry

    def remove(self, session_id: str) -> bool:
        for index, entry in enumerate(self._entries):
            if entry.session_id == session_id:
                del self._entries[index]
                return True
        return False

    def position(self, session_id: str) -> Optional[int]:
        """1-based position in the queue, or None when not queued."""
        for index, entry in enumerate(self._entries):
            if entry.session_id == session_id:
                return index + 1
        return None

    def tick(self, now: Optional[float] = None) -> Tuple[List[Tuple[QueueEntry, QueueEntry]], List[QueueEntry]]:
        """Pair compatible players and expire stale ones in a single pass.

        Returns (pairs, expired). Paired and expired entries are removed from
        the queue, so a player can never be paired after already being routed
        to an AI opponent.
        """
        now = self._clock() if now is None else now
        paired: List[Tuple[QueueEntry, QueueEntry]] = []
        claimed: set = set()

        for index, first in enumerate(self._entries):
            if first.session_id in claimed:
                continue
            for other in self._entries[index + 1:]:
                if other.session_id in claimed:
                    continue
                if abs(first.age - other.age) <= self.max_age_gap:
                    claimed.add(first.session_id)
                    claimed.add(other.session_id)
                    paired.append((first, other))
                    break

        expired = [
            entry
            for entry in self._entries
            if entry.session_id not in claimed and now - entry.queued_at >= self.timeout_seconds
        ]
        for entry in expired:
            claimed.add(entry.session_id)

        if claimed:
            self._entries = [e for e in self._entries if e.session_id not in claimed]

        return paired, expired

    def status(self, session_id: str, now: Optional[float] = None) -> Optional[Dict[str, object]]:
        """The queue_status frame body for one waiting player."""
        now = self._clock() if now is None else now
        for index, entry in enumerate(self._entries):
            if entry.session_id != session_id:
                continue
            elapsed = max(0.0, now - entry.queued_at)
            return {
                "elapsed_seconds": round(elapsed, 1),
                "timeout_seconds": self.timeout_seconds,
                "remaining_seconds": round(max(0.0, self.timeout_seconds - elapsed), 1),
                "position": index + 1,
                "waiting": len(self._entries),
            }
        return None
