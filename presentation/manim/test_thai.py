"""Stage 0 — ภาพทดสอบ: ไทยผ่าน Pango, สูตรผ่าน LaTeX, ป้าย, สีสองทะเล

รัน:  uv run manim -s -qh manim/test_thai.py ThaiTest
ดูว่า: วรรณยุกต์ไม่ชนสระ (น้ำ ที่ ปรากฏการณ์) · ตัวเล็กสุดยังอ่านออก · สูตรขึ้นครบ
"""

from manim import DOWN, LEFT, UP, MathTex, Scene, VGroup

from studio_style import (
    ANDAMAN, GULF, INK, MUTED, SIZE_BODY, SIZE_SMALL, SIZE_TITLE,
    course_tag, evidence_tag, kind_tag, setup_scene, thai,
)


class ThaiTest(Scene):
    def construct(self):
        setup_scene(self)
        title = thai("ทะเลสองฝั่ง ฟังภูมิอากาศคนละแบบ", size=SIZE_TITLE, weight="BOLD")
        body = thai("ปรากฏการณ์ · น้ำทะเล · ฤดูกาล · ผิดปกติ · ที่ปรึกษา · กรมทรัพยากรทางทะเลและชายฝั่ง", size=SIZE_BODY)
        mixed = thai("wavelet coherence (WTC) · Niño3.4 · K1+P1 พับไปที่คาบ 365.2 วัน", size=SIZE_BODY, color=MUTED)
        small = thai("ตัวเล็กสุดที่ยอมให้ขึ้นจอ: น้ำภูเก็ตต่ำกว่าปกติราว 29 ซม. นาน 7 เดือน (ปี 1997–98)", size=SIZE_SMALL)
        seas = VGroup(
            thai("■ อันดามัน · เกาะตะเภาน้อย", size=SIZE_BODY, color=ANDAMAN),
            thai("■ อ่าวไทย · เกาะหลัก", size=SIZE_BODY, color=GULF),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        formula = MathTex(
            r"R^2(s,\tau)=\frac{\bigl|S\!\left(s^{-1}W_{XY}\right)\bigr|^2}"
            r"{S\!\left(s^{-1}|W_X|^2\right)\,S\!\left(s^{-1}|W_Y|^2\right)}",
            color=INK, font_size=44,
        )
        tags = VGroup(evidence_tag("strong"), evidence_tag("single"), evidence_tag("inferred")).arrange(buff=0.25)
        col = VGroup(title, body, mixed, small, seas, formula, tags).arrange(DOWN, buff=0.38)
        col.scale_to_fit_width(min(col.width, 13.2))
        self.add(col, kind_tag("data"), course_tag("บทที่ 3 · Down-sampling"))
