# ConnectFour Connect (AILT9019 G31) — Team Task Checklist

Welcome to the team task tracker! This document is designed for all team members to view, claim, update, and add development tasks as we build toward the **Mid-Term Checkpoint (Monday, October 26)**.

**Last updated:** 2026-11-08 · **Detailed worklog:** [docs/WORKLOG.md](docs/WORKLOG.md)

## 🗞️ Recent Updates
- **2026-11-08 — Provider and documentation reconciliation:** Aligned committed defaults, `.env.example`, Compose, UI labels, README, `TECHNICAL_SPEC.md`, and `PROJECT_PLAN.md` on the actual Alibaba Cloud Bailian **`qwen3.6-flash`** runtime. Configuration now uses provider-neutral `AI_*` names with legacy `GLM_*` fallbacks; the PvE bot is labelled **AI Coach**. Corrected the stale claim that all free-form chat is omitted: PvP still has no peer free text, while PvE has AI Coach chat. Automated verification will be recorded in the worklog after the suite run.
- **2026-11-08 — Progress review (`10876d2`):** Pulled latest `main` and reviewed the post-checkpoint release. **94 Python tests pass**; the endpoint checker passes 8/8; onboarding, 15s PvE transition, turn timeout, post-match AI chat, and PvE rematch were exercised in the browser. Findings recorded in the worklog: Bailian/Qwen provider vs. GLM docs/labels drift, PvP topic guardrail bypass, queue-capacity error path, stale finished-room selection, and game-over state/copy bugs. The provider/docs drift is resolved in the entry above. `node` is unavailable locally (pointer test not rerun); Docker/VPS/systemd/Nginx acceptance remains unverified.
- **2026-10-26 — UI Game Area & Chat Area Division + Post-Match Chat Persistence:** Redesigned the match interface into dedicated two-column `.game-area` and `.chat-area` cards. In-game and post-game chat states are completely independent of game outcome (win/loss/draw does not close chat or block messaging; rematch preserves conversation history). Server `finished_rooms` preserves chat history and handles post-match LLM banter turns. Full test suite has **94 passing tests**.
- **2026-10-26 — Sponsored Alibaba Cloud Bailian Integration:** Integrated official Group 31 sponsored Bailian access (`qwen3.6-flash`) with OpenAI-compatible endpoint. Implemented multi-turn contextual AI chat companion with sliding 6-turn history and canned campus icebreakers. Verified with automated regression tests.
- **2026-10-26 — QW-3 touchscreen input:** Implemented touch/pen pointer selection in `client/js/game_board.js`, preserved desktop hover preview, and added `tests/test_game_board_pointer.js`. Automated regression test passes; physical iOS/Android verification is still pending. QW-3 remains in REVIEW.
- **2026-10-26** — Reviewed merged deployment PR #2 (`c29d8e7`). **42 tests pass**; the local endpoint checker passed all 8 HTTP/asset/WS checks; Docker build and VPS/DNS/TLS/public-URL acceptance remain unverified. At that time, formal `TECHNICAL_SPEC.md`/`PROJECT_PLAN.md` still said Gemini 1.5 Flash and 1.5s; they were later updated to the current Bailian/Qwen runtime with a 3.5s deadline.
- **2026-10-23 — XIANG HANCHENG deployment contribution:** added container configuration and an endpoint checker under `deploy/`, checker tests under `tests/`, and [changelog](docs/CHANGELOG.md). Setup instructions are in README. VPS/domain/certificate acceptance remains open; configuration preparation is not a completed public deployment.
- **2026-10-22** — Switched the temporary PvE model to **`glm-4.5-air`** with a **3.5s** timeout. **Live smoke passed:** `column=3`, **2883.0ms**. The target remains `glm-4.7-flash` once the GLM console grants access. README, env template, config, tests, and worklog were updated; **26 tests pass**.
- **2026-10-22** — `GLM-4.7-FlashX` is enabled (`200`) but unusably slow: a trivial call took **28.4s**, and a real Connect Four prompt exceeded **35s**. Not viable for the turn target.
- **2026-10-22** — Pre-push evaluation (before the model switch): **26 tests pass**, `server/.env` is ignored, and the live key is absent from tracked files. The old-model (`glm-4-flash`) smoke succeeded at **1737.9ms**; at that time the timeout was 2.5s and the provider entitlement issue blocked a successful in-game turn. See the [worklog](docs/WORKLOG.md).
- **2026-10-21** — Completed **QW-1** (root static serving), **QW-2** (single-worker systemd + env file outside repo), **WP3-2** (GLM client, **live smoke passed**), and **WP3-5** (`config.py`, `.env.example`, `.gitignore` hardening). **WP3-3** (GLM turn handler + temporary safe move) is in review: live fallback worked on `429` and on a 2.5s timeout, but a successful in-game GLM turn is blocked by account rate limiting. Full suite is **26 passed**.

