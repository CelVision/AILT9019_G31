# Changelog

## 2026-10-26 — Local acceptance hardening

- Added server-side registration, move, and reaction validation with explicit WebSocket error frames.
- Added authoritative queue status events, server-enforced 30-second turn timeouts, and short-lived PvP/PvE rematch handling.
- Wired the deterministic Minimax bot as the GLM failure fallback and updated the client/docs to describe GLM consistently.
- Added pointer input support for touch devices and protocol regression tests.
- Local verification: 75 automated tests, deployment checker, PvP/rematch WebSocket flow, and PvE Minimax fallback.

## 2026-10-23 — Deployment implementation

Branch: `deploy_XIANG-HANCHENG`. Contribution area: XIANG HANCHENG, deployment and distribution. Based on main commit `3726563`.

### Added

- `deploy/Dockerfile`: non-root Python 3.12 image, one Uvicorn worker and an HTTP health check. The application serves the existing frontend and WebSocket endpoint from one origin.
- `deploy/Dockerfile.dockerignore`: Dockerfile-specific build-context allowlist excluding credentials, Git history and local test data. The build context remains the repository root.
- `deploy/compose.yaml`: explicit build context and Dockerfile path; loopback-only port 8000; runtime GLM settings; health-based startup checks; read-only root filesystem, temporary storage and bounded logs.
- `deploy/check_public_url.py`: validates healthy JSON, nonempty HTML/CSS/JS and WebSocket upgrade/ping-pong. Verifies HTTPS certificates, rejects redirects and invalid origins, and exits unsuccessfully on failure. It does not register players or call GLM.
- `tests/test_deployment_check.py`: 16 regression cases covering malformed origins, WSS selection, resource failures, incorrect content types, unhealthy responses and WebSocket timeouts.

### Changed

- `deploy/connectfour.service`: journald logging, disabled bytecode writes, a private temporary directory, read-only system filesystem and restricted privilege escalation. The existing single-worker configuration and external environment-file path remain in use.
- `README.md`: corrected local same-origin startup, documented Docker/native VPS deployment, HTTPS/WSS checks, secrets, update/rollback and the exact deployment file locations.
- `TASKS.md` and `docs/WORKLOG.md`: recorded deployment implementation and outstanding public deployment checks; did not mark unverified VPS work complete.

### Structure and scope

All implementation files are under existing `deploy/` and `tests/` directories. This changelog is in `docs/`; setup instructions and handoff notes use the existing README and WORKLOG. No new top-level directory, root-level Docker/Compose files, CI workflow directory, standalone scan report or evidence directory is included in this branch.

Deployment code was adapted from `f78356b` and the earlier deployment-only ideas in `ca0b19e`. The old PR #1 is closed. The earlier UI accessibility changes were reverted by `1ca4377` and are not restored by this deployment change. Client game logic and backend game/AI logic are unchanged.

### Verification and remaining work

- On this branch, `python -m pytest tests/ -q` passed **42 tests with 3 existing deprecation warnings** (Python 3.12.14, 1.40s).
- Checked the relocated Compose context/Dockerfile/ignore-file resolution, documentation links, whitespace and equality of runtime configuration with the previously verified implementation.
- Docker is unavailable locally; the relocated container layout has not been rebuilt here. No CI workflow is added to this branch.

- The prior implementation `f78356b` passed container build/start, systemd/Compose validation and Nginx HTTPS/WSS tests in [GitHub Actions run 39890155611](https://github.com/CelVision/AILT9019_G31/actions/runs/39890155611). This is historical evidence for that implementation, not a CI run of the reorganized branch.
- Public VPS, DNS, trusted certificate setup and complete-game/manual accessibility acceptance still need to be performed. Configuration files and local connectivity checks do not establish a live public service.
