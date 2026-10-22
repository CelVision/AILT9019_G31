# ConnectFour Connect (AILT9019 G31) — Team Task Checklist

Welcome to the team task tracker! This document is designed for all team members to view, claim, update, and add development tasks as we build toward the **Mid-Term Checkpoint (Monday, October 26)**.

**Last updated:** 2026-10-22 · **Detailed worklog:** [docs/WORKLOG.md](file:///d:/Github%20Homepage/AILT9019_G31/docs/WORKLOG.md)

## 🗞️ Recent Updates

- **2026-10-22** — Model/API confirmed: config now uses the official API ID `glm-4.7-flash` (display name GLM-4.7-Flash), with thinking disabled for fast JSON game moves. Live verification of the new model is currently blocked by provider `429 / code 1302` rate limiting.
- **2026-10-22** — Pre-push evaluation complete: **26 tests pass**, `server/.env` is ignored, and the live key is absent from tracked files. The old-model (`glm-4-flash`) smoke succeeded at **1737.9ms**, but provider `429 / code 1302` rate limiting still blocks a successful in-game turn. Local/code timeout is **2.5s**; the technical spec still says 1.5s (WP3-8). See the [worklog](file:///d:/Github%20Homepage/AILT9019_G31/docs/WORKLOG.md).
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
| **WP1: Frontend Client** | HTML5/Canvas UI & Canned Chat | 8 | 4 | 0 | 🟢 Underway (50%) |
| **WP2: Backend Networking** | FastAPI, WebSockets & Queue | 7 | 3 | 0 | 🟢 Underway (43%) |
| **WP3: AI & GLM** | GLM-4.7-Flash, model config & fallback | 8 | 3 | 1 | 🟡 GLM-first (38%, WP3-3 in review) |
| **WP4: Infrastructure & VPS**| Ubuntu VPS, Nginx SSL & WSS | 4 | 1 | 0 | 🟢 Configs Ready |
| **WP5: Testing & Evaluation**| Suites A & B, 15-User Cohort | 6 | 1 | 0 | 🟢 Engine Tests Pass |

> Quick Wins are tracked separately below and are **not** included in these totals.

---

> **⚠️ AI Direction Update — 2026-10-22 (GLM-first, no Gemini, Minimax deferred)**
> - PvE calls **GLM-4.7-Flash** directly through an OpenAI-compatible endpoint, using a **server-side key**. Gemini is deferred and is not part of the current sprint.
> - The client may let the player enter or select a **model name** (default API ID `glm-4.7-flash`). The server validates it against an allowlist; the key is never sent to the client.
> - **Minimax is deliberately not wired during initial GLM testing.** This is a temporary deviation from `TECH_SPEC §5.2`. WP3-7 restores it before the checkpoint, or the deviation must be documented in the checkpoint report.
> - Keys live only in `server/.env` locally and `/etc/connectfour/connectfour.env` on the VPS. Never commit, log, or send a key to the browser.
> - **Old live check (2026-10-21, `glm-4-flash`):** the key was accepted and one move returned in **1737.9ms**. The 1.5s hard cap would reject it, so the code default and local `.env` use 2.5s pending a spec decision.
> - **Model update (2026-10-22):** official API model ID is `glm-4.7-flash` (display name GLM-4.7-Flash). Thinking is explicitly disabled for game moves. Live verification of the new model is currently blocked by provider `429 / code 1302` account rate limiting.
> - Test Suite B is deferred until the fallback path is restored; its 10 cases will mock the GLM adapter.

---

## 🟢 Quick Wins for Teammates (Oct 21–25)

Small, low-risk tasks that can be picked up without touching the GLM integration. Claim one with the normal `[IN PROGRESS]` workflow.

| ID | Task | Status | Effort | Priority | Files | Acceptance Criteria |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **QW-1** | Fix static assets served from `/` | ✅ DONE (10-21) | 15 min | Critical | `server/app/main.py` | `http://127.0.0.1:8000/` loads CSS/JS with HTTP 200; `/ws/game` still works |
| **QW-2** | Set `--workers 1` and move the env file outside the repo | ✅ DONE (10-21) | 10 min | Critical | `deploy/connectfour.service` | Service starts with `/etc/connectfour/connectfour.env`; rooms/queue stay consistent |
| **QW-3** | Add touch/pointer column selection | ⬜ TODO | 30 min | High | `client/js/game_board.js` | Tapping a column drops a token on iOS/Android; desktop hover unchanged |
| **QW-4** | Validate `queue_join` server-side and return an `error` frame | ⬜ TODO | 45 min | High | `server/app/main.py`, `client/js/app.js` | Underage, malformed birth year, and nickname length 2–16 get a clear inline error; no silent drop |
| **QW-5** | Emit `queue_status` every second | ⬜ TODO | 30 min | Medium | `server/app/main.py`, `client/js/app.js` | UI countdown matches server `elapsed_seconds` / `timeout_seconds` |
| **QW-6** | Highlight the last dropped token | ⬜ TODO | 30 min | Low | `client/js/game_board.js`, `client/js/app.js` | Last token pulses; highlight clears on the next move |

**Completion notes (2026-10-21):** QW-1 is verified by `tests/test_app_smoke.py` (root HTML, CSS, JS, `/api/health`, `/ws/game`). QW-2 is updated in the repo; applying it on the VPS and confirming the service restart is still pending.

**Already on the board and easy to close:** `WP1-4` (timer bar is already built — verify and mark done), `WP4-2`/`WP4-3` (configs exist — apply and verify), `WP5-3` (survey, non-code), `WP1-7` (sound, low priority). **Do not treat as quick wins:** `WP1-8` (rematch), `WP5-1` (Suite A), `WP2-3` (room manager extraction), `WP3-6` (model selector touches both client and server).

---

## 🚀 Sprint 1: Week 6 — Core Foundation & Local MVP (Oct 5 – Oct 11)

### WP0: Proposal Finalization
- [x] **[DONE]** `WP0-1`: Author revised proposal markdown with all 7 reviewer responses ([docs/proposal/](file:///d:/Github%20Homepage/AILT9019_G31/docs/proposal/AILT9019_Revised_Proposal_G31.md)) | **Assignee**: @Team | **Due**: 2026-10-07
- [x] **[DONE]** `WP0-2`: Generate Project Plan ([docs/PROJECT_PLAN.md](file:///d:/Github%20Homepage/AILT9019_G31/docs/PROJECT_PLAN.md)) and Technical Specification ([docs/TECHNICAL_SPEC.md](file:///d:/Github%20Homepage/AILT9019_G31/docs/TECHNICAL_SPEC.md)) | **Assignee**: @Team | **Due**: 2026-10-07
- [ ] **[TODO]** `WP0-3`: Final proofread and submission of Revised Proposal PDF via Moodle form | **Assignee**: @Team | **Priority**: Critical | **Due**: 2026-10-10 (Sat)
  - Verify all student IDs, group info, and word counts comply with template.

### WP1: Frontend Client (HTML5 / Canvas 2D)
- [x] **[DONE]** `WP1-1`: Create client scaffolding (`client/index.html`, `client/css/style.css`, `client/js/app.js`) | **Assignee**: @Team | **Due**: 2026-10-07
  - Modern dark-mode layout, responsive container for mobile/desktop.
- [x] **[DONE]** `WP1-2`: Implement HTML5 Canvas 7×6 Connect Four board renderer (`client/js/game_board.js`) | **Assignee**: @Team | **Due**: 2026-10-07
  - Draw 7 columns × 6 rows, empty circular slots, hover column indicator.
- [ ] **[TODO]** `WP1-3`: Implement token drop animation with gravity physics | **Assignee**: @Unassigned | **Priority**: Medium | **Due**: 2026-10-10
  - Smooth vertical descent with bounce/easing effect into destination cell.
- [ ] **[TODO]** `WP1-4`: Build 30-second turn countdown timer bar & active player badge | **Assignee**: @Unassigned | **Priority**: High | **Due**: 2026-10-10
  - Turn indicator ("Your Turn" vs. "Opponent's Turn") with shrinking timer bar.
  - **Status note:** the visual bar already exists in `client/js/app.js` and `client/index.html`; remaining work is mobile verification and closing the task. Server-side enforcement is separate.
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
- [ ] **[TODO]** `WP2-3`: Implement In-Memory Room Manager (`server/app/room_manager.py`) | **Assignee**: @Unassigned | **Priority**: High | **Due**: 2026-10-10
  - Thread-safe room creation, player pairing, turn rotation, clean room destruction on disconnect.
- [x] **[DONE]** `WP2-4`: WebSocket Game Gateway (`server/app/main.py` -> `/ws/game`) | **Assignee**: @Team | **Due**: 2026-10-07
  - Handle `queue_join`, `player_move`, `send_reaction`, disconnect events.
  - Local 2-player tab testing support with in-memory matchmaking pool.

---

## ⚡ Sprint 2: Week 7 — AI Integration, Matchmaking & VPS (Oct 12 – Oct 18)

### WP3: AI Agent & GLM Integration
- [x] **[DONE]** `WP3-1`: Implement local deterministic Minimax bot (`server/app/ai/minimax_fallback.py`) | **Assignee**: @Team | **Due**: 2026-10-07
  - Minimax with Alpha-Beta pruning (depth 4).
  - Evaluation weights: 4-in-row (+100,000), 3-in-row (+500), 2-in-row (+50), center control (+30).
  - Benchmark execution time verified at ~23.6ms (<50ms target).
  - **Current status:** code complete and tested, but intentionally not wired while GLM is validated directly (see WP3-7).
- [x] **[DONE]** `WP3-2`: Integrate **GLM-4.7-Flash** client (`server/app/ai/glm_client.py`) | **Assignee**: @Team | **Priority**: Critical | **Due**: 2026-10-23
  - Call the Zhipu/Z.ai OpenAI-compatible `/chat/completions` endpoint with `httpx`; no Gemini SDK.
  - Read `GLM_API_KEY`, `GLM_BASE_URL`, `GLM_MODEL` from the server environment only.
  - Serialize board + legal columns; enforce JSON `{"column": int, "canned_reaction_id": int}`; validate the column against legal moves.
  - Include a standalone smoke test (`python -m app.ai.glm_client`) that prints one move and its latency.
  - **2026-10-21 (old model `glm-4-flash`):** client, prompt, JSON parsing/validation, and mock transport tests are implemented (10 mocked tests pass). **Live smoke test passed:** `{"column": 3, "latency_ms": 1737.9, "model": "glm-4-flash"}`. Gateway wiring is under WP3-3.
  - **2026-10-22:** provider confirmed the base URL. Config switched to the official API ID `glm-4.7-flash` (display name GLM-4.7-Flash), and the request now sets `thinking: {"type": "disabled"}` for fast JSON moves. Retested after the update; still blocked by `429 / code 1302` account rate limiting.
  - Provider note: rapid calls returned `HTTP 429 / code 1302` (account rate limit); later 90s cooldowns still returned 429. The z.ai endpoint returned the same 429, so it is account-level. No retry/backoff is implemented yet.
- [ ] **[REVIEW]** `WP3-3`: Build GLM timeout & orchestration wrapper (fallback deferred) | **Assignee**: @Team | **Priority**: Critical | **Due**: 2026-10-23
  - Race the GLM request against `AI_TIMEOUT_SECONDS` (technical spec says 1.5s; code default and local env are now 2.5s after the 1.74s measurement — update the spec or reverse this).
  - On timeout/HTTP error/malformed JSON/illegal column, play a temporary safe legal move (center-out) so the room never stalls; do **not** call Minimax yet.
  - Emit `pve_fallback_notice` with a non-secret reason. Restore the Minimax path in WP3-7 before Oct 26.
  - **2026-10-21:** wired into `handle_ai_turn`; mocked GLM-success, GLM-error, and wait-for-timeout tests pass. **Live fallback verified:** GLM returned `429` once (handler time 1081.9ms) and a later call exceeded the 2.5s cap (handler time 2917.8ms); both fell back to the center move and passed the turn. A **successful in-game GLM turn is still pending** because of the account rate limit. A 1.5s cap would cancel the measured 1.74s smoke response; local `.env` uses 2.5s, which also timed out once. Decide 3–4s vs. optimize vs. accept fallback.
- [ ] **[TODO]** `WP3-4`: Dual bot personalities stretch feature (`server/app/ai/`) | **Assignee**: @Unassigned | **Priority**: Low | **Due**: 2026-10-24
  - "Casual Explorer" (relaxed depth, frequent reaction stickers) vs. "Tactical Challenger" (depth 5, strategic play).
  - Deferred until the GLM path is stable.
- [x] **[DONE]** `WP3-5`: Add `config.py`, `.env.example`, and secret-hygiene rules | **Assignee**: @Team | **Priority**: Critical | **Due**: 2026-10-21
  - Load `.env` with `python-dotenv`; fail closed when `GLM_API_KEY` is absent (PvE disabled or local mode).
  - Broaden `.gitignore` to `.env*` with `!.env.example`; never log or echo the key.
  - Completed 2026-10-21: added `server/app/config.py`, `server/.env.example`, package `__init__.py` files, and `tests/test_app_smoke.py`; removed unused `google-genai`.
  - Verified: no-key → `enabled=False`; dummy-key → allowlist/timeout parsed; `.env.example` is not ignored.
- [ ] **[TODO]** `WP3-6`: Add optional model-name selector + server allowlist | **Assignee**: @Unassigned | **Priority**: High | **Due**: 2026-10-22
  - Onboarding field defaults to `glm-4.7-flash`; the server accepts only allowlisted names.
  - Invalid model returns a clear error; never forward arbitrary strings to the provider.
- [ ] **[TODO]** `WP3-7`: Re-enable Minimax fallback before the checkpoint | **Assignee**: @Unassigned | **Priority**: High | **Due**: 2026-10-24
  - Restore the `pve_fallback_notice` + Minimax path after GLM validation; then run Suite B.
  - If intentionally skipped, record the deviation in the checkpoint report and demo notes.
- [ ] **[TODO]** `WP3-8`: Update AI references in README, TECH_SPEC, and PROJECT_PLAN (Gemini → GLM; deferred Minimax) | **Assignee**: @Unassigned | **Priority**: High | **Due**: 2026-10-24
  - Keep the formal docs consistent with the provider actually implemented; record the deviation.

### WP2: Age-Gated Matchmaking Queue
- [ ] **[TODO]** `WP2-5`: Implement in-memory FIFO Matchmaking Queue (`server/app/matchmaking.py`) | **Assignee**: @Unassigned | **Priority**: High | **Due**: 2026-10-14
  - Enforce age boundary: $\text{Age} \ge 18$.
  - Enforce age gap constraint: $|\text{Age}_A - \text{Age}_B| \le 3$.
- [ ] **[TODO]** `WP2-6`: Implement 15-second Queue Timeout & PvE Routing | **Assignee**: @Unassigned | **Priority**: High | **Due**: 2026-10-15
  - If no human peer matches within 15 seconds, pop user and seamlessly launch PvE room with AI bot.

### WP4: DevOps & Cloud Infrastructure
- [ ] **[TODO]** `WP4-1`: Provision Ubuntu Linux VPS instance & install dependencies | **Assignee**: @Unassigned | **Priority**: High | **Due**: 2026-10-13
  - Python 3.12+, Uvicorn, Nginx, Git, Certbot.
- [ ] **[TODO]** `WP4-2`: Configure Nginx reverse proxy with SSL & WebSocket upgrades | **Assignee**: @Unassigned | **Priority**: High | **Due**: 2026-10-14
  - Enable Let's Encrypt SSL (HTTPS and WSS).
  - Proxy `ws://127.0.0.1:8000/ws` to `wss://<domain>/ws`.
  - **Status note:** `deploy/nginx.conf` is ready; remaining work is applying it on the VPS and issuing the certificate.
- [ ] **[TODO]** `WP4-3`: Configure Systemd daemon (`deploy/connectfour.service`) | **Assignee**: @Unassigned | **Priority**: Medium | **Due**: 2026-10-15
  - Enable auto-restart on failure, log rotation in `/var/log/connectfour`.
  - **Status note:** the unit file exists; apply QW-2 (`--workers 1`, env file path) before enabling it.
- [ ] **[TODO]** `WP4-4`: Verify zero-configuration public URL access | **Assignee**: @Unassigned | **Priority**: Critical | **Due**: 2026-10-16
  - Test game loads on mobile Safari, Android Chrome, and desktop browsers without login/keys.

---

## 🧪 Sprint 3: Week 8 — Automated Testing, Evaluation & Polish (Oct 19 – Oct 25)

### WP5: Automated Test Suites
- [ ] **[TODO]** `WP5-1`: Author and run **Test Suite A** (20 Age Boundary Pairs) (`tests/test_suite_a_matchmaking.py`) | **Assignee**: @Unassigned | **Priority**: Critical | **Due**: 2026-10-20
  - 10 valid pairs ($|\Delta\text{Age}| \le 3$, Age $\ge 18$) $\rightarrow$ 100% paired PvP within 15s.
  - 5 age-gap refused pairs ($|\Delta\text{Age}| > 3$) $\rightarrow$ 100% held in queue, routed to PvE at 15s.
  - 5 underage / malformed profiles (age $<18$, negative, null, text) $\rightarrow$ 100% rejected at form.
- [ ] **[BLOCKED]** `WP5-2`: Author and run **Test Suite B** (10 LLM Fault Injections) (`tests/test_suite_b_fault_injection.py`) | **Assignee**: @Unassigned | **Priority**: Critical | **Due**: 2026-10-22
  - Inject HTTP 500 (2 cases), HTTP 429 quota exhaustion (2 cases), network latency $>3.5\text{s}$ (2 cases), malformed JSON / illegal column (4 cases).
  - Mock the GLM adapter; verify 100% fallback in $<1.5\text{s}$ with zero unhandled exceptions.
  - **Blocked** until WP3-7 restores the Minimax path.

### WP5: User Experience & Usability Cohort Testing
- [ ] **[TODO]** `WP5-3`: Prepare Cohort Evaluation Protocol & 5-point Likert Survey Form | **Assignee**: @Unassigned | **Priority**: High | **Due**: 2026-10-21
  - Survey questions: UI intuitiveness, latency satisfaction, comfort of canned phrase communication, comparison to text chat.
- [ ] **[TODO]** `WP5-4`: Recruit 15 university classmates & run evaluation sessions | **Assignee**: @Team | **Priority**: High | **Due**: 2026-10-23
  - Each tester completes 1 PvP match + 1 PvE match.
  - Validate benchmark: Task completion rate $\ge 85\%$ (at least 13/15 testers).
  - Validate benchmark: Average Likert comfort & usability $\ge 4.0 / 5.0$.
- [ ] **[TODO]** `WP5-5`: Analyze cohort metrics & compile summary graphs | **Assignee**: @Unassigned | **Priority**: Medium | **Due**: 2026-10-24

### WP1: Final Polish & Stretch Features
- [ ] **[TODO]** `WP1-7`: Add sound effects (token drop sound, win chime, sticker pop) | **Assignee**: @Unassigned | **Priority**: Low | **Due**: 2026-10-24
- [ ] **[TODO]** `WP1-8`: Implement post-game mutual rematch button | **Assignee**: @Unassigned | **Priority**: Medium | **Due**: 2026-10-24
  - Allow paired players to click "Rematch" without re-entering matchmaking queue.

---

## 🎯 Mid-Term Checkpoint Deliverables (Monday, October 26)

- [ ] **[TODO]** `DELIV-1`: Verify public HTTPS VPS URL is live and stable | **Assignee**: @Team | **Priority**: Critical | **Due**: 2026-10-25
- [ ] **[TODO]** `DELIV-2`: Record and edit 3–5 minute prototype walkthrough video | **Assignee**: @Team | **Priority**: Critical | **Due**: 2026-10-25
  - Demonstrate: guest entry, age filtering, live PvP game, 15s queue timeout $\rightarrow$ PvE AI fallback, canned reactions, fault injection recovery.
- [ ] **[TODO]** `DELIV-3`: Compile Test Suite execution logs (Suites A & B) & Cohort Survey results | **Assignee**: @Team | **Priority**: High | **Due**: 2026-10-26
- [ ] **[TODO]** `DELIV-4`: Package Mid-Term Checkpoint submission report & submit via Moodle | **Assignee**: @Team | **Priority**: Critical | **Due**: 2026-10-26

---

## 💡 Backlog / Colleague Idea Box
*Drop open ideas, UX enhancements, or bugs here for discussion:*
- [ ] Idea: Add quick visual indicator on board showing last dropped token highlight (pulsing yellow/red outline).
- [ ] Idea: Add dark/light mode toggle in top corner.
- [ ] Idea: Add animated confetti burst on win using Canvas 2D particle emitter.
- [ ] Note: Ensure Nginx WebSocket buffer size is tuned to prevent connection drops on mobile network handovers.
