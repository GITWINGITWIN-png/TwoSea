"""render ฉาก Manim แบบ clip mode แล้ววางคลิปทีละขั้นให้ deck (Slidev) ใช้

    PYTHONPATH=manim uv run python tools/export_clips.py manim/sq03_signal.py SQ03 [--res 1760,800] [--fps 30]

ฉาก clip mode แบ่ง section ด้วยชื่อ "<รหัสหน้า>__<ขั้น>" (เช่น SQ03_S030__2) — Manim (--save_sections) เขียนวิดีโอ
หนึ่งไฟล์ต่อ section · สคริปต์นี้คัดลอกเป็น deck/public/clips/<รหัสหน้า>/<ขั้น>.mp4 และดึงเฟรมสุดท้ายเป็น <ขั้น>.png
(ใช้ตอน export PDF และตอนย้อนหน้า — ภาพนิ่งที่ตรงกับตอนจบของขั้นนั้นพอดี)

section ที่ชื่อไม่ตรงรูปแบบ (เช่น section อัตโนมัติก่อนขั้นแรก) ข้ามไป
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLIPS = ROOT / "deck" / "public" / "clips"
MEDIA = ROOT / "renders" / "manim"  # ตาม manim.cfg
SECTION = re.compile(r"^(SQ\d{2}_S\d{3})__(\d+)$")


def render(scene_file: Path, scene: str, res: str, fps: int) -> Path:
    """render ทั้งฉากด้วย --save_sections · คืนโฟลเดอร์ sections ที่ Manim เขียน"""
    width, height = res.split(",")
    cmd = ["manim", "render", "--save_sections", "-r", res, "--fps", str(fps), str(scene_file), scene]
    subprocess.run(cmd, cwd=ROOT, check=True)
    sections = MEDIA / "videos" / scene_file.stem / f"{height}p{fps}" / "sections"
    if not sections.is_dir():
        raise SystemExit(f"ไม่พบโฟลเดอร์ sections ที่ {sections}")
    return sections


def last_frame(video: Path, png: Path) -> None:
    """เฟรมสุดท้ายของวิดีโอ — -sseof -0.3 (ค่า -0.05 ได้ไฟล์ว่างเงียบ ๆ กับวิดีโอ 15 fps: บทเรียนจาก fit test manim-slides)"""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.3", "-i", str(video),
                    "-frames:v", "1", "-update", "1", str(png)], check=True)


def export(sections: Path, scene: str) -> list[str]:
    index = json.loads((sections / f"{scene}.json").read_text())
    written = []
    for entry in index:
        m = SECTION.match(entry["name"])
        if not m or not entry.get("video"):
            continue
        page, step = m.group(1), int(m.group(2))
        out = CLIPS / page
        out.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(sections / entry["video"], out / f"{step}.mp4")
        last_frame(out / f"{step}.mp4", out / f"{step}.png")
        written.append(f"{page}/{step}")
    return written


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("scene_file", type=Path)
    ap.add_argument("scene")
    ap.add_argument("--res", default="1760,800", help="ความกว้าง,ความสูง ของพื้นที่เนื้อหา (px)")
    ap.add_argument("--fps", type=int, default=30)
    args = ap.parse_args()
    written = export(render(args.scene_file, args.scene, args.res, args.fps), args.scene)
    print(f"{len(written)} คลิป → {CLIPS.relative_to(ROOT)}: " + " · ".join(written))


if __name__ == "__main__":
    main()
