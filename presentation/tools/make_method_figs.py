"""รูปข้อมูลจริงสไตล์ D สำหรับหน้าวิธีที่ยังเป็นรูปรายงาน — วาดใหม่จากข้อมูลและโค้ดของโครงงาน DSP (อ่านอย่างเดียว)

    PYTHONDONTWRITEBYTECODE=1 ../.venv/bin/python tools/make_method_figs.py

หน้าที่ใช้ (ผล: deck/public/plots/*.png · ไม่อยู่ใน git):
  SQ03_S010  layer_hourly/season/inter/trend.png  ระดับน้ำรายชั่วโมงจริง 7 วัน + ชั้นฤดูกาล / ระหว่างปี / แนวโน้มระยะยาว (แกน มม.)
  SQ03_S020  spectrum_hourly.png                สเปกตรัมจริง (FFT) ของระดับน้ำรายชั่วโมงหนึ่งปี
  SQ03_S060  prep_raw.png · prep_resid.png         อ่าวไทยรายเดือนดิบ + เส้น fit → residual
  SQ05_S030  power_plain.png · power_coi.png       ระนาบกำลังเวฟเล็ตของอันดามัน ไม่มี / มีกรวยอิทธิพล
  SQ07_S010  noise_pair.png · noise_wtc.png · noise_thr.png   AR(1) หนึ่งคู่ · WTC ของมัน · เกณฑ์ 95% ตามคาบ
ใช้ฟังก์ชันของโครงงานเอง (wtc.preprocess / transform / coherence / significance) — ไม่เขียนวิธีซ้ำ
ข้อความอธิบายอยู่ใน HTML ของหน้า · ในรูปมีแค่แกนและตัวเลขบนแกน
"""

import sys
from pathlib import Path

import numpy as np
from matplotlib.ticker import MaxNLocator

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_wtc_fig import CMAP, DSP, INK, INK2, INK3, OUT, plt  # noqa: E402 — สี/ฟอนต์/โฟลเดอร์ชุดเดียวกับรูป WTC

sys.path.insert(0, str(DSP))
from wtc import coherence, preprocess, significance, transform  # noqa: E402
from wtc.loaders import read_psmsl, read_uhslc_grid  # noqa: E402

ANDAMAN, GULF, GREY = "#2F74C0", "#D9822B", "#8FA1AB"
PROC = DSP / "data" / "processed"


def canvas(w, h, left=0.055, right=0.995, top=0.95, bottom=0.2):
    """รูปขนาดพิกเซลจริงบนจอ 1920×1080 (100 dpi) · ตัวอักษรแกน 17 pt ≈ 24 px"""
    fig, ax = plt.subplots(figsize=(w / 100, h / 100), dpi=100)
    fig.subplots_adjust(left=left, right=right, top=top, bottom=bottom)
    ax.tick_params(colors=INK2, labelsize=17, length=5)
    for s in ax.spines.values():
        s.set_color("#C9D6DC")
    ax.spines[["top", "right"]].set_visible(False)
    return fig, ax


def xtitle(ax, text):
    """ชื่อแกนนอน (ผู้ใช้ 10-15: ทุกกราฟต้องมีชื่อแกน x และ y)"""
    ax.set_xlabel(text, color=INK2, fontsize=16, labelpad=4)


def xtitle_end(ax, text):
    """ชื่อแกนนอนแบบประหยัดที่: วางปลายขวาของแถวตัวเลขแกน (ไม่เพิ่มความสูงรูป) — ใช้กับรูปสี่ชั้นของ SQ03_S010
    ที่ความสูงรวมเต็มการ์ดพอดี · ต้องเว้นที่ว่างปลายขวาไว้ (ไม่มีขีดชิดขอบขวา)"""
    ax.annotate(text, xy=(1, 0), xycoords="axes fraction", xytext=(-6, -9), textcoords="offset points",
                ha="right", va="top", color=INK2, fontsize=15, fontweight="bold")


