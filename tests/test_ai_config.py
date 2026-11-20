"""Tests for provider-neutral AI settings and legacy GLM_* migration."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))

from app.config import (  # noqa: E402
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    get_ai_settings,
)

ENV_NAMES = (
    "AI_API_KEY",
    "AI_BASE_URL",
    "AI_MODEL",
    "AI_ALLOWED_MODELS",
    "GLM_API_KEY",
    "GLM_BASE_URL",
    "GLM_MODEL",
    "GLM_ALLOWED_MODELS",
)


def clear_ai_env(monkeypatch) -> None:
    for name in ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def test_defaults_target_bailian_qwen(monkeypatch):
    clear_ai_env(monkeypatch)

    settings = get_ai_settings()

    assert settings.api_key is None
    assert settings.base_url == DEFAULT_BASE_URL
    assert settings.default_model == DEFAULT_MODEL == "qwen3.6-flash"
    assert settings.allowed_models == ("qwen3.6-flash",)


def test_ai_env_names_take_precedence(monkeypatch):
    clear_ai_env(monkeypatch)
    monkeypatch.setenv("AI_API_KEY", "new-key")
    monkeypatch.setenv("AI_BASE_URL", "https://new.example.test/v1")
    monkeypatch.setenv("AI_MODEL", "new-model")
    monkeypatch.setenv("AI_ALLOWED_MODELS", "new-model, alternate-model")
    monkeypatch.setenv("GLM_API_KEY", "old-key")
    monkeypatch.setenv("GLM_BASE_URL", "https://old.example.test/v1")
    monkeypatch.setenv("GLM_MODEL", "old-model")

    settings = get_ai_settings()

    assert settings.api_key == "new-key"
    assert settings.base_url == "https://new.example.test/v1"
    assert settings.default_model == "new-model"
    assert settings.allowed_models == ("new-model", "alternate-model")


def test_legacy_glm_env_names_remain_supported(monkeypatch):
    clear_ai_env(monkeypatch)
    monkeypatch.setenv("GLM_API_KEY", "legacy-key")
    monkeypatch.setenv("GLM_BASE_URL", "https://legacy.example.test/v1/")
    monkeypatch.setenv("GLM_MODEL", "legacy-model")
    monkeypatch.setenv("GLM_ALLOWED_MODELS", "legacy-model, fallback-model")

    settings = get_ai_settings()

    assert settings.api_key == "legacy-key"
    assert settings.base_url == "https://legacy.example.test/v1"
    assert settings.default_model == "legacy-model"
    assert settings.allowed_models == ("legacy-model", "fallback-model")
