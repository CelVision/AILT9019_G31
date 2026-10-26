"""
Unit tests for the conversational chat agent (AI Coach).
"""

import asyncio
import json
import os
import sys
import httpx
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))

from app.config import AISettings
from app.ai.chat_agent import DAILY_TOPICS, SYSTEM_PROMPT, generate_chat_reply


def test_daily_topics_structure():
    assert len(DAILY_TOPICS) >= 4
    for topic in DAILY_TOPICS:
        assert "id" in topic and isinstance(topic["id"], int)
        assert "label" in topic and len(topic["label"]) > 0
        assert "prompt" in topic and len(topic["prompt"]) > 0


def make_settings(api_key: str | None = "sk-test-key") -> AISettings:
    return AISettings(
        api_key=api_key,
        base_url="https://example.com/v1",
        default_model="qwen3.6-flash",
        allowed_models=("qwen3.6-flash",),
        timeout_seconds=3.5,
    )


def test_generate_chat_reply_disabled():
    settings = make_settings(api_key="")
    reply = asyncio.run(generate_chat_reply([], settings=settings))
    assert "focusing on the board" in reply.lower()


def test_generate_chat_reply_success():
    class SuccessTransport(httpx.AsyncBaseTransport):
        def __init__(self):
            self.captured_request = None

        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            self.captured_request = request
            content = json.dumps({
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "I love grab-and-go cold brew from the student union!",
                    }
                }]
            }).encode("utf-8")
            return httpx.Response(200, content=content, request=request)

    transport = SuccessTransport()
    settings = make_settings("sk-test-key")

    history = [
        {"role": "user", "content": "What coffee do you drink?"}
    ]

    reply = asyncio.run(generate_chat_reply(history, settings=settings, transport=transport))
    assert "cold brew" in reply

    # Verify captured payload
    req_body = json.loads(transport.captured_request.content.decode("utf-8"))
    assert req_body["model"] == "qwen3.6-flash"
    assert req_body["messages"][0]["role"] == "system"
    assert req_body["messages"][1]["content"] == "What coffee do you drink?"


def test_generate_chat_reply_sliding_context_window():
    class CapturingTransport(httpx.AsyncBaseTransport):
        def __init__(self):
            self.captured_messages = []

        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content.decode("utf-8"))
            self.captured_messages = body["messages"]
            content = json.dumps({
                "choices": [{"message": {"role": "assistant", "content": "Sounds good!"}}]
            }).encode("utf-8")
            return httpx.Response(200, content=content, request=request)

    transport = CapturingTransport()
    settings = make_settings("sk-test-key")

    # 10 turns of history
    history = [{"role": "user" if i % 2 == 0 else "assistant", "content": f"msg {i}"} for i in range(10)]

    reply = asyncio.run(generate_chat_reply(history, settings=settings, transport=transport))
    assert reply == "Sounds good!"

    # system prompt (1) + last 6 turns = 7 messages total
    assert len(transport.captured_messages) == 7
    assert transport.captured_messages[0]["role"] == "system"
    assert transport.captured_messages[1]["content"] == "msg 4"
    assert transport.captured_messages[-1]["content"] == "msg 9"


def test_generate_chat_reply_server_error_fallback():
    class ErrorTransport(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, content=b'{"error": "Internal Error"}', request=request)

    transport = ErrorTransport()
    settings = make_settings("sk-test-key")

    reply = asyncio.run(generate_chat_reply([{"role": "user", "content": "Hi"}], settings=settings, transport=transport))
    assert "good game" in reply.lower()
