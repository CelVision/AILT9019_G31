"""Environment-backed application settings.

Secrets are read from the server environment only. For local development the
values may live in ``server/.env`` (ignored by Git); on the VPS they come from
``/etc/connectfour/connectfour.env`` via systemd. Never log or return the key.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

SERVER_DIR = Path(__file__).resolve().parents[1]
load_dotenv(SERVER_DIR / ".env")

DEFAULT_BASE_URL = (
    "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
)
DEFAULT_MODEL = "qwen3.6-flash"
# Live Connect Four probes returned legal moves in roughly 1.4–3.9s, so 3.5s
# keeps the UI responsive without dropping too many provider responses.
DEFAULT_TIMEOUT_SECONDS = 3.5


@dataclass(frozen=True)
class AISettings:
    """Validated AI configuration for the current process."""

    api_key: str | None
    base_url: str
    default_model: str
    allowed_models: tuple[str, ...]
    timeout_seconds: float

    @property
    def enabled(self) -> bool:
        """True only when a key is configured; otherwise PvE must stay local."""
        return bool(self.api_key)

    def is_model_allowed(self, model: str) -> bool:
        return model in self.allowed_models


def _parse_models(raw: str | None, default_model: str) -> tuple[str, ...]:
    models = [item.strip() for item in (raw or "").split(",") if item.strip()]
    if default_model not in models:
        models.insert(0, default_model)
    # Deduplicate while preserving order.
    return tuple(dict.fromkeys(models))


def _parse_timeout(raw: str | None) -> float:
    try:
        value = float(raw) if raw else DEFAULT_TIMEOUT_SECONDS
    except ValueError:
        value = DEFAULT_TIMEOUT_SECONDS
    return min(max(value, 0.5), 10.0)


def _env(name: str, legacy_name: str, default: str = "") -> str:
    """Return the first non-empty value, accepting legacy GLM_* names.

    The GLM_* aliases keep existing local checkouts and VPS environment files
    working while deployments migrate to the provider-neutral AI_* names.
    """

    for key in (name, legacy_name):
        value = os.getenv(key)
        if value is not None and value.strip():
            return value.strip()
    return default


def get_ai_settings() -> AISettings:
    """Build settings from the environment on each call (test-friendly)."""

    default_model = _env("AI_MODEL", "GLM_MODEL", DEFAULT_MODEL)
    base_url = _env("AI_BASE_URL", "GLM_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    api_key = _env("AI_API_KEY", "GLM_API_KEY") or None

    return AISettings(
        api_key=api_key,
        base_url=base_url,
        default_model=default_model,
        allowed_models=_parse_models(
            _env("AI_ALLOWED_MODELS", "GLM_ALLOWED_MODELS"), default_model
        ),
        timeout_seconds=_parse_timeout(os.getenv("AI_TIMEOUT_SECONDS")),
    )
