"""ชิ้นส่วนภาพที่ใช้ซ้ำทุกฉาก: กรอบกราฟ, เส้น/พื้นจากข้อมูล, ระนาบ WTC, แถบตอน, การ์ดสรุป, เวลาช็อต

หลัก: วาด "ตามข้อมูล" เท่านั้น — ไม่ smooth เพิ่ม ไม่ตัดช่วงทิ้งเงียบ ๆ (ช่วงไม่มีข้อมูล = เส้นขาด)
ใช้กรอบของเราเอง (Frame2D) แทน Axes ของ Manim เพราะต้องการแกน log ที่กลับหัว (คาบสั้นอยู่บนแบบรายงาน),
แกน y สองข้าง และป้ายตัวเลขด้วยฟอนต์ไทยเดียวกับทั้งคลิป
"""

from __future__ import annotations

import re
from functools import cache
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from manim import (  # noqa: E402
    DOWN, LEFT, ORIGIN, RIGHT, UP, UL,
    Arrow, Circle, DashedVMobject, Dot, Group, ImageMobject, Line, Rectangle, RoundedRectangle,
    VGroup, VMobject,
)
from manim.mobject.types.image_mobject import RESAMPLING_ALGORITHMS  # noqa: E402

from facts import ROOT, processed  # noqa: E402
from studio_style import (  # noqa: E402
    BG, INK, MUTED, NAVY, PANEL, SIZE_BODY, SIZE_SMALL, thai,
)

CHAPTERS = [  # บท v3: น้ำหนักอยู่ที่กระบวนการ DSP — ชื่อตอนบอกขั้นของสายประมวลผล
    "โจทย์", "โจทย์ในรูปสัญญาณ", "สุ่ม · กรอง · ลดอัตรา", "สหสัมพันธ์ไม่พอ", "CWT",
    "WTC และ MWC", "เทียบกับ noise", "ตีความทางกายภาพ", "เชื่อได้แค่ไหน", "สรุป",
]


# --- กรอบกราฟ -------------------------------------------------------------------------------------------

class Frame2D:
    """แปลงพิกัดข้อมูล (x, y) เป็นจุดบนจอ ภายในสี่เหลี่ยมกว้าง width สูง height ที่ center

    y_log: ใช้ log2 ของ y (คาบ) · y_flip: ค่าน้อยอยู่บน (แบบระนาบเวฟเล็ตในรายงาน)
    """

    def __init__(self, x_range, y_range, width, height, center=ORIGIN, *, y_log=False, y_flip=False):
        self.x0, self.x1 = x_range
        self.y_log, self.y_flip = y_log, y_flip
        self.y0, self.y1 = (np.log2(y_range[0]), np.log2(y_range[1])) if y_log else y_range
        self.w, self.h = width, height
        self.c = np.array(center, dtype=float)

    def _fy(self, y):
        y = np.log2(y) if self.y_log else y
        f = (y - self.y0) / (self.y1 - self.y0)
        return 1 - f if self.y_flip else f

    def p(self, x, y):
        fx = (x - self.x0) / (self.x1 - self.x0)
        return self.c + np.array([(fx - 0.5) * self.w, (self._fy(y) - 0.5) * self.h, 0.0])

    def border(self, color=MUTED, width=1.5):
        return Rectangle(width=self.w, height=self.h, stroke_color=color, stroke_width=width).move_to(self.c)

    def hline(self, y, color=MUTED, width=1.5, opacity=0.8):
        return Line(self.p(self.x0, y), self.p(self.x1, y), stroke_color=color, stroke_width=width,
                    stroke_opacity=opacity)

    def x_ticks(self, values, labels=None, size=SIZE_SMALL, color=MUTED):
        """ขีดและตัวเลขใต้ขอบล่างของกรอบ"""
        group = VGroup()
        bottom = self.c[1] - self.h / 2
        for v, lab in zip(values, labels or [str(v) for v in values]):
            x = self.c[0] + ((v - self.x0) / (self.x1 - self.x0) - 0.5) * self.w
            base = np.array([x, bottom, 0.0])
            tick = Line(base, base + DOWN * 0.08, stroke_color=color, stroke_width=1.5)
            group.add(tick, thai(lab, size=size, color=color).next_to(tick, DOWN, buff=0.08))
        return group

    def y_ticks(self, values, labels=None, side=LEFT, size=SIZE_SMALL, color=MUTED):
        """ขีดและตัวเลขที่ขอบซ้าย (หรือขวา) ของกรอบ — values เป็นหน่วยข้อมูล (ไม่ใช่ log)"""
        group = VGroup()
        edge = self.c[0] + (-self.w / 2 if side is LEFT else self.w / 2)
        for v, lab in zip(values, labels or [str(v) for v in values]):
            base = np.array([edge, self.p(self.x0, v)[1], 0.0])
            tick = Line(base, base + side * 0.08, stroke_color=color, stroke_width=1.5)
            group.add(tick, thai(lab, size=size, color=color).next_to(tick, side, buff=0.08))
        return group

    def x_title(self, text, size=SIZE_SMALL, color=MUTED, buff=0.55):
        return thai(text, size=size, color=color).next_to(self.border(), DOWN, buff=buff)

    def y_title(self, text, side=LEFT, size=SIZE_SMALL, color=MUTED, ticks=None, buff=0.2):
        """ชื่อแกนตั้ง (หมุน) — ส่ง ticks มาด้วยเพื่อวางถัดจากตัวเลขบนแกน ไม่ทับกัน"""
        label = thai(text, size=size, color=color).rotate(np.pi / 2 if side is LEFT else -np.pi / 2)
        return label.next_to(ticks if ticks is not None else self.border(), side, buff=buff)


