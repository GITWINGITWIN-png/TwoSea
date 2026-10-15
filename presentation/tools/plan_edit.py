"""วางแผน edit: แต่ละช็อตใช้สื่ออะไร ยาวเท่าไร เริ่มเฟรมไหน -> renders/edit_plan.json

    uv run python tools/plan_edit.py            # แล้วตามด้วย tools/build_edit.py ใน Blender

ลำดับการเลือกภาพของแต่ละช็อต (ดีสุดก่อน):
  final    renders/final/<ช็อต>.mov|mp4         ฉบับจริงที่ผ่านการตรวจแล้ว
  draft    วิดีโอ Manim ล่าสุด (1080p30 > 480p15) หรือ renders/blender/<ช็อต>.mp4
  fallback รูปจากรายงาน (00_input/report_figs) หรือการ์ดข้อความ (renders/cards) — เนื้อหาถูกเสมอ
ความยาว: context/timing.json (จากเสียงจริง) ถ้ามี ไม่อย่างนั้นประมาณจากจำนวนประโยค
"""

import json
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FPS = 30
SECONDS_PER_SENTENCE = 4.2
HEAD_SECONDS = 1.0   # ภาพนิ่งต้นคลิปก่อนเสียงแรก
GAP_SECONDS = 0.6    # ช่องหายใจระหว่างตอน


def pick_media(shot):
    sid, seq = shot["id"], shot["sequence"]
    for ext in ("mov", "mp4"):
        f = ROOT / "renders" / "final" / f"{sid}.{ext}"
        if f.exists():
            return {"type": "movie", "path": str(f)}, "final"
    if shot["tool"] == "manim":
        stem = Path(shot["scene_file"]).stem
        for q in ("1080p30", "480p15"):
            f = ROOT / "renders" / "manim" / "videos" / stem / q / f"{sid}.mp4"
            if f.exists():
                return {"type": "movie", "path": str(f)}, "draft"
    else:
        f = ROOT / "renders" / "blender" / f"{sid}.mp4"
        if f.exists():
            return {"type": "movie", "path": str(f)}, "draft"
    kind, value = shot["fallback"].split(":", 1)
    if kind == "fig":
        return {"type": "image", "path": str(ROOT / "00_input" / "report_figs" / f"{value}.png")}, "fallback"
    return {"type": "image", "path": str(ROOT / "renders" / "cards" / f"{sid}.png"), "card": value}, "fallback"


def make_cards(cards):
    """การ์ดข้อความของช็อตที่ภาพสำรองเป็น card: และป้าย 'ภาพสำรอง' (ซ้อนบนทุกช็อตที่ยังไม่มีภาพจริง)"""
    out = ROOT / "renders" / "cards"
    out.mkdir(parents=True, exist_ok=True)
    (out / "cards.json").write_text(json.dumps(cards, ensure_ascii=False))
    for scene, flags in (("Cards", []), ("FallbackTag", ["-t"])):
        subprocess.run(["uv", "run", "manim", "-s", "-qh", "--disable_caching", *flags,
                        "manim/cards.py", scene], cwd=ROOT, check=True, capture_output=True,
                       env={**__import__("os").environ, "PYTHONPATH": "manim"})


def main():
    shots = yaml.safe_load((ROOT / "context" / "shotlist.yaml").read_text())
    timing_file = ROOT / "context" / "timing.json"
    timing = json.loads(timing_file.read_text()) if timing_file.exists() else {}
    plan, frame, markers, cards, last_seq = [], int(HEAD_SECONDS * FPS) + 1, [], [], None
    for shot in shots:
        if shot["sequence"] != last_seq:
            if last_seq is not None:
                frame += int(GAP_SECONDS * FPS)
            markers.append({"frame": frame, "name": shot["sequence"]})
            last_seq = shot["sequence"]
        t = timing.get(shot["id"], {})
        seconds = t.get("seconds") or max(3.0, shot["sentences"] * SECONDS_PER_SENTENCE)
        media, status = pick_media(shot)
        if "card" in media:
            cards.append({"id": shot["id"], "text": media["card"], "sequence": shot["sequence"]})
        frames = round(seconds * FPS)
        plan.append({"id": shot["id"], "start": frame, "frames": frames, "media": media, "status": status,
                     "audio": t.get("audio")})
        frame += frames
    if cards:
        make_cards(cards)
    total = frame + FPS
    out = {"fps": FPS, "width": 1920, "height": 1080, "frame_end": total, "shots": plan, "markers": markers,
           "fallback_tag": str(ROOT / "renders" / "cards" / "fallback_tag.png")}
    (ROOT / "renders" / "edit_plan.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    counts = {s: sum(p["status"] == s for p in plan) for s in ("final", "draft", "fallback")}
    print(f"edit plan: {len(plan)} ช็อต · {total / FPS / 60:.1f} นาที · {counts}")


if __name__ == "__main__":
    main()
