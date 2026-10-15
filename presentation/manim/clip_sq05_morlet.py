"""คลิป SQ05_S020 (clip mode · theme D): เลื่อน Morlet wavelet ไปตามสัญญาณจริง → แถวของระนาบ เวลา × คาบ

render: PYTHONPATH=manim uv run python tools/export_clips.py manim/clip_sq05_morlet.py MorletClip --res 1680,600

ข้อมูลจริง: อนุกรมอันดามัน (andaman_mm_12m) · ค่า NaN แทนด้วย 0 · Morlet ω0 = F("cwt.morlet_w0")
ทุกแถวของระนาบคือ |ผลคูณรวม| ที่คำนวณจริงด้วย numpy (ไม่ใช่ภาพแต่ง) — แต่ไม่ได้ตัดกรวยอิทธิพล (COI) เพราะนี่คือคลิปอธิบายวิธี
คลิป (ไม่ใช่ภาพผลลัพธ์): ช่วงคาบที่แสดงจำกัดแค่พอให้เห็น wavelet ทั้งตัวบนจอ

ขั้น (section "<หน้า>__<ขั้น>"):
  SQ05_S020__1  Morlet (ส่วนจริงเส้นทึบ · ส่วนจินตภาพเส้นประจาง · ซองเกาส์เซียน) เลื่อนไปตามสัญญาณ → เติมแถวแรกของระนาบ
  SQ05_S020__2  เปลี่ยนสเกล (wavelet กว้างขึ้น) แล้ว**เลื่อนไปตามสัญญาณอีกรอบ** → แถวถัดไป · ทำทุกสเกลจนเป็นระนาบ
                (ผู้ใช้ 10-14: รุ่นเดิมแค่ขยาย wavelet อยู่กับที่ — CWT ต้องเลื่อนทุกสเกล)
                สองสเกลแรกเลื่อนช้าให้เห็น · สเกลที่เหลือเลื่อนเร็วสลับทิศ แถวเติมตามทิศที่เลื่อน
"""

import numpy as np
from manim import (
    RIGHT, UP, Create, DashedVMobject, FadeIn, ImageMobject, Line, Rectangle, Scene, Text, ValueTracker, VGroup,
    VMobject, always_redraw, config, linear, smooth,
)

from facts import F, derived
from studio_style import ANDAMAN, BG, GREY, INK, MUTED, NAVY, SEA_HIGH, SIZE_BODY, SIZE_SMALL, FONT, thai

config.background_color = BG
config.frame_height = 8.0
config.frame_width = 8.0 * config.pixel_width / config.pixel_height

# --- ข้อมูลและ CWT (คำนวณจริง) --------------------------------------------------------------------------
_d = derived()
T = _d["t"]                                   # ปี (รายเดือน)
SIG = np.nan_to_num(_d["andaman_mm_12m"])     # NaN -> 0
N = len(SIG)
DT = T[1] - T[0]                              # ปีต่อตัวอย่าง (ราว 1/12)
W0 = float(F("cwt.morlet_w0"))
P_MIN, P_MAX = 2.0, 12.0                      # ช่วงคาบ (ปี) ที่แสดงในระนาบ
PER_OCT = int(F("cwt.scales_per_octave"))     # 12 สเกลต่อ octave (เท่ากับรายงาน)
N_ROWS = int(round(np.log2(P_MAX / P_MIN) * PER_OCT)) + 1
PERIODS = P_MIN * 2 ** (np.arange(N_ROWS) / PER_OCT)
P_TO_S = 4 * np.pi / (W0 + np.sqrt(2 + W0**2))   # คาบ = P_TO_S × สเกล (ที่ ω0 = 6 สเกลแทบเท่าคาบ)


def morlet(tt, s):
    """Morlet เชิงซ้อน ψ(t/s) = exp(i ω0 t/s) · exp(−t²/2s²)  (t ในหน่วยปี)"""
    u = tt / s
    return np.exp(1j * W0 * u) * np.exp(-0.5 * u**2)


def cwt_row(period):
    """คูณแล้วรวมที่ทุกตำแหน่งเวลา = convolution กับ Morlet ของสเกลนี้ → ขนาด |W(t)|"""
    s = period / P_TO_S
    half = min(int(4 * s / DT), N - 1)
    k = np.arange(-half, half + 1) * DT
    psi = np.conj(morlet(k, s)) / np.sqrt(s)
    full = np.convolve(SIG, psi[::-1], mode="full")   # 'same' ให้ผิดความยาวเมื่อ wavelet ยาวกว่าสัญญาณ
    return np.abs(full[half:half + N]) * DT