def ytitle(ax, text):
    """ชื่อแกนตั้งแบบแนวนอน วางเหนือแกนชิดซ้าย — ตัวไทยหมุนแนวตั้งอ่านยาก (เคยเห็น "มม." เป็น "uu.")
    รูปที่ใช้ต้องเผื่อขอบบน (top ≤ ~0.88)"""
    ax.text(0, 1.03, text, transform=ax.transAxes, ha="left", va="bottom", color=INK2, fontsize=16)


def save(fig, name):
    fig.savefig(OUT / name, facecolor="white")
    plt.close(fig)
    print(OUT / name)


def fit_parts(t, y):
    """แยกเป็นแนวโน้ม + ฤดูกาล (ฮาร์มอนิก 1 ปี และ 1/2 ปี) ด้วยเมทริกซ์ออกแบบของโครงงาน · fit เฉพาะจุดที่มีข้อมูล"""
    X = preprocess._design(t)
    ok = np.isfinite(y)
    beta, *_ = np.linalg.lstsq(X[ok], y[ok], rcond=None)
    trend = X[:, :2] @ beta[:2]
    season = X[:, 2:] @ beta[2:]
    return trend, season


def raw_monthly(station, t):
    """ระดับน้ำรายเดือนดิบของ PSMSL (มม.) บนกริดเวลาเดียวกับ series.npz — ช่องว่าง = NaN
    (series.npz เก็บอนุกรมที่ผ่าน detrend_deseason + เติมช่องว่าง + normalize แล้ว ใช้แสดงขั้นเตรียมสัญญาณไม่ได้)"""
    tr, vr = read_psmsl(DSP / "data" / "raw" / "psmsl" / f"{station}_monthly.rlrdata")
    out = np.full(t.size, np.nan)
    idx = np.rint((tr - t[0]) * 12).astype(int)   # เทียบเป็นลำดับเดือน — ปีทศนิยมของสองแหล่งปัดต่างกันเล็กน้อย
    ok = (idx >= 0) & (idx < t.size) & np.isfinite(vr)
    out[idx[ok]] = vr[ok]
    return out


def running12(y):
    k = np.ones(12) / 12
    ok = np.isfinite(y).astype(float)
    num = np.convolve(np.nan_to_num(y), k, "same")
    den = np.convolve(ok, k, "same")
    out = num / np.where(den > 0.6, den, np.nan)
    return out


# --- SQ03_S010: หลายจังหวะซ้อนกัน ------------------------------------------------------------------------------
# สี่ชั้นเป็นรูปแยกกัน กว้าง 1400 px เท่าที่วางบนหน้า (ไม่ย่อ → ตัวอักษรแกนขนาดจริง) และขอบซ้ายเท่ากันทุกรูป → แกนเวลาตรงกัน
# ทุกชั้นมีแกน y หน่วย มม. (ผู้ใช้ 10-14: เดิมไม่มีหน่วยเลย)
LAYER_W, LAYER_LEFT = 1400, 0.1


def layer_canvas(h, bottom):
    fig, ax = canvas(LAYER_W, h, left=LAYER_LEFT, right=0.99, top=0.93, bottom=bottom)
    ax.tick_params(labelsize=15)
    ax.set_ylabel("มม.", color=INK2, fontsize=16, rotation=0, ha="right", va="center", labelpad=8)   # แนวนอน: "มม." ตะแคงอ่านยาก
    ax.yaxis.set_major_locator(MaxNLocator(nbins=3, symmetric=True))   # ขีดบวก/ศูนย์/ลบ ให้เห็นทั้งสองข้าง
    ax.axhline(0, color="#DCE6EA", lw=1.2, zorder=0)
    return fig, ax


def gap_spans(t, ok, min_months=6):
    """ช่วงที่ไม่มีข้อมูลติดกันอย่างน้อย min_months เดือน → [(ปีเริ่ม, ปีจบ)] ไว้แรเงาในรูป"""
    spans, i = [], 0
    while i < t.size:
        if not ok[i]:
            j = i
            while j < t.size and not ok[j]:
                j += 1
            if j - i >= min_months:
                spans.append((t[i], t[min(j, t.size - 1)]))
            i = j
        else:
            i += 1
    return spans


