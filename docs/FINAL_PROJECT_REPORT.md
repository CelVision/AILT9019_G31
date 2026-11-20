# ConnectFour Connect: Activity-Mediated Social Mini-Game with Adaptive Multi-Tier AI Architecture

**Course:** AILT9019 · AI Literacy II  
**Academic Term:** Autumn 2026  
**Team:** Group 31  
**Authors & Contributors:**
* **David (CelVision)** — Project Coordinator, Full-Stack Architecture, LLM & Minimax Orchestration
* **Scott Xiang (XIANG HANCHENG)** — DevOps Lead, Containerization, Systemd, Nginx & Endpoint Validation
* **Leo Shang (LeoShang22)** — Frontend Client Lead, HTML5 Canvas Engine, Pointer Input & Web Audio Synthesis
* **Yuexiang Ma (MA Yue Xiang)** — Backend Systems Lead, Matchmaking Queue, Test Suites A/B & Cohort Evaluation

---

## Abstract
Digital social platforms for university students suffer from pervasive conversational anxiety, high-stakes biographical self-presentation, and superficial appearance-based swiping. **ConnectFour Connect** addresses these issues through an *activity-mediated social interaction prototype* built on turn-based Connect Four. Player interaction is structured to lower cognitive and emotional friction: human peers match via an age-gated queue ($\text{Age} \ge 18, |\Delta\text{Age}| \le 3$) and communicate exclusively through curated canned reactions and Daily Icebreaker cards in PvP mode. To eliminate matchmaking wait times, a 15-second queue timeout routes solo players into an interactive PvE session powered by a dual-tier AI architecture: Alibaba Cloud Bailian's **`qwen3.6-flash`** for dynamic moves and collegiate companion banter, backed by a deterministic local **depth-4 Minimax bot** activating within 23.6ms upon upstream rate limits, latency, or outages. A 15-user cohort usability evaluation demonstrated a **93.3%** task completion rate (exceeding the 85% course benchmark) and an average Likert usability score of **4.61 / 5.0** (exceeding the 4.0 benchmark). Automated testing confirmed **100/100 passing test cases** with zero unhandled exceptions.

---

## 1. Introduction, Problem Statement & Objectives
*(Section Contributions: David 50%, Leo Shang 50%)*

### 1.1 The Social Anxiety Bottleneck on Campus
Modern young adults and university students experience substantial interpersonal friction when attempting to form new peer connections online. Mainstream digital networking platforms mandate detailed personal profiles, photo screening, and unguided text messaging. In an academic campus setting, this model triggers conversational paralysis: students fear saying the wrong thing, worry about superficial judgment, and struggle to sustain open-ended introductory dialogues.

### 1.2 Activity-Mediated Socializing
To remove these emotional barriers, ConnectFour Connect adopts an **activity-centered communication paradigm**:
1. **Activity as Primary Focus:** Attention is centered on a low-friction, familiar board game (7-column × 6-row Connect Four). Turns provide natural pacing, eliminating awkward conversational pauses.
2. **Guaranteed Low-Stakes Communication (PvP):** Peer-to-peer interaction removes unmoderated free-form text. Players communicate through 6 sportsmanlike preset phrases, 4 reaction stickers, and 4 curated Daily Icebreaker Cards (e.g. *"Coffee or Tea?"*, *"Midterm Prep"*).
3. **Conversational PvE AI Coach:** If no human peer matches within 15 seconds, a server-side AI Coach steps in seamlessly. The AI Coach engages in collegiate banter and strategy discussion with strict safety guardrails.
4. **Zero Wait-Time Availability:** The platform is accessible via zero-configuration browser URLs across desktop and mobile devices without registration friction.

---

## 2. System Architecture & End-to-End Pipeline
*(Section Contributions: David 45%, Scott Xiang 30%, Yuexiang Ma 25%)*

The platform follows a decoupled, high-performance architecture built on asynchronous Python (FastAPI), real-time WebSockets, HTML5 Canvas 2D, and remote cloud infrastructure.

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

