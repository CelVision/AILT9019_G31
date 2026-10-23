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

> **⚠️ Current sprint note (2026-10-22):** PvE temporarily uses **GLM-4.5-Air** because this account cannot yet access `glm-4.7-flash` or `glm-4.5-flash`. The live Connect Four prompt measured **~2.3–2.9s**, so the local deadline is **3.5s**. **GLM-4.7-Flash** remains the target once it is enabled in the GLM console. Gemini integration is deferred. The Minimax fallback is temporarily unwired; if GLM is unavailable, the server plays a safe center-out move so the room never stalls. See [docs/WORKLOG.md](docs/WORKLOG.md) for the current architecture and handoff notes.

---

## 🗂️ Documentation Navigation

All architectural, strategic, and task-tracking documents are organized in this repository:

| Document | Path | Description |
| :--- | :--- | :--- |
| **Deployment changelog** | [docs/CHANGELOG.md](docs/CHANGELOG.md) | Deployment implementation, verification and remaining work. |
| **Team Task Checklist** | [TASKS.md](TASKS.md) | **Start here for development!** Claim tasks, update statuses, and log backlog ideas. |
| **Development Worklog** | [docs/WORKLOG.md](docs/WORKLOG.md) | **Running handoff log:** decisions, completed changes, verification commands, and next steps. |
| **Technical Specification** | [docs/TECHNICAL_SPEC.md](docs/TECHNICAL_SPEC.md) | Full system architecture, WebSocket protocol frames, Connect Four physics, and test matrices. |
| **Project Plan** | [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) | Work Breakdown Structure (WBS), risk matrix, Gantt chart, and milestones through Oct 26. |
| **Revised Proposal** | [docs/proposal/](docs/proposal/AILT9019_Revised_Proposal_G31.md) | Formal course proposal submission (`.md`, `.docx`, `.pdf`) with peer review responses. |

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
│   ├── CHANGELOG.md                    # Deployment change history
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
│   ├── test_deployment_check.py        # Deployment checker regression tests
│   ├── test_suite_a_matchmaking.py     # Planned: 20 age boundary cases
│   └── test_suite_b_fault_injection.py # Planned: 10 LLM fault injection tests
└── deploy/                             # Production deployment configuration
    ├── Dockerfile                      # Non-root single-worker application image
    ├── Dockerfile.dockerignore         # Build-context allowlist
    ├── compose.yaml                    # Container deployment configuration
    ├── check_public_url.py             # Health, assets and WS/WSS checks
    ├── nginx.conf                      # Nginx reverse proxy with SSL & WSS
    └── connectfour.service             # Systemd daemon service configuration