def layers(t, Y):
    th, vh = read_uhslc_grid(DSP / "data" / "raw" / "uhslc" / "ko_taphao_noi_hourly.csv")
    start = np.datetime64("2010-03-01T00")
    sel = (th >= start) & (th < start + np.timedelta64(7 * 24, "h"))
    hours = (th[sel] - start).astype(int) / 24.0
    fig, ax = layer_canvas(200, bottom=0.24)
    ax.plot(hours, vh[sel] - np.nanmean(vh[sel]), color=INK, lw=2.2)
    ax.set_xlim(0, 7)
    ax.set_xticks(range(7))                             # ไม่ใส่ขีด 7 — ปลายขวาเป็นที่ของชื่อแกน
    xtitle_end(ax, "เวลา (วัน)")
    save(fig, "layer_hourly.png")

    y = raw_monthly("ko_taphao_noi", t)        # เกาะตะเภาน้อย รายเดือนดิบ (มม.)
    trend, season = fit_parts(t, y)
    resid = running12(y - trend - season)
    decades = list(range(1960, 2030, 10))

    # ฤดูกาลวาดจากสูตรฮาร์มอนิกบนกริดละเอียด (ไม่ใช่จุดรายเดือน) ให้เห็นเป็นคลื่นเรียบ
    tf = np.linspace(2005, 2009, 600)
    ok = np.isfinite(y)
    beta, *_ = np.linalg.lstsq(preprocess._design(t)[ok], y[ok], rcond=None)
    season_f = preprocess._design(np.concatenate([t, tf]))[t.size:, 2:] @ beta[2:]
    fig, ax = layer_canvas(150, bottom=0.25)
    ax.plot(tf, season_f, color=GREY, lw=2.4)
    ax.set_xlim(2005, 2009)
    ax.set_xticks([2005, 2006, 2007, 2008])            # ไม่ใส่ 2009 ที่ขอบขวา (ป้ายล้นรูป · ที่ของชื่อแกน)
    xtitle_end(ax, "ปี")
    save(fig, "layer_season.png")

    # ระหว่างปี = ค่าเฉลี่ย 12 เดือนของส่วนที่เหลือ · ช่วงที่ไม่มีข้อมูล (PSMSL ไม่มีค่า) แรเงาเทา ไม่เติม
    fig, ax = layer_canvas(170, bottom=0.22)
    for a, b in gap_spans(t, np.isfinite(resid)):
        ax.axvspan(a, b, color="#E6ECEF", zorder=0, lw=0)
    ax.plot(t, resid, color=ANDAMAN, lw=2.4)
    ax.fill_between(t, resid, 0, color=ANDAMAN, alpha=0.18)
    ax.set_xlim(t[0], t[-1])
    ax.set_xticks(decades)
    xtitle_end(ax, "ปี")
    save(fig, "layer_inter.png")

    # แนวโน้มเชิงเส้นระยะยาวของระดับน้ำ (วัดจากค่าเฉลี่ยทั้งช่วง)
    fig, ax = layer_canvas(150, bottom=0.25)
    ax.plot(t, trend - trend.mean(), color=GREY, lw=2.4)
    ax.set_xlim(t[0], t[-1])
    ax.set_xticks(decades)
    xtitle_end(ax, "ปี")
    save(fig, "layer_trend.png")


