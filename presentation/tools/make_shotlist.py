"""สร้าง context/shotlist.yaml จาก script.md — รายการหน้า เครื่องมือ ป้าย หัวข้อ ขั้น ภาพสำรอง และไฟล์ฉาก

    uv run python tools/make_shotlist.py

ภาพสำรอง (fallback) = รูปที่ตรงกันจากรายงาน (00_input/report_figs/) หรือการ์ดข้อความ
deck ใช้ภาพสำรองจนกว่าหน้าจริงจะเสร็จ — จึงนำเสนอได้ครบเรื่องเสมอ
(ชื่อไฟล์ยังเป็น "shot" ตามรุ่นคลิป · หนึ่งรายการ = หนึ่งหน้าสไลด์)
"""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "context" / "script.md"
OUT = ROOT / "context" / "shotlist.yaml"

SLUGS = {
    "SQ01": "opening", "SQ02": "data", "SQ03": "signal", "SQ04": "correlation", "SQ05": "wavelet",
    "SQ06": "coherence", "SQ07": "noise", "SQ08": "mechanism", "SQ09": "robustness", "SQ10": "summary",
    "SQ11": "appendix",
}

# ช็อต -> ภาพสำรอง: "fig:<ชื่อไฟล์ใน 00_input/report_figs>" หรือ "card:<ข้อความ>"
FALLBACK = {
    "SQ01_S030": "card:ทะเลสองฝั่ง ฟังภูมิอากาศคนละแบบ", "SQ01_S010": "fig:map02_two_seas",
    "SQ01_S020": "fig:fig11_events",
    "SQ02_S010": "fig:map01_indices", "SQ02_S040": "card:Y[n] กับ X[n]: คาบไหน · เมื่อไร · เกิน noise หรือไม่",
    "SQ03_S005": "card:กรอง + ลดอัตรา → เตรียมสัญญาณ → CWT → WTC / MWC → เทียบ noise → ตรวจทิศ",
    "SQ03_S010": "fig:w2-hourly-sample", "SQ03_S020": "fig:w2-aliasing-before-after",
    "SQ03_S040": "fig:fig02_filter",
    "SQ03_S060": "fig:w1-detrend-deseason",
    "SQ04_S020": "fig:fig11_events",
    "SQ05_S020": "card:CWT · Morlet ω0 = 6 · 12 สเกลต่อ octave",
    "SQ05_S030": "fig:w1-power-spectra",
    "SQ06_S020": "card:WTC = coherence ทุกจุดเวลา × คาบ · ลูกศร → ไปด้วยกัน · ← สวนทาง",
    "SQ06_S030": "fig:fig03_wtc_maps", "SQ06_S040": "card:MWC = coherence ของหลายดัชนีพร้อมกัน · ดัชนีเดียว → ลดรูปเป็น WTC",
    "SQ07_S010": "fig:w4-q1-pasc-null", "SQ07_S020": "fig:fig04_q1_pasc",
    "SQ07_S040": "fig:fig05_threshold_vs_q",
    "SQ08_S020": "fig:map03_mechanism", "SQ08_S030": "fig:map03_mechanism", "SQ08_S050": "fig:fig12_phase",
    "SQ08_S060": "card:เอลนีโญ / IOD → ลมศูนย์สูตร → คลื่นเคลวิน → อันดามัน",
    # SQ09_S030 ตัดแล้ว (10-14 · บท v7) · SQ03_S030 ตัดแล้ว (10-15 · บท v9)
    "SQ10_S010": "fig:map02_two_seas", "SQ10_S020": "card:ขอบคุณครับ · ถาม-ตอบ",
    # ภาคผนวก: รูปจากรายงานคือตัวหน้าเอง (ไม่มีแอนิเมชัน)
    "SQ11_S010": "fig:w2-monthly-vs-psmsl", "SQ11_S020": "fig:w2-filter-response",
    "SQ11_S030": "fig:w1-detrend-deseason", "SQ11_S040": "fig:w4-q1-pasc-null",
    "SQ11_S050": "fig:fig05_threshold_vs_q", "SQ11_S060": "fig:fig07_q3_best_per_q",
    "SQ11_S070": "fig:fig09_sensitivity", "SQ11_S080": "fig:fig10_scorecard",
    "SQ11_S090": "fig:map03_mechanism", "SQ11_S100": "fig:map01_indices",
    # หน้าอธิบายดัชนี (ทำมือ deck/pages/) · ภาพสำรอง = แผนที่ดัชนี
    "SQ11_S110": "fig:map01_indices", "SQ11_S120": "fig:map01_indices",
}

HEAD = re.compile(r"^### (SQ\d+)_(S\d+) · (.+)$")
TAG = re.compile(r"\[(C\d+|F)\]")


def main():
    shots, cur = [], None
    for line in SCRIPT.read_text().splitlines():
        if m := HEAD.match(line):
            sq, s, rest = m.groups()
            parts = [p.strip() for p in rest.split("·")]
            # วิดีโอ Blender จริง = "3D Blender" · "Blender ภาพนิ่ง + Manim" คือฉาก Manim บนภาพนิ่งที่ render ไว้
            tool = "blender" if parts[0].startswith("3D Blender") else "manim"
            # "วิธี" = ภาพอธิบายวิธี (filter bank, Welch, สูตร) ไม่ใช่ข้อมูลจริง → ป้าย "แผนภาพ" ตามกฎของฉาก
            kind = next((k for k, w in (("data", "ข้อมูลจริง"), ("schematic", "แผนภาพ"), ("schematic", "วิธี"),
                                        ("analogy", "เปรียบเทียบ"))
                         if any(w in p for p in parts)), "card")
            # ป้ายบท = "บทที่ N" + ชื่อหัวข้อถัดไปถ้ามี (เช่น "บทที่ 3 · Down-sampling")
            ci = next((i for i, p in enumerate(parts) if p.startswith("บทที่")), None)
            course = None if ci is None else " · ".join(parts[ci:ci + 2])
            cur = {"id": f"{sq}_{s}", "sequence": sq, "tool": tool, "kind": kind, "course": course,
                   "scene_file": f"manim/{sq.lower()}_{SLUGS[sq]}.py" if tool == "manim" else f"blend/shots/{sq}/",
                   "fallback": FALLBACK[f"{sq}_{s}"], "headline": "", "steps": 0, "sentences": 0, "visual": ""}
            shots.append(cur)
        elif cur and line.startswith("หัวข้อ:"):
            cur["headline"] = TAG.sub("", line[7:]).strip()
        elif cur and line.startswith("ภาพ:"):
            cur["visual"] = line[4:].strip()
        elif cur and re.match(r"^\d+\. ", line):
            cur["steps"] += 1
        elif cur and line.startswith("- "):
            cur["sentences"] += 1
    ids = {s["id"] for s in shots}
    if missing := set(FALLBACK) - ids:
        raise SystemExit(f"FALLBACK มีหน้าที่ไม่อยู่ในบท: {sorted(missing)}")
    if no_head := [s["id"] for s in shots if not s["headline"]]:
        raise SystemExit(f"หน้าที่ไม่มี 'หัวข้อ:': {no_head}")
    OUT.write_text("# สร้างโดย tools/make_shotlist.py จาก script.md — อย่าแก้มือ\n"
                   + yaml.safe_dump(shots, allow_unicode=True, sort_keys=False, width=120))
    print(f"shotlist.yaml: {len(shots)} หน้า · {sum(s['steps'] for s in shots)} ขั้น · "
          f"วิดีโอ Blender {sum(s['tool'] == 'blender' for s in shots)} หน้า")


if __name__ == "__main__":
    main()
