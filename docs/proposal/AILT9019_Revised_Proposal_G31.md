## AILT9019 · AI Literacy II

## Revised Project Proposal Template

Due: Saturday, 10 Oct (Week 6) · One submission per team, via the Moodle form

## 1. Background

Who is this for, what is stuck, why it matters this semester, and who or what it is not for. Also state where the idea comes from: which topic-list idea(s) and how far they were adapted, an external idea, or an original idea. A figure is optional.

Target User & Unmet Need: This project targets young adults and university students seeking low-pressure, casual online opportunities to meet and interact with new peers across different genders and diverse backgrounds. The central pain point is that contemporary digital social platforms rely almost exclusively on appearance-driven swipe mechanisms, high-stakes biographical self-presentation, and unprompted text icebreakers. This paradigm produces substantial social anxiety, awkwardness, and superficial judgments, leaving modern students with few natural, light- hearted channels to break the ice through a shared activity.

Semester Significance & Activity-Mediated Socializing: This prototype matters this semester as an exploration into activity-mediated, AI-supported social interaction within an accessible browser environment. By embedding interpersonal interaction inside a turn-based mini-game, conversation becomes secondary to shared play, eliminating awkward conversational pauses and lowering emotional stakes. Furthermore, integrating a backend AI fallback agent guarantees uninterrupted availability, enabling solo testers to experience complete interactive loops even during off-peak queue hours.

Target & Explicit Scope Boundaries: This platform is designed strictly for casual, shared-activity interaction between consenting adult peers. It is explicitly not a formal dating or matchmaking service, not an unmonitored private direct-messaging channel, not an offline meetup coordinator, and strictly not for cross-generational pairings or interactions involving minors.

Idea Source: Original team-conceived project idea, not adapted from the course topic list.

## 2. Project pipeline

End-to-end path: request → method → result, and what the team will actually build. A pipeline diagram is encouraged.

## End-to-End User Journey (Request → Method → Result):

- 1. Request & Entry: An end-user opens the public web URL on desktop or mobile. The user completes a lightweight guest registration by specifying a nickname and birth year (verifying age ≥ 18) and clicks "Find Match."

- 2. Matchmaking Queue & Age Filtering: The backend server validates submitted age parameters and registers the client in an in-memory matching pool. The system searches for active peers within an acceptable age variance (|ΔAge| ≤ 3 years). If a compatible human peer is found within the 15-second matchmaking window, both clients are routed into an isolated WebSocket room for a live Player-vs-Player (PvP) match. If the 15-second timer expires without a peer match, the server seamlessly initializes a backend Large Language Model (LLM) agent to serve as an AI opponent in a Player-vs-Environment (PvE) room.

- 3. Mini-Game Mechanics (Turn-Based Connect Four): The game is played on a vertical 7-column × 6-row grid. Two players take turns selecting an unoccupied column (0 ≤ col ≤ 6) to drop their colored token (Red or Yellow), which falls to the lowest unoccupied slot in that column via gravity. The first player to connect four tokens in an unbroken line (horizontally, vertically, or diagonally) immediately wins. If all 42 slots fill with no four-in-a-row, the match is declared a draw. A 30-second turn countdown timer prevents stalled sessions.

- 4. Structured LLM Move Generation (AI Core): When it is the AI's turn, the backend serializes the current 7×6 board matrix, active token identity, and legal column list into a structured JSON prompt payload. The backend queries the LLM API (Google Gemini 1.5 Flash) with strict JSON schema response formatting: `{"column": int, "canned_reaction_id": int}`. The server validates that the returned column is an unoccupied legal move. If the model outputs an illegal column, errors out, or fails to respond within 2.5 seconds, the server immediately triggers a local deterministic rule-based heuristic (e.g., minimax win/block column selection) within 100ms, ensuring seamless continuity.

