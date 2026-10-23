"""Failure-path tests for the operator-facing HTTP/WebSocket deployment check."""

import asyncio
import importlib.util
from pathlib import Path

import httpx
import pytest


spec = importlib.util.spec_from_file_location(
    "deployment_check", Path(__file__).resolve().parents[1] / "deploy/check_public_url.py"
)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


@pytest.mark.parametrize("value", [
    "file:///tmp/game", "https://", "https://user:password@example.org",
    "https://example.org/game", "https://example.org?secret=value",
    "https://example.org#section", "http://localhost:0", "http://localhost:70000",
])
def test_rejects_non_origins(value):
    with pytest.raises(ValueError):
        checker.normalize_origin(value)


def test_https_uses_wss_and_preserves_port():
    assert checker.normalize_origin("https://example.org:8443/") == (
        "https://example.org:8443", "wss://example.org:8443/ws/game"
    )


def mock_endpoints(monkeypatch, *, bad_path=None, status=200, media=None, health="healthy", pong=True):
    requested = []
    connections = []

    def handler(request):
        path = request.url.path
        requested.append(path)
        if path == "/api/health":
            return httpx.Response(200, json={"status": health})
        expected = dict(checker.ASSETS)[path]
        return httpx.Response(
            status if path == bad_path else 200,
            headers={"content-type": media if path == bad_path and media else expected},
            content="asset",
        )

    real_client = httpx.AsyncClient
    monkeypatch.setattr(checker.httpx, "AsyncClient", lambda **kwargs: real_client(
        transport=httpx.MockTransport(handler), **kwargs
    ))

    class FakeSocket:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            pass

        async def ping(self):
            future = asyncio.get_running_loop().create_future()
            if pong:
                future.set_result(None)
            return future

    def connect(url, **kwargs):
        connections.append(url)
        return FakeSocket()

    monkeypatch.setattr(checker, "connect", connect)
    return requested, connections


def test_checks_all_assets_and_secure_websocket(monkeypatch):
    requested, connections = mock_endpoints(monkeypatch)
    result = asyncio.run(checker.check_origin("https://example.org"))
    assert requested == ["/api/health"] + [path for path, _ in checker.ASSETS]
    assert connections == ["wss://example.org/ws/game"]
    assert len(result) == 8


@pytest.mark.parametrize("status", [301, 404, 500])
def test_rejects_redirects_and_missing_assets(monkeypatch, status):
    _, connections = mock_endpoints(monkeypatch, bad_path="/js/app.js", status=status)
    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(checker.check_origin("http://localhost:8000"))
    assert connections == []


def test_detects_html_served_instead_of_javascript(monkeypatch):
    mock_endpoints(monkeypatch, bad_path="/js/app.js", media="text/html")
    with pytest.raises(ValueError, match="content type"):
        asyncio.run(checker.check_origin("http://localhost:8000"))


def test_rejects_unhealthy_service(monkeypatch):
    mock_endpoints(monkeypatch, health="unhealthy")
    with pytest.raises(ValueError, match="healthy"):
        asyncio.run(checker.check_origin("http://localhost:8000"))


def test_fails_if_websocket_does_not_pong(monkeypatch):
    mock_endpoints(monkeypatch, pong=False)
    with pytest.raises(asyncio.TimeoutError):
        asyncio.run(checker.check_origin("http://localhost:8000", timeout=0.01))
