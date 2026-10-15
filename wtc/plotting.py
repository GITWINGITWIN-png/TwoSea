"""รูปผลลัพธ์ — coherence map, COI, ลูกศรเฟส, แผนที่ PASC/AWC

สถานะ: use_thai_font / period_axis / plot_coherence / plot_series (W1)
       plot_filter_response (W2 · 2026-09-30) · plot_pasc_curve (Q6) ยังไม่เขียน

ข้อตกลงของรูปในโปรเจกต์นี้
  - แกนคาบเป็น **log และกลับหัว** (คาบสั้นอยู่บน) ตามธรรมเนียมของรูปในเปเปอร์ต้นทาง
  - นอก COI ต้องเห็นว่าเป็นนอก COI เสมอ — ใช้การถมสีทับ ไม่ใช่แค่ลากเส้น
    เพราะรูปที่ไม่แสดง COI ชวนให้อ่านสัญญาณขอบเป็นของจริง
  - ลูกศรเฟส: ชี้ขวา = ไปด้วยกัน · ชี้ซ้าย = สวนทางกัน · ชี้ขึ้น = **อนุกรมแรกที่ส่งเข้า wtc() นำ**
    อนุกรมที่สองหนึ่งในสี่คาบ — ในโปรเจกต์นี้อนุกรมแรกคือ **ระดับน้ำ** (run_wtc.py เรียก wtc(Wy, Wx))
    ⇒ ชี้ขึ้น = ระดับน้ำนำดัชนี · ชี้ลง = ดัชนีนำระดับน้ำ (ทิศอิงพิกัดจอ ไม่กลับตามแกนคาบที่กลับหัว)
    🐛 แก้ 2026-10-07: เดิมเขียน "ชี้ขึ้น = X นำ Y" ซึ่งอ่านกลับด้าน เพราะทั้งโปรเจกต์เรียกดัชนีว่า X
    (ตรวจด้วยอนุกรมสังเคราะห์: ระดับน้ำนำ 6 เดือนที่คาบ 4 ปี ⇒ +45° — docs ในรายงานกลไก)
    (MWC ไม่มีเฟส — พล็อตได้แค่ขนาด ดู docs/source-paper-detail.md §6 จ)
"""
from __future__ import annotations
import numpy as np


def use_thai_font(size: int = 10) -> str:
    """ตั้งฟอนต์ให้พิมพ์ไทยในรูปได้ — คืนชื่อฟอนต์ที่เลือกได้จริง

    ถ้าไม่มีฟอนต์ไทยในเครื่อง ตัวอักษรไทยจะกลายเป็นกล่องสี่เหลี่ยมโดยไม่มี error
    ⇒ ฟังก์ชันนี้คืนชื่อออกมาให้โน้ตบุ๊กพิมพ์ดู จะได้รู้ตัวตั้งแต่ต้น

    ⚠️ **ต้องตั้งเป็นรายการ ไม่ใช่ชื่อเดียว** — Noto Sans Thai ไม่มีอักษรละติน ตัวเลข
    หรือแม้แต่จุดทศนิยมกับเครื่องหมาย % อยู่ในตัวมันเอง ถ้าตั้งชื่อเดียวทุกอย่างที่ไม่ใช่
    อักษรไทย**จะกลายเป็นกล่องทั้งหมด** (เจอจริงตอนรันโน้ตบุ๊กครั้งแรก 2026-09-20)
    matplotlib >= 3.6 เลือกฟอนต์ทีละอักขระตามลำดับในรายการนี้ ⇒ ใส่ DejaVu Sans ต่อท้าย
    """
    import matplotlib as mpl
    from matplotlib import font_manager as fm

    have = {f.name for f in fm.fontManager.ttflist}
    for name in ("Noto Sans Thai", "Sarabun", "Loma", "Garuda", "TH Sarabun New"):
        if name in have:
            mpl.rcParams["font.family"] = [name, "DejaVu Sans"]
            mpl.rcParams["font.size"] = size
            mpl.rcParams["axes.unicode_minus"] = False
            return name
    return "ไม่พบฟอนต์ไทย — ตัวอักษรไทยในรูปจะเป็นกล่อง"


def period_axis(ax, periods, label: str = "คาบ (ปี)") -> None:
    """ตั้งแกนคาบให้เป็น log ฐาน 2 · กลับหัว · ป้ายเป็นจำนวนปีอ่านง่าย

    ⚠️ ต้องตั้งป้ายเองแทนที่จะปล่อยให้ matplotlib จัดการ — ตัวจัดรูปแบบของสเกล log
    ใช้ mathtext เขียนเป็น 2^k ซึ่งกลายเป็น **กล่องสี่เหลี่ยม** เมื่อฟอนต์หลักเป็นฟอนต์ไทย
    (เจอจริงตอนรันโน้ตบุ๊ก 02 ครั้งแรก) และ "8 ปี" ก็อ่านง่ายกว่า "2^3" อยู่แล้ว
    """
    ax.set_yscale("log", base=2)
    ticks = [v for v in (0.25, 0.5, 1, 2, 4, 8, 16, 32, 64)
             if periods.min() <= v <= periods.max()]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{v:g}" for v in ticks])
    ax.minorticks_off()
    ax.set_ylim(periods.max(), periods.min())      # คาบสั้นอยู่บน
    ax.set_ylabel(label)