def runs(mask):
    """ช่วงต่อเนื่องที่ mask เป็นจริง -> ลิสต์ของ index arrays"""
    idx = np.flatnonzero(mask)
    if idx.size == 0:
        return []
    return np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1)


def series_line(frame, x, y, color, width=3.0, opacity=1.0):
    """เส้นจากข้อมูล — ตรงไหนเป็น NaN เส้นขาดตรงนั้น"""
    group = VGroup()
    for r in runs(np.isfinite(y)):
        if r.size < 2:
            continue
        pts = [frame.p(x[i], y[i]) for i in r]
        group.add(VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
                  .set_points_as_corners(pts))
    return group


def series_fill(frame, x, y, pos_color, neg_color, opacity=0.85):
    """พื้นระหว่างเส้นกับศูนย์: บวกสีหนึ่ง ลบอีกสีหนึ่ง (แบบ fig11 ของรายงาน)"""
    group = VGroup()
    for r in runs(np.isfinite(y)):
        if r.size < 2:
            continue
        xs, ys = x[r], y[r]
        for sign, color in ((1, pos_color), (-1, neg_color)):
            yy = np.where(sign * ys > 0, ys, 0.0)
            pts = [frame.p(xs[0], 0)] + [frame.p(a, b) for a, b in zip(xs, yy)] + [frame.p(xs[-1], 0)]
            poly = VMobject(stroke_width=0, fill_color=color, fill_opacity=opacity)
            poly.set_points_as_corners(pts + [pts[0]])
            group.add(poly)
    return group


def legend(items, size=SIZE_SMALL):
    """[(สี, ข้อความ), ...] -> ตำนานแนวนอน"""
    group = VGroup()
    for color, label in items:
        swatch = Line(ORIGIN, RIGHT * 0.45, stroke_color=color, stroke_width=6)
        group.add(VGroup(swatch, thai(label, size=size).next_to(swatch, RIGHT, buff=0.12)))
    return group.arrange(RIGHT, buff=0.45)


# --- ระนาบ WTC --------------------------------------------------------------------------------------------

@cache
def _viridis():
    return plt.get_cmap("viridis")


