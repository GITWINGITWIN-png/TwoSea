# CLAUDE.md — production "two-seas"

**deck สไลด์มีแอนิเมชัน** สำหรับนำเสนอโครงงาน DSP **"ทะเลสองฝั่ง ฟังภูมิอากาศคนละแบบ"** แบบ **พูดสด ~15 นาที**
(**กำลังย้าย** ไปเป็น Slidev เป็นตัว deck + คลิป Manim ทีละขั้น + วิดีโอ Blender · `main` ยังเป็น manim-slides v000) · **ส่ง PDF** ให้อาจารย์ (ไม่ต้องเป็น .pptx)
นำเสนอ **2026-10-15** · แผน: `~/.claude/plans/effervescent-stargazing-papert.md` (ทาง deck · 10-10 คืน) ต่อจาก
`~/.claude/plans/anomation-flickering-honey.md` (เนื้อหา · ตาราง · กติกา) · สเปกหน้าตา: `context/design-brief.md`
· สถานะ: `PROGRESS.md` · **ส่งต่องาน: `context/handoff.md`** · สถานะรุ่นคลิปเก็บไว้ที่ git tag `clip-v1`
เป็นงานจริงชิ้นแรกที่ทำตามวิธีของ MyStudio (`~/Projects/MyStudio`, design 07 §2) — Claude ทำหน้าที่ studiod ด้วยมือ

## กฎที่ห้ามละเมิด

- **ความจริงมีที่เดียว:** รายงาน `../reports/final/report.tex` + `../data/processed/` ของโครงงาน (โฟลเดอร์แม่ของ presentation/)
  (อ่านอย่างเดียว — งานนำเสนอห้ามแก้โค้ด ข้อมูล หรือรายงานของงานวิเคราะห์นอกโฟลเดอร์ presentation/)
- **ตัวเลขบนจอ/ในบทมาจาก `data/facts.json` เท่านั้น** (สร้างด้วย `tools/export_facts.py` ใน Python ของโครงงาน DSP)
  ห้ามพิมพ์ตัวเลขเองในไฟล์ฉาก — ใช้ `manim/facts.py`
- ทุกประโยคในโน้ตและทุก `หัวข้อ:` ในบทมี claim ID (`[C12]`) ใน `context/claims.yaml` · ไม่มี claim = ไม่พูด ไม่ขึ้นจอ
- ถ้อยคำ: "สอดคล้องกับ" ไม่ใช่ "พิสูจน์" · coherence ≠ เหตุและผล · อ่าวไทย = "ไม่พบสัญญาณที่ตรวจได้" ·
  WNPMI ไม่ใช่ "ตัวเด่น" · ไม่โยงไปเรื่องโลกร้อน · ระยะสองสถานี = "ราว 470 กม." (รายงานเขียนผิดว่า < 450)
- ภาพทุกช็อตมีป้าย ข้อมูลจริง / แผนภาพ / เปรียบเทียบ · ข้อความไทยใน Blender = ภาพ PNG จาก Pango เท่านั้น
- ไม่ใช้ generative AI สร้างภาพที่แสดงข้อมูล สถานที่ หรือเหตุการณ์

## คำสั่ง

```bash
PYTHONDONTWRITEBYTECODE=1 ../.venv/bin/python tools/export_facts.py  # ตัวเลข -> data/
uv run pytest                                                   # ตัวเลข = รายงาน
uv run python tools/check_claims.py                              # หัวข้อ + โน้ต ↔ claims ↔ facts · เวลาพูด
PYTHONPATH=manim uv run manim-slides render -ql manim/sq03_signal.py SQ03   # render หนึ่งตอน
uv run python tools/contact_sheet.py SQ03                       # เฟรมสุดท้ายทุกคลิกของตอน -> renders/contact/
uv run python tools/build_deck.py v001 [--hq] [--only SQ03]     # ทั้ง deck -> export/*.pptx|pdf|html + cues
./present.sh                                                    # นำเสนอเต็มจอ (Qt ผ่าน XWayland)
~/.steam/steam/steamapps/common/Blender/blender -b --factory-startup --python tools/<script>.py -- <args>
```

## ชื่อและไฟล์

- ช็อต `SQ03_S010` · รุ่นผลลัพธ์ `v###` · 1920×1080 · 30 fps · −16 LUFS
- `renders/`, `export/`, `media/`, `data/*.npz` ไม่อยู่ใน git (สร้างใหม่ได้) · ไฟล์ใหญ่ที่เก็บ = Git LFS
- git: local · `main` = ทางที่นำเสนอได้เสมอ · งานทดลองอยู่บน branch (ตอนนี้ `deck-slidev` — merge `--no-ff` เมื่อผ่านประตู 2)
  · commit ทีละขั้น `area: what changed` · ไม่มี remote · ไม่ push

## แบ่งงานตามโมเดล

session หลัก (Opus) = บท, claims, toolkit (`slides_kit`), ตรวจผล · subagent Sonnet = หน้าแอนิเมชันตอนละตัว / Blender SQ08
(อ่าน `context/scene-rules.md`) · subagent ไม่แก้ toolkit และไม่ commit
· `manim/slides_compat.py` = ตัวแก้ให้ manim-slides 5.7.0 ทำงานกับ Manim 0.22 — import `Slide` จากที่นี่เสมอ