- 5. Canned Social Interaction: Free-form text input is completely omitted to guarantee safety. Players interact using an in-game communication tray consisting of: (a) 6 preset phrases: "Good luck!", "Nice move!", "Thinking...", "Close one!", "Well played!", "Good game!"; and (b) 4 reaction stickers: Thumbs Up (👍), Applause (👏), Pondering (🤔), and Celebration (🎉). Messages broadcast through WebSockets and render as floating animated speech bubbles beside player avatars.

- 6. Result & Summary: An end-game modal reveals the match outcome (Win / Loss / Draw), session duration, and turns played, offering options to return to the matchmaking lobby or queue again.

## Build Boundary & Remote VPS Feasibility:

- What the team will build: (1) A responsive single-page web client built with HTML5, CSS3, and Canvas/JavaScript, featuring crisp board rendering, turn timers, and the canned interaction tray; (2) A lightweight backend built with Python (FastAPI + WebSockets) deployed on an Ubuntu Linux VPS, reverse-proxied via Nginx with SSL encryption (HTTPS/WSS); (3) A thread-safe, in-memory WebSocket room manager that cleanly partitions matches, maintains active game states, and destroys room memory upon termination, keeping memory overhead under 50MB RAM for concurrent test sessions; (4) A robust server-side LLM orchestration layer enforcing rigid JSON schema constraints and automated local heuristic fallback.

- What the team will NOT build: Native mobile applications, persistent relational databases storing user credentials or PII, or open audio/video/text chat services.


*Figure 1: End-to-End System Architecture and Interaction Pipeline*

## 3. Evaluation and test

How the team will tell the product works, including at least one case it should fail safely or refuse.

### 1. User Experience & Usability Cohort Testing:

- Sample Size & Cohort: A fixed cohort of 15 university student classmates will be recruited as test users.

- Evaluation Protocol: Each tester executes two distinct sessions: (a) one live PvP match paired with a classmate, and (b) one PvE match playing against the server-side LLM bot.

- Quantitative Passing Benchmarks: (1) Task Completion Rate ≥ 85%: At least 13 of 15 testers must successfully complete the full end-to-end journey (browser landing → age input → matchmaking queue → completing a full 7×6 Connect Four match → viewing summary modal) independently without facilitator intervention. (2) Usability & Interaction Comfort ≥ 4.0 / 5.0: Average rating on a post-test 5-point Likert survey assessing UI intuitiveness, latency, and comfort of canned phrase communication.

### 2. Automated Edge-Case & Fail-Safe Test Suites:

- Test Suite A: Age Boundary & Demographic Filtering (20 Automated Account Pairs):

  - Valid Cohorts (10 pairs): Test accounts with age ≥ 18 and |Age_A - Age_B| ≤ 3 (e.g., age 20 and 22). Passing Criterion: 10/10 (100%) paired into active PvP rooms within 15 seconds.

  - Age-Gap Refusal (5 pairs): Test accounts with |Age_A - Age_B| > 3 (e.g., age 19 and 25). Passing Criterion: 5/5 (100%) refused pairing; held in queue until the 15-second timer routes each user safely to separate PvE sessions.

  - Underage & Malformed Data Refusal (5 profiles): Submissions with age < 18, null fields, negative numbers, or non-integer characters. Passing Criterion: 5/5 (100%) immediate refusal at registration with a clear inline validation message ("Users must be 18+ to enter"). Zero accounts created.

### Test Suite B: External LLM Outage & Graceful Degradation (10 Simulated Fault Injections):

We simulate upstream API disruptions (HTTP 500 internal server error, HTTP 429 quota exhaustion, and forced 3.5-second network latency). Passing Criterion: 10/10 (100%) graceful degradation. The backend detects API unavailability within 1.5 seconds, falls back to the local deterministic heuristic bot without disconnecting the WebSocket room, and triggers an on-screen toast notification: "AI opponent operating in local fallback mode." The game proceeds seamlessly to completion with zero unhandled runtime exceptions. Live human PvP matchmaking remains 100% operational and unaffected.

