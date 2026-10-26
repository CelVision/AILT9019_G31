"""
Conversational Chat Agent for ConnectFour Connect (AI Companion / Daily Banter).
Uses the OpenAI-compatible Bailian / GLM endpoint for friendly collegiate banter.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import List, Dict, Any

import httpx

from app.config import AISettings, get_ai_settings

SYSTEM_PROMPT = (
    "You are AI Coach, a friendly, encouraging university student classmate playing Connect Four. "
    "You enjoy friendly banter, discussing daily campus life, study habits, exams, coffee, food, "
    "and Connect Four strategy. Keep your answers concise (under 60 words), casual, warm, and positive. "
    "Never ask for or share real-world personal contact information (no emails, phone numbers, social media), "
    "and politely deflect any inappropriate or non-collegiate topics. Always stay in character as a supportive student peer."
)

DAILY_TOPICS = [
    {"id": 1, "label": "☕ Coffee or Tea?", "prompt": "What is your go-to drink before morning classes?"},
    {"id": 2, "label": "📚 Midterm Prep", "prompt": "How is your midterm revision going this week?"},
    {"id": 3, "label": "🍕 Campus Food", "prompt": "What's the best cheap food spot near campus?"},
    {"id": 4, "label": "🎧 Study Music", "prompt": "Do you listen to music or prefer silence when studying?"},
]


async def generate_chat_reply(
    chat_history: List[Dict[str, str]],
    model: str | None = None,
    *,
    settings: AISettings | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> str:
    """
    Generates a conversational response from the AI companion.
    """
    cfg = settings or get_ai_settings()
    if not cfg.enabled:
        return "I'm focusing on the board right now! Nice move!"

    selected_model = model or cfg.default_model

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # Add up to 6 previous turns of context
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": selected_model,
        "messages": messages,
        "max_tokens": 150,
        "temperature": 0.7,
    }

    url = f"{cfg.base_url}/chat/completions"

    client_kwargs: Dict[str, Any] = {"timeout": cfg.timeout_seconds}
    if transport is not None:
        client_kwargs["transport"] = transport

    try:
        async with httpx.AsyncClient(**client_kwargs) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                reply = data["choices"][0]["message"]["content"].strip()
                return reply
            else:
                return "Good game! Let's see your next token drop!"
    except Exception:
        return "Thinking about my next move here! Good luck!"
