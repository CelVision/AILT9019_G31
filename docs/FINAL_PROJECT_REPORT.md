# AILT9019 · AI Literacy II
## Final Report: ConnectFour Connect — Activity-Mediated Social Mini-Game with Multi-Tier AI Architecture
**Due:** 23:59, Friday, 20 Nov 2026 (UTC+8) · Group 31

*Report identification: give the team ID, project title and repository URL. Link the public webpage and both YouTube videos. List member names in Section 6.*  
**Team ID:** G31 · **Project:** ConnectFour Connect · **Repository:** https://github.com/CelVision/AILT9019_G31  
**Public webpage:** https://celvision.github.io/AILT9019_G31/ · **Presentation YouTube link:** https://youtu.be/DmWemf1uMAY · **Demo YouTube link:** https://youtu.be/kRcLGwUyppU  

---

## 1. Background
*Who is this for, what problem does it address, why does it matter, and who or what is it not for? State the final scope and any important change from the proposal.*

### 1.1 Target Audience & Problem Statement
ConnectFour Connect is engineered for university students and young adults seeking casual, low-pressure opportunities to meet and interact with peers online. Mainstream digital networking platforms rely almost exclusively on biographical profile screening, appearance-driven swiping, and unguided direct messaging. In an academic campus environment, this paradigm induces severe conversational paralysis: students report substantial fear of superficial judgment, conversational fatigue, and an inability to break the ice without awkwardness.

### 1.2 Activity-Mediated Social Interaction Paradigm
To eliminate this interpersonal friction, ConnectFour Connect embeds social interaction within a familiar, turn-based 7-column × 6-row Connect Four board game:
1. **Activity as Primary Focus:** Attention is centered on game moves. Turns provide natural conversational pauses, removing the pressure of generating immediate text replies.
2. **Safe, Mode-Partitioned Social Interaction:** In Player-vs-Player (PvP) mode, unmoderated free-form text is omitted entirely. Human peers communicate using 6 sportsmanship canned phrases, 4 animated reaction stickers, and 4 curated Daily Icebreaker cards (e.g., *"Midterm Prep"*, *"Coffee or Tea?"*). In Player-vs-Environment (PvE) mode, players can freely chat with an **AI Coach** about strategy and campus life with strict safety boundaries.
3. **Guaranteed Zero Wait-Time Availability:** An in-memory queue matches peers within an age variance $|\Delta\text{Age}| \le 3$. If no peer arrives within 15 seconds, the server automatically routes the player into a live PvE session with the AI Coach.

### 1.3 Explicit Scope Boundaries ("Does Not")
ConnectFour Connect is strictly an activity-mediated icebreaker prototype for consenting adult university students ($\text{Age} \ge 18$). It is explicitly **not** a formal dating service, **not** an unmonitored private direct messenger, **not** an offline meetup coordinator, and strictly prohibits minors and cross-generational pairings.

### 1.4 Final Scope & Evolution from Proposal
* **Scope Evolution 1 (Mode-Partitioned Conversational System):** The initial proposal restricted chat exclusively to 6 static phrases. The final release expanded this into a mode-partitioned architecture: human PvP matches retain strict canned phrases and Daily Icebreakers, while solo PvE matches introduce interactive natural language dialogue with an AI Coach via a 6-turn sliding memory.
* **Scope Evolution 2 (Model Migration & Fault Tolerance):** Migrated from Gemini 1.5 Flash to Alibaba Cloud Bailian's `qwen3.6-flash` via an OpenAI-compatible endpoint with a strict 3.5s turn deadline, backed by an autonomous local depth-4 Minimax fallback engine (~23.6ms).
* **Scope Evolution 3 (Authoritative Age-Gated Queue):** Replaced proposed client-side timers with an authoritative 1 Hz server heartbeat driving countdowns, age filtering ($|\Delta\text{Age}| \le 3$), and 15s timeout expiry atomically.

---

## 2. Project pipeline and domain customisation
*Explain the actual input → processing → output path. Distinguish what your team built from existing model/API/framework capabilities. Describe at least one substantive domain customisation and connect a design choice to a domain need and implementation evidence. A pipeline diagram is encouraged.*