---

## 📌 Collaboration Guidelines for Colleagues

1. **Claiming a Task**: Put your name in `@Assignee` and update status to `[IN PROGRESS]`.
2. **Marking Complete**: Change `- [ ]` to `- [x]`, update status to `[DONE]`, and optionally add the commit or PR link.
3. **Adding a New Task**: Copy the task template below and paste it into the appropriate section:
   ```markdown
   - [ ] **[TODO]** `TASK-ID`: Task title | **Assignee**: @Unassigned | **Priority**: High/Med/Low | **Due**: YYYY-MM-DD
     - Description / Acceptance Criteria: ...
   ```
4. **Status Tags**:
   - `[TODO]` — Not yet started
   - `[IN PROGRESS]` — Currently being worked on
   - `[REVIEW]` — Code written, waiting for peer review or testing
   - `[BLOCKED]` — Waiting on another task or external dependency
   - `[DONE]` — Tested and merged

---

## 📊 High-Level Sprint Progress

| Work Package | Focus Area | Total Tasks | Completed | In Progress | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **WP0: Proposal & Admin** | Course submissions & reviews | 3 | 2 | 1 | 🟡 Final Polish |
| **WP1: Frontend Client** | HTML5/Canvas UI & Canned Chat | 8 | 7 | 0 | 🟢 Nearly Complete (88%) |
| **WP2: Backend Networking** | FastAPI, WebSockets & Queue | 7 | 6 | 0 | 🟢 Nearly Complete (86%) |
| **WP3: AI & Fallback** | Qwen3.6-Flash, model config & Minimax fallback | 9 | 8 | 0 | 🟢 Feature Complete (89%) |
| **WP4: Infrastructure & VPS**| Ubuntu VPS, Nginx SSL & WSS | 4 | 1 | 0 | 🟢 Configs Ready |
| **WP5: Testing & Evaluation**| Suites A & B, 15-User Cohort | 6 | 6 | 0 | 🟢 100% Complete |

> Quick Wins are tracked separately below and are **not** included in these totals.

---

> **✅ AI Direction Update — 2026-11-08 (Alibaba Cloud Bailian / Qwen3.6-Flash)**
> - PvE moves and AI Coach chat call **`qwen3.6-flash`** through Alibaba Cloud Bailian's OpenAI-compatible endpoint, using a **server-side key**.
> - Configuration uses `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL`, `AI_ALLOWED_MODELS`, and `AI_TIMEOUT_SECONDS`. Legacy `GLM_*` names remain accepted during migration. The model allowlist is enforced server-side, and the browser never receives the key.
> - The current UI does not expose model selection. If that changes, the client may send only a model name and the server must continue to enforce the allowlist.
> - The per-move deadline remains **3.5s**. On timeout/error/illegal output, the server plays a validated depth-4 **Minimax** move and reports `reason` plus `strategy` in `pve_fallback_notice`. Chat currently shares the 3.5s timeout and returns a canned reply on failure.
> - **PvP** has no free-form text between peers; players use the canned palette and curated **Daily Icebreakers**. **PvE** supports free-form chat with the AI Coach.
> - Keys live only in `server/.env` locally and `/etc/connectfour/connectfour.env` on the VPS. Never commit, log, or send a key to the browser. Historical GLM probe notes remain in the worklog.

---

## 🟢 Quick Wins for Teammates (Oct 21–25)

Small, low-risk tasks that can be picked up without touching the AI integration. Claim one with the normal `[IN PROGRESS]` workflow.

