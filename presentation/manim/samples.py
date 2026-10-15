"""ภาพตัวอย่างสำหรับประตู 1 — ให้ผู้ใช้ดูหน้าตา (สี ฟอนต์ ความหนาแน่น) ก่อนผลิตจริง

    PYTHONPATH=manim uv run manim -s -qh manim/samples.py SampleChart SampleWTC
"""

import numpy as np
from manim import DOWN, LEFT, RIGHT, UP, Line, Rectangle, Scene, VGroup

from facts import F, derived, num
from plots import Frame2D, chapter_bar, colorbar, legend, period_ticks, series_fill, series_line, wtc_key, wtc_plane
from studio_style import (
    ANDAMAN, DMI, GULF, INK, MUTED, NINO, SEA_HIGH, SEA_LOW, SIZE_BODY, SIZE_SMALL,
    kind_tag, setup_scene, thai,
)

MM_PER_SD = 100  # แกนขวา: 1 SD ของดัชนี วาดสูงเท่า 100 มม. (มีแกนขวาบอกหน่วย SD จริง)


class SampleChart(Scene):
    """หน้าตาแบบ SQ04_S010 — ระดับน้ำอันดามัน vs −Niño3.4 / −DMI (fig11 ของรายงาน)"""

    def construct(self):
        setup_scene(self)
        d = derived()
        t = d["t"]
        fr = Frame2D((t[0], t[-1]), (-260, 260), 10.4, 4.6, center=[0.15, -0.35, 0])
        fill = series_fill(fr, t, d["andaman_mm_12m"], SEA_HIGH, SEA_LOW, opacity=0.8)
        nino = series_line(fr, t, d["neg_nino34_12m"] * MM_PER_SD, NINO, width=3)
        dmi = series_line(fr, t, d["neg_dmi_12m"] * MM_PER_SD, DMI, width=3, opacity=0.9)

        y97 = F("event.dmcr_low_years")[0]
        band = Rectangle(width=abs(fr.p(y97 + 1.5, 0)[0] - fr.p(y97 + 0.5, 0)[0]), height=fr.h,
                         stroke_width=0, fill_color=INK, fill_opacity=0.10).move_to(
            [fr.p(y97 + 1.0, 0)[0], fr.c[1], 0])
        drop = thai(f"{y97}–{str(y97 + 1)[-2:]} · ต่ำลง ~{num('event.andaman_9798_min_mm', absval=True, round_to=10)} มม.",
                    size=SIZE_SMALL, color=INK)
        # ป้ายเหตุการณ์อยู่เหนือกรอบ ชิดขวา แล้วลากเส้นลงมาที่แถบไฮไลต์ — ไม่ทับข้อมูล
        drop.next_to(fr.border(), UP, buff=0.25).align_to(fr.border(), RIGHT)
        pointer = Line([band.get_center()[0], drop.get_bottom()[1] - 0.05, 0], band.get_top(),
                       stroke_color=INK, stroke_width=1.5)

        left = fr.y_ticks([-200, -100, 0, 100, 200], ["−200", "−100", "0", "100", "200"])
        right = fr.y_ticks([-200, -100, 0, 100, 200], ["−2", "−1", "0", "1", "2"], side=RIGHT)
        axes = VGroup(
            fr.border(), fr.hline(0), fr.x_ticks([1960, 1980, 2000, 2020]), left, right,
            fr.y_title("ระดับน้ำผิดปกติ (มม. · เฉลี่ย 12 เดือน)", ticks=left),
            fr.y_title("ดัชนีกลับด้าน (SD)", side=RIGHT, ticks=right),
        )
        title = thai("อันดามัน · เกาะตะเภาน้อย", size=SIZE_BODY, color=ANDAMAN, weight="SEMIBOLD")
        title.next_to(fr.border(), UP, buff=0.25).align_to(fr.border(), LEFT)
        key = legend([(SEA_LOW, "ต่ำกว่าปกติ"), (SEA_HIGH, "สูงกว่าปกติ"), (NINO, "−Niño3.4"), (DMI, "−DMI")])
        key.next_to(fr.border(), DOWN, buff=0.7)
        self.add(fill, band, nino, dmi, axes, title, pointer, drop, key, chapter_bar(4), kind_tag("data"))


class SampleWTC(Scene):
    """หน้าตาแบบ SQ06_S030 — ระนาบ WTC อันดามัน vs อ่าวไทย กับ Niño3.4 (fig03 ของรายงาน)"""

    def construct(self):
        setup_scene(self)
        w, h = 9.4, 2.6
        top = wtc_plane("ko_taphao_noi", "nino34", w, h, center=[-0.95, 1.25, 0])
        bot = wtc_plane("ko_lak", "nino34", w, h, center=[-0.95, -2.0, 0])
        parts = VGroup()
        for (fr, overlay, img), name, color in ((top, "อันดามัน × Niño3.4", ANDAMAN), (bot, "อ่าวไทย × Niño3.4", GULF)):
            self.add(img)
            label = thai(name, size=SIZE_BODY, color=color, weight="SEMIBOLD")
            label.next_to(fr.border(), UP, buff=0.12).align_to(fr.border(), LEFT)
            parts.add(overlay, fr.border(), period_ticks(fr, values=(0.5, 2, 8, 32)), label)
        fr_b = bot[0]
        parts.add(fr_b.x_ticks([1960, 1980, 2000, 2020]))
        ylab = thai("คาบ (ปี)", size=SIZE_SMALL, color=MUTED).rotate(np.pi / 2)
        ylab.move_to([fr_b.c[0] - fr_b.w / 2 - 1.0, (top[0].c[1] + fr_b.c[1]) / 2, 0])
        right_x = fr_b.c[0] + fr_b.w / 2 + 0.75
        cbar = colorbar(height=2.2).move_to([right_x, top[0].c[1] - 0.1, 0])
        key = wtc_key().next_to([right_x - 0.3, fr_b.c[1], 0], RIGHT, buff=0)
        self.add(parts, ylab, cbar, key, chapter_bar(6), kind_tag("data"))
