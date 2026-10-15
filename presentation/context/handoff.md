# Handoff — two-seas deck (เขียน 2026-10-14 ราว 02:30 · ก่อน compact)

> อ่านไฟล์นี้ก่อนทำงานต่อ · คู่กับ `PROGRESS.md` (สถานะย่อ) · `CLAUDE.md` (กฎโปรเจกต์)
> **ล็อก พ 2026-10-14 15:00 · นำเสนอ พฤ 2026-10-15** · branch `deck-slidev` (ยังไม่ merge เข้า `main` — `main` = manim-slides พื้นมืด ตาข่าย)

## สถานะตอนนี้

- **ทาง deck = Slidev** (ผู้ใช้เลือก 10-13 ดึก) · **สไตล์ = theme D** (สื่ออธิบายวิทยาศาสตร์ พื้นสว่าง) · หัวข้อ Kanit · เนื้อ Anuphan
  สเปก: `context/design-brief.md` ส่วน "การตัดสินใจ" · กระดานเลือกสไตล์: https://claude.ai/artifact/MM5rtrsUoDuBGqihmwoQFa
- **บท v6** (10-14) เพิ่มเหตุผลทางฟิสิกส์ใน SQ08 (4 หน้า) · เวลา **12.1 นาที** · ป้ายหลักฐานไม่ขึ้นจอ (อยู่ในโน้ต)
- บท v5 `context/script.md` (10-14) — ลดวิธีประมวลผล เน้นผล แบบ happy path · ตัด 6 หน้า (รายชื่อที่หัวไฟล์บท) · เนื้อหาที่ตัดอยู่ใน `ถ้าถูกถาม:`
  · เวลา **10.1 นาที** (เดิม 15.1) · ก่อนหน้า v4 = ปรับตาม 39 comment ของผู้ใช้ (Tandem Comments บล็อก JSON ท้ายไฟล์)
- **deck 38 หน้า** (หลัก 28 + ภาคผนวก 10) · PDF ล่าสุดดูใน `export/` (ไม่อยู่ใน git) · หน้าทำมือที่ตัดออก: `deck/pages/_cut/`
- `uv run python tools/check_claims.py` ✅ · `uv run pytest` 48 ผ่าน · commit ล่าสุด `a498f41`

## สายงาน (วิธีทำงานของ deck)

```
context/script.md ──tools/gen_deck.py──▶ deck/slides.md  (อย่าแก้มือ — สร้างใหม่ทุกครั้ง)
   หัวข้อ/ป้าย/โน้ต/เลขหน้า อัตโนมัติ · ตัวเลขในหัวข้อ → <Fact/> หรือ <Lit/> ตาม claim ของบรรทัด
   เนื้อหน้า = deck/pages/<รหัสหน้า>.md ถ้ามี (ทำมือ) · ไม่มี = รูปรายงานในการ์ด (fallback จาก context/shotlist.yaml)
data/derived.npz ──gen_deck──▶ deck/data/series.json (กราฟ) · data/facts.json ──▶ deck/data/facts.json
manim/clip_*.py ──tools/export_clips.py──▶ deck/public/clips/<หน้า>/<ขั้น>.mp4|png ──▶ <ManimClip>
```

คำสั่ง:
```bash
uv run python tools/gen_deck.py                                  # สร้าง deck/slides.md
uv run python tools/deck_shots.py SQ04_S020 SQ06_S030@1          # ภาพตรวจ renders/shots/main/<หน้า>.png (คลิกสุดท้าย · @N = คลิก N) + error ต่อหน้า
uv run python tools/check_claims.py                              # ต้อง ✅
PYTHONPATH=manim uv run python tools/export_clips.py manim/clip_sq03_alias.py AliasClip --res 1680,600
cd deck && npx slidev                                            # dev · กด P = presenter view (โน้ตไทย)
uv run python tools/export_pdf.py s011 [--range 1-26]               # PDF ส่งอาจารย์ (ล่าสุด s010) (ห้ามใช้ slidev export — ดูกับดัก)
PYTHONDONTWRITEBYTECODE=1 ../.venv/bin/python tools/export_facts.py   # ถ้าต้องเพิ่มข้อมูลลง derived.npz
```

ของกลาง (toolkit — session หลักแก้ · subagent ห้ามแก้):
- `deck/style.css` (ตัวแปรสี/การ์ด/ป้าย) · `deck/layouts/{page,cover,end}.vue` · `deck/components/`:
  `SeriesChart` (อนุกรมจริง · x-key · hlines · points · bare · at=คลิก) · `CoverWave` · `FigCard` · `Fact` · `Lit` · `ManimClip`
- `manim/studio_style.py` (theme D พื้นขาว · SIZE_BODY 22 · SIZE_SMALL 18) · คลิปตั้ง `config.frame_height = 8` + กว้างตามสัดส่วน
- กติกาสำหรับ subagent: `context/deck-page-rules.md` · ตัวอย่าง: `deck/pages/SQ04_S020.md`, `manim/clip_sq03_alias.py`