| ID | Task | Status | Effort | Priority | Files | Acceptance Criteria |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **QW-1** | Fix static assets served from `/` | ✅ DONE (10-21) | 15 min | Critical | `server/app/main.py` | `http://127.0.0.1:8000/` loads CSS/JS with HTTP 200; `/ws/game` still works |
| **QW-2** | Set `--workers 1` and move the env file outside the repo | ✅ DONE (10-21) | 10 min | Critical | `deploy/connectfour.service` | Service starts with `/etc/connectfour/connectfour.env`; rooms/queue stay consistent |
| **QW-3** | Add touch/pointer column selection | ✅ DONE (10-26) | 30 min | High | `client/js/game_board.js` | Touching a column drops a token; desktop hover preview remains functional. Automated regression test passes. |
| **QW-4** | Validate `queue_join` server-side and return an `error` frame | ✅ DONE (10-26) | 45 min | High | `server/app/main.py`, `server/app/matchmaking.py`, `client/js/app.js` | Underage, malformed birth year, and nickname length 2–16 get a clear inline error; no silent drop |
| **QW-5** | Emit `queue_status` every second | ✅ DONE (10-26) | 30 min | Medium | `server/app/main.py`, `client/js/app.js` | UI countdown matches server `elapsed_seconds` / `timeout_seconds` |
| **QW-6** | Highlight the last dropped token | ✅ DONE (11-20) | 30 min | Low | `client/js/game_board.js`, `client/js/app.js` | Last token highlighted with glowing cyan ring; clears on next move |

**Completion notes (2026-10-21):** QW-1 is verified by `tests/test_app_smoke.py` (root HTML, CSS, JS, `/api/health`, `/ws/game`). QW-2 is updated in the repo; applying it on the VPS and confirming the service restart is still pending.

**Already on the board and easy to close:** `WP1-4` (timer bar is already built — verify and mark done), `WP4-2`/`WP4-3` (configs exist — apply and verify), `WP5-3` (survey, non-code), `WP1-7` (sound, low priority). **Do not treat as quick wins:** `WP1-8` (rematch), `WP5-1` (Suite A), `WP2-3` (room manager extraction), `WP3-6` (model selector touches both client and server).

---

## 🚀 Sprint 1: Week 6 — Core Foundation & Local MVP (Oct 5 – Oct 11)

### WP0: Proposal Finalization
- [x] **[DONE]** `WP0-1`: Author revised proposal markdown with all 7 reviewer responses ([docs/proposal/](docs/proposal/AILT9019_Revised_Proposal_G31.md)) | **Assignee**: @Team | **Due**: 2026-10-07
- [x] **[DONE]** `WP0-2`: Generate Project Plan ([docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md)) and Technical Specification ([docs/TECHNICAL_SPEC.md](docs/TECHNICAL_SPEC.md)) | **Assignee**: @Team | **Due**: 2026-10-07
- [ ] **[TODO]** `WP0-3`: Final proofread and submission of Revised Proposal PDF via Moodle form | **Assignee**: @Team | **Priority**: Critical | **Due**: 2026-10-10 (Sat)
  - Verify all student IDs, group info, and word counts comply with template.

### WP1: Frontend Client (HTML5 / Canvas 2D)
- [x] **[DONE]** `WP1-1`: Create client scaffolding (`client/index.html`, `client/css/style.css`, `client/js/app.js`) | **Assignee**: @Team | **Due**: 2026-10-07
  - Modern dark-mode layout, responsive container for mobile/desktop.
- [x] **[DONE]** `WP1-2`: Implement HTML5 Canvas 7×6 Connect Four board renderer (`client/js/game_board.js`) | **Assignee**: @Team | **Due**: 2026-10-07
  - Draw 7 columns × 6 rows, empty circular slots, hover column indicator.
- [x] **[DONE]** `WP1-3`: Implement token drop animation with gravity physics | **Assignee**: @Team | **Completed**: 2026-11-20
  - Smooth vertical descent with gravity acceleration into destination cell in Canvas 2D (`client/js/game_board.js`).
- [x] **[DONE]** `WP1-4`: Build 30-second turn countdown timer bar & active player badge | **Assignee**: @Team | **Completed**: 2026-10-26
  - Turn indicator ("Your Turn" vs. "Opponent's Turn") with active timer bar.
  - Server-side 30-second turn timer enforcement with timeout forfeit.
