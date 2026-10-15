"""fit test ของ Slidev (D2): คลิป 3 ขั้นของหน้า SQ03_S030 แบบย่อ — ทดสอบตัวเล่น ไม่ใช่ฉากจริง

clip mode: วาดเฉพาะพื้นที่เนื้อหา (ไม่มีหัวข้อ/ป้าย — HTML ทำ) · หนึ่งขั้น = หนึ่ง section ชื่อ "<หน้า>__<ขั้น>"
render: PYTHONPATH=manim uv run python tools/export_clips.py manim/fit_clip.py FitClip --res 880,400
"""

from manim import (
    DOWN, UP, Create, DashedLine, FadeIn, GrowFromEdge, LaggedStart, Line, NumberLine, Scene, config,
)

from facts import F, num
from studio_style import ALERT, BG, INK, MUTED, SIZE_SMALL, thai

config.background_color = BG

# ความถี่องค์ประกอบน้ำขึ้นน้ำลง (รอบต่อวัน) — ค่าคงที่ทางฟิสิกส์ ใช้วางตำแหน่งเส้นในแผนภาพเท่านั้น ไม่ขึ้นจอเป็นตัวเลข
TIDES = {"O1": 0.9295, "P1": 0.9973, "K1": 1.0027, "M2": 1.9323, "S2": 2.0, "K2": 2.0055}
HEIGHT = {"O1": 1.6, "P1": 1.0, "K1": 2.3, "M2": 2.5, "S2": 1.4, "K2": 0.6}


class FitClip(Scene):
    def construct(self):
        axis = NumberLine(x_range=[0, 2.2, 0.5], length=12, color=MUTED, include_tip=False).shift(DOWN * 2)
        lines = {k: Line(axis.n2p(f), axis.n2p(f) + UP * HEIGHT[k], stroke_width=10, color=INK)
                 for k, f in TIDES.items()}

        self.next_section("SQ03_S030__1")
        self.play(Create(axis), run_time=0.6)
        self.play(LaggedStart(*[GrowFromEdge(m, DOWN) for m in lines.values()], lag_ratio=0.15), run_time=1.2)

        self.next_section("SQ03_S030__2")
        nyquist = DashedLine(axis.n2p(0.5) + UP * 3, axis.n2p(0.5), color=INK)
        self.play(Create(nyquist), lines["K1"].animate.set_color(ALERT), lines["P1"].animate.set_color(ALERT),
                  run_time=1.0)

        self.next_section("SQ03_S030__3")
        alias_f = 1 / F("alias.K1_days")  # สุ่มวันละครั้ง K1 พับไปที่ |f − 1| รอบต่อวัน
        for k in ("K1", "P1"):
            self.play(lines[k].animate.move_to(axis.n2p(alias_f) + UP * HEIGHT[k] / 2), run_time=0.7)
        label = thai(f"{num('alias.K1_days', 1)} วัน", size=SIZE_SMALL, color=ALERT)
        label.next_to(lines["K1"], UP, buff=0.2)
        self.play(FadeIn(label, shift=UP * 0.2), run_time=0.5)
        self.wait(0.3)
