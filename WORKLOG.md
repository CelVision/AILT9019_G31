# ConnectFour Connect — Development Worklog

**Purpose:** running handoff log for the team. Record decisions, completed work, verification results, and anything the next person needs to know. Newest entries first. **Never paste API keys, tokens, or real `.env` contents here.**

## 2026-10-26 — Protocol hardening and local acceptance fixes

- Added server-side registration validation with explicit `error` frames for invalid nicknames, ages, message payloads, columns, and reactions.
- Added authoritative `queue_status` frames, server-enforced 30-second turn expiry, and short-lived finished-room records for PvP/PvE rematches.
- Reconnected the deterministic depth-4 Minimax bot as the GLM failure fallback; the safe center-out selector remains only as a defensive last resort.
- Updated the browser for server queue status, validation errors, GLM naming, rematch waiting, board reset, and pointer input on touch devices.
- Added the 20-case age/profile Suite A and 10-case GLM fault Suite B. Verification: `75 passed`; local endpoint checker passed; live WebSocket verification passed for validation, queue status, PvP completion/rematch, and PvE Minimax fallback.

---

## 2026-10-26 — Matchmaking extraction, server-side validation, Minimax fallback

- **`server/app/matchmaking.py` (new):** the FIFO pool moved out of `main.py` into a `MatchmakingQueue` with an injectable clock: `add`/`remove`/`position`/`tick`/`status`, a three-year age window, the 15-second expiry, duplicate-join rejection and a 200-entry capacity limit. `tick()` pairs and expires in one pass and returns both lists, so pairing and expiry can no longer race each other.
- **`queue_join` is now validated server-side (QW-4):** nickname type/length (2–16), birth year type and plausibility, and the adult gate. Rejections return `{"type": "error", "payload": {code, message, field}}` instead of being silently dropped; accepted joins return an immediate `queue_status`.
- **`queue_status` heartbeat (QW-5):** a second background task pushes `elapsed_seconds` / `remaining_seconds` / `position` / `waiting` to every waiting player once per second. The browser no longer owns the queue countdown — `client/js/app.js` renders the server frame and sends `queue_join` from the `connected` handler instead of a one-second client timer.
- **Minimax restored (WP3-7):** `choose_fallback_move()` plays Minimax (depth 4) when GLM fails, validates the returned column against the live board, and degrades to a centre-out legal move only if Minimax raises or returns an unplayable column. `pve_fallback_notice` now carries `reason` and `strategy`.
- **Test Suite A (WP5-1) and Test Suite B (WP5-2) are in the repo:** 20 age/gap/malformed cases plus WebSocket-level rejection tests, and 10 fault injections (2× HTTP failure, 2× 429, 2× timeout, 4× malformed/illegal reply) with a must-block Minimax case and a GLM-success control. Suite B is no longer blocked.
- **Bug found and fixed while writing the tests:** `create_pvp_match` put the raw `QueueEntry` into `room["p2"]`, so the first PvP broadcast raised `TypeError: 'QueueEntry' object is not subscriptable`. Rooms now hold plain player dicts; `test_pvp_match_room_uses_plain_player_dicts` guards it.
- **Verification:** `python -m pytest tests/ -q` → **83 passed**. Live server (Uvicorn, `llm_enabled=false`): `deploy/check_public_url.py` → 8/8 checks; scripted WebSocket run → 7/7 (underage rejected, join returns `queue_status`, two compatible adults paired into one room, move broadcast to both, heartbeat remaining time strictly decreasing, position reported). A lone player was routed to PvE at **15.3 s** with bot nickname `AI Coach`.
- **Known limits:** the browser UI was syntax-checked (`node --check`) but not clicked through; the 30-second turn timer is still not enforced server-side (a forfeit rule is not implemented); `matchmaking_worker` still prints exceptions to stdout rather than logging them; `room_manager.py` extraction (WP2-3) is untouched; the PDF in `docs/proposal/` is still the pre-additions export.

## 2026-10-26 — Proposal additions (§2.3, §3.3, §4.3)

