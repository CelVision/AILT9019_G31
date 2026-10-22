"""GLM-4-Flash client for the PvE opponent.

The provider exposes an OpenAI-compatible ``/chat/completions`` endpoint. This
module keeps the network call, prompt, parsing, and validation in one place so
the WebSocket gateway (WP3-3) only has to ask for a move.

Security: the API key is read from :mod:`app.config` and is only ever placed in
the outbound Authorization header. It is never logged, returned, or included in
an exception message.
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any, List

import httpx

from app.config import AISettings, get_ai_settings

ROWS = 6
COLS = 7

SYSTEM_PROMPT = (
    "You are playing Connect Four on a 7-column by 6-row board. "
    "The board is a JSON matrix: 0 is empty, 1 is the human (Red), and 2 is you "
    "(Yellow). Row 0 is the top row; gravity means tokens fall to the highest "
    "numbered empty row in the chosen column. "
    "Choose the strategically best legal column: win if possible, otherwise "
    "block the opponent's immediate win. "
    'Respond with ONLY a JSON object of the form '
    '{"column": <integer 0-6>, "canned_reaction_id": <integer 0-6>}. '
    "Use 0 for no reaction. Do not include markdown or any other text."
)


class GLMError(RuntimeError):
    """A non-secret failure reason that the gateway can surface or log."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


@dataclass(frozen=True)
class GLMMove:
    column: int
    canned_reaction_id: int
    latency_ms: float


def legal_columns(board: List[List[int]]) -> List[int]:
    """Return columns whose top cell is empty, ordered center-out."""
    preferred = [3, 2, 4, 1, 5, 0, 6]
    return [col for col in preferred if board[0][col] == 0]


def safe_legal_column(board: List[List[int]]) -> int | None:
    """Temporary GLM-outage move: first legal column center-out.

    This is intentionally not Minimax. It keeps the room playable while GLM is
    being validated; WP3-7 replaces it with the real fallback.
    """
    legal = legal_columns(board)
    return legal[0] if legal else None


def _extract_json_object(content: str) -> dict[str, Any]:
    text = (content or "").strip()
    if text.startswith("```"):
        # Tolerate ```json ... ``` or ``` ... ``` wrappers.
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
        text = text.strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise GLMError("malformed_json")

    try:
        parsed = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise GLMError("malformed_json") from exc

    if not isinstance(parsed, dict):
        raise GLMError("malformed_json")
    return parsed


def parse_glm_content(content: str, legal: List[int]) -> tuple[int, int]:
    """Validate the model's JSON payload against the live board."""

    parsed = _extract_json_object(content)

    column = parsed.get("column")
    if isinstance(column, bool) or not isinstance(column, int):
        raise GLMError("invalid_column")
    if column not in legal:
        raise GLMError("illegal_column")

    reaction = parsed.get("canned_reaction_id", 0)
    if isinstance(reaction, bool) or not isinstance(reaction, int) or not 0 <= reaction <= 6:
        reaction = 0

    return column, reaction


def build_messages(board: List[List[int]], legal: List[int]) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": json.dumps(
                {
                    "board": board,
                    "legal_columns": legal,
                    "your_token": 2,
                    "opponent_token": 1,
                }
            ),
        },
    ]


async def request_glm_move(
    board: List[List[int]],
    model: str | None = None,
    *,
    settings: AISettings | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> GLMMove:
    """Ask GLM for one move.

    ``transport`` is injectable so tests can exercise the full parse/validate
    path without a network call or a real key.
    """

    cfg = settings or get_ai_settings()
    selected_model = model or cfg.default_model

    if not cfg.enabled:
        raise GLMError("missing_api_key")
    if not cfg.is_model_allowed(selected_model):
        raise GLMError("model_not_allowed")

    legal = legal_columns(board)
    if not legal:
        raise GLMError("no_legal_moves")

    payload = {
        "model": selected_model,
        "messages": build_messages(board, legal),
        "temperature": 0.2,
        "max_tokens": 64,
        "stream": False,
    }
    url = f"{cfg.base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }

    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(
            timeout=cfg.timeout_seconds, transport=transport
        ) as client:
            response = await client.post(url, headers=headers, json=payload)
    except httpx.TimeoutException as exc:
        raise GLMError("timeout") from exc
    except httpx.HTTPError as exc:
        raise GLMError("network_error") from exc

    if response.status_code >= 400:
        # Deliberately do not include the response body: it may contain
        # provider-side request details we do not want in logs.
        raise GLMError(f"http_{response.status_code}")

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise GLMError("bad_response") from exc

    if not isinstance(content, str):
        raise GLMError("bad_response")

    column, reaction = parse_glm_content(content, legal)
    latency_ms = (time.perf_counter() - started) * 1000
    return GLMMove(
        column=column,
        canned_reaction_id=reaction,
        latency_ms=latency_ms,
    )


def _main() -> None:
    """Standalone smoke test: ``python -m app.ai.glm_client`` from server/."""

    cfg = get_ai_settings()
    if not cfg.enabled:
        raise SystemExit(
            "GLM_API_KEY is not set. Copy server/.env.example to server/.env "
            "and add the key (never commit it)."
        )

    empty_board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    try:
        move = asyncio.run(request_glm_move(empty_board, settings=cfg))
    except GLMError as exc:
        raise SystemExit(f"GLM smoke test failed: {exc.reason}") from exc

    print(
        json.dumps(
            {
                "column": move.column,
                "canned_reaction_id": move.canned_reaction_id,
                "latency_ms": round(move.latency_ms, 1),
                "model": cfg.default_model,
            }
        )
    )


if __name__ == "__main__":
    _main()