# --- SQ03_S020: สเปกตรัมจริงของระดับน้ำรายชั่วโมง ------------------------------------------------------------------
def spectrum():
    """periodogram (หน้าต่าง Hann + FFT) ของระดับน้ำรายชั่วโมงจริงหนึ่งปีเต็ม (เกาะตะเภาน้อย 2010 · ไม่มีช่องว่าง)
    ยอดที่ราว 1 และ 2 รอบต่อวันคือน้ำขึ้นน้ำลงในข้อมูลจริง — อยู่นอกช่วงที่การสุ่มวันละครั้งจับได้ (≤ 0.5 รอบต่อวัน)
    แกน x = รอบต่อวัน 0–2.5 · แกน y = กำลัง (dB เทียบยอดสูงสุด) · ป้ายกลุ่มน้ำขึ้นน้ำลง / Nyquist อยู่ใน HTML ของหน้า"""
    th, vh = read_uhslc_grid(DSP / "data" / "raw" / "uhslc" / "ko_taphao_noi_hourly.csv")
    sel = (th >= np.datetime64("2010-01-01T00")) & (th < np.datetime64("2011-01-01T00"))
    x = vh[sel] - vh[sel].mean()
    assert np.isfinite(x).all(), "ปี 2010 ต้องไม่มีช่องว่าง"
    X = np.fft.rfft(x * np.hanning(x.size))
    f = np.fft.rfftfreq(x.size, d=1 / 24)      # รอบต่อวัน (สุ่มชั่วโมงละครั้ง = 24 ครั้งต่อวัน)
    P = 10 * np.log10(np.abs(X) ** 2 + 1e-12)
    P -= P.max()
    keep = f <= 2.5
    fig, ax = canvas(1600, 290, left=0.075, right=0.985, top=0.95, bottom=0.2)
    ax.axvspan(0, 0.5, color=ANDAMAN, alpha=0.16, lw=0, zorder=0)
    ax.axvline(0.5, color=ANDAMAN, lw=3, ls=(0, (5, 4)))
    ax.plot(f[keep], P[keep], color=INK, lw=1.1)
    ax.set_xlim(0, 2.5)
    ax.set_ylim(-100, 5)
    ax.set_xticks([0, 0.5, 1, 1.5, 2, 2.5])
    ax.set_xticklabels(["0", "0.5", "1", "1.5", "2", "2.5"])
    ax.set_yticks([-100, -50, 0])
    ax.set_ylabel("กำลัง (dB)", color=INK2, fontsize=17)
    save(fig, "spectrum_hourly.png")


# --- SQ03_S060: เตรียมสัญญาณ (อ่าวไทย) --------------------------------------------------------------------------
def prep(t, Y):
    y = raw_monthly("ko_lak", t)               # เกาะหลัก (อ่าวไทย) รายเดือนดิบ
    trend, season = fit_parts(t, y)
    fig, ax = canvas(1700, 310, top=0.86, bottom=80 / 310)
    ax.plot(t, y - np.nanmean(y), color=GULF, lw=1.2)
    ax.plot(t, trend + season - np.nanmean(y), color=INK, lw=1.6, alpha=0.85)
    ax.set_xlim(t[0], t[-1])
    ax.set_xticks(range(1960, 2030, 10))
    ytitle(ax, "ระดับน้ำ (มม.)")
    xtitle(ax, "ปี")
    save(fig, "prep_raw.png")
    fig, ax = canvas(1700, 310, top=0.86, bottom=80 / 310)
    r = y - trend - season
    ax.axhline(0, color="#DCE6EA", lw=1.2, zorder=0)
    ax.plot(t, r, color=GULF, lw=1.2)
    ax.set_xlim(t[0], t[-1])
    ax.set_ylim(*ax.get_ylim())
    ax.set_xticks(range(1960, 2030, 10))
    ytitle(ax, "ระดับน้ำที่เหลือ (มม.)")
    xtitle(ax, "ปี")
    save(fig, "prep_resid.png")


# --- SQ05_S030: ระนาบกำลังเวฟเล็ต (อันดามัน) ---------------------------------------------------------------------
def plane_axes(ax, per):
    ax.set_yscale("log", base=2)
    ax.set_ylim(per.max(), per.min())
    ax.set_yticks([0.5, 1, 2, 4, 8, 16, 32])
    ax.set_yticklabels(["0.5", "1", "2", "4", "8", "16", "32"])
    ax.set_xticks(range(1960, 2030, 10))
    ax.set_ylabel("คาบ (ปี)", color=INK2, fontsize=17)