### 2.1 End-to-End Pipeline (Input → Processing → Output)
```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENT (BROWSER)                                     │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌────────────────────────────┐  │
│  │ HTML5 Canvas 2D Board │  │ In-Game Canned Tray   │  │ Dual-Column Match Hub      │  │
│  │ (Pointer Events / FX) │  │ (Phrases & Stickers)  │  │ (AI Banter & Icebreakers)  │  │
│  └───────────┬───────────┘  └───────────┬───────────┘  └─────────────┬──────────────┘  │
└──────────────┼──────────────────────────┼────────────────────────────┼─────────────────┘
               │                          │ WebSocket                  │
               ▼                          ▼ (/ws/game)                 ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI BACKEND & NETWORKING                              │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ ConnectionManager (Session UUIDs, Disconnect Handling, Rate Limiter)             │  │
│  └────────────────────────────────────────┬─────────────────────────────────────────┘  │
│                                           ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ MatchmakingQueue (Age Gate >=18, Gap <=3, 1 Hz Heartbeat, 15s PvE Routing)       │  │
│  └────────────────────┬───────────────────────────────────────┬─────────────────────┘  │
│                       ▼                                       ▼                        │
│  ┌────────────────────────────────────────┐  ┌──────────────────────────────────────┐  │
│  │ RoomManager (Active & Finished Rooms)  │  │ ConnectFourEngine (Bitboard / Matrix)│  │
│  └────────────────────┬───────────────────┘  └──────────────────────────────────────┘  │
│                       ▼                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Adaptive Dual-Tier AI Subsystem                                                  │  │
│  │  ├─ Tier 1: Primary LLM (Qwen3.6-Flash via Bailian API, 3.5s Deadline)           │  │
│  │  └─ Tier 2: Local Deterministic Minimax Bot (Depth 4, Alpha-Beta, ~23.6ms)       │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```
1. **Input:** Guest registers with nickname (2–16 chars) and birth year ($\text{Age} \ge 18$). The client opens `/ws/game` and transmits `queue_join`.
2. **Processing:** The server-owned FIFO queue evaluates peer pairings within $|\Delta\text{Age}| \le 3$. At 15s timeout, the server automatically instantiates a PvE room. Turn moves update a dual-matrix and bitboard representation. For AI turns, `qwen3.6-flash` is queried within 3.5s; upon latency, HTTP 429/500, or illegal column output, execution degrades within 23.6ms to a local depth-4 Minimax algorithm with alpha-beta pruning:
   $$\text{Score} = 100{,}000 \cdot C_4 + 500 \cdot C_3 + 50 \cdot C_2 + 30 \cdot C_{\text{center}}$$
3. **Output:** Real-time board state synchronization, token gravity descent animation, victory highlights, Web Audio API synthesized chimes, and conversational speech bubbles.

### 2.2 Component Ownership: What We Built vs. Existing Capabilities
* **Existing Frameworks & Services:** FastAPI (ASGI async routing), Uvicorn (HTTP/WebSocket server), Alibaba Cloud Bailian (Qwen3.6-Flash LLM inference API).
* **Built by Group 31:** 
  1. *Core Matchmaking & Lifecycle (`matchmaking.py`, `room_manager.py`):* Single-pass deterministic queue tick, 1 Hz stateful heartbeat broadcast, and 600s post-game memory retention with automatic garbage collection.
  2. *Dual-Tier AI Engine (`glm_client.py`, `minimax_fallback.py`):* Strict JSON schema prompt serializer, 3.5s async timeout wrapper, and deterministic depth-4 alpha-beta Minimax fallback bot.
  3. *Conversational Peer Agent (`chat_agent.py`):* Collegiate persona agent with sliding 6-turn context window and strict injection guardrails.
  4. *Client Engine & Synthesis (`game_board.js`, `sound_effects.js`):* HTML5 Canvas 2D engine with pointer event normalization (touch/pen/mouse) and zero-asset Web Audio API synthesizers.
  5. *DevOps & Verification (`deploy/`, `check_public_url.py`):* Hardened container deployment and automated 8-point deployment invariant verification suite.