## 4. Distribution and accessibility

How someone else can open the app: API setup, first use without a coding background, and (if in scope) other agent environments.

## End-User Access & Zero-Configuration Deployment:

End-users and course evaluators can access and play the game directly by visiting the team's public HTTPS URL in any modern web browser (Chrome, Safari, Firefox, Edge) on desktop or mobile. The entire stack is hosted on a remote Linux VPS with an Nginx reverse proxy.

- Zero Local Setup: No software installation, Git cloning, command-line execution, or local environment configuration is needed.


- Zero Client-Side API Keys: Users do not need to provide their own OpenAI, Gemini, or third-party API keys. All LLM credentials and API calls are handled securely on the backend server.

- First-Use Onboarding: A non-technical user is greeted by a clean 1-minute onboarding modal that clearly explains the rules of Connect Four, demonstrates how to click a column to drop a token, and highlights the canned phrase tray.

## Fail-Safe Resilience & Agent Scope:

If the external LLM API becomes unavailable or experiences rate-limiting, the application remains fully functional: the server automatically falls back to local heuristic game algorithms, ensuring that any classmate or reviewer can evaluate the prototype at any time.

This project is conceived and packaged strictly as an interactive web mini-game; exporting reusable skill modules or tool manifests for other agent platforms (such as Pi Agent or desktop agent harnesses) is explicitly out of scope for this semester's prototype.

## 5. Ethics and risks

An explicit “does not”, plus main misuse or failure risks and how they are mitigated.

## Explicit "Does Not" Statement:

This platform explicitly does not facilitate open, unmonitored private text chat, audio or video calling, offline dating coordination, romantic partner screening, persistent contact exchange, or cross-demographic interactions between minors and adults. By strictly framing the product as an activity-centered, low-friction browser mini-game rather than a conventional dating or matchmaking platform, the prototype eliminates the pressures and vulnerabilities common to digital social applications.

## Identified Misuse & Technical Risks and Concrete Mitigations:

- 1. Harassment, Inappropriate Language, and Unsolicited Advances: Open digital chat channels frequently enable abusive commentary, harassment, and unsolicited sexual advances. Mitigation: Free-form text input and image uploads are omitted by architecture. Players communicate exclusively through a fixed palette of 6 sportsmanlike preset phrases ("Good luck!", "Nice move!", "Thinking...", "Close one!", "Well played!", "Good game!") and 4 friendly reaction stickers (👍, 👏, 🤔, 🎉). This eliminates any possibility of profanity, harassment, or non-consensual contact sharing.

- 2. Age Misrepresentation and Minor Vulnerability: Underage users entering adult social spaces or adults interacting with vulnerable youths. Mitigation: Hard registration gating rejects any user under 18 years of age. The matchmaking algorithm strictly rejects pairings where the age gap exceeds 3 years. Furthermore, the system collects zero personally identifiable information (PII)—no real names, phone numbers, email addresses, social media links, or GPS locations are requested or stored in persistent storage. Session data is completely purged upon socket disconnection.

- 3. LLM Hallucination, Toxic Dialogue, and Game State Desynchronization: A generative AI opponent could produce invalid board moves that break game state or generate unpredictable, offensive remarks. Mitigation: The LLM is restricted to a strict JSON schema output ({"column": int, "canned_reaction_id": int}). The AI cannot generate open text; its remarks are confined to the exact same pre-moderated canned phrase IDs available to human players. The backend validates all moves against the current board matrix before committing state changes, instantly overriding invalid moves with a deterministic local heuristic.


## 6. Checkpoints

Must-have and should-have acceptance items, plus a timeline through the mid-term check (Mon Oct 26).

## Acceptance Criteria (Deliverables):

