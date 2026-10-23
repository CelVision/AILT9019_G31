"""Check an application origin without creating players or calling an LLM.

Usage: python deploy/check_public_url.py https://game.example.org
Dependencies: server/requirements.txt. HTTPS certificates are verified.
"""

import argparse
import asyncio
from urllib.parse import urlsplit

import httpx
from websockets import connect


ASSETS = (
    ("/", "text/html"),
    ("/css/style.css", "text/css"),
    ("/js/app.js", "javascript"),
    ("/js/game_board.js", "javascript"),
    ("/js/socket_client.js", "javascript"),
    ("/js/canned_chat.js", "javascript"),
)


def normalize_origin(value: str) -> tuple[str, str]:
    """Accept only an origin, so HTTP and WebSocket check the same endpoint."""
    parts = urlsplit(value)
    if (
        parts.scheme not in {"http", "https"}
        or not parts.hostname
        or parts.username is not None
        or parts.password is not None
        or parts.path not in {"", "/"}
        or parts.query
        or parts.fragment
        or "?" in value
        or "#" in value
        or any(char.isspace() for char in value)
    ):
        raise ValueError("Supply an http:// or https:// origin without credentials or a path")
    # Accessing port also validates malformed/out-of-range ports.
    if parts.port is not None and parts.port == 0:
        raise ValueError("Port must be between 1 and 65535")
    origin = f"{parts.scheme}://{parts.netloc}"
    ws_scheme = "wss" if parts.scheme == "https" else "ws"
    return origin, f"{ws_scheme}://{parts.netloc}/ws/game"


async def check_origin(value: str, timeout: float = 10.0) -> list[str]:
    if timeout <= 0:
        raise ValueError("Timeout must be positive")
    origin, ws_url = normalize_origin(value)
    passed = []
    # Redirects fail deliberately: check the final origin rather than letting
    # HTML redirect to HTTPS while the WebSocket still probes another origin.
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
        response = await client.get(f"{origin}/api/health")
        response.raise_for_status()
        if response.json().get("status") != "healthy":
            raise ValueError("Health endpoint did not report healthy")
        passed.append("/api/health")
        for path, content_type in ASSETS:
            response = await client.get(f"{origin}{path}")
            response.raise_for_status()
            if content_type not in response.headers.get("content-type", "").lower():
                raise ValueError(f"Unexpected content type for {path}")
            if not response.content:
                raise ValueError(f"Empty response for {path}")
            passed.append(path)
    async with connect(ws_url, open_timeout=timeout, close_timeout=timeout) as socket:
        pong = await socket.ping()
        await asyncio.wait_for(pong, timeout=timeout)
    passed.append("/ws/game (upgrade and ping/pong)")
    return passed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Final HTTP or HTTPS origin; no path or credentials")
    parser.add_argument("--timeout", type=float, default=10.0, help="Per-operation timeout in seconds")
    args = parser.parse_args()
    try:
        results = asyncio.run(check_origin(args.url, args.timeout))
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}")
        return 1
    for result in results:
        print(f"PASS {result}")
    print("Checks passed. This verifies delivery and connectivity, not a complete game or accessibility audit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
