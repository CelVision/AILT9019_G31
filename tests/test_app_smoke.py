"""
Smoke tests for the FastAPI gateway and root-level client serving (QW-1).

These tests require the runtime dependencies in server/requirements.txt.
They are skipped automatically when FastAPI/httpx are not installed.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert isinstance(payload["llm_enabled"], bool)
    assert isinstance(payload["llm_model"], str) and payload["llm_model"]


def test_index_is_served_at_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "ConnectFour Connect" in response.text


def test_client_css_and_js_are_served_from_root():
    css = client.get("/css/style.css")
    assert css.status_code == 200
    assert "text/css" in css.headers["content-type"]

    js = client.get("/js/app.js")
    assert js.status_code == 200
    assert "javascript" in js.headers["content-type"]


def test_websocket_route_is_still_registered():
    paths = {getattr(route, "path", "") for route in app.routes}
    assert "/ws/game" in paths
