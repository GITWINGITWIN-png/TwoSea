# บทเรียนสำหรับ MyStudio (จดระหว่างงาน two-seas)

## 2026-10-10 · งานเปลี่ยนชนิดกลางทาง: คลิป → สไลด์พูดสด

- อาจารย์ต้องการนำเสนอสด (syllabus: "พัฒนาทักษะการสื่อสาร") — **ถามรูปแบบการส่งงานก่อนเลือกชนิด production**
  MyStudio ควรมีคำถามนี้ตอน intake: "ใครดู · ดูแบบไหน (เล่นเอง / พูดประกอบ) · ต้องส่งไฟล์อะไร"
- "สไลด์สำหรับพูดสด" เป็นชนิดงานใหม่ (design 07 มีแค่ film/game/video) — ใช้โครงเดิมได้เกือบหมด:
  โฟลเดอร์ · ประตู · pin · claims/facts · ภาพสำรอง ("deck นำเสนอได้ครบเสมอ" แทน "คลิปเล่นได้ครบเสมอ")
- งานเสียง/ตัดต่อหายทั้งก้อน แต่มี **การซ้อมพูด** เข้ามาแทนเป็นงานของผู้ใช้ — ตารางต้องจองเวลาซ้อม

## fit test: manim-slides 5.7.0 กับ Manim 0.22 (ผ่าน · มีเงื่อนไข)

- manim-slides อ่าน/ตั้ง config ของ Manim 7 ตัว — Manim 0.22 ลบ `write_to_movie`, `flush_cache` และ
  บังคับ `max_files_cached` เป็นจำนวนเต็ม → `manim/slides_compat.py` แก้สามจุด (แกน `partial_movie_files` ยังอยู่)
  บทเรียน: **ไล่ดูทุกจุดที่ต่อกันในครั้งเดียว** (grep ทุก `config[...]`) ดีกว่าแก้ทีละ error
- สีพื้นหลังต้องเป็น `ManimColor` ไม่ใช่สตริง (manim-slides เรียก `.to_hex()`)
- ตัวเล่น Qt (PySide6 6.12) พังบน GNOME Wayland (GLib อ่าน xsettings key `antialiasing` ที่ไม่มีแล้ว) →
  ใช้ `QT_QPA_PLATFORM=xcb` (XWayland) ได้
- PPTX: poster = เฟรมแรก **โดยตั้งใจ** — ถ้าใช้เฟรมสุดท้าย ภาพเฉลยจะแวบขึ้นก่อนแอนิเมชันตอนเล่น
  ฉบับอ่าน = PDF (เฟรมสุดท้ายของทุกขั้น)
- HTML `--offline --one-file`: ไม่มี URL ภายนอก วิดีโอฝังเป็น base64 · PPTX เปิดใน LibreOffice ได้
- เฟรมสุดท้ายของวิดีโอ 15 fps: `ffmpeg -sseof -0.05` ได้ไฟล์ว่างเงียบ ๆ — ใช้ `-sseof -0.3`

## 2026-10-10 คืน · fit test: Slidev 53.0.0 เป็นตัว deck + คลิป Manim ทีละขั้น

ทำไม: v000 (manim-slides) ทุกหน้าออกมาเป็น "หัวข้อ + รูปจากรายงาน" — เลย์เอาต์เป็นพิกัดใน Python · เห็นผลหลัง render ·
ลาก/ชี้บนสไลด์ไม่ได้ (research note `MyStudio/docs/research/2026-10-10-slide-animation-tools.md`)

| # | ทดสอบ | ผล |
|---|---|---|
| D1 | ไทยใน dev + PDF | ✅ สระ/วรรณยุกต์ถูก · Sarabun ฝังใน PDF (`pdffonts` emb yes) · "②" ไม่มีใน Sarabun → ดึง NotoSansMongolian มาแทน: วาดเลขในวงกลมด้วย HTML แทนอักขระ |
| D2 | `ManimClip` 3 ขั้นในเว็บที่ build แล้ว | ✅ ขั้นใหม่เล่นจากต้นแล้วค้างเฟรมสุดท้าย · ถอยหลังแสดง PNG ของขั้นนั้น (ดูบทเรียน Range ข้างล่าง) |
| D3 | presenter view ออฟไลน์ | ✅ หน้าปัจจุบัน + คลิกถัดไป (ภาพนิ่ง ไม่เล่นซ้อน) + โน้ตไทย + แถบคลิก · ไม่มี request ออกนอกเครื่อง · จอที่สองจริง: ผู้ใช้เช็ก |
| D4 | view-transition morph | ⏳ Chromium มี `startViewTransition` แต่ headless จับเฟรมกลางไม่ได้ → **ผู้ใช้ดูใน Firefox 157** (สำรอง: GSAP Flip) |
| D5 | `v-drag` เขียนตำแหน่งกลับ | ⏳ ผู้ใช้ลองลาก แล้วดู `git diff deck/slides.md` |
| D6 | PDF ไม่ใส่คลิก | ✅ ทุกหน้าอยู่ในสภาพสมบูรณ์ (v-click โผล่ครบ · คลิปเป็นเฟรมสุดท้ายของขั้นสุดท้าย) · `--with-clicks` = หน้าละคลิก ภาพตรงทุกขั้น |
| D7 | แก้ไฟล์ → เห็นผล | ✅ ~50 ms (เป้า ≤ 2 วินาที) |
| D8 | `<Fact>` + `check_claims` | ✅ เลขพิมพ์เองบนหน้า deck → fail พร้อมเลขบรรทัด · frontmatter / attribute / โน้ตไม่ถูกนับ |

บทเรียน:
- **Range request:** `python -m http.server` ไม่รองรับ HTTP Range → เบราว์เซอร์ seek วิดีโอไม่ได้ (ตกไปที่ 0) —
  อย่าพึ่งการ seek: ถอยหลังใช้ PNG เฟรมสุดท้ายที่ export_clips ทำไว้แล้ว ใช้ได้กับทุก server
- **build ล้ม:** Slidev 53.0.0 + ตัวย่อ CSS ค่าเริ่มต้น (lightningcss) ปฏิเสธกฎหนึ่งใน CSS รวม → `build.cssMinify: false`
  ใน `deck/vite.config.ts` (deck ออฟไลน์ ขนาดไม่สำคัญ) · `cssMinify: 'esbuild'` ใช้ไม่ได้เพราะ Vite รุ่นนี้ไม่มี esbuild
- **สีพื้นของคลิปเพี้ยนเล็กน้อย** (mp4 แปลงเป็น YUV) → กรอบคลิปเห็นเป็นสี่เหลี่ยม: ออกแบบพื้นที่เนื้อหาให้เป็นแผง (panel) อยู่แล้ว
  หรือ render แบบโปร่งใส — ตัดสินตอนทำ theme
- Slidev นับคลิกจาก `v-click` เท่านั้น — หน้าที่มีแต่คลิปต้องตั้ง `clicks:` ใน frontmatter
- `routerMode: hash` → เว็บที่ build แล้วเปิดจาก server ธรรมดาได้โดยไม่ต้องตั้ง fallback ของ route
- โน้ตหลายบรรทัดถูกต่อเป็นย่อหน้าเดียว → generator เขียนโน้ตเป็นรายการ `- ` ทีละประโยค
