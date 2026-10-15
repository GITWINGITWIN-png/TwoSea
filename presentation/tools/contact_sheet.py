"""รวมเฟรมสุดท้ายของทุกขั้น (ทุกคลิก) ในหนึ่งตอนเป็นภาพเดียว — ตรวจงานทั้งตอนด้วยการเปิดภาพครั้งเดียว

    uv run python tools/contact_sheet.py SQ03     # หลัง manim-slides render ของตอนนั้น -> renders/contact/SQ03.png

อ่านลำดับขั้นจาก slides/SQ03.json (ผลของ manim-slides) · ป้ายใต้ภาพ = ลำดับขั้น · loop · หัวข้อของหน้า
ใช้เฟรมสุดท้ายเพราะเป็นสภาพที่ค้างบนจอระหว่างคุณพูด (และเป็นสิ่งที่ PDF แสดง)
"""

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def last_frame(video, out):
    # ถอยจากท้าย 0.3 วินาที: ที่ 15 fps หนึ่งเฟรมยาว 0.067 วินาที ถ้าถอยน้อยกว่านี้ ffmpeg อาจได้ภาพว่างโดยไม่เตือน
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.3", "-i", str(video), "-update", "1",
                    "-vf", "scale=640:-1", str(out)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sequence", help="เช่น SQ03")
    seq = ap.parse_args().sequence.upper()
    config = ROOT / "slides" / f"{seq}.json"
    if not config.exists():
        raise SystemExit(f"ยังไม่มี {config} — render ตอนนั้นก่อน")
    slides = json.loads(config.read_text())["slides"]
    out = ROOT / "renders" / "contact" / f"{seq}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        cmd = ["magick", "montage"]
        for k, s in enumerate(slides, 1):
            png = Path(tmp) / f"{k:03d}.png"
            last_frame(ROOT / s["file"], png)
            first = s["notes"].splitlines()[0].lstrip("▶ ")[:42] if s["notes"] else ""
            cmd += ["-label", f"{k}{' · loop' if s['loop'] else ''} · {first}", str(png)]
        cmd += ["-tile", "3x", "-geometry", "+6+6", "-background", "#0E1A26", "-fill", "#EEF3F8",
                "-font", subprocess.check_output(["fc-match", "Sarabun", "-f", "%{file}"], text=True), "-pointsize", "15", str(out)]
        subprocess.run(cmd, check=True)
    print(out, f"({len(slides)} ขั้น)")


if __name__ == "__main__":
    main()
