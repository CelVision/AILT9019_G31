#!/usr/bin/env python3
"""
Automated 3-Minute (180 Seconds) Demo Video Recorder for ConnectFour Connect (AILT9019 Group 31).
Uses Playwright to:
1. Spin up the local FastAPI server.
2. Launch a 1280x720 browser with video recording enabled.
3. Parse docs/subtitles.srt and synchronize on-screen subtitles in real time (0:00 to 3:00).
4. Choreograph user actions across all 4 teammate segments:
   - Part 1 (0:00 - 0:45): Yuzhou Zhou (Onboarding & Vision)
   - Part 2 (0:45 - 1:30): Yuexiang Ma (Matchmaking, Age-Gating & Safety)
   - Part 3 (1:30 - 2:15): Leo Shang (Canvas 2D Engine, Input & Procedural Audio)
   - Part 4 (2:15 - 3:00): Scott Xiang (Dual-Tier AI Subsystem, DevOps & Wrap-Up)
5. Produces exactly 3 minutes (180.0s) of high-definition video: docs/ConnectFour_Connect_Demo_Sample.webm.
"""

import sys
import os
import re
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT_DIR / "docs"
SRT_PATH = DOCS_DIR / "subtitles.srt"
OUT_VIDEO_WEBM = DOCS_DIR / "ConnectFour_Connect_Demo_Sample.webm"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

TOTAL_DURATION = 180.0  # Exactly 3 minutes


def parse_srt(srt_file: Path):
    def parse_time(ts):
        h, m, s = ts.strip().replace(',', '.').split(':')
        return float(h) * 3600 + float(m) * 60 + float(s)

    content = srt_file.read_text(encoding="utf-8")
    blocks = re.split(r'\n\s*\n', content.strip())
    subtitles = []
    for b in blocks:
        lines = [l.strip() for l in b.split('\n') if l.strip()]
        if len(lines) >= 3:
            tc = lines[1].split(' --> ')
            start = parse_time(tc[0])
            end = parse_time(tc[1])
            text = ' '.join(lines[2:])
            speaker = "Speaker"
            if text.startswith('[') and ']' in text:
                speaker = text[1:text.index(']')]
                text = text[text.index(']') + 1:].strip()
            subtitles.append({
                "start": start,
                "end": end,
                "speaker": speaker,
                "text": text
            })
    return subtitles