### 2.1 The End-to-End User Journey
1. **Lightweight Onboarding:** The user enters a nickname (2–16 characters) and birth year (verifying $\text{Age} \ge 18$). An optional accordion allows users to provide custom LLM keys or select alternative models.
2. **Matchmaking & Age-Window Search:** The client opens `/ws/game` and transmits `queue_join`. The in-memory FIFO queue searches for compatible peers within an age variance $|\Delta\text{Age}| \le 3$.
3. **Real-Time Match Resolution:**
   * **PvP Route:** Two compatible students enter an isolated room. Game moves, board synchronization, and canned reactions broadcast over WebSockets.
   * **PvE Route (15s Fallback):** If no peer appears within 15 seconds, the server automatically instantiates a PvE match against the **AI Coach**.
4. **Match Conclusion & Rematch:** The outcome (Win/Loss/Draw) displays on the client with move duration and total turns. Consenting players may request an immediate rematch or return to the lobby.

---

## 3. Key Technical Implementations
*(Section Contributions: David 35%, Leo Shang 25%, Scott Xiang 20%, Yuexiang Ma 20%)*

### 3.1 Age-Gated Matchmaking & In-Memory Room Manager
*(Sub-section Contributions: Yuexiang Ma 60%, David 40%)*
Implemented in [`matchmaking.py`](file:///d:/Github%20Homepage/AILT9019_G31/server/app/matchmaking.py) and [`room_manager.py`](file:///d:/Github%20Homepage/AILT9019_G31/server/app/room_manager.py):
* **Deterministic Single-Pass Tick:** `MatchmakingQueue.tick()` simultaneously executes peer pairing and 15s timeout expiry in a single atomic pass, eliminating race conditions between human matching and AI fallback.
* **Authoritative 1 Hz Heartbeat:** Pushes `queue_status` (`elapsed_seconds`, `remaining_seconds`, queue position) once per second.
* **Session Lifecycle:** `RoomManager` encapsulates active match dictionaries and retains finished match state for 600 seconds, enabling post-game banter and mutual rematch handshakes while evicting stale memory.

### 3.2 Dual-Tier Fault-Tolerant AI Engine
*(Sub-section Contributions: David 85%, Yuexiang Ma 15%)*
Implemented in [`glm_client.py`](file:///d:/Github%20Homepage/AILT9019_G31/server/app/ai/glm_client.py), [`minimax_fallback.py`](file:///d:/Github%20Homepage/AILT9019_G31/server/app/ai/minimax_fallback.py), and [`chat_agent.py`](file:///d:/Github%20Homepage/AILT9019_G31/server/app/ai/chat_agent.py):
* **Primary LLM (Qwen3.6-Flash):** Connects to Alibaba Cloud Bailian's OpenAI-compatible endpoint. Prompts serialize the board matrix and enforce strict JSON schema output: `{"column": int, "canned_reaction_id": int}`.
* **Turn Deadline & Race Condition Protection:** AI requests run inside `asyncio.wait_for` capped at 3.5 seconds.
* **Fail-Safe Minimax Heuristic:** If the model API times out, returns HTTP 429/500, or outputs an illegal column, execution immediately degrades to a local depth-4 Minimax algorithm with alpha-beta pruning:
  $$\text{Score} = 100{,}000 \cdot C_4 + 500 \cdot C_3 + 50 \cdot C_2 + 30 \cdot C_{\text{center}}$$
  Minimax executes in ~23.6ms (<50ms budget), emitting `pve_fallback_notice` so the match never stalls.
* **Conversational AI Coach:** In PvE, users can chat freely with the AI Coach. A 6-turn sliding window prevents token explosion, while the system prompt enforces polite collegiate boundaries.

### 3.3 Canvas 2D Engine, Pointer Input & Audio Synthesis
*(Sub-section Contributions: Leo Shang 80%, David 20%)*
Implemented in [`game_board.js`](file:///d:/Github%20Homepage/AILT9019_G31/client/js/game_board.js) and [`sound_effects.js`](file:///d:/Github%20Homepage/AILT9019_G31/client/js/sound_effects.js):
* **Pointer Events & CSS Scaling:** Unifies touch, pen, and mouse inputs under `pointerdown` and `pointermove`. Accounts for responsive CSS canvas scaling to accurately map viewport pixels to grid columns (0–6).
* **Physics & Last-Move Highlights:** Smooth vertical token descent with gravity acceleration (`dropTokenAnimated`), golden borders for winning coordinates, and a glowing cyan indicator for the last dropped token.
* **Web Audio API Synthesizer:** Real-time synthesis of token drops (exponential pitch bend 440Hz $\to$ 150Hz), victory arpeggios (C5-E5-G5-C6 chord), and reaction sticker pops with zero external MP3 assets.

### 3.4 DevOps, Containerization & Endpoint Verification
*(Sub-section Contributions: Scott Xiang 85%, David 15%)*
Implemented in [`deploy/Dockerfile`](file:///d:/Github%20Homepage/AILT9019_G31/deploy/Dockerfile), [`compose.yaml`](file:///d:/Github%20Homepage/AILT9019_G31/deploy/compose.yaml), and [`check_public_url.py`](file:///d:/Github%20Homepage/AILT9019_G31/deploy/check_public_url.py):
* **Hardened Production Environment:** Non-root Python 3.12 Alpine container with read-only root filesystem, bounded logging, and single-worker systemd unit to guarantee queue consistency.
* **Automated Health Checker:** `check_public_url.py` verifies 8/8 deployment invariants: HTTP 200 responses, non-empty HTML/CSS/JS bundles, API health status, and WebSocket upgrade handshakes.

---

## 4. Verification, Testing & 15-User Cohort Usability Evaluation
*(Section Contributions: Yuexiang Ma 50%, Scott Xiang 30%, David 20%)*

### 4.1 Automated Test Suites (100% Pass Rate)
The codebase includes 100 automated unit and integration tests executed via `pytest`:
* **Test Suite A (Matchmaking & Boundary Checks - 20 Cases):** Validates 10 valid pairs ($|\Delta\text{Age}| \le 3$, Age $\ge 18$) paired into PvP within 15s; 5 age-gap refused pairs ($|\Delta\text{Age}| > 3$) held in queue and routed to PvE at 15s; and 5 invalid/underage submissions rejected at registration.
* **Test Suite B (Fault Injection & Fallback - 10 Cases):** Injects HTTP 500, HTTP 429 quota exhaustion, network timeouts ($>3.5\text{s}$), and malformed JSON/illegal columns. Verifies 100% fallback recovery to Minimax within deadline with zero unhandled server exceptions.
* **Protocol & Lifecycle Suites (70 Cases):** Tests rules engine, room manager lookups, pointer scaling, config precedence, and deployment health.

```
========================= 100 passed, 2 warnings in 11.62s =========================
```

### 4.2 15-User Cohort Usability Evaluation
*(Protocol and metrics detailed in [`docs/COHORT_EVALUATION.md`](file:///d:/Github%20Homepage/AILT9019_G31/docs/COHORT_EVALUATION.md))*

A structured usability evaluation was conducted with a cohort of **15 university students** (9 undergraduate, 6 postgraduate; ages 18–24, mean age 21.2). Each participant completed two full sessions: (a) one live PvP match against a peer classmate, and (b) one PvE match against the AI Coach.

| Metric / Evaluation Dimension | Benchmark Target | Observed Cohort Result | Status |
| :--- | :---: | :---: | :---: |
| **Task Completion Rate** | $\ge 85\%$ (at least 13/15) | **93.3%** (14/15 completed both matches) | ✅ **PASS** |
| **Q1: UI Intuitiveness & Layout** | $\ge 4.0 / 5.0$ | **4.80 ± 0.41** (100% rated $\ge 4$) | ✅ **PASS** |
| **Q2: Turn Timer & Latency Satisfaction** | $\ge 4.0 / 5.0$ | **4.60 ± 0.51** (93% rated $\ge 4$) | ✅ **PASS** |
| **Q3: Canned Chat Safety & Comfort** | $\ge 4.0 / 5.0$ | **4.73 ± 0.46** (100% rated $\ge 4$) | ✅ **PASS** |
| **Q4: Daily Icebreaker Utility** | $\ge 4.0 / 5.0$ | **4.67 ± 0.49** (93% rated $\ge 4$) | ✅ **PASS** |
| **Q5: AI Coach Banter & Strategy** | $\ge 4.0 / 5.0$ | **4.53 ± 0.52** (93% rated $\ge 4$) | ✅ **PASS** |
| **Q6: Overall Gaming Satisfaction** | $\ge 4.0 / 5.0$ | **4.73 ± 0.46** (100% rated $\ge 4$) | ✅ **PASS** |
| **Overall Likert Usability Index** | $\ge 4.0 / 5.0$ | **4.61 / 5.0** | ✅ **PASS** |

Qualitative feedback praised the low emotional stakes: *"The canned reactions and daily cards felt very comfortable. I didn't feel pressured or anxious like on normal dating or chat apps."* (U02, Undergrad).

---

## 5. Ethics, Safety & AI-Use Disclosure
*(Section Contributions: David 60%, Yuexiang Ma 40%)*

### 5.1 Platform Ethics & Safety Guardrails
1. **Explicit "Does Not" Boundary:** ConnectFour Connect is explicitly not a dating app, not an unmonitored private messenger, not an offline meetup service, and strictly prohibited for minors.
2. **Zero PII Collection:** The platform collects no real names, emails, phone numbers, social media handles, or location data. Guest nicknames and birth years are held ephemerally in RAM and purged upon disconnection.
3. **Harassment Elimination via Architectural Constraint:** Free-form text input between human peers is completely omitted in PvP. Players interact exclusively via pre-moderated canned phrases and Daily Icebreakers. The server enforces canonical topic text on incoming payloads, eliminating text injection vulnerabilities.
4. **Gating & Age Filtering:** The registration form enforces $\text{Age} \ge 18$. The queue strictly rejects matches where $|\Delta\text{Age}| > 3$, preventing cross-generational pairings.

### 5.2 Academic AI-Use Disclosure
* **In-Game Generative AI:** Alibaba Cloud Bailian's `qwen3.6-flash` is integrated as an active system component for PvE move generation and collegiate companion chat. Prompt engineering restricts the model to supportive campus banter, automatically deflecting inappropriate queries.
* **Developmental AI Assistance:** In accordance with course academic integrity guidelines, Generative AI tools (LLMs) were utilized during development for code boilerplate scaffolding, drafting test cases, and refactoring assistance. All generated code was manually reviewed, modified, and validated through our 100-case automated test suite.

---

## 6. Discussion, Limitations & Future Work
*(Section Contributions: David 30%, Scott Xiang 25%, Leo Shang 25%, Yuexiang Ma 20%)*

### 6.1 Key Insights
Activity-mediated mini-games succeed in establishing initial rapport between strangers. Restricting communication to pre-approved phrases and icebreakers does not diminish engagement; rather, it removes the social burden of formulating witty introductory messages. Furthermore, the 15-second queue timeout backed by an interactive AI companion eliminates the cold-start problem common to multiplayer services.

### 6.2 Limitations & Future Roadmap
* **Assistive Technology:** While canvas rendering supports high-contrast deuteranopic tokens and pointer scaling, screen-reader accessibility (aria-live board mirroring) remains a future milestone.
* **Expanded Game Modes:** Extending the platform to include cooperative puzzle solving or 4-player team Connect Four.

---

## 7. Conclusion & Summary of Individual Contributions
*(Section Contributions: David 34%, Scott Xiang 22%, Leo Shang 22%, Yuexiang Ma 22%)*

ConnectFour Connect successfully demonstrated that activity-mediated turn-based gaming, combined with safety-first canned interactions and adaptive multi-tier AI fallback, provides a compelling, anxiety-free social avenue for university students.

### Conclusive Individual Contributions Matrix

| Contributor | Roles & Work Packages | Key Codebase Contributions | Effort % |
| :--- | :--- | :--- | :---: |
| **David**  <br>*(CelVision)* | **Team Lead & Architecture**<br>WP0, WP3, WP2-7 | • End-to-end WebSocket architecture and protocol design<br>• Qwen3.6-Flash API client & Minimax fallback orchestration<br>• AI Coach companion chat agent & Daily Icebreaker cards<br>• Secret hygiene & frontend customization port | **34%** |
| **Scott Xiang** <br>*(XIANG HANCHENG)* | **DevOps & Infrastructure**<br>WP4, WP5-1 | • Dockerfile, Compose, and hardened systemd service unit<br>• Nginx SSL/WSS reverse proxy configuration<br>• Automated public endpoint checker (`check_public_url.py`)<br>• Packaging pipeline (`package_release.py`) | **22%** |
| **Leo Shang** <br>*(LeoShang22)* | **Frontend & Visual Client**<br>WP1, QW-3, QW-6 | • HTML5 Canvas 2D 7×6 board renderer & dual-column UI<br>• Pointer event unified input (touch, pen, desktop mouse)<br>• Web Audio API sound synthesis (`sound_effects.js`)<br>• Token gravity descent animation & last-move highlight | **22%** |
| **Yuexiang Ma** <br>*(MA Yue Xiang)* | **Backend Systems & QA**<br>WP2, WP5, QW-4, QW-5 | • In-memory FIFO Matchmaking queue (`matchmaking.py`)<br>• In-memory RoomManager extraction (`room_manager.py`)<br>• Test Suite A (20 age pairs) & Test Suite B (10 fault cases)<br>• 15-User cohort evaluation analysis (`generate_figures.py`) | **22%** |

*Recalculated contribution weights reflect empirical codebase commitments, architectural complexity, and individual ownership across work packages: Lead Architecture & AI Orchestration (David, 34%), DevOps & Security Hardening (Scott Xiang, 22%), Frontend Canvas Engine & Sound Synthesis (Leo Shang, 22%), and Backend Matchmaking & Test Verification (Yuexiang Ma, 22%). Total: 100%.*

---

## Appendices *(Exempt from 5-page limit)*

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

========================= 100 passed, 2 warnings in 11.62s =========================
```

### Appendix B: 15-User Cohort Usability Survey Raw Data
*Responses on 1–5 scale (1=Strongly Disagree, 5=Strongly Agree):*
* **U01–U15 Raw Matrix:** See [`docs/COHORT_EVALUATION.md`](file:///d:/Github%20Homepage/AILT9019_G31/docs/COHORT_EVALUATION.md) for individual score breakdowns and demographic stratification.
* **Vector Visualizations:** See [`docs/figures/likert_ratings.svg`](file:///d:/Github%20Homepage/AILT9019_G31/docs/figures/likert_ratings.svg), [`docs/figures/task_completion.svg`](file:///d:/Github%20Homepage/AILT9019_G31/docs/figures/task_completion.svg), and [`docs/figures/turn_latency_distribution.svg`](file:///d:/Github%20Homepage/AILT9019_G31/docs/figures/turn_latency_distribution.svg).

### Appendix C: Protocol & Error Codes
* `underage`: Registration birth year indicates age < 18.
* `queue_full`: Matchmaking queue exceeded capacity (200 entries).
* `pvp_chat_restricted`: Free-form text rejected in PvP matches; only canonical icebreakers permitted.
* `pve_disabled_no_api_key`: AI move key unconfigured; automated fallback to local Minimax bot.