- [x] **[DONE]** `WP1-5`: Construct Canned Social Reaction Tray (`client/js/canned_chat.js`) | **Assignee**: @Team | **Due**: 2026-10-07
  - 6 preset phrases: *"Good luck!"*, *"Nice move!"*, *"Thinking..."*, *"Close one!"*, *"Well played!"*, *"Good game!"*.
  - 4 reaction stickers: 👍, 👏, 🤔, 🎉.
  - Floating speech bubbles above player avatars.
- [x] **[DONE]** `WP1-6`: Build 1-minute Onboarding & Guest Registration modal | **Assignee**: @Team | **Due**: 2026-10-07
  - Form inputs: Nickname (2–16 chars) and Birth Year ($\ge 18$ check).
  - Simple rules graphic explaining column clicking and 4-in-a-row goal.

### WP2: Backend Networking & Local Room Management
- [x] **[DONE]** `WP2-1`: Initialize backend structure (`server/requirements.txt`, `server/app/main.py`) | **Assignee**: @Team | **Due**: 2026-10-07
  - FastAPI app with static file mounting and Uvicorn server.
  - **Known issue:** assets currently 404 when the app is opened at `/`; tracked as QW-1. CORS is not configured (same-origin only).
- [x] **[DONE]** `WP2-2`: Implement Connect Four Rules Engine (`server/app/game_engine.py`) | **Assignee**: @Team | **Due**: 2026-10-07
  - 7×6 matrix state, legal move validation, gravity row calculation.
  - 4-in-a-row win detection (horizontal, vertical, diagonal $\nearrow/\searrow$).
  - Draw condition (42 cells filled).
  - Unit tests verified in `tests/test_connect4_engine.py`.
- [x] **[DONE]** `WP2-3`: Implement In-Memory Room Manager (`server/app/room_manager.py`) | **Assignee**: @Team | **Completed**: 2026-11-20
  - Thread-safe active room creation, player pairing, turn rotation, finished room retention, and stale room eviction.
  - Unit tests verified in `tests/test_room_manager.py`.
- [x] **[DONE]** `WP2-4`: WebSocket Game Gateway (`server/app/main.py` -> `/ws/game`) | **Assignee**: @Team | **Due**: 2026-10-07
  - Handle `queue_join`, `player_move`, `send_reaction`, disconnect events.
  - Local 2-player tab testing support with in-memory matchmaking pool.

---

## ⚡ Sprint 2: Week 7 — AI Integration, Matchmaking & VPS (Oct 12 – Oct 18)

### WP3: AI Agent & Fallback
- [x] **[DONE]** `WP3-1`: Implement local deterministic Minimax bot (`server/app/ai/minimax_fallback.py`) | **Assignee**: @Team | **Due**: 2026-10-07
  - Minimax with Alpha-Beta pruning (depth 4).
  - Evaluation weights: 4-in-row (+100,000), 3-in-row (+500), 2-in-row (+50), center control (+30).
  - Benchmark execution time verified at ~23.6ms (<50ms target).
  - **Current status:** wired as the active fallback in WP3-7.
- [x] **[DONE]** `WP3-2`: Integrate the OpenAI-compatible AI move client (`server/app/ai/glm_client.py`; current model **Qwen3.6-Flash**) | **Assignee**: @Team | **Priority**: Critical | **Due**: 2026-10-23
  - Call Alibaba Cloud Bailian's OpenAI-compatible `/chat/completions` endpoint with `httpx`; no provider-specific SDK.
  - Read `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL`, and `AI_ALLOWED_MODELS` from the server environment only; legacy `GLM_*` names remain supported during migration.
  - Serialize board + legal columns; enforce JSON `{"column": int, "canned_reaction_id": int}`; validate the column against legal moves.
  - Include a standalone smoke test (`python -m app.ai.glm_client`) that prints one move and its latency.
  - **History:** the original GLM probes and entitlement findings (2026-10-21/22) are retained in [docs/WORKLOG.md](docs/WORKLOG.md). Bailian/Qwen superseded them on 2026-10-26.
- [x] **[DONE]** `WP3-3`: Build AI timeout & orchestration wrapper | **Assignee**: @Team | **Priority**: Critical | **Completed**: 2026-10-26
  - Race the AI request against `AI_TIMEOUT_SECONDS` (current default **3.5s**).
  - On timeout/HTTP error/malformed JSON/illegal column, use the local Minimax fallback so the room never stalls.
  - Emit `pve_fallback_notice` with a non-secret `reason`; the current strategy fields are `minimax` / `safe_move`.