- Inserted three subsections into `docs/proposal/AILT9019_Revised_Proposal_G31.md` and the matching `.docx`: **§2.3** matchmaking state machine, disconnect handling and capacity limits; **§3.3** a quantitative latency, load and soak benchmark protocol; **§4.3** accessibility commitments under WCAG 2.1 AA.
- Scope was held deliberately narrow: these are the three parts of the template the submitted draft answers least. No existing section was rewritten, and no other prose was moved, so the added text can be reviewed or reverted block by block.
- **Known inconsistency left untouched:** §2 still names Gemini 1.5 Flash with a 2.5 s deadline while the code runs GLM-4.5-Air at 3.5 s; the Minimax fallback is still unwired; `create_pve_match` still labels the bot `"Gemini Bot"`. The PDF under `docs/proposal/` has **not** been regenerated from the updated `.docx`.
- **Commitments, not shipped behaviour:** the §2.3 claims about a `queue_status` heartbeat, a queue cap with `queue_full`, and server-side turn forfeit describe intended design. The queue tick currently matches, expires to PvE and emits `opponent_disconnected`. `queue_status` (QW-5) and the queue cap are implemented in the follow-up matchmaking PR.

## 2026-10-26 — Deployment PR #2 review (`c29d8e7`)

- Pulled and reviewed the merged deployment contribution: Dockerfile, Dockerfile-specific build-context ignore, Compose service, endpoint checker, checker regression tests, hardened systemd unit, README rewrite, and deployment notes.
- **Verified locally:** `python -m pytest tests/ -q` → **42 passed** (2 existing FastAPI deprecation warnings). `python deploy/check_public_url.py http://127.0.0.1:8000` passed all 8 checks against a locally started Uvicorn server. `compileall`, `git diff --check`, and local documentation-link checks passed.
- **No blocking implementation defects found** in the checker or Compose/systemd definitions reviewed statically. The Dockerfile-specific ignore file correctly limits the context to `server/app`, `server/requirements.txt`, and `client`; secrets are not copied into the image.
- **Still unverified:** Docker is not installed on this workstation, so the image was not built. Nginx/systemd/VPS/DNS/TLS/public-URL acceptance remains open (WP4-2 through WP4-4). The PR is deployment configuration, not a live deployment.
- **Documentation blocker:** `docs/TECHNICAL_SPEC.md` and `docs/PROJECT_PLAN.md` still describe **Gemini 1.5 Flash** with a **1.5s** budget, while the README/code now use **GLM-4.5-Air** with a **3.5s** budget. Update these formal documents before the checkpoint report.
- **Minor notes:** the deployment changelog reports 3 deprecation warnings (2 observed here); the Dockerfile-specific ignore depends on BuildKit for the strongest build-context exclusion; the new local README command omits `--reload` for development.

---

## 2026-10-23 — XIANG HANCHENG deployment implementation

- **Branch:** `deploy_XIANG-HANCHENG`, based on `3726563`. The old deployment PR #1 is closed; this work uses the team member's existing branch.
- **Structure:** all container files and the endpoint checker are under `deploy/`; regression tests are under `tests/`; changes are recorded in `docs/CHANGELOG.md`. Setup and rollback instructions are in the existing README. No new top-level directory or CI workflow is included.
- **Implementation:** non-root, single-worker Docker image; Compose with loopback port binding, runtime GLM settings, health checks, a read-only filesystem and bounded logs; HTTP/assets/WS/WSS checker; journald logging and systemd service restrictions.
- **Reproduction:** from the repository root, run `docker compose -f deploy/compose.yaml up --build --detach --wait --wait-timeout 120`, then check the running origin with `python deploy/check_public_url.py http://127.0.0.1:8000` in the project's Python environment.
- **Verification on this branch:** Python 3.12.14, `python -m pytest tests/ -q` returned **42 passed, 3 existing deprecation warnings in 1.40s**. Checked that Compose resolves its build context to the repository root and uses `deploy/Dockerfile` with the adjacent Dockerfile-specific ignore file. Verified that the image recipe, ignore rules, checker and Compose runtime settings match the previously tested implementation. Documentation links and Git whitespace checks passed.
- **Limits:** Docker is not installed locally, so the reorganized container layout has not been built here. Historical container/systemd/Nginx HTTPS/WSS CI evidence for the prior `f78356b` implementation is linked in the changelog; it is not a CI result for this branch. Public VPS/domain/certificate setup and full game/manual accessibility acceptance are still pending. The prior UI accessibility changes remain reverted.