## หน้าที่ทำมือแล้ว (17)

SQ01_S020 · SQ02_S010 · SQ02_S040 · SQ03_S005 · SQ03_S020 (คลิป) · SQ03_S030 (ตัดแล้ว v9) · SQ03_S040 · SQ04_S020 · SQ05_S020 (คลิป Morlet) ·
SQ07_S020 · SQ07_S030 · SQ07_S040 · SQ07_S050 · SQ08_S030 · SQ08_S050 · SQ09_S010 · SQ09_S030 · SQ10_S010 · + ปก (CoverWave ผ่าน gen_deck)

## งานที่เหลือ — เรียงตามความสำคัญ

1. **ผู้ใช้ซ้อม 1 รอบกับ presenter view แล้วบอกว่าติดอะไร** (ยังไม่ได้ซ้อมเลย — ตาราง "ซ้อม" ใน PROGRESS ว่าง)
2. **SQ06_S030 (WTC อันดามัน vs อ่าวไทย)** — หน้าผลหลัก ยังเป็นรูปรายงาน · ผู้ใช้เคยติ `v001_wtc.png` (ตัวใหญ่ · มืด)
   ทางทำ: คลิป Manim หรือ `<img>` ระนาบจาก `data/processed` ของโครงงาน DSP (อ่านอย่างเดียว) วาดใหม่ด้วย matplotlib สไตล์ D → PNG ใน deck/public/figs
   ต้องมีเส้นขาว = เกินเกณฑ์ 95% · เส้นประ = COI · ไม่มีป้าย pycwt (ผู้ใช้สั่งตัด)
3. ~~หน้าที่ยังเป็นภาพสำรอง~~ **ครบแล้ว (10-14 เช้า)** — หน้าหลักทุกหน้าเป็นสไตล์ D: รูปข้อมูลจริงจาก `tools/make_method_figs.py` ·
   `tools/make_wtc_fig.py` · แผนที่ชายฝั่งจริง + ความลึกทะเลจาก `tools/make_basemap.py` (รันด้วย Python ของ DSP · ผลอยู่ `deck/public/plots/` ไม่อยู่ใน git)
4. ภาคผนวก SQ11 — **ผู้ใช้สั่งพักไว้** อย่าทำจนกว่าจะสั่ง
5. merge `deck-slidev` → `main` แบบ `--no-ff` เมื่อผ่านประตู 2 (ผู้ใช้คลิกผ่าน deck แล้วตกลง) · ก่อนล็อก: `git tag deck-final` · สำเนา PDF 3 ที่

## รอผู้ใช้ตัดสิน

- **บท v5 ตัดมากไปไหม** — เวลา 10.1 นาที เหลือที่ว่างราว 3–4 นาที · ถ้าจะเติมคืน: สัดส่วนฤดูกาล 81/30% (SQ03_S060) ·
  หน้า SQ07_S030 (กับดัก MWC · ใช้คำ "ไต่ขึ้นแบบเดียวกัน") · หน้า SQ09_S020 (สองคลัง)
- **C74** (ความหมายชื่อ K1/M2 จันทร์/อาทิตย์) และ **C75** (เหตุผลเลือก Morlet) **ไม่อยู่ในรายงานโดยตรง** — ติด ⚠ ใน claims.yaml · C75 ย้ายไป `ถ้าถูกถาม:` ของ SQ05_S020 แล้ว (ไม่พูดเอง)
- เครดิตหน้าจบ "ทำร่วมกับ Claude (Anthropic)" — ยังไม่ได้ตัดสิน (ตอนนี้ไม่มีในหน้า)
- Tandem thread ที่ยังเปิด: 2e04 (เรนเดอร์ 3D ใหม่) · c0fb (คลื่นข้อมูลจริง — ทำแล้วบนปก/SQ02 → ปิดได้) · 46e8 (สไตล์ — เลือก D แล้ว → ปิดได้ · ภาคผนวกยังพัก)

## กับดักที่เจอแล้ว (อย่าพลาดซ้ำ)

- **ทุกกราฟต้องมีชื่อแกน x และ y** (ผู้ใช้ 10-15) — `SeriesChart` ใช้ `x-label` / `y-label` / `y-label-right` ·
  matplotlib ใช้ `xtitle()` / `ytitle()` ใน make_method_figs (ชื่อแกน y แนวนอนเหนือแกน ตัวไทยหมุนแนวตั้งอ่านไม่ออก) ·
  รูปที่สูงเต็มการ์ดพอดีใช้ `xtitle_end()` (ปลายขวาของแถวตัวเลข) · หลังสร้างรูปเช็กว่าแถวขอบล่าง/ขวาไม่มีหมึก (ป้ายตกขอบ)
