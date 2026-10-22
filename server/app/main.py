"""
FastAPI Server & WebSocket Gateway for ConnectFour Connect
"""

import asyncio
import json
import os
import time
import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from app.config import get_ai_settings
from app.game_engine import ConnectFourEngine
from app.ai.glm_client import GLMError, request_glm_move, safe_legal_column


app = FastAPI(title="ConnectFour Connect")

# In-memory Matching Queue
# Queue entry: {"ws": WebSocket, "session_id": str, "nickname": str, "birth_year": int, "age": int, "queued_at": float}
matching_pool: List[Dict] = []

# Active Game Rooms
# room_id -> Room Data
active_rooms: Dict[str, Dict] = {}


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

            # 1. Check for compatible human pairs (|ΔAge| <= 3)
            for i in range(len(matching_pool)):
                if i in matched_indices:
                    continue
                user_a = matching_pool[i]

                for j in range(i + 1, len(matching_pool)):
                    if j in matched_indices:
                        continue
                    user_b = matching_pool[j]

                    if abs(user_a["age"] - user_b["age"]) <= 3:
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
                if now - user["queued_at"] >= 15.0:
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
        "turn_start": time.time()
    }
    active_rooms[room_id] = room

    # Notify Player 1
    await manager.send_json(user_a["ws"], "match_found", {
        "room_id": room_id,
        "is_pve": False,
        "assigned_player": 1,
        "opponent_nickname": user_b["nickname"],
        "opponent_age": user_b["age"],
        "turn_duration_seconds": 30
    })

    # Notify Player 2
    await manager.send_json(user_b["ws"], "match_found", {
        "room_id": room_id,
        "is_pve": False,
        "assigned_player": 2,
        "opponent_nickname": user_a["nickname"],
        "opponent_age": user_a["age"],
        "turn_duration_seconds": 30
    })


async def create_pve_match(user: dict):
    room_id = f"rm_{uuid.uuid4().hex[:8]}"
    engine = ConnectFourEngine()

    bot_user = {
        "ws": None,
        "session_id": "bot",
        "nickname": "Gemini Bot",
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
        "turn_start": time.time()
    }
    active_rooms[room_id] = room

    await manager.send_json(user["ws"], "match_found", {
        "room_id": room_id,
        "is_pve": True,
        "assigned_player": 1,
        "opponent_nickname": "Gemini Bot",
        "opponent_age": user["age"],
        "turn_duration_seconds": 30
    })


