"""
Mocked tests for the GLM-4.7-Flash adapter.

No real API key or network access is required: every request goes through an
httpx.MockTransport. Live verification is the standalone smoke test:
    cd server && python -m app.ai.glm_client
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))

import httpx
import pytest

from app.ai.glm_client import GLMError, parse_glm_content, request_glm_move
from app.config import AISettings

EMPTY_BOARD = [[0 for _ in range(7)] for _ in range(6)]
LEGAL = [0, 1, 2, 3, 4, 5, 6]


def settings(api_key: str | None = "test-key", allowed=("glm-4.7-flash",)) -> AISettings:
    return AISettings(
        api_key=api_key,
        base_url="https://glm.example.test/api/paas/v4",
        default_model="glm-4.7-flash",
        allowed_models=allowed,
        timeout_seconds=1.0,
    )


def transport(content: str, status: int = 200, check=None) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        if check is not None:
            check(request)
        return httpx.Response(
            status,
            json={"choices": [{"message": {"content": content}}]},
        )

    return httpx.MockTransport(handler)


def test_parse_valid_json():
    assert parse_glm_content('{"column": 3, "canned_reaction_id": 2}', LEGAL) == (3, 2)


def test_parse_fenced_json_and_default_reaction():
    content = '```json\n{"column": 4}\n```'
    assert parse_glm_content(content, LEGAL) == (4, 0)


def test_parse_rejects_malformed_json():
    with pytest.raises(GLMError) as exc:
        parse_glm_content("I choose column three", LEGAL)
    assert exc.value.reason == "malformed_json"


def test_parse_rejects_illegal_column():
    with pytest.raises(GLMError) as exc:
        parse_glm_content('{"column": 9}', LEGAL)
    assert exc.value.reason == "illegal_column"


def test_request_sends_auth_and_parses_move():
    def check(request: httpx.Request) -> None:
        assert request.url.path.endswith("/chat/completions")
        assert request.headers.get("authorization") == "Bearer test-key"
        body = json.loads(request.read())
        assert body["model"] == "glm-4.7-flash"
        assert body["thinking"] == {"type": "disabled"}

    move = asyncio.run(
        request_glm_move(
            EMPTY_BOARD,
            settings=settings(),
            transport=transport('{"column": 3, "canned_reaction_id": 1}', check=check),
        )
    )
    assert move.column == 3
    assert move.canned_reaction_id == 1
    assert move.latency_ms >= 0


def test_request_requires_api_key():
    with pytest.raises(GLMError) as exc:
        asyncio.run(
            request_glm_move(
                EMPTY_BOARD,
                settings=settings(api_key=None),
                transport=transport('{"column": 3}'),
            )
        )
    assert exc.value.reason == "missing_api_key"


def test_request_rejects_model_outside_allowlist():
    with pytest.raises(GLMError) as exc:
        asyncio.run(
            request_glm_move(
                EMPTY_BOARD,
                model="glm-4-plus",
                settings=settings(),
                transport=transport('{"column": 3}'),
            )
        )
    assert exc.value.reason == "model_not_allowed"


def test_request_http_error_does_not_leak_key():
    with pytest.raises(GLMError) as exc:
        asyncio.run(
            request_glm_move(
                EMPTY_BOARD,
                settings=settings(),
                transport=transport("boom", status=500),
            )
        )
    assert exc.value.reason == "http_500"
    assert "test-key" not in str(exc.value)


def test_request_timeout():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("slow", request=request)

    with pytest.raises(GLMError) as exc:
        asyncio.run(
            request_glm_move(
                EMPTY_BOARD,
                settings=settings(),
                transport=httpx.MockTransport(handler),
            )
        )
    assert exc.value.reason == "timeout"


def test_request_rejects_full_column():
    board = [row[:] for row in EMPTY_BOARD]
    for row in range(6):
        board[row][3] = 1

    with pytest.raises(GLMError) as exc:
        asyncio.run(
            request_glm_move(
                board,
                settings=settings(),
                transport=transport('{"column": 3}'),
            )
        )
    assert exc.value.reason == "illegal_column"