```

---

## 💻 Getting Started (For Team Members)

### 1. Prerequisites
- Python 3.12+ (or 3.14)
- A modern web browser (Chrome, Edge, Safari, Firefox)
- (Optional for AI) GLM API key (Zhipu/Z.ai), stored in `server/.env` or the server environment — never committed

### 2. Local setup

Run from the repository root:

```bash
python3 -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows: use python instead of python3 above, then .venv\Scripts\Activate.ps1
python -m pip install -r server/requirements.txt
python -m uvicorn app.main:app --app-dir server --host 127.0.0.1 --port 8000 --workers 1
```

Open **http://127.0.0.1:8000/**. The same service provides the frontend, `/api/health` and `/ws/game`; no frontend build or separate static server is needed. A static server on port 3000 cannot provide the client's same-origin WebSocket backend.

GLM is optional for a local run: without a key, the existing PvE handler uses a local legal-move fallback. For GLM, copy `server/.env.example` to `server/.env`, edit it locally and restart. Never commit a real key.

### 3. Deployment from the deploy directory

All commands below run from the **repository root**. Docker Engine/Desktop with modern Compose v2 is required for the container option:

```bash
docker compose -f deploy/compose.yaml config --quiet
docker compose -f deploy/compose.yaml up --build --detach --wait --wait-timeout 120
docker compose -f deploy/compose.yaml ps
```

Open **http://127.0.0.1:8000/**. Compose resolves its build context to the repository root and uses `deploy/Dockerfile` with its adjacent `Dockerfile.dockerignore`. Direct builds use `docker build -f deploy/Dockerfile -t connectfour:local .` from the root.

The image runs as a non-root user. Compose binds port 8000 to loopback, drops Linux capabilities, uses a read-only filesystem with temporary `/tmp`, and limits container log size. Keep **one instance and one worker**: rooms and matchmaking live in process memory. Restarting ends active games. Health checks report an unhealthy service, but the restart policy only restarts a process that exits.

For GLM settings, copy and edit the example, then pass the same environment file on each deployment command:

```bash
cp server/.env.example server/.env
# Edit server/.env locally, then:
docker compose --env-file server/.env -f deploy/compose.yaml up --build --detach --wait --wait-timeout 120
```

On a VPS, prefer a protected file outside the checkout, such as `/etc/connectfour/connectfour.env`. Only listed runtime settings enter the container; secrets are excluded from the build context. Use `config --quiet` to validate configuration without printing resolved credentials.

```bash
docker compose -f deploy/compose.yaml logs --tail 100 game
docker compose -f deploy/compose.yaml down
```

### 4. Native Ubuntu VPS alternative

Use either Compose or systemd on port 8000. For a native service, install Python 3.12+ with venv support and put a trusted checkout at `/var/www/AILT9019_G31`. Ensure `www-data` can traverse the checkout and read application files:

```bash
cd /var/www/AILT9019_G31
python3 -m venv server/venv
server/venv/bin/python -m pip install -r server/requirements.txt
sudo install -d -m 750 -o root -g www-data /etc/connectfour
# Optional: create/edit /etc/connectfour/connectfour.env for GLM.
# Set root:www-data ownership and mode 640 on that file.
sudo install -m 644 deploy/connectfour.service /etc/systemd/system/connectfour.service
sudo systemctl daemon-reload
sudo systemctl enable --now connectfour
sudo systemctl status connectfour --no-pager
sudo journalctl -u connectfour -n 100 --no-pager
```

The optional environment file is read by systemd. Without a key the application uses its local fallback. The service binds to loopback, uses one worker and logs to journald; no application log directory needs to be created. Its filesystem restrictions require the checkout to stay outside user home directories.

### 5. Public HTTPS and WSS

1. Point the domain's DNS to the VPS and allow inbound TCP 80/443 in the host and provider firewalls. Keep port 8000 private.
2. Install Nginx and obtain a trusted certificate using a DNS challenge or a temporary HTTP-only site. The HTTPS template cannot load before its certificate files exist.
3. Copy `deploy/nginx.conf` to `/etc/nginx/sites-available/connectfour`. Replace **every** `connectfour.example.com`, including certificate paths, with the actual domain. Resolve conflicting default sites before enabling it.
4. Enable and validate the site:

   ```bash
   sudo ln -s /etc/nginx/sites-available/connectfour /etc/nginx/sites-enabled/connectfour
   sudo nginx -t
   sudo systemctl reload nginx
   ```

5. Run the checker below against the final HTTPS origin. The browser automatically selects `wss://`; Nginx forwards the upgrade at `/ws/game`.
6. Configure certificate renewal and Nginx reload; with Certbot, verify using `sudo certbot renew --dry-run`.

Deployment templates do not establish that a public service is live. Record the commit, domain, date and observed results after running acceptance checks.

### 6. Tests and deployment acceptance

With the Python environment active, from the repository root:

```bash
python -m pytest tests/ -q
# Start the application in another terminal before this command:
python deploy/check_public_url.py http://127.0.0.1:8000
# Replace the example with the real final HTTPS origin:
python deploy/check_public_url.py https://your-domain.example --timeout 10
```

The checker requires healthy JSON, nonempty HTML/CSS/JS with appropriate content types, and a WebSocket upgrade plus ping/pong. HTTPS certificate verification stays enabled. Redirects fail deliberately so HTTP and WebSocket checks probe the same final origin. Failures exit with status 1. No player is registered and no GLM call is made.

After connectivity succeeds, use synthetic nicknames and compatible adult birth years in two browsers to verify matching, one move on both screens and a reaction. Separately check the no-peer PvE route and fallback notice. These game and manual accessibility checks are separate from infrastructure verification.

### 7. Updates and rollback

Save the current commit and keep its container image before an update. Tag builds with a commit ID by setting `CONNECTFOUR_IMAGE_TAG`. Replace `NEW_COMMIT` and `PREVIOUS_COMMIT` below with the relevant commit IDs; ensure the previous image exists locally before relying on rollback.

```bash
CONNECTFOUR_IMAGE_TAG=NEW_COMMIT docker compose --env-file /etc/connectfour/connectfour.env -f deploy/compose.yaml up --build --detach --wait --wait-timeout 120
# If verification fails, use the retained previous image without rebuilding:
CONNECTFOUR_IMAGE_TAG=PREVIOUS_COMMIT docker compose --env-file /etc/connectfour/connectfour.env -f deploy/compose.yaml up --no-build --detach --wait --wait-timeout 120
```

For native systemd, restore the previously tested checkout and dependency environment, restart `connectfour`, and rerun the checker. Updates and rollback interrupt in-memory games. Keep secrets outside the checkout.

---

## 👥 Collaboration & Contribution Workflow

To keep development organized and aligned with our proposal milestones:

1. **Check the Task Board**: Open [TASKS.md](TASKS.md).
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
5. **Mark Done**: Update [TASKS.md](TASKS.md) with `[x]` and `[DONE]`.

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

*For technical questions or protocol references, please consult [docs/TECHNICAL_SPEC.md](docs/TECHNICAL_SPEC.md).*