- Must-Have Deliverables: (1) Functional browser Connect Four mini-game (7×6 grid) with Canvas board rendering, turn indicators, 30s countdown timers, and win/draw detection; (2) Age-gated matchmaking service enforcing age ≥ 18 and |Age_A - Age_B| ≤ 3 matchmaking constraints with a 15s queue timeout; (3) Lightweight bidirectional WebSocket room synchronization managing turn transitions, move validation, and graceful player disconnects; (4) Server-side LLM PvE fallback triggered automatically upon queue timeout, generating structured JSON moves; (5) Safe canned interaction palette featuring 6 preset phrases and 4 reaction stickers with zero free-text input; (6) Automated fault degradation to local deterministic heuristic bot activating in <1.5 seconds upon LLM API timeout or error.

- Should-Have Deliverables (Stretch Targets): (1) Dual AI bot personalities (selectable "Casual Explorer" vs. "Tactical Challenger"); (2) Post-game mutual rematch button allowing consenting players to launch another round together; (3) Sound effects and token-drop physics animations.

## Development Timeline through Mid-Term Check (Mon Oct 26):

- Week 5 (Sep 28 – Oct 4): Initial proposal submitted; received 3 comprehensive peer reviews; conducted gap analysis; structured revision roadmap.

- Week 6 (Oct 5 – Oct 11): Finalize revised proposal (submission Oct 10); build Connect Four client UI with HTML5/Canvas; construct local FastAPI WebSocket room manager; integrate age validation and canned phrase communication tray.

- Week 7 (Oct 12 – Oct 18): Deploy backend to remote Ubuntu VPS; configure Nginx reverse proxy with HTTPS/WSS; integrate Gemini 1.5 Flash API with JSON schema enforcement; implement server-side deterministic heuristic fallback layer.

- Week 8 (Oct 19 – Oct 25): Execute automated test suites (20 age pairs and 10 simulated API fault injections); run structured usability trials with 15 peer classmates; optimize latency and responsive layouts.

- Mid-Term Checkpoint (Mon Oct 26): Deliver live public VPS URL, complete demonstration walkthrough video, documented test suite execution logs, and prototype progress report.

*Figure 2: Project Development Timeline and Checkpoints through Mid-Term Check*


## 7. Response to reviewers

For every review your proposal received: cite the Reviewer ID, name the suggestion in a few words, state adopted / partially adopted / not adopted, and give one line why. No penalty for declining — but every review gets a visible response. Three rows are usually enough.

| Reviewer ID | Suggestion (short) | Response | Why (one line) |
| --- | --- | --- | --- |
| R-2V3G | Add implementation detail and pipeline diagram | adopted | Detailed Connect Four mechanics and an end-to-end architecture pipeline diagram (Figure 1) are now in Section 2. |
| R-2V3G | Fix sample size and test cohort for evaluation | adopted | Defined a fixed 15-classmate user testing cohort and quantitative completion targets in Section 3. |
| R-2V3G | Add timeline figure and eliminate cross-section repetition | adopted | Added Figure 2 milestone chart and removed redundant age-filtering text across sections. |
| R-Y8WW | Detail mini-game rules and structured LLM move generation | adopted | Specified Connect Four 7×6 rules, rigid JSON schema move formatting, and heuristic fallback in Section 2. |
| R-Y8WW | Define quantitative passing criteria for edge cases | adopted | Established 100% pass targets on 20 age checks and 10 simulated API failure tests in Section 3. |
| R-Y8WW | Re-assess VPS WebSocket feasibility vs must-have AI scope | partially adopted | Retained lightweight in-memory WebSocket rooms, backed by automated PvE fallback to prevent server strain. |
| R-4MPB | Rephrase "opposite-sex" framing to modern inclusive terminology | adopted | Rephrased to "peers of different genders and backgrounds" in Section 1 to ensure inclusivity. |
| R-4MPB | List concrete examples of canned phrases and reaction stickers | adopted | Specified the exact 6 preset phrases and 4 reaction stickers in Section 2 and Section 5. |

Add rows as needed — one row per review.