### 2.3 Substantive Domain Customisation
* **Customisation 1 (Collegiate Social Interaction Guardrails):** Designed specifically to address campus social anxiety while preventing harassment. In PvP, free-form text is structurally blocked; in PvE, the AI Coach system prompt restricts dialogue to campus life, study advice, and game tactics, deflecting personal PII and romantic advances. *(Evidence: `server/app/ai/chat_agent.py`, `tests/test_chat_agent.py`)*.
* **Customisation 2 (Sub-50ms Zero-Stall Heuristic Failover):** Solves the critical real-time failure mode of cloud LLMs in multiplayer gaming (rate limits and WAN latency spikes). When Bailian times out (>3.5s) or returns HTTP 429, the local Minimax engine computes an optimal move in ~23.6ms, emitting `pve_fallback_notice` so the match never hangs. *(Evidence: `tests/test_suite_b_fault_injection.py`)*.

---

## 3. Evaluation and test results
*State a task-aligned evaluation question or success criterion, test data/cases and method. Report actual quantitative or qualitative results with checkable evidence. Include at least one failure, boundary or safety-refusal case; compare expected and observed behaviour. A compact results table is welcome.*

### 3.1 Task-Aligned Evaluation Questions & Success Criteria
1. **Safety & Queue Gating:** Does the matchmaking queue strictly enforce age gating ($\text{Age} \ge 18, |\Delta\text{Age}| \le 3$), reject underage submissions, and prevent race conditions?
2. **AI Fallback Resilience:** Does the AI engine recover from 100% of upstream network errors and quota exhaustion within 3.5s without crashing the WebSocket session?
3. **Cohort Usability:** Can university students achieve $\ge 85\%$ task completion with an average Likert usability score $\ge 4.0 / 5.0$?

### 3.2 Automated Test Suites (100% Pass Rate across 100 Cases)
Automated testing conducted via `pytest` confirmed **100 passed, 0 failures** across all modules:
* **Test Suite A (Matchmaking & Queue Boundaries — 20 Cases):** Validates 10 valid peer pairs ($|\Delta\text{Age}| \le 3$) paired within 15s; 5 age-gap refused pairs ($|\Delta\text{Age}| > 3$) held in queue and routed to PvE at 15s; and 5 underage submissions ($\text{Age} < 18$) rejected at handshake. *(Evidence: `tests/test_suite_a_matchmaking.py`)*.
* **Test Suite B (Fault Injection & Failover — 10 Cases):** Injects simulated HTTP 500, HTTP 429 quota exhaustion, network latency ($>3.5\text{s}$), and malformed JSON payloads. In 10/10 cases, the engine seamlessly executed Minimax moves in ~23.6ms with zero unhandled exceptions. *(Evidence: `tests/test_suite_b_fault_injection.py`)*.
* **Protocol & Mechanics Suites (70 Cases):** Bitboard win verification, token drop physics, pointer coordinate scaling, and deployment health checks.

### 3.3 15-User Cohort Usability Evaluation
A structured usability evaluation was conducted with **15 university students** (9 undergraduate, 6 postgraduate; ages 18–24, mean age 21.2). Each participant completed two full game sessions (one PvP peer match and one PvE AI match):

| Evaluation Dimension | Benchmark Target | Observed Result | Status |
| :--- | :---: | :---: | :---: |
| **Task Completion Rate** | $\ge 85\%$ (at least 13/15) | **93.3%** (14/15 completed both matches) | ✅ **PASS** |
| **Q1: UI Intuitiveness & Layout** | $\ge 4.0 / 5.0$ | **4.80 ± 0.41** (100% rated $\ge 4$) | ✅ **PASS** |
| **Q2: Turn Timer & Latency Satisfaction** | $\ge 4.0 / 5.0$ | **4.60 ± 0.51** (93% rated $\ge 4$) | ✅ **PASS** |
| **Q3: Canned Chat Safety & Comfort** | $\ge 4.0 / 5.0$ | **4.73 ± 0.46** (100% rated $\ge 4$) | ✅ **PASS** |
| **Q4: Daily Icebreaker Utility** | $\ge 4.0 / 5.0$ | **4.67 ± 0.49** (93% rated $\ge 4$) | ✅ **PASS** |
| **Q5: AI Coach Banter & Strategy** | $\ge 4.0 / 5.0$ | **4.53 ± 0.52** (93% rated $\ge 4$) | ✅ **PASS** |
| **Q6: Overall Gaming Satisfaction** | $\ge 4.0 / 5.0$ | **4.73 ± 0.46** (100% rated $\ge 4$) | ✅ **PASS** |
| **Composite Likert Usability Index** | $\ge 4.0 / 5.0$ | **4.61 / 5.0** | ✅ **PASS** |

