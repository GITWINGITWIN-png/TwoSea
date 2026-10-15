"""render ทุกตอนของ deck แล้ว export ไฟล์นำเสนอและไฟล์ส่ง

    uv run python tools/build_deck.py v000            # -ql (เร็ว ใช้ตรวจ)
    uv run python tools/build_deck.py v002 --hq       # -qh 1080p30 ฉบับจริง
    uv run python tools/build_deck.py v001 --only SQ03 SQ05   # render ใหม่เฉพาะบางตอน แล้ว export ทั้ง deck

ได้ใน export/:
  two-seas_<v>.pptx       ไฟล์ส่งอาจารย์ — หนึ่งคลิก = หนึ่ง slide วิดีโอเล่นเอง + โน้ตผู้พูด
  two-seas_<v>.pdf        ฉบับอ่าน — เฟรมสุดท้ายของทุกคลิก
  two-seas_<v>.html       ฉบับนำเสนอสำรอง — ออฟไลน์ ไฟล์เดียว (Firefox · กด S = โน้ต)
  cues_<v>.md             โน้ตทุกหน้าสำหรับเปิดบนมือถือ
แล้วพิมพ์ตารางสถานะ: หน้าไหนเป็นแอนิเมชันแล้ว / ยังเป็นภาพสำรอง

นำเสนอจากโน้ตบุ๊ก (หลัง build):  ./present.sh
"""

import argparse
import importlib
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "manim"))
os.environ["PYTHONPATH"] = str(ROOT / "manim")

import slides_kit  # noqa: E402

SLUG_FILES = {p.stem.split("_")[0].upper(): p for p in sorted((ROOT / "manim").glob("sq[0-9][0-9]_*.py"))}
SEQS = sorted(SLUG_FILES)  # SQ01 … SQ11 (ภาคผนวกอยู่ท้าย)


def render(seq, hq):
    # media_dir แยกต่อตอน: render ขนานใช้ cache ข้อความ (texts/*.svg) ร่วมกันไม่ได้ — process หนึ่งลบไฟล์ที่อีกตัวกำลังใช้
    cmd = ["uv", "run", "manim-slides", "render", "-qh" if hq else "-ql",
           "--media_dir", str(ROOT / "renders" / "manim" / seq.lower()), str(SLUG_FILES[seq]), seq]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        tail = "\n".join((r.stdout + r.stderr).splitlines()[-15:])
        raise SystemExit(f"render {seq} ไม่ผ่าน:\n{tail}")
    return seq


def convert(dest, extra=()):
    subprocess.run(["uv", "run", "manim-slides", "convert", *extra, *SEQS, str(dest)], cwd=ROOT, check=True,
                   capture_output=True)


def status():
    rows, animated_total, main_total = [], 0, 0
    for seq in SEQS:
        module = importlib.import_module(SLUG_FILES[seq].stem)
        cls = getattr(module, seq)
        pages = slides_kit.pages_of(seq)
        done = set(cls.animated_pages())
        for p in pages:
            is_video = p["tool"] == "blender"
            if seq != slides_kit.APPENDIX:
                main_total += 1
                animated_total += p["id"] in done
            rows.append((p["id"], "แอนิเมชัน" if p["id"] in done else ("ภาคผนวก" if seq == slides_kit.APPENDIX
                                                                       else "ภาพสำรอง"),
                         "วิดีโอ Blender" if is_video else ""))
    return rows, animated_total, main_total


def cues(path):
    lines = ["# โน้ตผู้พูด — ทะเลสองฝั่ง ฟังภูมิอากาศคนละแบบ", ""]
    for pid in slides_kit.pages():
        lines += [f"## {slides_kit.page_number(pid)} · {pid}", "", slides_kit.notes(pid), ""]
    path.write_text("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version", help="เช่น v000")
    ap.add_argument("--hq", action="store_true", help="render -qh 1080p30 (ฉบับจริง)")
    ap.add_argument("--only", nargs="*", help="render ใหม่เฉพาะตอนเหล่านี้")
    args = ap.parse_args()

    subprocess.run(["uv", "run", "python", "tools/make_shotlist.py"], cwd=ROOT, check=True, capture_output=True)
    check = subprocess.run(["uv", "run", "python", "tools/check_claims.py"], cwd=ROOT, capture_output=True, text=True)
    if check.returncode != 0:
        raise SystemExit("check_claims ไม่ผ่าน — แก้ก่อน build:\n" + check.stdout[-2000:])

    todo = [s.upper() for s in args.only] if args.only else SEQS
    # render ขนาน 3 ตอน: แต่ละตอนเป็น process แยก (Manim ใช้ CPU หลักเดียวต่อ process เป็นส่วนใหญ่)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for seq in pool.map(lambda s: render(s, args.hq), todo):
            print(f"  render {seq} ✓")

    out = ROOT / "export"
    out.mkdir(exist_ok=True)
    base = out / f"two-seas_{args.version}"
    convert(base.with_suffix(".pptx"))
    convert(base.with_suffix(".pdf"))
    convert(base.with_suffix(".html"), ["--offline", "--one-file"])
    cues(out / f"cues_{args.version}.md")

    rows, done, total = status()
    print(f"\nสถานะ {args.version}: แอนิเมชัน {done}/{total} หน้าหลัก")
    for pid, state, note in rows:
        if state != "แอนิเมชัน":
            continue
        print(f"  ✓ {pid} {note}")
    left = [pid for pid, state, _ in rows if state == "ภาพสำรอง"]
    if left:
        print(f"  ยังเป็นภาพสำรอง ({len(left)}): {' '.join(left)}")
    for f in sorted(out.glob(f"*{args.version}*")):
        print(f"  {f.relative_to(ROOT)}  {f.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