---

## 2026-10-22 — Temporary switch: GLM-4.5-Air at 3.5s

- Changed the runtime model to **`glm-4.5-air`** in `server/.env`, `server/.env.example`, and `server/app/config.py`; the allowlist now contains only that model.
- Set `AI_TIMEOUT_SECONDS=3.5` because the live client prompt measured 2.28s and the standalone smoke measured 2.88s. This leaves margin for provider queueing without falling back unnecessarily.
- Updated `tests/test_glm_client.py`, `README.md`, `TASKS.md`, and this worklog to describe the temporary model.
- **Live smoke passed:** `{"column": 3, "canned_reaction_id": 0, "latency_ms": 2883.0, "model": "glm-4.5-air"}`.
- **Tests:** `python -m pytest tests/ -q` → **26 passed**.
- **Target unchanged:** restore `glm-4.7-flash` once the GLM console grants access. Do not treat `glm-4.5-air` as the final sprint model.

---

## 2026-10-22 — GLM-4.7-FlashX probe: valid but unusable latency

- `glm-4.7-flashx` (lowercase API ID) returns **200** with `thinking: disabled`, so the model is enabled for this account.
- A trivial “Reply with OK” request took **28,361ms**.
- A real client-prompt Connect Four request exceeded the **35s** probe timeout and raised `GLMError("timeout")`.
- The latency makes this model unsuitable for a PvE turn with the current 2.5s target. It is not a drop-in replacement for GLM-4.7-Flash.
- The best available fallback remains `glm-4.5-air` at ~2.28s; alternatively, enable `glm-4.7-flash` in the console.

---

## 2026-10-22 — Model probe: GLM-4.5-Flash unavailable, GLM-4.5-Air works

- `glm-4.5-flash` → `HTTP 429 / code 1302`, the same entitlement response as `glm-4.7-flash`. It is also absent from the account's `/models` list.
- `glm-4.5-air` → **200**. This is the closest available lightweight model in the account list.
- A real client-prompt probe with `glm-4.5-air` and `thinking: disabled` returned a legal move: `column=3`, `canned_reaction_id=0`, **latency 2279.3ms** (measured with a 5s probe timeout). That fits the current 2.5s cap only narrowly; a 3.0–3.5s timeout would be safer.
- Recommendation: use `glm-4.5-air` temporarily to unblock the demo, or claim/enable `glm-4.7-flash` in the console and keep the requested model. No application code changed yet.

---

## 2026-10-22 — GLM 429 diagnosed: model access, not the key

- Retried `cd server; python -m app.ai.glm_client` immediately and again after a two-minute cooldown; both returned `HTTP 429 / code 1302`.
- The 429 is **not account-wide**. With the same key:
  - `GET /api/paas/v4/models` returns **200** (the key is valid).
  - `glm-5.3-flash` returns **200**.
  - `glm-4.7` returns **200** (`thinking: disabled`, 4.96s).
  - `glm-4.7-flash` returns **429 / 1302**.
- The key's model list contains `glm-4.7`, `glm-5.3-flash`, etc., but **not `glm-4.7-flash`** (and not `glm-4-flash`). The 429 is therefore a model-entitlement/availability response, not a key problem. The console can show the key as "unused" because the failed calls never reach a model.
- The docs still list `glm-4.7-flash` and link a trial center. Next step: claim/enable GLM-4.7-Flash for this account, or temporarily use an available model. `glm-5.3-flash` requires `thinking` set to `low`, `high`, or `max` (it rejects `disabled`).
- No application code changes were made for this diagnosis; the suite remains **26 passed**.

---

## 2026-10-22 — Model confirmation: GLM-4.7-Flash