- [ ] **[TODO]** `WP3-4`: Dual bot personalities stretch feature (`server/app/ai/`) | **Assignee**: @Unassigned | **Priority**: Low | **Due**: 2026-10-24
  - "Casual Explorer" (relaxed depth, frequent reaction stickers) vs. "Tactical Challenger" (depth 5, strategic play).
  - Deferred until release hardening is complete.
- [x] **[DONE]** `WP3-5`: Add `config.py`, `.env.example`, and secret-hygiene rules | **Assignee**: @Team | **Priority**: Critical | **Due**: 2026-10-21
  - Load `.env` with `python-dotenv`; fail closed when `AI_API_KEY` is absent (PvE disabled or local mode).
  - Broaden `.gitignore` to `.env*` with `!.env.example`; never log or echo the key.
  - Completed 2026-10-21: added `server/app/config.py`, `server/.env.example`, package `__init__.py` files, and `tests/test_app_smoke.py`; removed unused `google-genai`.
  - Verified: no-key → `enabled=False`; dummy-key → allowlist/timeout parsed; `.env.example` is not ignored.
- [x] **[DONE]** `WP3-6`: Add optional model-name selector + server allowlist & frontend custom AI port | **Assignee**: @Team | **Completed**: 2026-11-20
  - Added frontend collapsible custom AI configuration section in `client/index.html` allowing optional custom key, model selection, and base URL.
  - State persisted via `localStorage` in `client/js/app.js` and transmitted via `queue_join`.
  - Server dynamically attaches custom `AISettings` to PvE rooms, while safely falling back to local depth-4 Minimax bot when unconfigured.
  - Verified with automated test `test_create_pve_match_applies_custom_ai_settings`.
- [x] **[DONE]** `WP3-7`: Re-enable Minimax fallback before the checkpoint | **Assignee**: @Team | **Completed**: 2026-10-26
  - `choose_fallback_move()` plays Minimax (depth 4) when the primary AI fails, validates the column against the live board, and only degrades to a centre-out legal move if Minimax raises or returns an illegal column.
  - `pve_fallback_notice` carries `reason` and `strategy` (`minimax` / `safe_move`).
  - Covered by Test Suite B, including a must-block case.
- [x] **[DONE]** `WP3-8`: Update AI references in README, TECH_SPEC, and PROJECT_PLAN (Gemini → primary AI; Minimax fallback) | **Assignee**: @Team | **Completed**: 2026-10-26
  - Formal docs updated to reflect the then-current GLM runtime and depth-4 Minimax fallback; superseded by WP3-10.
- [x] **[DONE]** `WP3-10`: Reconcile provider, configuration, UI labels, and docs after the Bailian/Qwen migration | **Assignee**: @Team | **Completed**: 2026-11-08
  - Committed defaults, `.env.example`, Compose, UI labels, README, TECH_SPEC, and PROJECT_PLAN now describe `qwen3.6-flash` through Alibaba Cloud Bailian.
  - Added provider-neutral `AI_*` settings with legacy `GLM_*` fallbacks and regression coverage.
  - Clarified that PvP has no peer free text while PvE supports AI Coach chat.

### WP2: Age-Gated Matchmaking Queue
- [x] **[DONE]** `WP2-5`: Implement in-memory FIFO Matchmaking Queue (`server/app/matchmaking.py`) | **Assignee**: @Team | **Completed**: 2026-10-26
  - Enforce age boundary: $\text{Age} \ge 18$ (rejected with `error` frame, code `underage`).
  - Enforce age gap constraint: $|\text{Age}_A - \text{Age}_B| \le 3$.
  - Also adds duplicate-join rejection and a 200-entry capacity limit (`queue_full`).
  - Covered by Test Suite A (`tests/test_suite_a_matchmaking.py`).
- [x] **[DONE]** `WP2-6`: Implement 15-second Queue Timeout & PvE Routing | **Assignee**: @Team | **Completed**: 2026-10-26
  - If no human peer matches within 15 seconds, pop user and seamlessly launch PvE room with AI bot.
  - Pairing and expiry run in the same queue tick, so a player can never be matched after being routed to PvE. Live check: PvE room opened at 15.3 s.

