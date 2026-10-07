# ConnectFour Connect (AILT9019 G31) — Team Task Checklist

Welcome to the team task tracker! This document is designed for all team members to view, claim, update, and add development tasks as we build toward the **Mid-Term Checkpoint (Monday, October 26)**.

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
| **WP3: AI & Minimax** | Gemini 1.5 Flash & Heuristic | 6 | 1 | 0 | 🟢 Initialized (17%) |
| **WP4: Infrastructure & VPS**| Ubuntu VPS, Nginx SSL & WSS | 4 | 1 | 0 | 🟢 Configs Ready |
| **WP5: Testing & Evaluation**| Suites A & B, 15-User Cohort | 6 | 1 | 0 | 🟢 Engine Tests Pass |

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
- [x] **[DONE]** `WP1-5`: Construct Canned Social Reaction Tray (`client/js/canned_chat.js`) | **Assignee**: @Team | **Due**: 2026-10-07
  - 6 preset phrases: *"Good luck!"*, *"Nice move!"*, *"Thinking..."*, *"Close one!"*, *"Well played!"*, *"Good game!"*.
  - 4 reaction stickers: 👍, 👏, 🤔, 🎉.
  - Floating speech bubbles above player avatars.
- [x] **[DONE]** `WP1-6`: Build 1-minute Onboarding & Guest Registration modal | **Assignee**: @Team | **Due**: 2026-10-07
  - Form inputs: Nickname (2–16 chars) and Birth Year ($\ge 18$ check).
  - Simple rules graphic explaining column clicking and 4-in-a-row goal.

### WP2: Backend Networking & Local Room Management
- [x] **[DONE]** `WP2-1`: Initialize backend structure (`server/requirements.txt`, `server/app/main.py`) | **Assignee**: @Team | **Due**: 2026-10-07
  - FastAPI app with CORS middleware, static file mounting, Uvicorn server.
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

### WP3: AI Agent & Heuristic Fallback
- [x] **[DONE]** `WP3-1`: Implement local deterministic Minimax bot (`server/app/ai/minimax_fallback.py`) | **Assignee**: @Team | **Due**: 2026-10-07
  - Minimax with Alpha-Beta pruning (depth 4).
  - Evaluation weights: 4-in-row (+100,000), 3-in-row (+500), 2-in-row (+50), center control (+30).
  - Benchmark execution time verified at ~23.6ms (<50ms target).
- [ ] **[TODO]** `WP3-2`: Integrate Google Gemini 1.5 Flash client (`server/app/ai/gemini_client.py`) | **Assignee**: @Unassigned | **Priority**: Critical | **Due**: 2026-10-15
  - Connect via official SDK (`google-genai`) using server environment API key.
  - Board state serialization into structured prompt.
  - Enforce strict JSON output schema: `{"column": int, "canned_reaction_id": int}`.
- [ ] **[TODO]** `WP3-3`: Build 1.5-second Timeout & Fallback Orchestration wrapper | **Assignee**: @Unassigned | **Priority**: Critical | **Due**: 2026-10-16
  - Race Gemini request against 1.5s `asyncio.wait_for`.
  - Fall back to Minimax immediately if Gemini times out, returns HTTP 429/500, or picks an invalid column.
  - Emit `pve_fallback_notice` toast event to client.
- [ ] **[TODO]** `WP3-4`: Dual bot personalities stretch feature (`server/app/ai/`) | **Assignee**: @Unassigned | **Priority**: Low | **Due**: 2026-10-18
  - "Casual Explorer" (relaxed depth, frequent reaction stickers) vs. "Tactical Challenger" (depth 5, strategic play).

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
- [ ] **[TODO]** `WP4-3`: Configure Systemd daemon (`deploy/connectfour.service`) | **Assignee**: @Unassigned | **Priority**: Medium | **Due**: 2026-10-15
  - Enable auto-restart on failure, log rotation in `/var/log/connectfour`.
- [ ] **[TODO]** `WP4-4`: Verify zero-configuration public URL access | **Assignee**: @Unassigned | **Priority**: Critical | **Due**: 2026-10-16
  - Test game loads on mobile Safari, Android Chrome, and desktop browsers without login/keys.

---

## 🧪 Sprint 3: Week 8 — Automated Testing, Evaluation & Polish (Oct 19 – Oct 25)

### WP5: Automated Test Suites
- [ ] **[TODO]** `WP5-1`: Author and run **Test Suite A** (20 Age Boundary Pairs) (`tests/test_suite_a_matchmaking.py`) | **Assignee**: @Unassigned | **Priority**: Critical | **Due**: 2026-10-20
  - 10 valid pairs ($|\Delta\text{Age}| \le 3$, Age $\ge 18$) $\rightarrow$ 100% paired PvP within 15s.
  - 5 age-gap refused pairs ($|\Delta\text{Age}| > 3$) $\rightarrow$ 100% held in queue, routed to PvE at 15s.
  - 5 underage / malformed profiles (age $<18$, negative, null, text) $\rightarrow$ 100% rejected at form.
- [ ] **[TODO]** `WP5-2`: Author and run **Test Suite B** (10 LLM Fault Injections) (`tests/test_suite_b_fault_injection.py`) | **Assignee**: @Unassigned | **Priority**: Critical | **Due**: 2026-10-22
  - Inject HTTP 500 (2 cases), HTTP 429 quota exhaustion (2 cases), network latency $>3.5\text{s}$ (2 cases), malformed JSON / illegal column (4 cases).
  - Verify 100% fallback to Minimax in $<1.5\text{s}$ with zero unhandled exceptions.

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