- **Endpoint confirmed:** `https://open.bigmodel.cn/api/paas/v4`, with `/chat/completions` appended by the client.
- **Official API model ID:** `glm-4.7-flash` (lowercase). The display name is **GLM-4.7-Flash**; the uppercase `F` in the user-provided curl is display casing, so the code uses the lowercase API ID.
- **Thinking disabled:** the GLM-4.7 family enables thinking by default. Because the game needs one small JSON object quickly, the request now sends `"thinking": {"type": "disabled"}` and keeps `max_tokens: 64`.
- **Updated:** `server/.env`, `server/.env.example`, `server/app/config.py`, `server/app/ai/glm_client.py`, `tests/test_glm_client.py`, README, TASKS, and this worklog.
- **Live test status:** the new model could not be verified yet because the account still returns provider `HTTP 429 / code 1302` (rate limit). A retest after the update also returned 429. The old `glm-4-flash` smoke success remains the only live latency sample.
- **Next:** wait for the account rate-limit window, run `cd server; python -m app.ai.glm_client`, and record the latency with thinking disabled. If the model ID is rejected, check the provider console for the exact enabled model list.

---

## 2026-10-22 — Pre-push evaluation

- **Tests:** `python -m pytest tests/ -q` → **26 passed**, 2 existing `on_event` deprecation warnings.
- **Syntax/whitespace:** `py_compile` OK; `git diff --check` clean.
- **Secrets:** `server/.env` is ignored by Git; the live key is not present in any tracked file. The live key was shared in chat and should be rotated before public release or transcript sharing.
- **Live GLM:** one full smoke request succeeded at **1737.9 ms** (`column: 3`) using the old `glm-4-flash` model. The account then hit provider `HTTP 429 / code 1302` rate limiting; `z.ai` returned the same limit. In-game fallback was verified on both 429 and a 2.5s timeout, but a successful in-game GLM turn is still blocked by the rate limit.
- **Timeout:** `server/app/config.py`, `server/.env.example`, and the local `server/.env` use **2.5s**. The technical spec still says 1.5s; WP3-8 must update it or the decision must be reversed.
- **Push target:** `origin/main` (`https://github.com/CelVision/AILT9019_G31.git`).

---

## 2026-10-21 — GLM-first direction, static serving, systemd, config scaffolding

### Decisions

- **GLM-first:** PvE will call **GLM-4-Flash** through an OpenAI-compatible `/chat/completions` endpoint, using a **server-side key**. Gemini is deferred and is not part of the current sprint.
- **Minimax deferred:** `server/app/ai/minimax_fallback.py` remains in the repo, but it is **intentionally not wired** while GLM is validated directly. On GLM failure, the temporary orchestration plays a safe legal move so the room never stalls (WP3-3); the real Minimax fallback returns in WP3-7 before the checkpoint.
- **Key policy:** the key never enters Git, the browser, or logs. Local development uses `server/.env` (ignored); the VPS uses `/etc/connectfour/connectfour.env` via systemd. The user-facing model name is not secret, but the server must validate it against an allowlist.
- **No Gemini dependency:** `google-genai` was removed from `server/requirements.txt`; GLM calls will use `httpx` (already a dependency).

### Completed