@app.websocket("/ws/game")
async def websocket_endpoint(websocket: WebSocket):
    session_id = uuid.uuid4().hex
    await manager.connect(session_id, websocket)
    current_room_id: Optional[str] = None

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")
            payload = message.get("payload", {})

            if msg_type == "queue_join":
                nickname = payload.get("nickname", "Guest")[:16]
                birth_year = int(payload.get("birth_year", 2000))
                age = 2026 - birth_year

                if age >= 18:
                    matching_pool.append({
                        "ws": websocket,
                        "session_id": session_id,
                        "nickname": nickname,
                        "birth_year": birth_year,
                        "age": age,
                        "queued_at": time.time()
                    })

            elif msg_type == "player_move":
                # Find player's room
                room = None
                for rid, r in active_rooms.items():
                    if r["p1"]["session_id"] == session_id or (not r["is_pve"] and r["p2"]["session_id"] == session_id):
                        room = r
                        current_room_id = rid
                        break

                if not room:
                    continue

                engine = room["engine"]
                player_num = 1 if room["p1"]["session_id"] == session_id else 2

                if room["current_turn"] != player_num:
                    continue

                col = payload.get("column")
                if col is not None and engine.is_legal_move(col):
                    success, row = engine.drop_token(col, player_num)
                    if success:
                        is_win, win_coords = engine.check_win(row, col)
                        is_draw = engine.is_draw()

                        # Broadcast board update
                        room["current_turn"] = 2 if player_num == 1 else 1
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
                            await manager.send_json(room["p1"]["ws"], "game_over", game_over_payload)
                            if not room["is_pve"]:
                                await manager.send_json(room["p2"]["ws"], "game_over", game_over_payload)
                            del active_rooms[room["room_id"]]
                            continue

                        elif is_draw:
                            game_over_payload = {"winner": 0, "reason": "draw"}
                            await manager.send_json(room["p1"]["ws"], "game_over", game_over_payload)
                            if not room["is_pve"]:
                                await manager.send_json(room["p2"]["ws"], "game_over", game_over_payload)
                            del active_rooms[room["room_id"]]
                            continue

                        # If PvE, trigger AI move
                        if room["is_pve"] and room["current_turn"] == 2:
                            asyncio.create_task(handle_ai_turn(room))

            elif msg_type == "send_reaction":
                category = payload.get("category")
                reaction_id = payload.get("id")

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

    except WebSocketDisconnect:
        manager.disconnect(session_id)
        # Remove from queue if present
        matching_pool[:] = [u for u in matching_pool if u["session_id"] != session_id]

        # Handle active room disconnect
        if current_room_id and current_room_id in active_rooms:
            room = active_rooms.pop(current_room_id, None)
            if room and not room["is_pve"]:
                other_user = room["p2"] if room["p1"]["session_id"] == session_id else room["p1"]
                await manager.send_json(other_user["ws"], "game_over", {
                    "winner": 2 if room["p1"]["session_id"] == session_id else 1,
                    "reason": "opponent_disconnected"
                })


async def handle_ai_turn(room: dict):
    """Execute a GLM PvE move; use a safe center-out move if GLM is unavailable.

    Minimax is deliberately not called here during the GLM-first phase (WP3-3).
    WP3-7 restores it as the real fallback before the checkpoint.
    """
    await asyncio.sleep(0.4)  # Natural human-like pause
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

    if ai_col is None:
        ai_col = safe_legal_column(engine.get_board())
        if fallback_reason and not room.get("fallback_notified"):
            room["fallback_notified"] = True
            await manager.send_json(room["p1"]["ws"], "pve_fallback_notice", {
                "message": f"GLM unavailable ({fallback_reason}); using a safe move."
            })

    if ai_col is None:
        await manager.send_json(room["p1"]["ws"], "game_over", {
            "winner": 0, "reason": "draw"
        })
        active_rooms.pop(room["room_id"], None)
        return

    success, row = engine.drop_token(ai_col, player=2)

    if not success:
        # Defensive: the board changed between validation and drop.
        safe_col = safe_legal_column(engine.get_board())
        if safe_col is None:
            await manager.send_json(room["p1"]["ws"], "game_over", {
                "winner": 0, "reason": "draw"
            })
            active_rooms.pop(room["room_id"], None)
            return
        ai_col = safe_col
        glm_move = None  # The GLM move was not applied; do not send its reaction.
        success, row = engine.drop_token(ai_col, player=2)
        if not success:
            return

    is_win, win_coords = engine.check_win(row, ai_col)
    is_draw = engine.is_draw()

    room["current_turn"] = 1
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
        await manager.send_json(room["p1"]["ws"], "game_over", {
            "winner": 2, "reason": "connect4", "winning_coordinates": win_coords
        })
        active_rooms.pop(room["room_id"], None)
    elif is_draw:
        await manager.send_json(room["p1"]["ws"], "game_over", {
            "winner": 0, "reason": "draw"
        })
        active_rooms.pop(room["room_id"], None)


# Serve the client SPA from the site root so index.html's relative asset paths
# (css/style.css, js/*.js) resolve correctly. This mount MUST stay last:
# Starlette matches routes in registration order, so /api/* and /ws/* defined
# above still take precedence over the static catch-all.
client_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "client"))
if os.path.isdir(client_dir):
    app.mount("/", StaticFiles(directory=client_dir, html=True), name="client")