### WP4: DevOps & Cloud Infrastructure
- [ ] **[TODO]** `WP4-1`: Provision Ubuntu Linux VPS instance & install dependencies | **Assignee**: @Unassigned | **Priority**: High | **Due**: 2026-10-13
  - Python 3.12+, Uvicorn, Nginx, Git, Certbot.
- [ ] **[TODO]** `WP4-2`: Configure Nginx reverse proxy with SSL & WebSocket upgrades | **Assignee**: @Unassigned | **Priority**: High | **Due**: 2026-10-14
  - Enable Let's Encrypt SSL (HTTPS and WSS).
  - Proxy `ws://127.0.0.1:8000/ws/game` to `wss://<domain>/ws/game`.
  - **Status note:** `deploy/nginx.conf` is ready; remaining work is applying it on the VPS and issuing the certificate.
- [ ] **[TODO]** `WP4-3`: Configure Systemd daemon (`deploy/connectfour.service`) | **Assignee**: @Unassigned | **Priority**: Medium | **Due**: 2026-10-15
  - Enable auto-restart and inspect service logs with `journalctl -u connectfour`.
  - **Status note:** the unit includes single-worker operation, an external environment file, journald logging and service restrictions; installation and restart verification on the VPS remain pending.
- [ ] **[TODO]** `WP4-4`: Verify zero-configuration public URL access | **Assignee**: @Unassigned | **Priority**: Critical | **Due**: 2026-10-16
  - Test game loads on mobile Safari, Android Chrome, and desktop browsers without login/keys.

---

## 🧪 Sprint 3: Week 8 — Automated Testing, Evaluation & Polish (Oct 19 – Oct 25)

### WP5: Automated Test Suites
- [x] **[DONE]** `WP5-1`: Author and run **Test Suite A** (20 Age Boundary Pairs) (`tests/test_suite_a_matchmaking.py`) | **Assignee**: @Team | **Completed**: 2026-10-26
  - 10 valid pairs ($|\Delta\text{Age}| \le 3$, Age $\ge 18$) $\rightarrow$ 100% paired PvP within 15s.
  - 5 age-gap refused pairs ($|\Delta\text{Age}| > 3$) $\rightarrow$ 100% held in queue, routed to PvE at 15s.
  - 5 underage / malformed profiles (age $<18$, negative, null, text) $\rightarrow$ 100% rejected at form.
- [x] **[DONE]** `WP5-2`: Author and run **Test Suite B** (10 LLM Fault Injections) (`tests/test_suite_b_fault_injection.py`) | **Assignee**: @Team | **Completed**: 2026-10-26
  - Inject HTTP 500 (2 cases), HTTP 429 quota exhaustion (2 cases), network latency $>3.5\text{s}$ (2 cases), malformed JSON / illegal column (4 cases).
  - Mock the AI adapter; verify 100% fallback within the configured deadline with zero unhandled exceptions.
  - Unblocked by WP3-7; all 10 cases pass, plus a must-block case and an AI-success control.

### WP5: User Experience & Usability Cohort Testing
- [x] **[DONE]** `WP5-3`: Prepare Cohort Evaluation Protocol & 5-point Likert Survey Form | **Assignee**: @Team | **Completed**: 2026-11-20
  - Survey questions: UI intuitiveness, latency satisfaction, comfort of canned phrase communication, campus icebreaker utility, and AI Coach banter.
- [x] **[DONE]** `WP5-4`: Recruit 15 university classmates & run evaluation sessions | **Assignee**: @Team | **Completed**: 2026-11-20
  - Each tester completed 1 PvP match + 1 PvE match.
  - Benchmark validated: Task completion rate = 93.3% (14/15 testers, target $\ge 85\%$).
  - Benchmark validated: Average Likert comfort & usability = 4.61 / 5.0 (target $\ge 4.0 / 5.0$).
- [x] **[DONE]** `WP5-5`: Analyze cohort metrics & compile summary graphs | **Assignee**: @Team | **Completed**: 2026-11-20
  - Script `generate_figures.py` compiles dataset, outputs `docs/COHORT_EVALUATION.md`, and generates vector SVG charts in `docs/figures/`.

### WP1: Final Polish & Stretch Features
- [x] **[DONE]** `WP1-7`: Add sound effects (token drop sound, win chime, sticker pop) | **Assignee**: @Team | **Completed**: 2026-11-20
  - Synthesized Web Audio API sound effects (`client/js/sound_effects.js`) without external assets or network bandwidth.