| Task | Change |
| :--- | :--- |
| **QW-1** | `server/app/main.py` now mounts the client at `/` with `StaticFiles(..., html=True)` **after** all API/WebSocket routes. `index.html`'s relative `css/style.css` and `js/*.js` paths now resolve. Removed the unused `FileResponse` import and old `/static` mount. |
| **QW-2** | `deploy/connectfour.service` now runs **one** Uvicorn worker (in-memory rooms/queue are per-process) and reads `EnvironmentFile=-/etc/connectfour/connectfour.env` (optional, outside the repo). Added `PYTHONUNBUFFERED=1` and `--proxy-headers`. |
| **WP3-5** | Added `server/app/config.py` (`GLM_API_KEY`, `GLM_BASE_URL`, `GLM_MODEL`, `GLM_ALLOWED_MODELS`, `AI_TIMEOUT_SECONDS`), `server/.env.example`, `server/app/__init__.py`, `server/app/ai/__init__.py`; broadened `.gitignore` to `.env*` with `!.env.example`; removed `google-genai`. `/api/health` now reports `llm_enabled` and `llm_model` (never the key). |
| **WP3-2** | Added `server/app/ai/glm_client.py`: OpenAI-compatible GLM request via `httpx`, board/legal-column serialization, strict JSON extraction/validation, model allowlist enforcement, and a standalone smoke test (`python -m app.ai.glm_client`). Added `tests/test_glm_client.py` using `httpx.MockTransport`; no real API call or key needed. **Live smoke passed at 1737.9ms**; provider rate limiting documented below. |
| **WP3-3 (review)** | Wired `handle_ai_turn` to `request_glm_move` with a configurable `asyncio.wait_for` (2.5s local default). On any GLM failure it plays a temporary center-out legal move and sends one `pve_fallback_notice` per room. Minimax is **not** called. Added `tests/test_ai_turn.py` for GLM success, GLM error, and timeout paths. **Live fallback verified**; successful in-game GLM turn still blocked by rate limit. |
| **Tests** | Added `tests/test_app_smoke.py` covering `/api/health`, `/` HTML serving, root CSS/JS, and the `/ws/game` route. Added mocked GLM adapter and AI-turn tests. |

### Verification (run 2026-10-21, Windows / Python 3.14)

```text
python -m pytest tests/ -q
26 passed, 2 warnings in 1.78s

python tests/test_connect4_engine.py
ALL CONNECT FOUR ENGINE TESTS PASSED!

python -m py_compile server/app/main.py server/app/config.py server/app/ai/glm_client.py tests/test_app_smoke.py tests/test_glm_client.py tests/test_ai_turn.py
OK

git check-ignore -v server/.env .env.production server/.env.local server/.env.example
server/.env          -> .gitignore:34:.env
.env.production      -> .gitignore:35:.env.*
server/.env.local    -> .gitignore:35:.env.*
server/.env.example  -> .gitignore:36:!.env.example (not ignored)
```

Config smoke tests:

```text
# No key in the environment
enabled=False
default_model=glm-4-flash
allowed=('glm-4-flash',)
timeout=2.5

# Dummy key + GLM_ALLOWED_MODELS='glm-4-flash, glm-4-air' + AI_TIMEOUT_SECONDS=2
enabled=True
model=glm-4-flash
allowed=('glm-4-flash', 'glm-4-air')
timeout=2.0
base_url=https://open.bigmodel.cn/api/paas/v4
```

GLM live smoke test (2026-10-21):

```text
cd server
python -m app.ai.glm_client

# Successful full request after the rate-limit window cleared:
{"column": 3, "canned_reaction_id": 0, "latency_ms": 1737.9, "model": "glm-4-flash"}
```

The key was accepted by `glm-4-flash` on the mainland endpoint. The first simple request also returned HTTP 200. Rapid diagnostic calls then returned:

```text
HTTP 429
{"error":{"code":"1302","message":"您的账户已达到速率限制，请您控制请求频率"}}
```

Translation: “Your account has reached the rate limit; please control request frequency.” One request succeeded after a cooldown, but later 90-second cooldowns still returned 429, so the window is longer or shared. This is provider-side account rate limiting, not a bad key. The current handler falls back to the temporary safe move on 429. There is no retry/backoff because the 1.5–2.5s move budget leaves no room for one.

### Live latency finding (important)

- Measured smoke-test latency: **1737.9 ms** for a valid `glm-4-flash` move.
- The technical-spec target is **1.5s**; the proposal says **2.5s**.
- `handle_ai_turn` wraps the request in `asyncio.wait_for(..., timeout=AI_TIMEOUT_SECONDS)`. With 1.5s, the successful 1.74s response above would be cancelled and replaced by the safe move.
- Local `server/.env` was therefore set to `AI_TIMEOUT_SECONDS=2.5` for in-game testing. `server/app/config.py` and `server/.env.example` now also default to **2.5s**, matching the proposal. The technical spec still says 1.5s and must be updated (WP3-8) or the decision reversed.
- One sample is not enough to set a final budget; repeat the smoke test when the account is not rate-limited, ideally from the deployment region.

### Live in-game / endpoint checks

