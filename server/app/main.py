"""
FastAPI Server & WebSocket Gateway for ConnectFour Connect
"""

import asyncio
import json
import os
import time
import uuid
from datetime import date
from typing import Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from app.config import get_ai_settings
from app.game_engine import ConnectFourEngine
from app.ai.glm_client import GLMError, request_glm_move, safe_legal_column
from app.ai.minimax_fallback import get_minimax_move


app = FastAPI(title="ConnectFour Connect")

CURRENT_YEAR = date.today().year
MIN_BIRTH_YEAR = 1920
MIN_NICKNAME_LENGTH = 2
MAX_NICKNAME_LENGTH = 16
QUEUE_TIMEOUT_SECONDS = 15
TURN_DURATION_SECONDS = 30

# In-memory Matching Queue
# Queue entry: {"ws": WebSocket, "session_id": str, "nickname": str, "birth_year": int, "age": int, "queued_at": float}
matching_pool: List[Dict] = []

# Active Game Rooms
# room_id -> Room Data
active_rooms: Dict[str, Dict] = {}
# Finished rooms are retained briefly so both PvP players can request a
# rematch without entering the general matchmaking queue again.
finished_rooms: Dict[str, Dict] = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_json(self, websocket: WebSocket, msg_type: str, payload: dict):
        try:
            await websocket.send_text(json.dumps({"type": msg_type, "payload": payload}))
        except Exception:
            pass


manager = ConnectionManager()


def protocol_error(code: str, message: str, field: str | None = None) -> dict:
    payload = {"code": code, "message": message}
    if field:
        payload["field"] = field
    return payload


def validate_registration(payload: dict) -> tuple[dict | None, dict | None]:
    """Validate the public registration fields before queueing a player."""
    nickname = payload.get("nickname")
    if not isinstance(nickname, str):
        return None, protocol_error("invalid_nickname", "Nickname must be 2–16 characters.", "nickname")
    nickname = nickname.strip()
    if not MIN_NICKNAME_LENGTH <= len(nickname) <= MAX_NICKNAME_LENGTH:
        return None, protocol_error("invalid_nickname", "Nickname must be 2–16 characters.", "nickname")

    birth_year = payload.get("birth_year")
    if isinstance(birth_year, bool):
        birth_year = None
    try:
        birth_year = int(birth_year)
    except (TypeError, ValueError):
        birth_year = None
    latest_valid_birth_year = CURRENT_YEAR - 18
    if birth_year is None or not MIN_BIRTH_YEAR <= birth_year <= latest_valid_birth_year:
        return None, protocol_error(
            "invalid_birth_year",
            f"Birth year must be between {MIN_BIRTH_YEAR} and {latest_valid_birth_year} (18+).",
            "birth_year",
        )

    return {
        "nickname": nickname,
        "birth_year": birth_year,
        "age": CURRENT_YEAR - birth_year,
    }, None


def ages_compatible(age_a: int, age_b: int) -> bool:
    return abs(age_a - age_b) <= 3


async def send_room_event(room: dict, msg_type: str, payload: dict) -> None:
    """Send one event to every connected human in a room."""
    await manager.send_json(room["p1"]["ws"], msg_type, payload)
    if not room["is_pve"]:
        await manager.send_json(room["p2"]["ws"], msg_type, payload)


def remember_finished_room(room: dict) -> None:
    finished_rooms[room["room_id"]] = {
        "room_id": room["room_id"],
        "is_pve": room["is_pve"],
        "p1": room["p1"],
        "p2": room["p2"],
        "rematch_requests": set(),
        "finished_at": time.time(),
    }


async def finish_room(room: dict, payload: dict) -> None:
    """Notify players, remove live state, and retain a short rematch record."""
    if active_rooms.get(room["room_id"]) is not room:
        return
    active_rooms.pop(room["room_id"], None)
    room["ended"] = True
    remember_finished_room(room)
    await send_room_event(room, "game_over", payload)


async def expire_turn(room: dict) -> None:
    winner = 2 if room["current_turn"] == 1 else 1
    await finish_room(
        room,
        {
            "winner": winner,
            "reason": "turn_timeout",
            "timed_out_player": room["current_turn"],
        },
    )


def find_room_for_session(session_id: str) -> tuple[str | None, dict | None]:
    for room_id, room in active_rooms.items():
        if room["p1"]["session_id"] == session_id:
            return room_id, room
        if not room["is_pve"] and room["p2"]["session_id"] == session_id:
            return room_id, room
    return None, None


@app.get("/api/health")
async def health_check():
    ai = get_ai_settings()
    return {
        "status": "healthy",
        "active_rooms": len(active_rooms),
        "queued_users": len(matching_pool),
        # Never return the key. These two fields are safe for operators.
        "llm_enabled": ai.enabled,
        "llm_model": ai.default_model,
    }