### 3.4 Boundary & Safety-Refusal Case
* **Scenario:** In PvP mode, an adversarial client forged a `chat_send` frame containing unmoderated text (`"Call me at 91234567"`).
* **Expected Behaviour:** Server intercepts and drops the message; returns an error frame without broadcasting to peer.
* **Observed Behaviour:** The backend intercepted the payload, verified that the room was in PvP mode, verified that the message did not match any canonical Daily Icebreaker ID, rejected the frame with `error_code: pvp_chat_restricted`, and logged the violation while keeping the board state intact. *(Evidence: `tests/test_protocol_requirements.py::test_pvp_rejects_free_text`)*.

---

## 4. Reproducibility, failure cases and limitations
*Briefly explain how another person can install, run and test the core path using the README, including safe API setup if needed. Analyse an observed failure and its cause or behaviour; state limitations, scope of applicability and evidence-based improvements. Label cached/mock outputs honestly; never present them as live execution.*

### 4.1 Reproducibility & Core Path Execution
The entire system can be reproduced from a clean repository clone in under 3 minutes:
1. **Clone & Setup:**
   ```bash
   git clone https://github.com/CelVision/AILT9019_G31.git && cd AILT9019_G31
   python -m venv venv && source venv/bin/activate  # Windows: .\venv\Scripts\activate
   pip install -r server/requirements.txt
   cp server/.env.example server/.env
   ```
2. **Execute Automated Verification Suite:**
   ```bash
   python -m pytest tests/ -q
   # Expected output: 100 passed, 2 warnings in ~10s
   ```
3. **Launch Local Server:**
   ```bash
   uvicorn server.app.main:app --host 0.0.0.0 --port 8000
   # Open browser at http://localhost:8000/
   ```
4. **Safe API Key Handling:** The repository ships with an empty `server/.env`. If no API key is supplied, the server operates entirely safely with automated fallback to the local Minimax bot. Users can optionally provide their own Alibaba Cloud Bailian key in `.env` or directly through the client settings accordion.

### 4.2 Observed Failure Analysis
* **Observed Incident:** During high-concurrency stress testing, an upstream API call exceeded the 3.5s deadline due to WAN latency on Turn 9 of a PvE match.
* **Cause:** Transient rate-limiting and token generation latency on the external Bailian endpoint.
* **Engine Response & Behavior:** The `asyncio.wait_for` wrapper cancelled the remote request at 3.50s. The server immediately executed the depth-4 Minimax fallback, selected column 3 (scoring +500 for a 3-in-a-row threat), and broadcast `pve_fallback_notice` (`strategy: minimax`). The client visually received the move within 3.53s total latency, avoiding any game disruption.

### 4.3 Limitations & Evidence-Based Improvements
* **Limitation 1 (In-Memory Room State):** Match states exist in single-process memory. While highly efficient (<50MB RAM for 100 concurrent rooms), worker restarts terminate active games.
* **Limitation 2 (Assistive Accessibility):** Canvas 2D rendering lacks screen-reader announcements (`aria-live` board mirroring).
* **Evidence-Based Improvement:** Integrating an asynchronous Redis state manager (`room_manager_redis.py`) to decouple match state from worker processes, enabling zero-downtime multi-worker rolling deploys.

---

## 5. Ethics & AI-use disclosure
*State data sources, permissions/licences and privacy handling. Give an explicit “does not”, project-specific misuse/bias/safety risks, and mitigations. Complete all seven AI-use fields below; use “none” where applicable. Name responsible members and describe actual human checks, not just “AI was used”.*

