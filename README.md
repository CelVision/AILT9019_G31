# ConnectFour Connect

> **AILT9019 · AI Literacy II — Group 31**  
> **Activity-Mediated Social Mini-Game with AI Fallback Agent**  
> *Target Checkpoint: Mid-Term Checkpoint (Monday, October 26, 2026)*

[![Course](https://img.shields.io/badge/Course-AILT9019_AI_Literacy_II-blue.svg)](https://moodle.hku.hk/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_WebSocket-009688.svg)](https://fastapi.tiangolo.com/)
[![LLM](https://img.shields.io/badge/AI_Core-GLM_4.5_Air-orange.svg)](https://open.bigmodel.cn/)
[![Status](https://img.shields.io/badge/Status-Sprint_1_Underway-success.svg)](#-sprint-roadmap--team-tasks)

---

## 📖 Overview

Contemporary digital social platforms rely almost exclusively on appearance-driven swipe mechanisms, biographical self-presentation, and unprompted text icebreakers. This paradigm produces substantial social anxiety, superficial judgment, and conversational fatigue.

**ConnectFour Connect** is an activity-mediated social interaction prototype:
1. **Activity-First Socializing**: Interpersonal interaction takes place within a live, turn-based 7×6 Connect Four game. The shared game rules eliminate awkward pauses and lower emotional stakes.
2. **Safe Canned Communication**: Free-form text input is completely omitted by design. Players interact exclusively using a sportsmanship palette of **6 preset phrases** and **4 reaction stickers** with animated speech bubbles.
3. **Age-Gated In-Memory Matchmaking**: Players complete lightweight guest registration (Nickname + Birth Year). The backend enforces $\text{Age} \ge 18$ and pairs users with peers within an acceptable age difference ($|\Delta\text{Age}| \le 3$).
4. **Guaranteed Zero-Wait Availability (AI Fallback)**: If a human peer is not found within the 15-second matchmaking queue, the server automatically routes the player into a PvE room with an intelligent **GLM-4.5-Air** opponent (temporary; **GLM-4.7-Flash** is the target once account access is enabled).
5. **Fail-Safe Fallback**: If the upstream LLM returns a rate-limit/error response or exceeds the **3.5s** move deadline, the server immediately plays a safe center-out legal move so the room never stalls; the deterministic Minimax bot is retained and will be re-wired in WP3-7.
6. **Zero Persistent PII**: All user sessions and room memory exist strictly in RAM and are immediately purged upon socket disconnection.

> **⚠️ Current sprint note (2026-10-22):** PvE temporarily uses **GLM-4.5-Air** because this account cannot yet access `glm-4.7-flash` or `glm-4.5-flash`. The live Connect Four prompt measured **~2.3–2.9s**, so the local deadline is **3.5s**. **GLM-4.7-Flash** remains the target once it is enabled in the GLM console. Gemini integration is deferred. The Minimax fallback is temporarily unwired; if GLM is unavailable, the server plays a safe center-out move so the room never stalls. See [docs/WORKLOG.md](file:///d:/Github%20Homepage/AILT9019_G31/docs/WORKLOG.md) for the current architecture and handoff notes.

---

## 🗂️ Documentation Navigation

All architectural, strategic, and task-tracking documents are organized in this repository:

| Document | Path | Description |
| :--- | :--- | :--- |
| **Team Task Checklist** | [TASKS.md](file:///d:/Github%20Homepage/AILT9019_G31/TASKS.md) | **Start here for development!** Claim tasks, update statuses, and log backlog ideas. |
| **Development Worklog** | [docs/WORKLOG.md](file:///d:/Github%20Homepage/AILT9019_G31/docs/WORKLOG.md) | **Running handoff log:** decisions, completed changes, verification commands, and next steps. |
| **Technical Specification** | [docs/TECHNICAL_SPEC.md](file:///d:/Github%20Homepage/AILT9019_G31/docs/TECHNICAL_SPEC.md) | Full system architecture, WebSocket protocol frames, Connect Four physics, and test matrices. |
| **Project Plan** | [docs/PROJECT_PLAN.md](file:///d:/Github%20Homepage/AILT9019_G31/docs/PROJECT_PLAN.md) | Work Breakdown Structure (WBS), risk matrix, Gantt chart, and milestones through Oct 26. |
| **Revised Proposal** | [docs/proposal/](file:///d:/Github%20Homepage/AILT9019_G31/docs/proposal/AILT9019_Revised_Proposal_G31.md) | Formal course proposal submission (`.md`, `.docx`, `.pdf`) with peer review responses. |

---

## 📁 Repository Structure

```
AILT9019_G31/
├── README.md                           # Main repository overview & getting started guide
├── TASKS.md                            # Collaborative team task checklist & sprint board
├── docs/                               # Engineering & course documentation
│   ├── PROJECT_PLAN.md                 # WBS, milestones, sprint Gantt chart & risks
│   ├── TECHNICAL_SPEC.md               # Protocols, data models, AI fallback & engine spec
│   ├── WORKLOG.md                      # Running development log & handoff notes
│   └── proposal/                       # Proposal submission documents
│       ├── AILT9019_Revised_Proposal_G31.md
│       ├── AILT9019_Revised_Proposal_G31.docx
│       └── AILT9019_Revised_Proposal_G31.pdf
├── client/                             # Frontend single-page application
│   ├── index.html                      # Single-page responsive layout
│   ├── css/
│   │   └── style.css                   # Vibrant dark-mode UI & design system
│   └── js/
│       ├── app.js                      # Application controller & state coordinator
│       ├── game_board.js               # Canvas 2D 7x6 board & gravity animations
│       ├── canned_chat.js              # Canned phrase palette & speech bubbles
│       └── socket_client.js            # WebSocket protocol connection handler
├── server/                             # FastAPI backend service
│   ├── requirements.txt                # Python dependencies
│   ├── .env.example                    # GLM/AI settings template (never commit .env)
│   └── app/
│       ├── __init__.py
│       ├── main.py                     # ASGI entrypoint & WebSocket endpoint (/ws/game)
│       ├── config.py                   # Environment-backed AI settings & secret hygiene
│       ├── game_engine.py              # 7x6 Connect Four rules, win & draw logic
│       ├── matchmaking.py              # In-memory FIFO queue & age filtering (planned)
│       ├── room_manager.py             # Active room lifecycle & ephemeral state (planned)
│       ├── schemas.py                  # Pydantic protocol models & event payloads
│       └── ai/
│           ├── __init__.py
│           ├── glm_client.py           # GLM-4.5-Air OpenAI-compatible client (temporary)
│           └── minimax_fallback.py     # Deterministic Alpha-Beta heuristic bot
├── tests/                              # Automated test suites & verification
│   ├── test_connect4_engine.py         # Connect Four rules & win detection tests
│   ├── test_app_smoke.py               # FastAPI root/static/health/WS smoke tests
│   ├── test_glm_client.py              # Mocked GLM request/parse/validation tests
│   ├── test_ai_turn.py                 # GLM PvE turn + safe-move fallback tests
│   ├── test_suite_a_matchmaking.py     # Test Suite A: 20 age boundary cases
│   └── test_suite_b_fault_injection.py # Test Suite B: 10 LLM fault injection tests
└── deploy/                             # Production deployment configuration
    ├── nginx.conf                      # Nginx reverse proxy with SSL & WSS
    └── connectfour.service             # Systemd daemon service configuration
```

---

## 💻 Getting Started (For Team Members)

### 1. Prerequisites
- Python 3.12+ (or 3.14)
- A modern web browser (Chrome, Edge, Safari, Firefox)
- (Optional for AI) GLM API key (Zhipu/Z.ai), stored in `server/.env` or the server environment — never committed

### 2. Backend Setup
```bash
# Navigate to server directory
cd server

# Create and activate virtual environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure the AI layer (optional for PvP; required for GLM PvE)
# Windows PowerShell:
Copy-Item .env.example .env
# macOS / Linux:
# cp .env.example .env
# Then edit .env and set GLM_API_KEY=... Never commit the real .env.

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
The FastAPI server will be available at `http://127.0.0.1:8000`.  
WebSocket endpoint will be ready at `ws://127.0.0.1:8000/ws/game`.

### 3. Frontend Setup
The frontend is a lightweight, dependency-free vanilla HTML5/Canvas client.
You can either:
- Open `client/index.html` directly in your browser, or
- Serve it via Python's built-in HTTP server:
```bash
cd client
python -m http.server 3000
```
Then visit `http://localhost:3000` in two separate browser tabs to test multiplayer!

### 4. Running Automated Tests
```bash
# Run all unit tests and test suites
pytest tests/ -v
```

---

## 👥 Collaboration & Contribution Workflow

To keep development organized and aligned with our proposal milestones:

1. **Check the Task Board**: Open [TASKS.md](file:///d:/Github%20Homepage/AILT9019_G31/TASKS.md).
2. **Claim a Task**: Pick an unassigned task (`@Unassigned`), add your name, and set the status to `[IN PROGRESS]`.
3. **Branching Convention**:
   - `feat/wp1-canvas-renderer`
   - `feat/wp2-websocket-gateway`
   - `feat/wp3-glm-ai`
   - `fix/connect4-diagonal-check`
4. **Testing Before Merge**: Ensure all unit tests pass before committing:
   ```bash
   pytest tests/
   ```
5. **Mark Done**: Update [TASKS.md](file:///d:/Github%20Homepage/AILT9019_G31/TASKS.md) with `[x]` and `[DONE]`.

---

## 📅 Key Deadlines & Deliverables

| Date | Milestone | Deliverable |
| :--- | :--- | :--- |
| **Sat, Oct 10 (Week 6)** | Proposal Final Submission | Submit Revised Proposal PDF via Moodle form |
| **Sun, Oct 11 (Week 6)** | Sprint 1 Review | Local 2-player PvP prototype working over WebSockets |
| **Sun, Oct 18 (Week 7)** | Sprint 2 Review | Cloud VPS deployment + GLM AI integration |
| **Sun, Oct 25 (Week 8)** | Sprint 3 Review | 100% pass on Test Suites A & B; 15-student user trials completed |
| **Mon, Oct 26** | **Mid-Term Checkpoint** | Live public URL + walkthrough demo video + progress report |

---

*For technical questions or protocol references, please consult [docs/TECHNICAL_SPEC.md](file:///d:/Github%20Homepage/AILT9019_G31/docs/TECHNICAL_SPEC.md).*