- **In-game attempt 1 (2.5s timeout):** GLM returned `http_429`; the handler played the safe center column and set `fallback_notified=True`. Total handler time was **1081.9 ms**, including the 0.4s human-like pause. This verifies the fallback path end to end.
- **In-game attempt 2 (after a 90s cooldown):** the GLM request did not finish inside 2.5s; `asyncio.wait_for` cancelled it and the safe move was played. Total handler time was **2917.8 ms** (0.4s pause + 2.5s timeout).
- **z.ai international endpoint:** returned `http_429` in 618.7 ms with the same key. The account-level rate limit applies across both endpoints; switching endpoints does not bypass it.
- **Conclusion:** the client and fallback are working; the remaining blocker is the provider account’s rate limit. A 2.5s budget may still be marginal when the provider queues a request. Options are (a) use 3–4s and accept a slower opponent, (b) optimize/retry later, or (c) demo with the safe move when GLM is rate-limited. Do not run burst tests; they make the rate limit worse.

Root routing check after QW-1:

```text
GET /             -> 200 (index.html)
GET /css/style.css -> 200
GET /js/app.js    -> 200
GET /api/health   -> 200
GET /docs         -> 200
GET /openapi.json -> 200
```

The two pytest warnings are the existing `@app.on_event("startup")` deprecation in `server/app/main.py:115`; behavior is unchanged. A future cleanup can move the matchmaking worker into a lifespan handler.

### Files touched

```text
.gitignore
TASKS.md
deploy/connectfour.service
server/requirements.txt
server/app/main.py
server/app/__init__.py                 (new)
server/app/ai/__init__.py              (new)
server/app/ai/glm_client.py            (new)
server/app/config.py                   (new)
server/.env.example                    (new)
server/.env                            (local only, ignored — contains the key; never commit)
tests/test_app_smoke.py                (new)
tests/test_glm_client.py               (new)
tests/test_ai_turn.py                  (new)
docs/WORKLOG.md                        (new)
```

### Handoff notes / risks

1. **Local run:** `server/.env` now exists locally with the supplied key and is ignored by Git. For a fresh checkout, copy `server/.env.example` to `server/.env` and fill `GLM_API_KEY`. The app still starts without a key; `get_ai_settings().enabled` is `False` until one is present. Without a key, PvE remains playable using the temporary center-out safe move and shows one fallback toast per room — this is intentional for GLM validation, not the final opponent.
2. **VPS setup:** create `/etc/connectfour/connectfour.env` with `sudo install -m 640 -o root -g www-data /dev/null ...`, then add the key. The leading `-` in `EnvironmentFile=-...` means the service also starts if the file is absent.
3. **Do not expose the key:** the browser only sends a model name. The server must never echo `GLM_API_KEY` in errors, logs, health output, or room state. The key was shared in chat during testing, so rotate it before making the repo public or sharing this transcript.
4. **429 handling:** the provider’s code `1302` is account rate limiting; rapid test calls trigger it. Current behavior is the safe-move fallback. Add retry/backoff only if the move budget is increased.
5. **Suite B is blocked** until WP3-7 restores the Minimax fallback; its 10 cases should mock the GLM adapter, not call the real API.
6. **Formal docs still say Gemini** (`README.md`, `docs/TECHNICAL_SPEC.md`, `docs/PROJECT_PLAN.md`). WP3-8 updates them; until then, this worklog is the source of truth for the current sprint.
7. **`TASKS.md` counts:** Quick Wins are tracked separately and are not included in the WP totals.

### Next up

- **WP3-2 (finish):** live smoke test passed; wait for the rate-limit window and record a second latency sample without bursts. Do not paste the key into chat or the worklog.
- **WP3-3 (finish):** fallback path is verified live. GLM in-game success is currently blocked by 429/timeouts; decide whether to raise `AI_TIMEOUT_SECONDS` to 3–4s, optimize the call, or accept fallback during the demo.
- **WP3-7 (restore fallback):** replace the temporary safe move with the Minimax fallback before the checkpoint, then unblock Test Suite B.
- **QW-3:** touch/pointer support in `client/js/game_board.js`.
- **QW-4:** server-side `queue_join` validation and an `error` frame.