def _blend(rgb, amount):
    """ผสมสีเข้ากับพื้นหลัง (ใช้ทำบริเวณนอก COI ให้จาง เหมือนรายงาน)"""
    bg = np.array([int(BG[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    return rgb * (1 - amount) + bg * amount


def wtc_plane(station, index, width, height, center=ORIGIN, *, arrows=True, arrow_step=(8, 30)):
    """ระนาบ wavelet coherence จาก wtc_q1.npz ของโครงงาน DSP

    สี = R² (viridis เหมือนรายงาน) · นอก COI จางลง · เส้นขาว = เกินเกณฑ์ 95% (sig & valid) ·
    เส้นประ = COI · ลูกศร = เฟส (cos θ, sin θ): ขวา = ไปด้วยกัน, ซ้าย = สวนทาง, ขึ้น = ระดับน้ำนำ
    แสดงลูกศรเฉพาะบริเวณที่มีนัยสำคัญ เพื่อให้อ่านง่ายบนจอ (รายงานแสดงทั่วทั้งกรวย)
    คืน (frame, VGroup ของเส้น/ลูกศร, ImageMobject)
    """
    q = processed("wtc_q1.npz")
    si = [str(s) for s in q["stations"]].index(station)
    xi = [str(s) for s in q["indices"]].index(index)
    R2, sig, valid, ph = q["R2"][si, xi], q["sig"][si, xi], q["valid"][si, xi], q["phase"][si, xi]
    t, per, coi = q["t"], q["periods"], q["coi"]
    frame = Frame2D((t[0], t[-1]), (per[0], per[-1]), width, height, center, y_log=True, y_flip=True)

    inside = per[:, None] <= coi[None, :]
    rgb = _viridis()(np.clip(R2, 0, 1))[..., :3]
    rgb[~inside] = _blend(rgb[~inside], 0.6)
    img_arr = (np.dstack([rgb, np.ones(R2.shape)]) * 255).astype(np.uint8)  # แถว 0 = คาบสั้นสุด = ด้านบน
    img = ImageMobject(img_arr)
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
    img.stretch_to_fit_width(width).stretch_to_fit_height(height).move_to(center)

    overlay = VGroup()
    # เส้นเกณฑ์ 95%: contour ของ mask บนกริด (เวลา, log2 คาบ) ด้วย matplotlib แล้วแปลงเป็นเส้นบนจอ
    mask = (sig & valid & inside).astype(float)
    fig = plt.figure()
    cs = plt.contour(t, np.log2(per), mask, levels=[0.5])
    for seg in cs.allsegs[0]:
        if len(seg) >= 3:
            pts = [frame.p(a, 2 ** b) for a, b in seg]
            overlay.add(VMobject(stroke_color=INK, stroke_width=2.5).set_points_as_corners(pts))
    plt.close(fig)
    # COI
    coi_clip = np.clip(coi, per[0], per[-1])
    coi_line = VMobject(stroke_color=INK, stroke_width=2).set_points_as_corners(
        [frame.p(a, b) for a, b in zip(t, coi_clip)])
    overlay.add(DashedVMobject(coi_line, num_dashes=60, dashed_ratio=0.55))
    # ลูกศรเฟส
    if arrows:
        s_step, t_step = arrow_step
        L = 0.17
        for i in range(0, len(per), s_step):
            for j in range(0, len(t), t_step):
                if sig[i, j] and valid[i, j] and inside[i, j]:
                    c = frame.p(t[j], per[i])
                    d = np.array([np.cos(ph[i, j]), np.sin(ph[i, j]), 0.0]) * L
                    overlay.add(Arrow(c - d / 2, c + d / 2, buff=0, stroke_width=2.2, color=INK,
                                      max_tip_length_to_length_ratio=0.45, max_stroke_width_to_length_ratio=12))
    return frame, overlay, img


def period_ticks(frame, values=(0.5, 1, 2, 4, 8, 16, 32), **kw):
    labels = [("0.5" if v == 0.5 else str(int(v))) for v in values]
    return frame.y_ticks(list(values), labels, **kw)


def colorbar(height=2.4, width=0.22, label="R²"):
    """แถบสี viridis 0–1 พร้อมป้าย — คืน Group (ภาพ + ตัวหนังสือ) ย้ายด้วย .move_to() ได้ทั้งก้อน"""
    n = 64
    rgb = _viridis()(np.linspace(1, 0, n))[:, :3]  # บน = 1
    arr = (np.dstack([np.repeat(rgb[:, None, :], 4, axis=1), np.ones((n, 4))]) * 255).astype(np.uint8)
    img = ImageMobject(arr).stretch_to_fit_width(width).stretch_to_fit_height(height)
    return Group(
        img,
        thai("1", size=SIZE_SMALL, color=MUTED).next_to(img.get_corner(UP + RIGHT), RIGHT, buff=0.1),
        thai("0", size=SIZE_SMALL, color=MUTED).next_to(img.get_corner(DOWN + RIGHT), RIGHT, buff=0.1),
        thai(label, size=SIZE_SMALL, color=MUTED).next_to(img, UP, buff=0.15),
    )


def wtc_key(size=SIZE_SMALL):
    """คำอธิบายสัญลักษณ์ของระนาบ WTC แบบแนวตั้ง (วางข้างแถบสี)"""
    solid = Line(ORIGIN, RIGHT * 0.4, stroke_color=INK, stroke_width=2.5)
    dashed = DashedVMobject(Line(ORIGIN, RIGHT * 0.4, stroke_color=INK, stroke_width=2), num_dashes=3)
    rows = [
        (solid, "เกินเกณฑ์ 95%"),
        (dashed, "กรวยอิทธิพล"),
        (Arrow(LEFT * 0.2, RIGHT * 0.2, buff=0, stroke_width=2.5, color=INK), "ไปด้วยกัน"),
        (Arrow(RIGHT * 0.2, LEFT * 0.2, buff=0, stroke_width=2.5, color=INK), "สวนทาง"),
        (Arrow(DOWN * 0.2, UP * 0.2, buff=0, stroke_width=2.5, color=INK), "ระดับน้ำนำ"),
    ]
    group = VGroup()
    for sym, text in rows:
        sym_box = VGroup(sym).set_width(0.4) if sym.width > 0.4 else VGroup(sym)
        group.add(VGroup(sym_box, thai(text, size=size, color=MUTED).next_to(sym_box, RIGHT, buff=0.15)))
    return group.arrange(DOWN, aligned_edge=LEFT, buff=0.18)


# --- แถบตอน + การ์ดสรุป -------------------------------------------------------------------------------------

def chapter_bar(n):
    """แถบบนสุด: จุด 10 จุด (ตอนปัจจุบันเด่น) + ชื่อตอน — บอกคนดูว่าอยู่ตรงไหนของเรื่อง"""
    dots = VGroup(*[
        Circle(radius=0.07, stroke_width=0, fill_color=INK if i == n else MUTED,
               fill_opacity=1.0 if i == n else (0.55 if i < n else 0.25))
        for i in range(1, len(CHAPTERS) + 1)
    ]).arrange(RIGHT, buff=0.16)
    title = thai(f"{n} · {CHAPTERS[n - 1]}", size=SIZE_SMALL, color=MUTED)
    return VGroup(dots, title).arrange(RIGHT, buff=0.3).to_corner(UL, buff=0.32)


def summary_card(text):
    """การ์ดสรุปท้ายตอน"""
    body = thai(text, size=SIZE_BODY, color=INK, weight="SEMIBOLD")
    head = thai("สรุป", size=SIZE_SMALL, color=MUTED)
    content = VGroup(head, body).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    box = RoundedRectangle(corner_radius=0.12, width=content.width + 0.8, height=content.height + 0.5,
                           fill_color=PANEL, fill_opacity=0.96, stroke_color=NAVY, stroke_width=3)
    content.move_to(box)
    return VGroup(box, content).to_edge(DOWN, buff=0.45)


# --- เวลา ------------------------------------------------------------------------------------------------

SECONDS_PER_SENTENCE = 4.2  # ใช้ชั่วคราวจนกว่าจะมีเสียงจริง


@cache
def _sentences_per_shot():
    counts, shot = {}, None
    for line in (ROOT / "context" / "script.md").read_text().splitlines():
        if m := re.match(r"^### (SQ\d+_S\d+)", line):
            shot = m.group(1)
            counts[shot] = 0
        elif shot and line.startswith("- "):
            counts[shot] += 1
    return counts


def shot_seconds(shot):
    """ความยาวช็อต (วินาที) — ตอนนี้ประมาณจากจำนวนประโยค หลังอัดเสียงจะอ่านจาก context/timing.json"""
    timing = ROOT / "context" / "timing.json"
    if timing.exists():
        import json
        data = json.loads(timing.read_text())
        if shot in data:
            return data[shot]
    return max(3.0, _sentences_per_shot().get(shot, 1) * SECONDS_PER_SENTENCE)
