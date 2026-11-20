# ConnectFour Connect: 3-Minute Demo Video Script & Storyboard

**Course:** AILT9019 · AI Literacy II  
**Academic Term:** Autumn 2026  
**Team:** Group 31  
**Project:** ConnectFour Connect — Activity-Mediated Social Mini-Game with Multi-Tier AI Architecture  
**Target Duration:** Exactly 3 Minutes (180 Seconds)  
**Deliverables:** Video (`.mp4` / `.webm`) + Synchronized Subtitles (`subtitles.srt`, `subtitles.vtt`)

---

## 1. Overview & Speaker Allocation

All four team members present in the video, with roles and speaking times directly aligned with their architectural contributions:

| Segment | Timecode | Speaker | Core Topic & Responsibility | Deliverable / On-Screen Focus |
| :---: | :---: | :--- | :--- | :--- |
| **Part 1** | `0:00 - 0:45` *(45s)* | **Yuzhou Zhou** *(CelVision)*<br>**Team Lead & Architecture** | • Campus social anxiety problem hook<br>• Activity-mediated interaction paradigm<br>• Guest onboarding & AI Settings accordion | Landing page title card → Guest registration (`Alex_HKU`, Birth Year `2003`) → Custom AI Settings |
| **Part 2** | `0:45 - 1:30` *(45s)* | **Yuexiang Ma** *(MA Yue Xiang)*<br>**Backend Systems & QA** | • Age-gated queue ($Age \ge 18, \|\Delta Age\| \le 3$)<br>• Single-pass deterministic queue tick & heartbeat<br>• 15s timeout auto-routing to PvE room | Matchmaking queue countdown (`Finding peer... 15s`) → Underage rejection → Seamless 15s PvE transition |
| **Part 3** | `1:30 - 2:15` *(45s)* | **Leo Shang** *(LeoShang22)*<br>**Frontend Client Lead** | • HTML5 Canvas 2D engine & Pointer Events<br>• Token descent gravity & cyan move indicator<br>• Zero-asset Web Audio API sound synthesis | Mouse hover & column select → Token drop animation → Canned reaction tray & audio chimes |
| **Part 4** | `2:15 - 3:00` *(45s)* | **Scott Xiang** *(XIANG HANCHENG)*<br>**DevOps & Infrastructure** | • Qwen3.6-Flash conversational AI Coach in PvE<br>• Local depth-4 Minimax failover (<25ms)<br>• Deployment verification & wrap-up | Daily Icebreaker card ("Midterm Prep") → AI Coach chat bubble → Heuristic failover notice → Wrap-up |

---

## 2. Second-by-Second Storyboard & Script

### Part 1: Project Vision & Onboarding (0:00 – 0:45)
**Speaker:** Yuzhou Zhou (Team Lead)

* **[0:00 - 0:15] Visual:** Title card displaying *ConnectFour Connect: Activity-Mediated Social Mini-Game with Multi-Tier AI Architecture (AILT9019 Group 31)*, followed by a screen transition to the live web application lobby at `http://localhost:8000/`.
  * **Spoken Lines (Yuzhou Zhou):**  
    > "Hello everyone! I'm Yuzhou Zhou, team lead for Group 31. Modern university students experience substantial conversational anxiety on mainstream social platforms, where appearance-driven swiping and unguided direct messaging create fear of judgment and conversational paralysis."
* **[0:15 - 0:30] Visual:** Mouse enters the guest registration card. Types nickname `Alex_HKU`, selects birth year `2003` (verifying Age 23 $\ge 18$). Cursor hovers over and expands the *"AI & Advanced Settings"* accordion, showing custom API key and model selection options.
  * **Spoken Lines (Yuzhou Zhou):**  
    > "With ConnectFour Connect, we introduce an activity-mediated social paradigm: interpersonal interaction is centered around turn-based Connect Four, where game moves provide organic pacing and lower emotional friction. Onboarding is lightweight and collects zero persistent PII—players simply enter a nickname and birth year."
* **[0:30 - 0:45] Visual:** Cursor clicks the vibrant blue **"Find Match"** button. The card transitions to the live Matchmaking Queue view, showing the spinning radar icon and a 1-hertz authoritative countdown: *"Finding peer... 15s remaining"*.
  * **Spoken Lines (Yuzhou Zhou):**  
    > "When clicking 'Find Match', our WebSocket gateway initiates an authoritative 1-hertz heartbeat countdown driven strictly by server state rather than client-side timers."

---

### Part 2: Matchmaking, Age-Gating & Safety Enforcement (0:45 – 1:30)
**Speaker:** Yuexiang Ma (Backend Systems & QA Lead)

* **[0:45 - 1:05] Visual:** Queue screen displaying active status: `Queue position: 1 · Target age gap: |ΔAge| ≤ 3 years`. A split screen or popover briefly shows a rejected underage registration attempt returning `error: underage (Must be 18 or older)`.
  * **Spoken Lines (Yuexiang Ma):**  
    > "Hi, I'm Yuexiang Ma, backend systems and QA lead. I designed our in-memory FIFO matchmaking queue and room lifecycle manager. Our queue enforces an age filter where only peers with an age gap within three years are paired together, while rejecting registrations under eighteen."