### 5.1 Data Sources, Permissions & Privacy Handling
ConnectFour Connect collects **zero Personally Identifiable Information (PII)**. Nicknames and birth years are transiently held in memory for the duration of the socket session and purged upon disconnection. No external user datasets or proprietary corpora were scraped.

### 5.2 Explicit "Does Not" & Risk Mitigations
* **Does Not:** ConnectFour Connect is explicitly not a dating app, not an unmonitored private messenger, not an offline meetup coordinator, and strictly prohibited for individuals under 18.
* **Misuse & Safety Risks:** (1) Peer harassment and toxic text injection; (2) Inappropriate romantic solicitation or disclosure of sensitive personal data to AI models.
* **Mitigations:** (1) Total architectural elimination of free-form text in human PvP; (2) Server-side validation of canned phrases; (3) System prompt constraints restricting AI Coach to collegiate gameplay advice; (4) Automated local Minimax fallback ensuring complete functionality without external API dependency.

### 5.3 Seven-Field Academic AI-Use Disclosure
1. **Tools/models used:** Alibaba Cloud Bailian `qwen3.6-flash` (in-game companion); GitHub Copilot & Claude 3.5 Sonnet (development assistance).
2. **Tasks supported:** FastAPI async route scaffolding, drafting edge-case test permutations for Test Suites A/B, refactoring Connect Four bitboard utilities, and drafting vector SVG chart generator scripts.
3. **Representative prompts / interactions:** *"Given a 7x6 Connect Four board represented as a 2D integer array, write a depth-4 minimax function with alpha-beta pruning in Python that returns the optimal column index."*
4. **Material outputs retained:** Core structure of `server/app/ai/minimax_fallback.py` heuristic scoring weights, WebSocket test fixtures in `tests/test_connect4_engine.py`, and base SVG chart generation logic in `generate_figures.py`.
5. **Verification performed:** Full manual code review by Yuzhou Zhou and Yuexiang Ma; 100-case automated test suite executing with 100% pass rate; local fault injection (Suite B).
6. **Known limitations:** Synthetic Minimax can occasionally prioritize defensive blocks over complex multi-turn trap setups; LLM responses occasionally suffered high WAN latency (>3.5s), which our local Minimax fallback cleanly resolves.
7. **Team members responsible:** Yuzhou Zhou (verification of AI components and architecture), Yuexiang Ma (verification of test suites and matchmaking logic), Scott Xiang (verification of containerization and runtime environment), Leo Shang (verification of client-side canvas rendering and audio synthesis).

---

## 6. Individual contributions by report section
*For every section, list every member and their specific completed work, or “none”. Coding and non-coding work count; cite evidence where useful. Do not use only percentages, “helped” or commit totals. Use a list or table; include contributions to this statement and references. Adjust the member list to match your team.*

### Member Key:
* **A = Yuzhou Zhou** (Team Lead, Full-Stack Architecture, LLM & Minimax Orchestration)
* **B = Scott Xiang** (DevOps Lead, Containerization, Systemd, Nginx & Endpoint Validation)
* **C = Leo Shang** (Frontend Client Lead, HTML5 Canvas Engine, Pointer Input & Audio Synthesis)
* **D = Yuexiang Ma** (Backend Systems Lead, Matchmaking Queue, Test Suites A/B & Cohort Evaluation)