def plain_log_ticks(ax, axis: str = "both") -> None:
    """ป้ายของแกน log เป็นตัวเลขธรรมดา (2, 10, 365, 1e+06) แทน 10^k แบบ mathtext

    ⚠️ ตัวจัดรูปแบบปริยายของแกน log เขียนป้ายด้วย `\\mathdefault{10^{k}}` ซึ่ง mathtext
    **ไม่ fallback ข้ามฟอนต์** ⇒ พอฟอนต์หลักเป็นฟอนต์ไทย ป้ายทั้งแกนกลายเป็นกล่อง
    (เจอสองครั้งแล้ว: รูป coherence ใน W1 และ periodogram ใน W2) — ใช้ฟังก์ชันนี้กับทุกแกน log
    """
    from matplotlib.ticker import FuncFormatter, NullFormatter
    fmt = FuncFormatter(lambda val, _: f"{val:g}")
    axes = {"x": [ax.xaxis], "y": [ax.yaxis], "both": [ax.xaxis, ax.yaxis]}[axis]
    for a in axes:
        a.set_major_formatter(fmt)
        a.set_minor_formatter(NullFormatter())


def plot_coherence(ax, t, periods, R2, coi, phase=None, *, title="",
                   levels=None, arrow_step=(6, 24), sig_mask=None):
    """ระนาบเวลา-คาบของ coherence + เงา COI + (ถ้าให้มา) ลูกศรเฟสและเส้นชั้นนัยสำคัญ

    sig_mask  ให้มาเมื่อมี significance แล้ว (W4) — จะลากเส้นชั้นรอบพื้นที่ที่ผ่านเกณฑ์
    arrow_step (ทุกกี่สเกล, ทุกกี่เดือน) — ถี่เกินไปรูปจะอ่านไม่ออก
    """
    import matplotlib.pyplot as plt

    levels = np.linspace(0, 1, 11) if levels is None else levels
    cf = ax.contourf(t, periods, R2, levels=levels, cmap="viridis", extend="neither")

    if sig_mask is not None:
        ax.contour(t, periods, sig_mask.astype(float), levels=[0.5],
                   colors="white", linewidths=1.6)

    # นอก COI: ถมทับด้วยสีขาวโปร่ง + ลากเส้นขอบกรวย
    ax.fill_between(t, coi, periods.max(), color="white", alpha=0.7, zorder=3)
    ax.plot(t, coi, "k--", lw=1.2, zorder=4)

    if phase is not None:
        si, ti = arrow_step
        T, P = np.meshgrid(t[::ti], periods[::si])
        ph = phase[::si, ::ti]
        inside = P <= np.interp(T, t, coi)
        u, v = np.where(inside, np.cos(ph), np.nan), np.where(inside, np.sin(ph), np.nan)
        ax.quiver(T, P, u, v, scale=25, width=0.0018, color="k", zorder=5)

    period_axis(ax, periods)
    ax.set_xlabel("ปี")
    ax.set_title(title)
    return cf


def plot_filter_response(ax, design, tides: dict | None = None, *, fs_out: float = 1.0):
    """การตอบสนองขนาด (dB) ของ FIR ที่ออกแบบเอง + กรอบสเปก + ตำแหน่งน้ำขึ้นน้ำลง

    กรอบสเปกวาดไว้ในรูปเสมอ — รูปการตอบสนองที่ไม่มีสเปกกำกับบอกไม่ได้ว่าตัวกรอง "ดีพอ" ไหม
    fs_out = อัตราสุ่มหลัง decimate (รอบ/วัน) ⇒ ลากเส้น Nyquist ใหม่ไว้ให้เห็นว่าอะไรจะพับ
    """
    f, H = design.response()
    db = 20 * np.log10(np.maximum(H, 1e-12))
    ax.plot(f, db, lw=1.1, color="C0", label=f"FIR Kaiser {design.numtaps} taps")
    ax.axvspan(0, design.f_pass, color="C2", alpha=0.12, label=f"passband ≤ {design.f_pass:g} cpd")
    ax.axvspan(design.f_stop, f.max(), color="C3", alpha=0.08,
               label=f"stopband ≥ {design.f_stop:g} cpd")
    ax.hlines(-design.atten_db, design.f_stop, f.max(), colors="C3", ls="--", lw=1.2,
              label=f"สเปก −{design.atten_db:g} dB")
    ax.axvline(fs_out / 2, color="k", ls=":", lw=1, label=f"Nyquist ใหม่ {fs_out / 2:g} cpd")
    if tides:
        for name, fr in tides.items():
            ax.axvline(fr, color="0.5", lw=0.6)
            ax.text(fr, 3, name, rotation=90, fontsize=7, ha="center", va="bottom", color="0.3")
    ax.set_xlim(0, min(2.2, f.max()))
    ax.set_ylim(-130, 12)
    ax.set_xlabel("ความถี่ (รอบ/วัน)")
    ax.set_ylabel("|H(f)| (dB)")
    ax.legend(fontsize=7, loc="lower left")


def plot_series(ax, t, y, mask=None, *, label="", color="C0"):
    """อนุกรมเวลา + จุดที่เป็นของเติม (ถ้าส่ง mask มา)

    ของเติมต้องมองเห็นในรูปเสมอ ไม่ใช่กลืนไปกับข้อมูลจริง — มิฉะนั้นเวลาอ่านรูป
    จะแยกไม่ออกว่าช่วงไหนเป็นของที่เราแต่งขึ้นมาเอง
    """
    ax.plot(t, y, lw=0.7, color=color, label=label)
    if mask is not None and mask.any():
        ax.plot(t[mask], y[mask], ".", ms=2.5, color="crimson",
                label=f"ของเติม {mask.sum()} จุด ({mask.mean():.1%})")
    ax.set_xlabel("ปี")
    if label:
        ax.legend(loc="upper left", fontsize=8)