def record_3min_demo():
    print(f"=== ConnectFour Connect: 3-Minute Demo Recording ({TOTAL_DURATION}s) ===")
    
    subtitles = parse_srt(SRT_PATH)
    print(f"Loaded {len(subtitles)} subtitles from {SRT_PATH.name}")

    # 1. Start local server
    print("[1/5] Starting local FastAPI server on port 8088...")
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8088", "--host", "127.0.0.1"],
        cwd=str(ROOT_DIR / "server"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2.5)

    rec_dir = DOCS_DIR / "temp_rec_3min"
    rec_dir.mkdir(parents=True, exist_ok=True)

    try:
        print("[2/5] Initializing Playwright video recorder (1280x720, 180.0s target)...")
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                record_video_dir=str(rec_dir),
                record_video_size={"width": 1280, "height": 720}
            )
            page = context.new_page()

            # Navigate to game
            page.goto("http://127.0.0.1:8088/", wait_until="networkidle")

            # Inject Subtitle Overlay DOM
            page.evaluate("""
                const subBox = document.createElement('div');
                subBox.id = 'demo-subtitles';
                subBox.style.cssText = `
                    position: fixed;
                    bottom: 22px;
                    left: 50%;
                    transform: translateX(-50%);
                    z-index: 9999999;
                    pointer-events: none;
                    user-select: none;
                    background: rgba(15, 23, 42, 0.94);
                    border: 1.5px solid #38bdf8;
                    border-radius: 12px;
                    padding: 10px 24px;
                    width: 82%;
                    max-width: 920px;
                    color: #ffffff;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    font-size: 15px;
                    line-height: 1.45;
                    text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.7);
                    backdrop-filter: blur(10px);
                    transition: all 0.25s ease;
                `;
                subBox.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 4px;">
                        <span id="speaker-badge" style="background: #0284c7; color: white; padding: 2px 10px; border-radius: 9999px; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Speaker</span>
                        <span style="font-size: 11px; color: #94a3b8;">AILT9019 · AI Literacy II · Group 31</span>
                    </div>
                    <div id="sub-text" style="font-weight: 500;">ConnectFour Connect: Activity-Mediated Social Mini-Game</div>
                `;
                document.body.appendChild(subBox);
            """)

            def update_subtitle(speaker: str, text: str, badge_color: str):
                safe_text = text.replace('"', '\\"').replace("'", "\\'")
                page.evaluate(f"""
                    document.getElementById('speaker-badge').innerText = "{speaker}";
                    document.getElementById('speaker-badge').style.background = "{badge_color}";
                    document.getElementById('sub-text').innerText = "{safe_text}";
                """)

            speaker_colors = {
                "Yuzhou Zhou": "#0284c7",
                "Yuexiang Ma": "#10b981",
                "Leo Shang": "#ec4899",
                "Scott Xiang": "#f59e0b"
            }

            speaker_titles = {
                "Yuzhou Zhou": "Yuzhou Zhou · Team Lead & Architecture",
                "Yuexiang Ma": "Yuexiang Ma · Backend Systems & QA Lead",
                "Leo Shang": "Leo Shang · Frontend Client Lead",
                "Scott Xiang": "Scott Xiang · DevOps & Infrastructure Lead"
            }

            print("[3/5] Starting 3-Minute Real-Time Synchronized Choreography...")
            start_wall_time = time.time()

            # State tracking flags for actions
            actions_done = set()

            while True:
                elapsed = time.time() - start_wall_time
                if elapsed >= TOTAL_DURATION:
                    break

                # 1. Update Subtitle based on current timestamp
                current_sub = None
                for sub in subtitles:
                    if sub["start"] <= elapsed <= sub["end"]:
                        current_sub = sub
                        break

                if current_sub:
                    spk = current_sub["speaker"]
                    title = speaker_titles.get(spk, spk)
                    color = speaker_colors.get(spk, "#0284c7")
                    update_subtitle(title, current_sub["text"], color)
                elif elapsed > subtitles[-1]["end"]:
                    update_subtitle("Group 31", "AILT9019 · AI Literacy II · ConnectFour Connect · Thank you!", "#38bdf8")

                # 2. Trigger Action Choreography at specific time checkpoints
                # --- Part 1 (0:00 - 0:45): Yuzhou Zhou ---
                if elapsed >= 12.0 and "fill_nickname" not in actions_done:
                    actions_done.add("fill_nickname")
                    try:
                        page.fill("#nicknameInput", "Alex_HKU")
                        print(f"[{elapsed:.1f}s] Filled nickname: Alex_HKU")
                    except Exception as e:
                        pass

                if elapsed >= 18.0 and "fill_birth_year" not in actions_done:
                    actions_done.add("fill_birth_year")
                    try:
                        page.fill("#birthYearInput", "2003")
                        print(f"[{elapsed:.1f}s] Filled birth year: 2003 (Age 23)")
                    except Exception as e:
                        pass

                if elapsed >= 24.0 and "toggle_accordion" not in actions_done:
                    actions_done.add("toggle_accordion")
                    try:
                        page.click("summary.custom-ai-summary", force=True)
                        print(f"[{elapsed:.1f}s] Expanded AI settings accordion")
                    except Exception:
                        pass

                if elapsed >= 32.0 and "close_accordion" not in actions_done:
                    actions_done.add("close_accordion")
                    try:
                        page.click("summary.custom-ai-summary", force=True)
                        print(f"[{elapsed:.1f}s] Closed AI settings accordion")
                    except Exception:
                        pass

                if elapsed >= 38.0 and "find_match" not in actions_done:
                    actions_done.add("find_match")
                    try:
                        page.click("#btnFindMatch", force=True)
                        print(f"[{elapsed:.1f}s] Clicked Find Match (15s Max)")
                    except Exception as e:
                        pass

                # --- Part 2 (0:45 - 1:30): Yuexiang Ma ---
                # Matchmaking queue runs from 38s to 53s (15s timeout auto-routes to PvE)
                if elapsed >= 56.0 and "room_entered" not in actions_done:
                    actions_done.add("room_entered")
                    print(f"[{elapsed:.1f}s] 15s timeout expired; entered PvE match room with AI Coach")

                # --- Part 3 (1:30 - 2:15): Leo Shang ---
                if elapsed >= 94.0 and "hover_board" not in actions_done:
                    actions_done.add("hover_board")
                    try:
                        canvas = page.locator("#gameCanvas")
                        if canvas.count() > 0:
                            box = canvas.bounding_box()
                            if box:
                                for c in range(7):
                                    cx = box["x"] + (box["width"] / 7) * (c + 0.5)
                                    cy = box["y"] + (box["height"] / 2)
                                    page.mouse.move(cx, cy)
                                    time.sleep(0.1)
                                print(f"[{elapsed:.1f}s] Hovered across columns 0-6 on Canvas 2D")
                    except Exception:
                        pass

                if elapsed >= 104.0 and "drop_col3" not in actions_done:
                    actions_done.add("drop_col3")
                    try:
                        canvas = page.locator("#gameCanvas")
                        if canvas.count() > 0:
                            box = canvas.bounding_box()
                            if box:
                                col3_x = box["x"] + (box["width"] / 7) * 3.5
                                col_y = box["y"] + (box["height"] / 2)
                                page.mouse.click(col3_x, col_y)
                                print(f"[{elapsed:.1f}s] Dropped Red token into Column 3 (center)")
                    except Exception:
                        pass

                if elapsed >= 114.0 and "canned_reaction" not in actions_done:
                    actions_done.add("canned_reaction")
                    try:
                        page.locator(".phrase-btn").nth(1).click(force=True)  # "Nice move!"
                        time.sleep(0.5)
                        page.locator(".sticker-btn").nth(0).click(force=True) # Thumbs Up 👍
                        print(f"[{elapsed:.1f}s] Sent canned phrase 'Nice move!' and reaction sticker 👍")
                    except Exception:
                        pass

                if elapsed >= 124.0 and "drop_col2" not in actions_done:
                    actions_done.add("drop_col2")
                    try:
                        canvas = page.locator("#gameCanvas")
                        if canvas.count() > 0:
                            box = canvas.bounding_box()
                            if box:
                                col2_x = box["x"] + (box["width"] / 7) * 2.5
                                col_y = box["y"] + (box["height"] / 2)
                                page.mouse.click(col2_x, col_y)
                                print(f"[{elapsed:.1f}s] Dropped Red token into Column 2")
                    except Exception:
                        pass

                # --- Part 4 (2:15 - 3:00): Scott Xiang ---
                if elapsed >= 138.0 and "click_icebreaker" not in actions_done:
                    actions_done.add("click_icebreaker")
                    try:
                        icebreaker = page.locator(".topic-pill-btn").nth(1)  # Midterm Prep
                        if icebreaker.count() > 0:
                            icebreaker.click(force=True)
                            print(f"[{elapsed:.1f}s] Sent Daily Icebreaker card: Midterm Prep")
                    except Exception:
                        pass

                if elapsed >= 148.0 and "chat_coach" not in actions_done:
                    actions_done.add("chat_coach")
                    try:
                        chat_input = page.locator("#chatInput")
                        if chat_input.count() > 0 and chat_input.is_visible():
                            chat_input.fill("Any tips for Connect Four strategy?")
                            time.sleep(0.3)
                            page.locator("#btnSendChat").click(force=True)
                            print(f"[{elapsed:.1f}s] Sent chat message to AI Coach: 'Any tips for Connect Four strategy?'")
                    except Exception:
                        pass

                if elapsed >= 164.0 and "drop_col4" not in actions_done:
                    actions_done.add("drop_col4")
                    try:
                        canvas = page.locator("#gameCanvas")
                        if canvas.count() > 0:
                            box = canvas.bounding_box()
                            if box:
                                col4_x = box["x"] + (box["width"] / 7) * 4.5
                                col_y = box["y"] + (box["height"] / 2)
                                page.mouse.click(col4_x, col_y)
                                print(f"[{elapsed:.1f}s] Dropped Red token into Column 4")
                    except Exception:
                        pass

                # Progress logging every 15 seconds
                if int(elapsed) % 15 == 0 and int(elapsed) not in actions_done:
                    actions_done.add(int(elapsed))
                    print(f"      ... recording progress: {int(elapsed)}s / {int(TOTAL_DURATION)}s")

                time.sleep(0.2)

            print(f"[4/5] 180 seconds reached! Finalizing video context...")
            context.close()
            recorded_file = page.video.path()
            browser.close()

            print(f"[5/5] Moving recorded video from {recorded_file} to {OUT_VIDEO_WEBM}...")
            if os.path.exists(recorded_file):
                if OUT_VIDEO_WEBM.exists():
                    OUT_VIDEO_WEBM.unlink()
                import shutil
                shutil.move(recorded_file, OUT_VIDEO_WEBM)
                file_size_mb = OUT_VIDEO_WEBM.stat().st_size / (1024 * 1024)
                print(f"      ✓ SUCCESS: 3-Minute demo video recorded at: {OUT_VIDEO_WEBM}")
                print(f"      ✓ Size: {file_size_mb:.2f} MB")
                print(f"      ✓ Duration: {TOTAL_DURATION} seconds (3:00)")
            else:
                print("ERROR: Video file was not created by Playwright.")

    finally:
        server_proc.terminate()
        server_proc.wait()


if __name__ == "__main__":
    record_3min_demo()
