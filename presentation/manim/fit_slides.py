"""fit test ของ manim-slides 5.7.0 — ทดสอบก่อนตัดสินใจใช้กับ deck จริง (แผน 2026-10-10)

    PYTHONPATH=manim uv run manim-slides render -ql manim/fit_slides.py FitSlides
    uv run manim-slides present FitSlides

ครอบคลุมทุกอย่างที่ deck จริงต้องใช้:
หัวข้อไทย + ป้าย · เส้นข้อมูลจริงจาก derived() · ตัวเลขจาก facts · หน้า loop · วิดีโอภายนอก (src=) · โน้ตผู้พูด
"""

from manim import DOWN, UP, Create, Dot, FadeIn, FadeOut, MoveAlongPath, Write

from slides_compat import Slide  # manim-slides 5.7.0 + Manim 0.22 (ดูเหตุผลในไฟล์นั้น)

from facts import ROOT, derived, num
from plots import Frame2D, chapter_bar, series_line
from studio_style import ANDAMAN, GULF, INK, MUTED, SIZE_BODY, SIZE_TITLE, course_tag, kind_tag, setup_scene, thai


class FitSlides(Slide):
    skip_reversing = True  # deck จริงไม่ใช้การเล่นถอยหลัง — ไม่ต้องเสียเวลาสร้างวิดีโอกลับด้าน

    def construct(self):
        setup_scene(self)
        # ค้างเฟรมสุดท้ายของทุกขั้นเล็กน้อย: manim-slides เตือนว่าไม่อย่างนั้นแอนิเมชันสุดท้ายอาจดูไม่จบ
        self.wait_time_between_slides = 0.1
        bar = chapter_bar(3)
        self.add_to_canvas(bar=bar)  # canvas = ของที่ค้างข้ามหน้า (แถบตอน)
        self.add(bar)

        # ขั้น 1 — หัวข้อไทย + ป้าย (คำที่เคยมีปัญหาวรรณยุกต์ในภาพทดสอบเดิม)
        self.next_slide(notes="ขั้น 1 · หัวข้อไทย: ปรากฏการณ์ น้ำ ฤดูกาล ผิดปกติ")
        head = thai("ทดสอบหัวข้อ: ปรากฏการณ์ · น้ำ · ฤดูกาล · ผิดปกติ", size=SIZE_TITLE, weight="SEMIBOLD")
        head.to_edge(UP, buff=1.1)
        self.play(FadeIn(head), FadeIn(kind_tag("data")), FadeIn(course_tag("บทที่ 3 · Down-sampling").shift(DOWN * 0.6)))

        # ขั้น 2 — เส้นข้อมูลจริง (ค่าเฉลี่ย 12 เดือนของสองทะเล)
        self.next_slide(notes="ขั้น 2 · เส้นข้อมูลจริงจาก derived(): อันดามัน (น้ำเงิน) กับอ่าวไทย (ส้ม)")
        d = derived()
        t = d["t"]
        frame = Frame2D((t[0], t[-1]), (-250, 250), 11.5, 3.6, center=DOWN * 0.6)
        lines = [series_line(frame, t, d["andaman_mm_12m"], ANDAMAN), series_line(frame, t, d["gulf_mm_12m"], GULF)]
        self.play(Create(frame.border()), *[Create(x) for x in lines], run_time=2)

        # ขั้น 3 — ตัวเลขจาก facts (ห้ามพิมพ์เอง)
        self.next_slide(notes="ขั้น 3 · ตัวเลขจาก facts: ฤดูกาลกินความแปรปรวน")
        share = thai(f"ฤดูกาลกิน: อ่าวไทย {num('season.share_gulf')}% · อันดามัน {num('season.share_andaman')}%",
                     size=SIZE_BODY, color=INK).to_edge(DOWN, buff=0.5)
        self.play(Write(share), run_time=1.2)

        # ขั้น 4 — หน้า loop (เหมือน Morlet เลื่อน / คลื่นเคลวินวน)
        self.next_slide(loop=True, notes="ขั้น 4 · loop: จุดวิ่งตามเส้นอันดามันวนไปเรื่อย ๆ จนกว่าจะคลิก")
        dot = Dot(color=INK, radius=0.09)
        path = lines[0][0]
        self.play(MoveAlongPath(dot, path), run_time=3)

        # ขั้น 5 — วิดีโอภายนอก (แทนวิดีโอ Blender คลื่นเคลวิน)
        self.next_slide(src=ROOT / "renders" / "fit" / "src_test.mp4", notes="ขั้น 5 · วิดีโอภายนอกผ่าน src=")

        # ขั้น 6 — จบ: ล้างจอ เหลือแถบตอน
        self.next_slide(notes="ขั้น 6 · ล้างจอ (แถบตอนบน canvas ต้องค้างอยู่)")
        bye = thai("จบการทดสอบ", size=SIZE_TITLE, color=MUTED)
        self.play(FadeOut(*self.mobjects_without_canvas), FadeIn(bye))
