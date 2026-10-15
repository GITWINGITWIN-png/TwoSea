"""ถ่ายภาพหน้า deck (Slidev) ไว้ตรวจด้วยตา — สร้าง deck ใหม่จากบท → build → ถ่ายหน้าที่ระบุในสภาพคลิกสุดท้าย

    uv run python tools/deck_shots.py SQ04_S020 SQ07_S020          # ได้ renders/shots/<ชื่อ>/<รหัสหน้า>.png
    uv run python tools/deck_shots.py --name agentB --port 8772 SQ07_S020
    uv run python tools/deck_shots.py SQ08_S030@2                     # สภาพคลิกที่ 2 → renders/shots/main/SQ08_S030@2.png

แต่ละหน้าพิมพ์ "ok" หรือ error ของหน้านั้น · ทำงานพร้อมกันหลายตัวได้ถ้า --name และ --port ไม่ซ้ำกัน
(--name แยกโฟลเดอร์ build · --port แยก server) · ภาพใหญ่ 1920×1080 = ขนาดจริงบนโปรเจกเตอร์
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECK = ROOT / "deck"


def page_index():
    """{รหัสหน้า: (ลำดับหน้าใน deck เริ่ม 1, จำนวนคลิก)} จาก deck/slides.md"""
    out, n = {}, 0
    for block in re.split(r"\n---\n(?=id: )", (DECK / "slides.md").read_text()):
        if m := re.search(r"^id: (SQ\d{2}_S\d{3})$", block, re.M):
            n += 1
            clicks = re.search(r"^clicks: (\d+)$", block, re.M)
            out[m.group(1)] = (n, int(clicks.group(1)) if clicks else 0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pages", nargs="+")
    ap.add_argument("--name", default="main")
    ap.add_argument("--port", type=int, default=8771)
    args = ap.parse_args()

    subprocess.run([sys.executable, str(ROOT / "tools" / "gen_deck.py")], check=True)
    out = ROOT / "renders" / "shots" / args.name
    site = out / "site"
    r = subprocess.run(["npx", "slidev", "build", "--out", str(site)], cwd=DECK, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:], r.stderr[-3000:])
        raise SystemExit("slidev build ล้ม")
    index = page_index()
    # "รหัสหน้า@N" = ถ่ายสภาพคลิก N แทนคลิกสุดท้าย (ชื่อไฟล์ติด @N ด้วย)
    wanted = [(p.partition("@")[0], p.partition("@")[2]) for p in args.pages]
    if missing := [p for p, _ in wanted if p not in index]:
        raise SystemExit(f"ไม่มีหน้า {missing}")
    server = subprocess.Popen([sys.executable, "-m", "http.server", str(args.port)], cwd=site,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(0.8)
        targets = [f"{index[p][0]}:{p}@{n}:{n}" if n else f"{index[p][0]}:{p}:{index[p][1]}" for p, n in wanted]
        subprocess.run(["node", str(ROOT / "tools" / "deck_shot.cjs"), str(DECK / "node_modules" / "playwright-chromium"),
                        str(args.port), str(out), *targets], check=True)
    finally:
        server.terminate()
    print(f"ภาพอยู่ที่ {out.relative_to(ROOT)}/<รหัสหน้า>.png")


if __name__ == "__main__":
    main()
