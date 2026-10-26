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

DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
DEFAULT_MODEL = "glm-4.5-air"
# Temporary model while GLM-4.7-Flash access is enabled. The live Connect Four
# prompt measured ~2.3–2.9s, so 3.5s leaves margin for provider queueing/jitter.
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


def get_ai_settings() -> AISettings:
    """Build settings from the environment on each call (test-friendly)."""

    default_model = os.getenv("GLM_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    base_url = (
        os.getenv("GLM_BASE_URL", DEFAULT_BASE_URL).strip().rstrip("/")
        or DEFAULT_BASE_URL
    )
    api_key = (os.getenv("GLM_API_KEY") or "").strip() or None

    return AISettings(
        api_key=api_key,
        base_url=base_url,
        default_model=default_model,
        allowed_models=_parse_models(os.getenv("GLM_ALLOWED_MODELS"), default_model),
        timeout_seconds=_parse_timeout(os.getenv("AI_TIMEOUT_SECONDS")),
    )