# Matchmaking Background Task
async def matchmaking_worker():
    while True:
        try:
            now = time.time()
            matched_indices = set()

            # Publish authoritative queue progress once per second. The
            # browser may render a local countdown, but this keeps it in sync
            # with the server's actual queue clock.
            for user in list(matching_pool):
                if now - user.get("last_status_at", 0) >= 1.0:
                    elapsed = min(QUEUE_TIMEOUT_SECONDS, int(now - user["queued_at"]))
                    await manager.send_json(user["ws"], "queue_status", {
                        "status": "searching",
                        "elapsed_seconds": elapsed,
                        "timeout_seconds": QUEUE_TIMEOUT_SECONDS,
                    })
                    user["last_status_at"] = now

            # 1. Check for compatible human pairs (|ΔAge| <= 3)
            for i in range(len(matching_pool)):
                if i in matched_indices:
                    continue
                user_a = matching_pool[i]

                for j in range(i + 1, len(matching_pool)):
                    if j in matched_indices:
                        continue
                    user_b = matching_pool[j]

                    if ages_compatible(user_a["age"], user_b["age"]):
                        # Found compatible human pair!
                        matched_indices.add(i)
                        matched_indices.add(j)
                        asyncio.create_task(create_pvp_match(user_a, user_b))
                        break

            # 2. Check for 15s queue timeouts -> Route to PvE
            for k in range(len(matching_pool)):
                if k in matched_indices:
                    continue
                user = matching_pool[k]
                if now - user["queued_at"] >= QUEUE_TIMEOUT_SECONDS:
                    matched_indices.add(k)
                    asyncio.create_task(create_pve_match(user))

            # Remove matched or timed-out users from pool
            if matched_indices:
                remaining = [
                    matching_pool[idx]
                    for idx in range(len(matching_pool))
                    if idx not in matched_indices
                ]
                matching_pool.clear()
                matching_pool.extend(remaining)

            # Enforce the turn deadline on the server. A client-side timer is
            # only a visual aid and cannot be trusted to end a stalled turn.
            for room in list(active_rooms.values()):
                if now - room["turn_start"] >= TURN_DURATION_SECONDS:
                    await expire_turn(room)

            # Avoid retaining completed room metadata forever.
            for room_id, room in list(finished_rooms.items()):
                if now - room["finished_at"] >= 300:
                    finished_rooms.pop(room_id, None)

        except Exception as e:
            print("Matchmaking error:", e)

        await asyncio.sleep(0.5)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(matchmaking_worker())


async def create_pvp_match(user_a: dict, user_b: dict):
    room_id = f"rm_{uuid.uuid4().hex[:8]}"
    engine = ConnectFourEngine()

    room = {
        "room_id": room_id,
        "is_pve": False,
        "engine": engine,
        "p1": user_a,
        "p2": user_b,
        "current_turn": 1,
        "turn_start": time.time(),
    }
    active_rooms[room_id] = room

    # Notify Player 1
    await manager.send_json(user_a["ws"], "match_found", {
        "room_id": room_id,
        "is_pve": False,
        "assigned_player": 1,
        "opponent_nickname": user_b["nickname"],
        "opponent_age": user_b["age"],
        "turn_duration_seconds": TURN_DURATION_SECONDS
    })

    # Notify Player 2
    await manager.send_json(user_b["ws"], "match_found", {
        "room_id": room_id,
        "is_pve": False,
        "assigned_player": 2,
        "opponent_nickname": user_a["nickname"],
        "opponent_age": user_a["age"],
        "turn_duration_seconds": TURN_DURATION_SECONDS
    })


async def create_pve_match(user: dict):
    room_id = f"rm_{uuid.uuid4().hex[:8]}"
    engine = ConnectFourEngine()

    bot_user = {
        "ws": None,
        "session_id": "bot",
        "nickname": "GLM Bot",
        "age": user["age"],
        "is_bot": True
    }

    room = {
        "room_id": room_id,
        "is_pve": True,
        "engine": engine,
        "p1": user,
        "p2": bot_user,
        "current_turn": 1,
        "turn_start": time.time(),
    }
    active_rooms[room_id] = room

    await manager.send_json(user["ws"], "match_found", {
        "room_id": room_id,
        "is_pve": True,
        "assigned_player": 1,
        "opponent_nickname": "GLM Bot",
        "opponent_age": user["age"],
        "turn_duration_seconds": TURN_DURATION_SECONDS
    })


