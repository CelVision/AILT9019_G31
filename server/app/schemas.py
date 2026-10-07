"""
Data models and WebSocket event schemas for ConnectFour Connect.
"""

from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CellState(IntEnum):
    EMPTY = 0
    PLAYER_1 = 1  # Red (typically Human P1)
    PLAYER_2 = 2  # Yellow (Human P2 or Bot)


class GameStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class PlayerSession(BaseModel):
    session_id: str
    nickname: str = Field(..., min_length=2, max_length=16)
    birth_year: int = Field(..., ge=1920, le=2008)  # Enforce age >= 18
    calculated_age: int
    is_bot: bool = False
    connected: bool = True


class ConnectFourRoom(BaseModel):
    room_id: str
    is_pve: bool = False
    player_1: PlayerSession
    player_2: PlayerSession
    current_turn: int = 1  # 1 or 2
    board: List[List[int]] = Field(
        default_factory=lambda: [[0 for _ in range(7)] for _ in range(6)]
    )
    status: GameStatus = GameStatus.IN_PROGRESS
    winner: Optional[int] = None  # 1, 2, 0 (draw), or None
    winning_coordinates: Optional[List[List[int]]] = None
    move_count: int = 0
    turn_deadline_ts: float = 0.0


# WebSocket Protocol Envelope
class WSEvent(BaseModel):
    type: str
    payload: Dict[str, Any] = Field(default_factory=dict)


# AI Response Schema
class AIMoveResponse(BaseModel):
    column: int = Field(..., ge=0, le=6)
    canned_reaction_id: int = Field(default=0, ge=0, le=6)