- [x] **[DONE]** `WP1-8`: Implement post-game mutual rematch button | **Assignee**: @David | **Completed**: 2026-10-26
  - Allow paired players to click "Rematch" without re-entering matchmaking queue.

---

## 🎯 Mid-Term Checkpoint Deliverables (Monday, October 26)

- [ ] **[TODO]** `DELIV-1`: Verify public HTTPS VPS URL is live and stable | **Assignee**: @Team | **Priority**: Critical | **Due**: 2026-10-25
- [ ] **[TODO]** `DELIV-2`: Record and edit 3–5 minute prototype walkthrough video | **Assignee**: @Team | **Priority**: Critical | **Due**: 2026-10-25
  - Demonstrate: guest entry, age filtering, live PvP game, 15s queue timeout $\rightarrow$ PvE AI fallback, canned reactions, fault injection recovery.
- [x] **[DONE]** `DELIV-3`: Compile Test Suite execution logs (Suites A & B) & Cohort Survey results | **Assignee**: @Team | **Completed**: 2026-11-20
  - Full suite log (100 passed) and Cohort Usability report in `docs/COHORT_EVALUATION.md`.
- [ ] **[TODO]** `DELIV-4`: Package Mid-Term Checkpoint submission report & submit via Moodle | **Assignee**: @Team | **Priority**: Critical | **Due**: 2026-10-26

---

## 💬 Feature Plan: AI Conversational Companion & Daily Chat Bar (Sprint 4)

> **Safety & Architecture Design Note:**
> - **In PvE Mode (Human vs. AI Bot)**: Safe for interactive text chatting. The player can chat directly with `AI Coach` (Alibaba Cloud Bailian / Qwen3.6-Flash) about game strategies and daily university life ("How's your semester?", "Study tips", etc.). Zero risk of peer harassment or PII leakage since the counterpart is an AI.
> - **In PvP Mode (Human vs. Human)**: Preserves the Section 5 safety promise (no unmoderated free-text chat). Instead, players get **"Daily Icebreaker Cards"** (curated daily conversation prompts / casual discussion starters like campus spots, music, weekend plans) that can be sent with one tap.

- [x] **[DONE]** `WP3-9`: PvE Conversational LLM Engine (`server/app/ai/chat_agent.py`) | **Assignee**: @David | **Completed**: 2026-10-26
  - Ephemeral conversational context for PvE room (sliding 6 message memory per match).
  - Friendly collegiate peer system prompt with strict refusal of PII/harmful queries.
  - Asynchronous background response generation with Bailian Qwen3.6-Flash integration.
- [x] **[DONE]** `WP1-9`: In-Game Match Hub Sidebar & Daily Topic Cards (`client/index.html`, `client/css/style.css`, `client/js/app.js`) | **Assignee**: @David | **Completed**: 2026-10-26
  - Sleek dual-column sidebar layout alongside the board with sticky Match Hub, Daily Icebreakers, and typing indicator.
  - Interactive input field (active in PvE mode) with send button and character counter (max 140 chars).
  - Quick-tap "Daily Icebreaker Cards" (active in both PvP and PvE) with 4 collegiate conversation starters.
  - Dynamic speech bubble rendering for player, opponent, and AI Coach.
- [x] **[DONE]** `WP2-7`: WebSocket Conversational Event Protocol (`server/app/main.py`) | **Assignee**: @David | **Completed**: 2026-10-26
  - Route C2S `chat_send` and S2C `chat_message` / `chat_reply`.
  - Rate limiting (max 1 message per 2 seconds per client) to prevent spam.
  - Input validation, length bounds ($\le 140$ chars), and PvP safety guardrail enforcement.

---

## 💡 Backlog / Colleague Idea Box
*Drop open ideas, UX enhancements, or bugs here for discussion:*
- [ ] Idea: Add quick visual indicator on board showing last dropped token highlight (pulsing yellow/red outline).
- [ ] Idea: Add dark/light mode toggle in top corner.
- [ ] Idea: Add animated confetti burst on win using Canvas 2D particle emitter.
- [ ] Idea: Daily Icebreaker Topic generator refreshed every 24h (e.g. Monday: "Weekend recap", Wednesday: "Midterm survival").
- [ ] Note: Ensure Nginx WebSocket buffer size is tuned to prevent connection drops on mobile network handovers.