* **[1:05 - 1:20] Visual:** The queue countdown ticks down: `2s... 1s... 0s`. At exactly 15.0 seconds, the client seamlessly receives `pve_match_found` from the server. The screen smoothly transitions into an active match room with the **AI Coach**.
  * **Spoken Lines (Yuexiang Ma):**  
    > "To eliminate waiting times, if no compatible peer matches within our fifteen-second timeout, the single-pass queue engine automatically instantiates a PvE room with our AI Coach, ensuring solo testers experience zero wait time."
* **[1:20 - 1:30] Visual:** Focus shifts to the in-game communication tray. Mouse hovers over the canned reaction buttons.
  * **Spoken Lines (Yuexiang Ma):**  
    > "In PvP matches, free-form text is structurally blocked by architectural design—players communicate exclusively through sportsmanlike canned phrases and Daily Icebreakers, completely eliminating peer harassment."

---

### Part 3: Canvas 2D Engine, Input & Procedural Audio (1:30 – 2:15)
**Speaker:** Leo Shang (Frontend Client Lead)

* **[1:30 - 1:45] Visual:** Full view of the responsive 7×6 Connect Four board. Mouse moves horizontally across the top of columns 0 through 6; a hovering circular ghost token highlights the active column. Cursor clicks column 3 (center).
  * **Spoken Lines (Leo Shang):**  
    > "Hello, I'm Leo Shang, frontend client lead. I developed the HTML5 Canvas 2D board engine and client interaction layer. We use a unified Pointer Events architecture that seamlessly normalizes multi-touch, stylus, and desktop mouse clicks with responsive coordinate scaling."
* **[1:45 - 2:00] Visual:** The Red token accelerates downwards with realistic gravity into row 5 (`dropTokenAnimated`). A glowing cyan ring highlights the token as the last played move. Opponent/AI responds in column 2. Player clicks the canned tray: *"Nice move!"* and the clapping sticker 👏 appears as an animated floating speech bubble.
  * **Spoken Lines (Leo Shang):**  
    > "Notice the smooth vertical gravity descent animation as tokens drop into the lowest vacant slot, and our glowing cyan indicator marking the most recent move. Floating speech bubbles render real-time sportsmanship reactions with smooth CSS animations."
* **[2:00 - 2:15] Visual:** Audio visualizer or sound effect demonstration: player drops another token (audible pitch bend 440Hz $\to$ 150Hz), clicks a sticker (pop sound), and triggers a 4-in-a-row victory (golden glowing boxes and celebratory arpeggio chime).
  * **Spoken Lines (Leo Shang):**  
    > "To maintain zero bandwidth overhead and instant audio playback, I implemented procedural sound synthesis using the native Web Audio API—synthesizing token drops, victory arpeggios, and reaction pops entirely with custom mathematical waveforms without loading any MP3 files."

---

### Part 4: Dual-Tier AI Subsystem, DevOps & Wrap-Up (2:15 – 3:00)
**Speaker:** Scott Xiang (DevOps & Infrastructure Lead)

* **[2:15 - 2:35] Visual:** In the in-game Match Hub sidebar, player clicks the Daily Icebreaker card *"Midterm Prep: What's your favorite study spot on campus?"*. In PvE mode, the player types: *"Any tips for Connect Four?"*. Within 1.8 seconds, a conversational reply from **AI Coach** (`qwen3.6-flash`) appears with strategic advice and friendly campus banter.
  * **Spoken Lines (Scott Xiang):**  
    > "Hi everyone, I'm Scott Xiang, DevOps and deployment lead. In PvE mode, we integrated Alibaba Cloud Bailian's Qwen3.6-Flash through an OpenAI-compatible endpoint. The AI Coach acts as an engaging campus peer while enforcing strict conversational guardrails."
* **[2:35 - 2:50] Visual:** A simulated network timeout or latency spike is triggered. At 3.5 seconds, the server immediately triggers local Tier 2 fallback: within 23.6ms, the local Depth-4 Minimax bot plays column 3 and displays `strategy: minimax` in a subtle badge, keeping the game completely uninterrupted.
  * **Spoken Lines (Scott Xiang):**  
    > "Most importantly, we engineered an autonomous fail-safe: if the upstream API times out past three-and-a-half seconds or encounters a rate limit, our local depth-four Minimax algorithm immediately calculates the optimal move in under twenty-four milliseconds."
* **[2:50 - 3:00] Visual:** Brief terminal view showing `check_public_url.py` passing 8/8 deployment checks, followed by the concluding slide: GitHub URL (`https://github.com/CelVision/AILT9019_G31`) and Public Webpage (`https://celvision.github.io/AILT9019_G31/`).
  * **Spoken Lines (Scott Xiang):**  
    > "On the infrastructure side, the platform runs in a hardened non-root container with read-only filesystems. ConnectFour Connect delivers a safe, zero-latency, anxiety-free social gaming experience. Thank you!"

---

## 3. Production & Recording Instructions

1. **Resolution & Format:** 1920×1080 (1080p), 30 fps or 60 fps, 16:9 aspect ratio.
2. **Audio Levels:** Normalize narration to -14 LUFS to -16 LUFS; game sound effects mixed at -18 dB relative to voice.
3. **Subtitles:** Import `docs/subtitles.srt` into your video editor (CapCut, Premiere Pro, DaVinci Resolve) or upload directly to YouTube as a `.srt` / `.vtt` closed captions track.
4. **Speaker Tagging:** Ensure in-video subtitle styles display speaker names in brackets (e.g., `[Yuzhou Zhou]`, `[Yuexiang Ma]`, `[Leo Shang]`, `[Scott Xiang]`).