@app.websocket("/ws/game")
async def websocket_endpoint(websocket: WebSocket):
    session_id = uuid.uuid4().hex
    await manager.connect(session_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except (TypeError, json.JSONDecodeError):
                await manager.send_json(
                    websocket,
                    "error",
                    protocol_error("invalid_json", "Message must be valid JSON."),
                )
                continue

            if not isinstance(message, dict):
                await manager.send_json(
                    websocket,
                    "error",
                    protocol_error("invalid_message", "Message must be a JSON object."),
                )
                continue
            msg_type = message.get("type")
            payload = message.get("payload", {})
            if not isinstance(payload, dict):
                await manager.send_json(
                    websocket,
                    "error",
                    protocol_error("invalid_payload", "Payload must be a JSON object."),
                )
                continue

            if msg_type == "queue_join":
                registration, error = validate_registration(payload)
                if error:
                    await manager.send_json(websocket, "error", error)
                    continue

                # A browser can retry after a reconnect; do not enqueue the
                # same socket twice.
                matching_pool[:] = [
                    user for user in matching_pool if user["session_id"] != session_id
                ]
                user = {
                    "ws": websocket,
                    "session_id": session_id,
                    **registration,
                    "queued_at": time.time(),
                    "last_status_at": 0.0,
                }
                matching_pool.append(user)
                await manager.send_json(websocket, "queue_status", {
                    "status": "searching",
                    "elapsed_seconds": 0,
                    "timeout_seconds": QUEUE_TIMEOUT_SECONDS,
                })

            elif msg_type == "player_move":
                # Find player's room
                room_id, room = find_room_for_session(session_id)

                if not room:
                    continue

                engine = room["engine"]
                player_num = 1 if room["p1"]["session_id"] == session_id else 2

                if room["current_turn"] != player_num:
                    continue

                if time.time() - room["turn_start"] >= TURN_DURATION_SECONDS:
                    await expire_turn(room)
                    continue

                col = payload.get("column")
                if isinstance(col, bool) or not isinstance(col, int):
                    await manager.send_json(
                        websocket,
                        "error",
                        protocol_error("invalid_column", "Column must be an integer from 0 to 6.", "column"),
                    )
                    continue
                if engine.is_legal_move(col):
                    success, row = engine.drop_token(col, player_num)
                    if success:
                        is_win, win_coords = engine.check_win(row, col)
                        is_draw = engine.is_draw()

                        # Broadcast board update
                        room["current_turn"] = 2 if player_num == 1 else 1
                        room["turn_start"] = time.time()
                        update_payload = {
                            "board": engine.get_board(),
                            "last_move": {"player": player_num, "row": row, "column": col},
                            "current_turn": room["current_turn"]
                        }
                        await manager.send_json(room["p1"]["ws"], "board_update", update_payload)
                        if not room["is_pve"]:
                            await manager.send_json(room["p2"]["ws"], "board_update", update_payload)

                        if is_win:
                            game_over_payload = {
                                "winner": player_num,
                                "reason": "connect4",
                                "winning_coordinates": win_coords
                            }
                            await finish_room(room, game_over_payload)
                            continue

                        elif is_draw:
                            game_over_payload = {"winner": 0, "reason": "draw"}
                            await finish_room(room, game_over_payload)
                            continue

                        # If PvE, trigger AI move
                        if room["is_pve"] and room["current_turn"] == 2:
                            asyncio.create_task(handle_ai_turn(room))

                else:
                    await manager.send_json(
                        websocket,
                        "error",
                        protocol_error("illegal_column", "That column is full or outside the board.", "column"),
                    )

            elif msg_type == "send_reaction":
                category = payload.get("category")
                reaction_id = payload.get("id")
                valid_range = (
                    category == "phrase" and isinstance(reaction_id, int) and not isinstance(reaction_id, bool) and 1 <= reaction_id <= 6
                ) or (
                    category == "sticker" and isinstance(reaction_id, int) and not isinstance(reaction_id, bool) and 1 <= reaction_id <= 4
                )
                if not valid_range:
                    await manager.send_json(
                        websocket,
                        "error",
                        protocol_error("invalid_reaction", "Choose one of the available phrases or stickers."),
                    )
                    continue

                for rid, r in active_rooms.items():
                    if r["p1"]["session_id"] == session_id or (not r["is_pve"] and r["p2"]["session_id"] == session_id):
                        sender_num = 1 if r["p1"]["session_id"] == session_id else 2
                        reaction_payload = {
                            "from_player": sender_num,
                            "category": category,
                            "id": reaction_id
                        }
                        # Broadcast to opponent
                        if sender_num == 1 and not r["is_pve"]:
                            await manager.send_json(r["p2"]["ws"], "broadcast_reaction", reaction_payload)
                        elif sender_num == 2:
                            await manager.send_json(r["p1"]["ws"], "broadcast_reaction", reaction_payload)
                        break

            elif msg_type == "rematch_request":
                finished = next(
                    (
                        room for room in finished_rooms.values()
                        if room["p1"]["session_id"] == session_id
                        or (not room["is_pve"] and room["p2"]["session_id"] == session_id)
                    ),
                    None,
                )
                if not finished:
                    await manager.send_json(
                        websocket,
                        "error",
                        protocol_error("rematch_unavailable", "This match is no longer available for rematch."),
                    )
                    continue

                if finished["is_pve"]:
                    finished_rooms.pop(finished["room_id"], None)
                    await create_pve_match(finished["p1"])
                else:
                    finished["rematch_requests"].add(session_id)
                    if len(finished["rematch_requests"]) == 2:
                        finished_rooms.pop(finished["room_id"], None)
                        await create_pvp_match(finished["p1"], finished["p2"])
                    else:
                        await manager.send_json(websocket, "rematch_waiting", {
                            "message": "Waiting for your opponent to accept the rematch."
                        })

    except WebSocketDisconnect:
        manager.disconnect(session_id)
        # Remove from queue if present
        matching_pool[:] = [u for u in matching_pool if u["session_id"] != session_id]

        # Handle active room disconnect. Look it up by session so a rematch
        # created before the socket closes is cleaned up correctly as well.
        _, room = find_room_for_session(session_id)
        if room:
            await finish_room(room, {
                "winner": 2 if room["p1"]["session_id"] == session_id else 1,
                "reason": "opponent_disconnected",
            })


async def handle_ai_turn(room: dict):
    """Execute a GLM PvE move and fall back to the local Minimax bot."""
    await asyncio.sleep(0.4)  # Natural human-like pause
    if room.get("ended"):
        return
    engine = room["engine"]
    settings = get_ai_settings()

    ai_col = None
    glm_move = None
    fallback_reason = None

    try:
        glm_move = await asyncio.wait_for(
            request_glm_move(engine.get_board(), settings=settings),
            timeout=settings.timeout_seconds,
        )
        ai_col = glm_move.column
    except asyncio.TimeoutError:
        fallback_reason = "timeout"
    except GLMError as exc:
        fallback_reason = exc.reason
    except Exception:
        fallback_reason = "unexpected_error"

    if room.get("ended") or (
        room["room_id"] in active_rooms and active_rooms[room["room_id"]] is not room
    ):
        return

    if ai_col is None:
        try:
            ai_col = get_minimax_move(engine.get_board(), depth=4, bot_piece=2)
        except Exception:
            # Minimax is deterministic and local, but the safe move keeps the
            # room playable even if a future heuristic change raises.
            ai_col = safe_legal_column(engine.get_board())
        if fallback_reason and not room.get("fallback_notified"):
            room["fallback_notified"] = True
            await manager.send_json(room["p1"]["ws"], "pve_fallback_notice", {
                "message": f"GLM unavailable ({fallback_reason}); using the local Minimax bot."
            })

    if ai_col is None:
        await finish_room(room, {"winner": 0, "reason": "draw"})
        return

    success, row = engine.drop_token(ai_col, player=2)

    if not success:
        # Defensive: the board changed between validation and drop.
        safe_col = safe_legal_column(engine.get_board())
        if safe_col is None:
            await finish_room(room, {"winner": 0, "reason": "draw"})
            return
        ai_col = safe_col
        glm_move = None  # The GLM move was not applied; do not send its reaction.
        success, row = engine.drop_token(ai_col, player=2)
        if not success:
            return

    is_win, win_coords = engine.check_win(row, ai_col)
    is_draw = engine.is_draw()

    room["current_turn"] = 1
    room["turn_start"] = time.time()
    update_payload = {
        "board": engine.get_board(),
        "last_move": {"player": 2, "row": row, "column": ai_col},
        "current_turn": 1
    }
    await manager.send_json(room["p1"]["ws"], "board_update", update_payload)

    if glm_move and glm_move.canned_reaction_id and not is_win:
        await manager.send_json(room["p1"]["ws"], "broadcast_reaction", {
            "from_player": 2,
            "category": "phrase",
            "id": glm_move.canned_reaction_id,
        })

    if is_win:
        await manager.send_json(room["p1"]["ws"], "broadcast_reaction", {
            "from_player": 2, "category": "phrase", "id": 5  # "Well played!"
        })
        await finish_room(room, {
            "winner": 2, "reason": "connect4", "winning_coordinates": win_coords
        })
    elif is_draw:
        await finish_room(room, {"winner": 0, "reason": "draw"})


# Serve the client SPA from the site root so index.html's relative asset paths
# (css/style.css, js/*.js) resolve correctly. This mount MUST stay last:
# Starlette matches routes in registration order, so /api/* and /ws/* defined
# above still take precedence over the static catch-all.
client_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "client"))
if os.path.isdir(client_dir):
    app.mount("/", StaticFiles(directory=client_dir, html=True), name="client")