- **ข้อความบนจอห้ามมี "·"** (ผู้ใช้ 10-14) — ใช้ช่องว่าง จุลภาค "และ" หรือขึ้นบรรทัด · **กล่องดำ (bubble) ห้ามซ้ำหัวข้อหรือเนื้อหาในหน้าเดียวกัน**
- **"แนวโน้ม" ต้องบอกว่าของอะไร** → "แนวโน้มระยะยาวของระดับน้ำ" · หน่วยในหน้าเดียวกันต้องเหมือนกัน (หน้า SQ08_S030 = มม.)
- **แอนิเมชัน CSS ต้องจบก่อนพิมพ์/ถ่าย** — `export_pdf.cjs` / `deck_shot.cjs` เรียก `document.getAnimations().finish()` แล้ว

- **ห้ามใช้ `npx slidev export` ทำ PDF — ใช้ `tools/export_pdf.py`** (Slidev 53.0.0 พังทั้งสองโหมด):
  แบบรวดเดียว (ค่าเริ่มต้น) ย่อสไลด์เหลือ ~79% ชิดมุมซ้ายบน + ขอบดำ + หน้าท้ายภาคผนวกหาย (s005–s007 · หาสาเหตุในหน้าไม่เจอ ตัด CoverWave ก็ยังย่อ) ·
  `--per-slide` ไม่มีขอบดำแต่เปิดทุกหน้าที่คลิก 0 → ของที่โผล่ด้วย v-click หาย (s008)
  · `export_pdf.cjs` อ่าน `window.__slidev__.nav.clicksTotal` (มีเฉพาะ dev server) แล้วพิมพ์ที่คลิกสุดท้าย · พิมพ์บรรทัด ⚠ ถ้าหน้าไหนไปไม่ถึง

- **ห้ามเขียนแท็ก `<script setup>` ในคอมเมนต์ HTML ของหน้า** — Slidev ดึงไปเป็นบล็อกจริง → "Element is missing end tag"
- รูปที่สร้างจากสคริปต์อยู่ `deck/public/plots/` (ไม่อยู่ใน git): `tools/make_wtc_fig.py` (WTC) · `tools/make_basemap.py` (แผนที่ชายฝั่งจริง)
  รันด้วย Python ของโครงงาน DSP · หน้าแผนที่วางลูกศรด้วยพิกัด lon/lat ผ่าน px() ใน script ของหน้า

- **ป้ายหลักฐาน หนักแน่น/งานเดียว/อนุมาน ห้ามขึ้นจอ** (ผู้ใช้ 10-14) — gen_deck ใส่ในโน้ตให้เอง

- **Slidev headmatter ต้องเป็นบรรทัดแรก** — มี comment ก่อน `---` แล้วทั้ง deck ว่าง
- **คีย์ frontmatter ที่ Slidev สงวน:** `author`, `presenter` (ใช้ `byline` แทน) · `no` → YAML เป็น boolean (ใช้ `page`)
- **layout อ่าน frontmatter ผ่าน `defineProps`** — `useSlideContext().$frontmatter` ใน Slidev 53.0.0 = undefined
- **ชื่อ class สั้นใน `<style scoped>` ชนกับ UnoCSS** (`grid`, `zero`, `band`) — ใช้ prefix (SeriesChart ใช้ `sc-`) · CSS ทับ attribute stroke
- **บรรทัดว่างกลาง HTML ในหน้า md** → Markdown ตัดบล็อก → "Element is missing end tag" (gen_deck ตัดให้แล้ว)
- `<Fact :index>` รองรับติดลบแล้ว · gen_deck แปลงเป็นบวก
- lint: ตัด `<style>`/`<script>` ก่อนตรวจ · แท็กที่ attribute มี `>` (เช่น `$clicks >= 1`) อ่านถูกแล้ว
- **Manim clip:** `-r 1680,600` คงความกว้างเฟรม 14.2 → ภาพโดนตัด — ต้องตั้ง `config.frame_height = 8; frame_width = 8 * px_w / px_h`
- thai("...") ห้ามมีเลขพิมพ์เอง (ใช้ f-string + num()) · ชื่อ K1/AR(1)/R²/ω0 ไม่นับ
- รายงานเขียนระยะสองสถานี "< 450 กม." ผิด — ใช้ "ราว 470 กม." (C02)
- subagent ทำงานขนานได้ด้วย `deck_shots.py --name X --port 87xx` คนละค่า · โควตาใช้งานหมดได้กลางทาง (รีเซ็ต 02:00 ตามเวลาไทย)

## กฎที่ห้ามลืม (ย่อจาก CLAUDE.md)

ตัวเลขบนจอ/ในบท มาจาก `data/facts.json` เท่านั้น · ทุกประโยคพูด/หัวข้อ/โน้ต `ถ้าถูกถาม:` มี claim · "สอดคล้องกับ" ไม่ใช่ "พิสูจน์" ·
อ่าวไทย = "ไม่พบสัญญาณที่ตรวจได้" · WNPMI ไม่ใช่ตัวเด่น · ส้ม = อ่าวไทยเท่านั้น · ทุกหน้ามีป้าย ข้อมูลจริง/แผนภาพ/เปรียบเทียบ ·
ห้ามเขียนลงโครงงาน DSP · commit ทีละขั้น `area: what changed` · ไม่ push