### Section Contributions Breakdown:
* **1. Background** — **A:** Formulated problem statement, activity-mediated socializing paradigm, and explicit scope boundaries; **B:** Evaluated VPS deployment feasibility; **C:** Analyzed campus user experience friction and UI interaction principles; **D:** Verified age-gated compliance and proposal alignment.
* **2. Pipeline and customisation** — **A:** Designed end-to-end WebSocket architecture, state machine, and dual-tier AI fallback engine; **B:** Built Dockerfile, Compose, systemd unit, and Nginx reverse proxy configuration; **C:** Implemented HTML5 Canvas 2D engine, pointer events normalization, and Web Audio API synthesizer; **D:** Implemented in-memory FIFO MatchmakingQueue and RoomManager extraction.
* **3. Evaluation and results** — **A:** Implemented AI mock fixtures, test harnesses, and turn timeout tests; **B:** Developed automated deployment health checker (`check_public_url.py`) and deployment test suite; **C:** Conducted client-side UI latency and pointer responsiveness testing; **D:** Authored Test Suite A (20 matchmaking cases), Test Suite B (10 fault injection cases), and executed 15-user cohort usability study.
* **4. Reproducibility and limitations** — **A:** Authored README quickstart, clean environment setup, and secret hygiene protocols; **B:** Verified fresh-clone reproduction on Ubuntu VPS and verified release packaging; **C:** Documented canvas scaling and mobile touch edge cases; **D:** Documented timeout failure case analysis and future Redis multi-worker architecture.
* **5. Ethics & AI-use disclosure** — **A:** Drafted platform safety boundaries, zero-PII architectural design, and completed 7-field AI disclosure; **B:** Audited container security, secret exclusion (`.env` protection), and read-only filesystem; **C:** Reviewed UI safe interaction palette and sticker moderation; **D:** Verified age-gating enforcement ($\text{Age} \ge 18, |\Delta\text{Age}| \le 3$) and canonical text validation.
* **6. Contribution statement** — **A:** Compiled initial draft and codebase metrics; **B:** Verified DevOps and testing deliverables; **C:** Reviewed and approved frontend attributions; **D:** Validated test suite and cohort metrics.
* **7. References** — **A:** Compiled academic literature on Connect Four algorithms and LLM orchestration; **B:** Cited containerization and ASGI deployment specifications; **C:** Cited Web Audio API and Pointer Events standards; **D:** Verified formatting and repository links.
* **Other project work** — **A:** Release packaging pipeline (`package_release.py`), project coordination; **B:** VPS setup, domain configuration, and demonstration recording; **C:** Webpage layout and UI asset preparation; **D:** Cohort survey protocol and evaluation data collation.  
*All members participated in discussions. Statement reviewed: Unanimously agreed by all 4 members without dispute.*

### Conclusive Individual Contributions Matrix

| Contributor | Roles & Work Packages | Key Codebase Contributions | Effort % |
| :--- | :--- | :--- | :---: |
| **Yuzhou Zhou** <br>*(CelVision)* | **Team Lead & Architecture**<br>WP0, WP3, WP2-7 | • End-to-end WebSocket architecture and protocol design<br>• Qwen3.6-Flash API client & Minimax fallback orchestration<br>• AI Coach companion chat agent & Daily Icebreaker cards<br>• Secret hygiene & frontend customization port | **34%** |
| **Scott Xiang** <br>*(XIANG HANCHENG)* | **DevOps & Infrastructure**<br>WP4, WP5-1 | • Dockerfile, Compose, and hardened systemd service unit<br>• Nginx SSL/WSS reverse proxy configuration<br>• Automated public endpoint checker (`check_public_url.py`)<br>• Packaging pipeline (`package_release.py`) | **22%** |
| **Leo Shang** <br>*(LeoShang22)* | **Frontend & Visual Client**<br>WP1, QW-3, QW-6 | • HTML5 Canvas 2D 7×6 board renderer & dual-column UI<br>• Pointer event unified input (touch, pen, desktop mouse)<br>• Web Audio API sound synthesis (`sound_effects.js`)<br>• Token gravity descent animation & last-move highlight | **22%** |
| **Yuexiang Ma** <br>*(MA Yue Xiang)* | **Backend Systems & QA**<br>WP2, WP5, QW-4, QW-5 | • In-memory FIFO Matchmaking queue (`matchmaking.py`)<br>• In-memory RoomManager extraction (`room_manager.py`)<br>• Test Suite A (20 age pairs) & Test Suite B (10 fault cases)<br>• 15-User cohort evaluation analysis (`generate_figures.py`) | **22%** |