def power(t, Y):
    z = Y[0]                                   # อนุกรมที่สายประมวลผลป้อนเข้า CWT จริง (เตรียม + เติมช่องว่าง + normalize แล้ว)
    W, scales, per, coi = transform.cwt(z)
    keep = per <= 40
    P = np.log2(np.abs(W[keep]) ** 2 + 1e-6)
    levels = np.linspace(np.percentile(P, 5), np.percentile(P, 99.5), 12)
    for name, with_coi in (("power_plain.png", False), ("power_coi.png", True)):
        fig, ax = canvas(1700, 560, top=0.98, bottom=0.15)
        ax.contourf(t, per[keep], P, levels=levels, cmap=CMAP, extend="both")
        if with_coi:
            ax.fill_between(t, coi, per[keep].max(), color="white", alpha=0.78, zorder=3)
            ax.plot(t, coi, "--", color=INK, lw=2.4, zorder=4)
        plane_axes(ax, per[keep])
        ax.set_xlim(t[0], t[-1])
        xtitle(ax, "ปี")
        ax.spines[["top", "right"]].set_visible(True)
        save(fig, name)


# --- SQ07_S010: noise สองตัวที่ไม่เกี่ยวกัน --------------------------------------------------------------------
def noise(t):
    r = np.load(PROC / "wtc_q1.npz", allow_pickle=True)
    si = [str(s) for s in r["stations"]].index("ko_taphao_noi")
    xi = [str(s) for s in r["indices"]].index("soi")
    a_y, a_x = float(r["a_y"][si, xi]), float(r["a_x"][si, xi])
    rng = np.random.default_rng(7)             # เลือก seed ที่ให้ก้อนชัด เพื่ออธิบาย (คู่ใดก็สร้างก้อนได้)
    y = significance.ar1_surrogate(t.size, a_y, 1.0, rng)
    x = significance.ar1_surrogate(t.size, a_x, 1.0, rng)
    fig, ax = canvas(1700, 250, bottom=90 / 250, top=0.85)
    ax.plot(t, y + 3.2, color=INK3, lw=1.3)
    ax.plot(t, x - 3.2, color=INK, lw=1.3)
    ax.set_xlim(t[0], t[-1]); ax.set_yticks([]); ax.set_xticks(range(1960, 2030, 10))
    ax.spines["left"].set_visible(False)
    ytitle(ax, "ค่าที่สุ่มได้ (ไม่มีหน่วย สองเส้นวางเหลื่อมกัน)")
    xtitle(ax, "ปี")
    save(fig, "noise_pair.png")

    Wy, scales, per, coi = transform.cwt(y)
    Wx, *_ = transform.cwt(x)
    R2, _ = coherence.wtc(Wx, Wy, transform.DT_MONTHLY, transform.DJ, scales)
    thr = r["threshold"][si, xi]
    keep = per <= 40
    fig, ax = canvas(1100, 400, top=0.97, bottom=0.2, left=0.085)
    ax.contourf(t, per[keep], R2[keep], levels=np.linspace(0, 1, 11), cmap=CMAP)
    ax.fill_between(t, coi, per[keep].max(), color="white", alpha=0.72, zorder=3)
    ax.plot(t, coi, "--", color=INK2, lw=1.6, zorder=4)
    plane_axes(ax, per[keep])
    ax.set_xlim(t[0], t[-1]); ax.set_xticks(range(1960, 2030, 20))
    xtitle(ax, "ปี")
    ax.spines[["top", "right"]].set_visible(True)
    save(fig, "noise_wtc.png")

    rp = r["periods"]
    fig, ax = canvas(560, 400, top=0.86, bottom=0.2, left=0.2, right=0.93)
    ok = np.isfinite(thr) & (rp <= 40)
    ax.plot(rp[ok], thr[ok], color="#C0392B", lw=3)
    ax.set_xscale("log", base=2)
    ax.set_xticks([0.5, 2, 8, 32]); ax.set_xticklabels(["0.5", "2", "8", "32"])
    ax.set_ylim(0, 1); ax.set_yticks([0, 0.5, 1])
    ax.set_xlabel("คาบ (ปี)", color=INK2, fontsize=17)
    ytitle(ax, "เกณฑ์ coherence 95%")
    save(fig, "noise_thr.png")


def main():
    d = np.load(PROC / "series.npz", allow_pickle=True)
    t, Y = d["t"], d["Y"]
    OUT.mkdir(parents=True, exist_ok=True)
    layers(t, Y)
    spectrum()
    prep(t, Y)
    power(t, Y)
    noise(t)


if __name__ == "__main__":
    main()