MAG = np.array([cwt_row(p) for p in PERIODS])         # (N_ROWS, N)
MAG = MAG / np.percentile(MAG, 99.5)                  # หน่วยสมมติ: ปรับให้เห็นสีทั้งระนาบ (สีใช้เปรียบเทียบในภาพเดียว)
MAG = np.clip(MAG, 0, 1) ** 0.8

# --- เรขาคณิตของจอ (เฟรมกว้าง 22.4 สูง 8) ---------------------------------------------------------------
X0, X1 = -9.1, 8.9                           # แกนเวลา
SIG_Y, SIG_AMP = 2.3, 1.25                    # แถบสัญญาณ
PL_TOP, PL_BOT = 0.05, -3.35                  # ระนาบ เวลา × คาบ
ROW_H = (PL_TOP - PL_BOT) / N_ROWS
SIG_SCALE = SIG_AMP / np.max(np.abs(SIG))


def tx(year):
    return X0 + (year - T[0]) / (T[-1] - T[0]) * (X1 - X0)


def py(period):
    """คาบ (ปี) → y กลางแถวบนระนาบ (แกนลอการิทึม = แต่ละแถวห่างเท่ากัน)"""
    r = np.log2(period / P_MIN) * PER_OCT
    return PL_BOT + (r + 0.5) * ROW_H


# สีของระนาบ: ขาว → ฟ้าอ่อน → อันดามัน → กรมท่า (เฉพาะสีของ studio_style)
_STOPS = [(0.0, "#FFFFFF"), (0.35, SEA_HIGH), (0.7, ANDAMAN), (1.0, NAVY)]


def _hex(c):
    return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)], dtype=float)


def colourise(v):
    out = np.zeros(v.shape + (3,))
    xs = [s[0] for s in _STOPS]
    for ch in range(3):
        out[..., ch] = np.interp(v, xs, [_hex(s[1])[ch] for s in _STOPS])
    return out


RGB = colourise(MAG)


def plane_image(done_rows, partial_cols=0, from_right=False):
    """ภาพของระนาบ: แถวที่ 0..done_rows-1 เต็ม · แถวที่ done_rows เติม partial_cols คอลัมน์ (จากซ้าย หรือจากขวาถ้า from_right) · ที่เหลือโปร่งใส"""
    rgba = np.zeros((N_ROWS, N, 4), dtype=np.uint8)
    n_full = int(done_rows)
    rgba[:n_full, :, :3] = RGB[:n_full]
    rgba[:n_full, :, 3] = 255
    if n_full < N_ROWS and partial_cols > 0:
        c = int(partial_cols)
        cols = slice(N - c, N) if from_right else slice(0, c)
        rgba[n_full, cols, :3] = RGB[n_full, cols]
        rgba[n_full, cols, 3] = 255
    img = ImageMobject(np.flipud(rgba))           # แถวคาบสั้นอยู่ล่าง
    img.set_resampling_algorithm(0)  # 0 = nearest: เห็นเป็นแถว
    img.stretch_to_fit_width(X1 - X0)
    img.stretch_to_fit_height(PL_TOP - PL_BOT)
    img.move_to([(X0 + X1) / 2, (PL_TOP + PL_BOT) / 2, 0])
    return img