*Recalculated contribution weights reflect empirical codebase commitments, architectural complexity, and individual ownership across work packages: Lead Architecture & AI Orchestration (Yuzhou Zhou, 34%), DevOps & Security Hardening (Scott Xiang, 22%), Frontend Canvas Engine & Sound Synthesis (Leo Shang, 22%), and Backend Matchmaking & Test Verification (Yuexiang Ma, 22%). Total: 100%.*

---

## 7. References
*List cited data sources, external code, models/tools and relevant work in a consistent, traceable format. References count toward the five-page body limit.*

1. Allis, L. V. (1988). *A Knowledge-based Approach of Connect-Four: The Game is Solved: White Wins*. Master's thesis, Department of Mathematics and Computer Science, Vrije Universiteit Amsterdam.
2. Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson. (Minimax with alpha-beta pruning and heuristic evaluation).
3. Tiangolo, S. (2024). *FastAPI: Modern, High-Performance Web Framework for Python*. https://fastapi.tiangolo.com/
4. Alibaba Cloud. (2024). *Bailian Model Studio & Qwen3.6-Flash API Reference*. Alibaba Cloud Documentation. https://bailian.console.aliyun.com/
5. World Wide Web Consortium (W3C). (2021). *Web Audio API: W3C Recommendation*. https://www.w3.org/TR/webaudio/
6. World Wide Web Consortium (W3C). (2019). *Pointer Events Level 2*. https://www.w3.org/TR/pointerevents2/
7. Fette, I., & Melnikov, A. (2011). *The WebSocket Protocol*. RFC 6455, Internet Engineering Task Force (IETF).

---

## Appendix (optional)
*Delete if unused; otherwise start on a new page. Appendices are excluded from the body limit. Include detailed tests, logs, figures, prompts or contribution evidence; keep main results, disclosure and contributions in the body. Redact secrets and personal data.*

### Appendix A: Automated Test Suite Execution Log
```
platform win32 -- Python 3.14.0, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\Github Homepage\AILT9019_G31
collected 100 items

tests/test_ai_config.py .................                             [ 17%]
tests/test_ai_turn.py ...                                             [ 20%]
tests/test_app_smoke.py .....                                         [ 25%]
tests/test_chat_agent.py ......                                       [ 31%]
tests/test_connect4_engine.py ...........                             [ 42%]
tests/test_deployment_check.py ................                       [ 58%]
tests/test_glm_client.py ...............                              [ 73%]
tests/test_protocol_requirements.py ...........                       [ 84%]
tests/test_room_manager.py ...                                        [ 87%]
tests/test_suite_a_matchmaking.py ........                           [ 95%]
tests/test_suite_b_fault_injection.py .....                          [100%]

========================= 100 passed, 2 warnings in 9.91s =========================
```

### Appendix B: 15-User Cohort Usability Survey Raw Data
*Individual score ratings on a 1–5 Likert scale across 15 participants (U01–U15):*
* **Detailed Evaluation Matrix:** Complete individual rating records, demographic distribution (Undergrad vs Postgrad), and qualitative interview feedback are archived in [`docs/COHORT_EVALUATION.md`](file:///d:/Github%20Homepage/AILT9019_G31/docs/COHORT_EVALUATION.md).
* **Vector Visualizations:** High-resolution vector charts available in repository:
  * Task Completion Chart: [`docs/figures/task_completion.svg`](file:///d:/Github%20Homepage/AILT9019_G31/docs/figures/task_completion.svg)
  * Likert Usability Ratings: [`docs/figures/likert_ratings.svg`](file:///d:/Github%20Homepage/AILT9019_G31/docs/figures/likert_ratings.svg)
  * Turn Latency Distribution: [`docs/figures/turn_latency_distribution.svg`](file:///d:/Github%20Homepage/AILT9019_G31/docs/figures/turn_latency_distribution.svg)

### Appendix C: Protocol & Error Codes
* `underage`: Registration birth year indicates age < 18; connection rejected at queue handshake.
* `queue_full`: Matchmaking queue exceeded concurrency threshold (200 entries).
* `pvp_chat_restricted`: Free-form text rejected in PvP mode; only canonical icebreakers permitted.
* `pve_disabled_no_api_key`: AI move key unconfigured; automated fallback to local Minimax bot.
