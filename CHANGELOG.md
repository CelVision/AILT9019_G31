# Changelog

This changelog records repository-backed changes to ConnectFour Connect. It distinguishes code on `main` from work that was later reverted. Dates use Hong Kong time. No tagged release or live production deployment is established by this document.

Reviewed on 2026-10-23:

- `origin/main`: [`3726563`](https://github.com/CelVision/AILT9019_G31/commit/3726563114f91b2319b5aac126c321ec2e0dbbef).
- `origin/codex/distribution-accessibility`: [`1ca4377`](https://github.com/CelVision/AILT9019_G31/commit/1ca437756fb0bdc91d08a4818c2f3ec4b9ea9d3c).
- Both tips have identical tracked file contents. The accessibility branch contains an implementation commit followed by its revert.

## Unreleased

### Documentation and verification — 2026-10-23

- Added this history and a [midterm repository review](docs/MIDTERM_REPOSITORY_REVIEW.md) with current limitations, deployment handoff priorities, and contribution wording.
- Independently reran the existing Python suite against `3726563` in a clean Python 3.12.14 environment: **26 passed, 3 deprecation warnings**. See [test output](docs/evidence/2026-10-23-pytest.txt) and [resolved dependencies](docs/evidence/2026-10-23-python-packages.txt).
- No application behavior was changed during this documentation review. Browser accessibility tests, a live GLM call, Docker execution, and public HTTPS/WSS deployment were not verified in this review.

## 2026-10-22 — Accessibility and distribution implementation, subsequently reverted

**Historical contribution; not active in the reviewed code.**

Author recorded by Git: **Scott Xiang**. Implementation: [`ca0b19e`](https://github.com/CelVision/AILT9019_G31/commit/ca0b19ee85b6dd91554811ab4eb591aaaea33f55), 13:42 HKT. Revert: [`1ca4377`](https://github.com/CelVision/AILT9019_G31/commit/1ca437756fb0bdc91d08a4818c2f3ec4b9ea9d3c), 14:26 HKT. The revert message does not explain the reason.

### Added in the historical implementation

- Keyboard column buttons with Enter/Space activation, arrow-key navigation, and Home/End support.
- A semantic board table, column descriptions, move/reaction announcements, accessible reaction labels, and numbered tokens that supplement color.
- Native modal dialogs and focus handling, visible focus indicators, narrow-screen layouts, minimum touch target sizing, and reduced-motion styles.
- Touch/click column selection based on the actual pointer position instead of requiring a prior hover.
- Queue registration after the WebSocket opens, stale-callback guards, connection recovery, and a fresh-queue “Find Another Match” action.
- Local system fonts in place of external font requests.
- Dockerfile and Compose configuration with a non-root container user, health check, one application worker, and a loopback-bound host port.
- `deploy/check_public_url.py` for HTTP assets, health status, and WebSocket ping/pong checks.
- Distribution/accessibility documentation, Playwright and axe browser checks, and a GitHub Actions workflow for Python, browser, and container checks.

### Verification recorded at that commit

The [historical worklog](https://github.com/CelVision/AILT9019_G31/blob/ca0b19ee85b6dd91554811ab4eb591aaaea33f55/docs/WORKLOG.md) reports **26 Python tests and 18 browser tests passed**, plus a local endpoint check. These are historical author-reported results, not browser results reproduced during this review. It also states that Docker was not available locally and public HTTPS, manual screen-reader, and real-device testing remained outstanding. A workflow definition is not evidence of a successful CI run.

### Reverted

- `1ca4377` removes the complete preceding accessibility/distribution change, including its tests and Docker tooling.
- These features must not be described as merged, available to current players, WCAG-certified, or deployed to production. The implementation remains inspectable in Git history and can substantiate completed development work.

## 2026-10-22 — Current GLM configuration and backend integration

### Changed

- [`3726563`](https://github.com/CelVision/AILT9019_G31/commit/3726563114f91b2319b5aac126c321ec2e0dbbef): switched the temporary default and allowlist to `glm-4.5-air`, with a 3.5-second AI deadline. Updated configuration, environment template, tests, and documentation.
- [`a586014`](https://github.com/CelVision/AILT9019_G31/commit/a586014): used `glm-4.7-flash` and explicitly disabled thinking before the later model switch.
- Diagnostic documentation commits `a3edc6e`, `7eb63aa`, `f31d2af`, and `9ce9ff3` record account/model availability and latency probes. Their historical measurements are not new measurements from this review.

### Added and fixed

In [`63822d5`](https://github.com/CelVision/AILT9019_G31/commit/63822d5):

- Added an HTTPX GLM client with model allowlisting, response parsing, and legal-move validation.
- Integrated GLM into PvE turns with a configurable timeout, a temporary center-out legal-move fallback, and a fallback notice.
- Added environment-backed settings, a safe environment template, and health fields that expose enabled/model status without exposing the API key.
- Served the client at the site root after API/WebSocket routes so relative CSS/JS paths resolve.
- Updated systemd to use one worker for in-memory rooms/queues and an optional environment file outside the repository.
- Added HTTP/static smoke checks, mocked GLM adapter tests, and AI-turn/fallback tests.

The worklog describes some of this work under 2026-10-21; the Git commit is dated 2026-10-22. The Minimax module exists but is not called by the current AI-turn handler. An unavailable GLM currently triggers a local legal move in PvE, not a separately implemented single-player mode.

## 2026-10-07 — Initial project and prototype

- [`a7ac308`](https://github.com/CelVision/AILT9019_G31/commit/a7ac308): initial proposal material.
- [`ac4cc35`](https://github.com/CelVision/AILT9019_G31/commit/ac4cc35): added the browser client and Canvas board, canned reactions, FastAPI/WebSocket gateway, in-memory matchmaking and PvE routing, game engine, Minimax module, engine tests, deployment templates, and project documentation.
- Nginx and systemd files are deployment configuration templates. Their presence does not establish that a VPS, domain, certificate, or public game service was provisioned.

## Known limitations at the reviewed main commit

- The current Canvas board has no keyboard move controls or semantic board alternative; clicking depends on `hoverCol`, which makes touch-only interaction unreliable.
- The README's separate frontend server on port 3000 conflicts with the client's same-origin WebSocket selection. Use the backend-served page at port 8000 for the reviewed setup.
- Registration sends `queue_join` once after one second rather than waiting for socket readiness; a slower connection can lose the request.
- The UI still labels the opponent as Gemini, although current backend configuration uses GLM.
- The client sends `rematch_request`, but the server has no matching handler. The turn countdown is displayed without server-side timeout enforcement.
- Room cleanup depends on a room ID populated by a player move; disconnecting before that player's first move can leave room state behind. The README's unconditional immediate-purge claim is therefore too broad.
- Full age-boundary and fault-injection suites listed in project plans are absent from the current tree. Existing unit tests do not establish complete browser, accessibility, or production behavior.
- Public deployment and manual accessibility verification remain unverified. See the [review](docs/MIDTERM_REPOSITORY_REVIEW.md) before claiming completion.
