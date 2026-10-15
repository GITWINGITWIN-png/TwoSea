"""คลิป SQ03_S020 + SQ03_S030 (clip mode · theme D): Nyquist ของการลดอัตรา แล้ว aliasing พับน้ำขึ้นน้ำลงลงมาเป็นฤดูกาล

render: PYTHONPATH=manim uv run python tools/export_clips.py manim/clip_sq03_alias.py AliasClip --res 1680,600

clip mode = วาดเฉพาะพื้นที่ในการ์ด — หัวข้อ ป้าย และตัวเลขที่เป็นข้อความอธิบายอยู่ใน HTML ของหน้า (deck/pages/SQ03_S0x0.md)
ขั้น (section "<หน้า>__<ขั้น>"):
  SQ03_S020__1  แกนความถี่ + น้ำขึ้นน้ำลงสองกลุ่มพร้อมชื่อกลุ่ม
  SQ03_S020__2  เส้น Nyquist ที่ fs/2 ตกลงมา · พื้นที่ "ใช้ได้" ทางซ้าย · ทุกเส้นน้ำขึ้นน้ำลงอยู่ขวา → แดง
  SQ03_S030__1  แกนพับ: ทุกเส้นย้ายไปที่ความถี่ alias |f − round(f)| · ซูมช่วงความถี่ต่ำเป็นแกนคาบ (วัน)
                K1 + P1 ทับเส้นฤดูกาลที่ 365.2 วัน · K2 ทับครึ่งปีที่ 182.6 วัน
"""

from manim import (
    DOWN, LEFT, RIGHT, UP, Create, DashedLine, FadeIn, FadeOut, GrowFromEdge, LaggedStart, Line, Rectangle,
    Scene, Text, VGroup, config,
)

from facts import F, num
from studio_style import ALERT, ANDAMAN, BG, EVENT, INK, MUTED, SIZE_BODY, SIZE_SMALL, FONT, thai

config.background_color = BG
# เฟรมสูง 8 หน่วย กว้างตามสัดส่วนพิกเซลของคลิป (1680×600 → 22.4) — ค่าเริ่มต้นของ Manim คงความกว้าง 14.2 แล้วตัดภาพ
config.frame_height = 8.0
config.frame_width = 8.0 * config.pixel_width / config.pixel_height

# ความถี่องค์ประกอบน้ำขึ้นน้ำลง (รอบต่อวัน) — ค่าคงที่ทางดาราศาสตร์ ใช้วางตำแหน่งเส้นเท่านั้น ไม่ขึ้นจอเป็นตัวเลข
# (ค่าเดียวกับที่ export_facts ใช้คำนวณ alias.K1_days ฯลฯ)
TIDES = {"O1": 0.9295, "P1": 0.9973, "K1": 1.0027, "M2": 1.9323, "S2": 2.0, "K2": 2.0055}
HEIGHT = {"O1": 1.9, "P1": 1.2, "K1": 2.7, "M2": 3.0, "S2": 1.7, "K2": 0.8}  # ความสูงเชิงเปรียบเทียบ (แผนภาพ)
FS = 1.0          # สุ่มวันละครั้ง
F_MAX = 2.5       # แกนความถี่ 0 → 2.5 รอบต่อวัน
AXIS_LEN = 19.0
BASE_Y = -2.6


def axis_label(text):
    return Text(text, font=FONT, font_size=SIZE_SMALL, color=MUTED)