class MorletClip(Scene):
    def construct(self):
        self.camera.background_color = BG

        # --- สัญญาณจริง ------------------------------------------------------------------------------
        sig_pts = [[tx(t), SIG_Y + v * SIG_SCALE, 0] for t, v in zip(T, SIG)]
        signal = VMobject(color=ANDAMAN, stroke_width=3).set_points_as_corners(sig_pts)
        sig_zero = Line([X0, SIG_Y, 0], [X1, SIG_Y, 0], color=MUTED, stroke_width=1.5, stroke_opacity=0.5)

        # กรอบระนาบ + แกน
        frame = Rectangle(width=X1 - X0, height=PL_TOP - PL_BOT, stroke_color=MUTED, stroke_width=2, fill_opacity=0)
        frame.move_to([(X0 + X1) / 2, (PL_TOP + PL_BOT) / 2, 0])
        year_ticks = VGroup()
        for yr in (1960, 1980, 2000, 2020):
            year_ticks.add(Line([tx(yr), PL_BOT, 0], [tx(yr), PL_BOT - 0.12, 0], color=MUTED, stroke_width=2))
            year_ticks.add(Text(str(yr), font=FONT, font_size=SIZE_SMALL, color=MUTED).move_to([tx(yr), PL_BOT - 0.42, 0]))
        t_unit = thai("เวลา (ปี)", size=SIZE_SMALL, color=MUTED).move_to([X1 + 1.15, PL_BOT - 0.42, 0])
        p_ticks = VGroup()
        for p in (2, 4, 8):
            p_ticks.add(Line([X0 - 0.12, py(p), 0], [X0, py(p), 0], color=MUTED, stroke_width=2))
            p_ticks.add(Text(str(p), font=FONT, font_size=SIZE_SMALL, color=MUTED).move_to([X0 - 0.4, py(p), 0]))
        p_unit = thai("คาบ (ปี)", size=SIZE_SMALL, color=MUTED).move_to([X0 - 0.85, PL_TOP + 0.35, 0])
        # แกนตั้งของแถบสัญญาณ (ผู้ใช้ 10-15: ทุกกราฟต้องมีชื่อแกน x และ y) — ขีด ±200 มม. + ชื่อแกนเหนือขีด แบบเดียวกับ "คาบ (ปี)"
        sig_ticks = VGroup()
        for mm in (-200, 0, 200):
            y = SIG_Y + mm * SIG_SCALE
            sig_ticks.add(Line([X0 - 0.12, y, 0], [X0, y, 0], color=MUTED, stroke_width=2))
            sig_ticks.add(Text(str(mm).replace("-", "−"), font=FONT, font_size=SIZE_SMALL, color=MUTED).move_to([X0 - 0.5, y, 0]))
        sig_label = VGroup(sig_ticks, thai("ระดับน้ำ (มม.)", size=SIZE_SMALL, color=ANDAMAN).move_to([X0 - 0.85, SIG_Y + 1.42, 0]))

        # --- wavelet (วาดใหม่ทุกเฟรมจาก ValueTracker ของตำแหน่งและคาบ) ---------------------------------
        pos = ValueTracker(T[0] + 3)       # ตำแหน่งกลาง wavelet (ปี)
        per = ValueTracker(P_MIN)          # คาบของ wavelet (ปี)
        WAV_AMP = 0.95

        def wav_curve(kind):
            s = per.get_value() / P_TO_S
            span = 2.6 * s                                     # ครอบซอง ±2.6σ
            ts = np.linspace(-span, span, 260)
            psi = morlet(ts, s)
            if kind == "env":
                ys = np.exp(-0.5 * (ts / s) ** 2)
            elif kind == "re":
                ys = psi.real
            else:
                ys = psi.imag
            xs = [tx(pos.get_value() + t) for t in ts]
            pts = [[x, SIG_Y + WAV_AMP * y, 0] for x, y in zip(xs, ys) if X0 <= x <= X1]
            return pts

        def make(kind):
            def build():
                pts = wav_curve(kind)
                m = VMobject()
                if len(pts) < 2:
                    return m
                m.set_points_as_corners(pts)
                if kind == "re":
                    m.set_stroke(INK, width=5)
                elif kind == "im":
                    m.set_stroke(MUTED, width=3.5, opacity=0.9)
                    m = DashedVMobject(m, num_dashes=60, dashed_ratio=0.55)
                else:
                    m.set_stroke(GREY, width=2.5, opacity=0.9)
                return m
            return always_redraw(build)

        def window():
            pts = wav_curve("env")
            if len(pts) < 2:
                return VMobject()
            x_lo, x_hi = pts[0][0], pts[-1][0]
            r = Rectangle(width=max(x_hi - x_lo, 0.01), height=2 * SIG_AMP + 0.3, stroke_width=0,
                          fill_color=ANDAMAN, fill_opacity=0.08)
            return r.move_to([(x_lo + x_hi) / 2, SIG_Y, 0])

        win = always_redraw(window)
        env, re_, im_ = make("env"), make("re"), make("im")

        # ตำแหน่งปัจจุบัน -> เส้นประลงไปที่แถวของระนาบ
        marker = always_redraw(lambda: Line(
            [tx(pos.get_value()), SIG_Y - SIG_AMP - 0.15, 0], [tx(pos.get_value()), py(per.get_value()), 0],
            color=INK, stroke_width=2, stroke_opacity=0.6))
        row_mark = always_redraw(lambda: Line(
            [X0, py(per.get_value()), 0], [X1, py(per.get_value()), 0], color=INK, stroke_width=2, stroke_opacity=0.35))
        # ป้ายสเกล ↔ คาบ ติดกับแถวปัจจุบัน
        scale_tag = always_redraw(lambda: thai("สเกล ↔ คาบ", size=SIZE_SMALL, color=INK).move_to(
            [X1 + 1.15, py(per.get_value()), 0]))

        # คำอธิบายเส้น (legend) ตรงขอบบนของแถบสัญญาณ
        def legend_item(label, kind, x):
            line = Line([x, 3.72, 0], [x + 0.9, 3.72, 0])
            if kind == "re":
                line.set_stroke(INK, width=5)
            elif kind == "im":
                line = DashedVMobject(line.set_stroke(MUTED, width=3.5), num_dashes=6, dashed_ratio=0.55)
            else:
                line.set_stroke(GREY, width=2.5)
            text = thai(label, size=SIZE_SMALL, color=INK).next_to(line, RIGHT, buff=0.15)
            return VGroup(line, text)

        legend = VGroup(
            legend_item("ส่วนจริง", "re", X0 + 2.6),
            legend_item("ส่วนจินตภาพ", "im", X0 + 5.2),
            legend_item("ซองเกาส์เซียน", "env", X0 + 8.6),
        )

        # --- ระนาบ (ภาพคำนวณจริง) -------------------------------------------------------------------
        state = ValueTracker(0.0)          # = จำนวนแถวที่เสร็จ (ทศนิยม = ความคืบหน้าในแถวที่กำลังทำ)
        leftward = ValueTracker(0.0)       # 1 = แถวที่กำลังทำเลื่อนจากขวาไปซ้าย (เติมแถวจากขวา)
        def build_plane():
            v = state.get_value()
            return plane_image(int(v), (v - int(v)) * N, from_right=leftward.get_value() > 0.5)
        plane = always_redraw(build_plane)

        # === ขั้น 1: เลื่อนไปตามสัญญาณ เติมแถวแรก ==============================================================
        self.next_section("SQ05_S020__1")
        self.play(Create(frame), FadeIn(year_ticks), FadeIn(t_unit), FadeIn(p_ticks), FadeIn(p_unit), run_time=0.6)
        self.play(Create(signal), FadeIn(sig_zero), FadeIn(sig_label), run_time=1.2)
        self.add(win)
        self.play(FadeIn(win), FadeIn(env), FadeIn(re_), FadeIn(im_), FadeIn(legend), FadeIn(row_mark),
                  FadeIn(scale_tag), run_time=0.8)
        self.add(plane, marker)
        self.add(win, env, re_, im_)       # ให้ wavelet อยู่เหนือสัญญาณ
        # เลื่อนจากต้นไปปลายอนุกรม: แถวแรกเติมตามตำแหน่ง (state ในช่วง 0..1 = ความคืบหน้าของแถวที่ 0)
        t_start, t_end = T[0] + 3, T[-1] - 3
        pos.set_value(t_start)
        self.play(
            pos.animate.set_value(t_end),
            state.animate.set_value(0.999),
            run_time=6.5, rate_func=linear,
        )
        self.play(state.animate.set_value(1.0), run_time=0.2)
        self.wait(0.4)

        # === ขั้น 2: เปลี่ยนสเกล -> แถวถัดไปซ้อนขึ้นเป็นระนาบ ================================================
        self.next_section("SQ05_S020__2")
        # ทุกสเกล: ขยาย wavelet เป็นสเกลถัดไป แล้วเลื่อนไปตามสัญญาณทั้งเส้น = convolution หนึ่งแถว
        # สองสเกลแรกช้าให้เห็นวิธี · ที่เหลือเร็ว สลับทิศ (ไปแล้วกลับ) ไม่ต้องกระโดดกลับต้นเส้น
        per_at = lambda rows: P_MIN * 2 ** (rows / PER_OCT)  # noqa: E731
        going_right = False                     # แถวแรกจบที่ปลายขวา → แถวถัดไปเลื่อนกลับทางซ้าย
        for r in range(1, N_ROWS):
            slow = r <= 2
            self.play(per.animate.set_value(per_at(r)), run_time=0.5 if slow else 0.06)
            leftward.set_value(0.0 if going_right else 1.0)
            self.play(
                pos.animate.set_value(t_end if going_right else t_start),
                state.animate.set_value(r + 0.999),
                run_time=2.6 if slow else 0.16, rate_func=linear,
            )
            state.set_value(float(r + 1))
            going_right = not going_right
        self.wait(0.6)