class AliasClip(Scene):
    def construct(self):
        x0 = -AXIS_LEN / 2
        fx = lambda f: x0 + f / F_MAX * AXIS_LEN  # noqa: E731 — ความถี่ (รอบ/วัน) → ตำแหน่ง x
        axis = Line([x0, BASE_Y, 0], [x0 + AXIS_LEN, BASE_Y, 0], color=MUTED, stroke_width=3)
        ticks = VGroup(*[
            VGroup(Line([fx(v), BASE_Y, 0], [fx(v), BASE_Y - 0.15, 0], color=MUTED, stroke_width=3),
                   axis_label(f"{v:g}").move_to([fx(v), BASE_Y - 0.5, 0]))
            for v in (0, 0.5, 1, 1.5, 2, 2.5)
        ])
        unit = thai("รอบต่อวัน", size=SIZE_SMALL, color=MUTED).next_to(axis, RIGHT, buff=0.25).shift(DOWN * 0.45)
        lines = {k: Line([fx(f), BASE_Y, 0], [fx(f), BASE_Y + HEIGHT[k], 0], stroke_width=9, color=INK)
                 for k, f in TIDES.items()}
        diurnal = thai("วันละรอบ · K1 O1 P1", size=SIZE_BODY, color=INK).move_to([fx(0.97), BASE_Y + 3.4, 0])
        semi = thai("วันละสองรอบ · M2 S2 K2", size=SIZE_BODY, color=INK).move_to([fx(1.97), BASE_Y + 3.7, 0])

        # --- SQ03_S020 ขั้น 1 -------------------------------------------------------------------------
        self.next_section("SQ03_S020__1")
        self.play(Create(axis), FadeIn(ticks), FadeIn(unit), run_time=0.7)
        self.play(LaggedStart(*[GrowFromEdge(m, DOWN) for m in lines.values()], lag_ratio=0.12), run_time=1.3)
        self.play(FadeIn(diurnal, shift=UP * 0.2), FadeIn(semi, shift=UP * 0.2), run_time=0.6)

        # --- SQ03_S020 ขั้น 2: Nyquist = fs/2 ---------------------------------------------------------
        self.next_section("SQ03_S020__2")
        ok_zone = Rectangle(width=fx(FS / 2) - x0, height=4.6, fill_color=ANDAMAN, fill_opacity=0.10, stroke_width=0)
        ok_zone.move_to([(x0 + fx(FS / 2)) / 2, BASE_Y + 2.3, 0])
        ok_text = thai("ใช้ได้", size=SIZE_BODY, color=ANDAMAN).move_to([(x0 + fx(FS / 2)) / 2, BASE_Y + 4.2, 0])
        nyq = DashedLine([fx(FS / 2), BASE_Y + 4.6, 0], [fx(FS / 2), BASE_Y, 0], color=INK, stroke_width=4,
                         dash_length=0.18)
        nyq_text = thai("Nyquist", size=SIZE_BODY, color=INK).next_to(nyq, UP, buff=0.12)
        self.play(FadeIn(ok_zone), Create(nyq), FadeIn(nyq_text), run_time=0.9)
        self.play(*[m.animate.set_color(ALERT) for m in lines.values()], FadeIn(ok_text), run_time=0.7)
        self.wait(0.3)

        # --- SQ03_S030 ขั้น 1: พับ แล้วซูมเป็นแกนคาบ ---------------------------------------------------
        self.next_section("SQ03_S030__1")
        # พับรอบ fs/2 ซ้ำ ๆ = ความถี่ที่เห็นหลังสุ่มคือ |f − round(f / fs) · fs|
        alias = {k: abs(f - round(f / FS) * FS) for k, f in TIDES.items()}
        self.play(FadeOut(diurnal), FadeOut(semi), FadeOut(ok_text), run_time=0.4)
        self.play(*[lines[k].animate.move_to([fx(alias[k]), BASE_Y + HEIGHT[k] / 2, 0]) for k in TIDES],
                  run_time=1.6)
        self.wait(0.2)

        # ซูม: ช่วงความถี่ต่ำมากแสดงเป็นคาบ (วัน) — ฤดูกาล 365.2 และครึ่งปี 182.6 วัน
        old = VGroup(axis, ticks, unit, ok_zone, nyq, nyq_text, *lines.values())
        self.play(FadeOut(old), run_time=0.5)
        p_axis = Line([x0, BASE_Y, 0], [x0 + AXIS_LEN, BASE_Y, 0], color=MUTED, stroke_width=3)
        k1_days, k2_days = F("alias.K1_days"), F("alias.K2_days")
        px = lambda d: x0 + 1.0 + (d / 400) * (AXIS_LEN - 2.0)  # noqa: E731 — คาบ (วัน) 0 → 400
        season = Rectangle(width=0.55, height=4.2, fill_color=EVENT, fill_opacity=0.9, stroke_width=0)
        season.move_to([px(k1_days), BASE_Y + 2.1, 0])
        half = season.copy().move_to([px(k2_days), BASE_Y + 2.1, 0])
        s_text = thai("ฤดูกาล (ปีละรอบ)", size=SIZE_BODY, color=INK).next_to(season, UP, buff=0.15)
        h_text = thai("ครึ่งปี", size=SIZE_BODY, color=INK).next_to(half, UP, buff=0.15)
        unit2 = thai("คาบ (วัน)", size=SIZE_SMALL, color=MUTED).next_to(p_axis, RIGHT, buff=0.25).shift(DOWN * 0.45)
        k1 = Line([px(k1_days) - 0.08, BASE_Y, 0], [px(k1_days) - 0.08, BASE_Y + HEIGHT["K1"], 0], stroke_width=9, color=ALERT)
        p1 = Line([px(k1_days) + 0.08, BASE_Y, 0], [px(k1_days) + 0.08, BASE_Y + HEIGHT["P1"], 0], stroke_width=9, color=ALERT)
        k2 = Line([px(k2_days), BASE_Y, 0], [px(k2_days), BASE_Y + HEIGHT["K2"], 0], stroke_width=9, color=ALERT)
        k1_text = thai(f"K1 + P1 → {num('alias.K1_days', 1)} วัน", size=SIZE_BODY, color=ALERT)
        k1_text.next_to(season, LEFT, buff=0.3).shift(UP * 0.6)
        k2_text = thai(f"K2 → {num('alias.K2_days', 1)} วัน", size=SIZE_BODY, color=ALERT)
        k2_text.next_to(half, LEFT, buff=0.3).shift(UP * 0.2)
        self.play(Create(p_axis), FadeIn(unit2), FadeIn(season), FadeIn(half), FadeIn(s_text), FadeIn(h_text),
                  run_time=0.8)
        self.play(GrowFromEdge(k1, DOWN), GrowFromEdge(p1, DOWN), GrowFromEdge(k2, DOWN), run_time=0.8)
        self.play(FadeIn(k1_text, shift=LEFT * 0.2), FadeIn(k2_text, shift=LEFT * 0.2), run_time=0.6)
        self.wait(0.4)
