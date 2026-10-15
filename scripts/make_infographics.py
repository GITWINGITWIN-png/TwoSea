#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle, Ellipse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_figures import COLOR, NAME, PROC, SEAS, save  # noqa: E402
from wtc.plotting import use_thai_font  # noqa: E402

FIGS = {}

# ค่าคงที่ทางภูมิศาสตร์ (ตามนิยาม ไม่ใช่ผล)
STATION_LL = {
    "ko_taphao_noi": (98.433, 7.833),
    "ko_lak": (99.817, 11.800),
    "fort_phrachula_chomklao": (100.583, 13.550),
}
STATION_TH = {"ko_taphao_noi": "เกาะตะเภาน้อย (ภูเก็ต)", "ko_lak": "เกาะหลัก (ประจวบฯ)",
              "fort_phrachula_chomklao": "ป้อมพระจุลฯ"}
BOXES = {
    "nino34": [(190, -5, 240, 5)],
    "dmi": [(50, -10, 70, 10), (90, -10, 110, 0)],
    "wnpmi": [(100, 5, 130, 15), (110, 20, 140, 30)],
}
SOI_POINTS = {"ตาฮิติ": (210.4, -17.55), "ดาร์วิน": (130.84, -12.46)}
ICOL = {"nino34": "#c0392b", "soi": "#c0392b", "dmi": "#7d3c98", "wnpmi": "#1e8449"}
LAND, OCEAN = "#e9e4d8", "#dbe9f4"
DEPTH = (("bathymetry_K_200", "#bcd6ea"), ("bathymetry_J_1000", "#93bcdc"),
         ("bathymetry_H_3000", "#6b9fc9"))
ORDER = ("soi", "dmi", "wnpmi", "nino34", "amo", "tpi", "nao", "pdo")


def figure(fn):
    FIGS[fn.__name__] = fn
    return fn


def load_sens() -> tuple[dict, dict]:
    from wtc.series import VARIANTS
    S, M = {}, {}
    for n in VARIANTS:
        f = PROC / f"sens_{n}.npz"
        if f.exists():
            z = np.load(f, allow_pickle=True)
            S[n], M[n] = json.loads(str(z["summary"])), json.loads(str(z["meta"]))
    return S, M


def base_map(ax, extent, depth=True, borders=True):
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    ax.set_facecolor(OCEAN)
    if depth:
        for name, c in DEPTH:
            ax.add_feature(cfeature.NaturalEarthFeature("physical", name, "10m"),
                           facecolor=c, edgecolor="none", zorder=0.5)
    res = "10m" if depth else "50m"
    ax.add_feature(cfeature.NaturalEarthFeature("physical", "land", res),
                   facecolor=LAND, edgecolor="#8c8475", linewidth=0.4, zorder=1)
    if borders:
        ax.add_feature(cfeature.NaturalEarthFeature("cultural", "admin_0_boundary_lines_land", "50m"),
                       facecolor="none", edgecolor="#a39a8a", linewidth=0.4, linestyle=":", zorder=1.1)


def depth_legend(ax, loc="lower left"):
    from matplotlib.patches import Patch
    hs = [Patch(facecolor=OCEAN, edgecolor="0.6", label="< 200 ม."),
          Patch(facecolor=DEPTH[0][1], edgecolor="0.6", label="200–1,000 ม."),
          Patch(facecolor=DEPTH[1][1], edgecolor="0.6", label="1,000–3,000 ม."),
          Patch(facecolor=DEPTH[2][1], edgecolor="0.6", label="> 3,000 ม.")]
    leg = ax.legend(handles=hs, title="ความลึกของทะเล", loc=loc, fontsize=7.5, title_fontsize=8,
                    framealpha=0.92)
    leg.set_zorder(20)
    return leg


def coastal_arrow(ax, pts, color, lw, alpha=1.0, head=(6, 10), zorder=6):
    import cartopy.crs as ccrs
    pc = ccrs.PlateCarree()
    xs, ys = zip(*pts)
    ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, alpha=alpha, transform=pc, zorder=zorder,
            solid_capstyle="round", solid_joinstyle="round")
    ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], transform=pc, lw=lw, color=color, alpha=alpha, zorder=zorder,
                                 arrowstyle=f"-|>,head_width={head[0]},head_length={head[1]}"))


@figure
def map01_indices():
    import cartopy.crs as ccrs
    pc = ccrs.PlateCarree()
    fig = plt.figure(figsize=(13, 5.0))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(central_longitude=160))
    base_map(ax, (35, 285, -27, 38), depth=False, borders=False)
    ax.gridlines(draw_labels=False, linewidth=0.3, color="0.6", alpha=0.5, xlocs=range(-180, 181, 30),
                 ylocs=range(-30, 41, 15))
    ax.plot([35, 285], [0, 0], color="0.45", lw=0.6, ls="--", transform=pc)

    def box(k, x0, y0, x1, y1, label=None, ha="center", dy=1.2):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, transform=pc, facecolor=ICOL[k], alpha=0.24,
                               edgecolor=ICOL[k], linewidth=1.6, zorder=3))
        if label:
            ax.text((x0 + x1) / 2 if ha == "center" else x0, y1 + dy, label, transform=pc, ha=ha, va="bottom",
                    fontsize=8.5, color=ICOL[k], weight="bold", zorder=6)

    (n34,) = BOXES["nino34"]
    box("nino34", *n34, label="Niño3.4\nอุณหภูมิผิวน้ำแปซิฟิกกลาง (El Niño / La Niña)")
    w, e = BOXES["dmi"]
    box("dmi", *w, label="DMI ฝั่งตะวันตก")
    box("dmi", *e)
    ax.text(100, -10 - 1.4, "DMI ฝั่งตะวันออก\n(นอกฝั่งสุมาตรา–ชวา)", transform=pc, ha="center", va="top",
            fontsize=8.5, color=ICOL["dmi"], weight="bold", zorder=6)
    ax.text(60, -10 - 1.4, "IOD = ผลต่างอุณหภูมิผิวน้ำ\nตะวันตก − ตะวันออก", transform=pc, ha="center",
            va="top", fontsize=7.5, color=ICOL["dmi"], zorder=6)
    s, nb = BOXES["wnpmi"]
    box("wnpmi", *s)
    box("wnpmi", *nb)
    ax.text(nb[2] + 2, (nb[1] + nb[3]) / 2, "WNPMI = ลม 850 hPa\nกล่องใต้ − กล่องเหนือ\n(มรสุมแปซิฟิกตะวันตกเฉียงเหนือ)\nกล่องใต้เริ่มที่ 100°E: ไม่ครอบคลุมอันดามัน",
            transform=pc, ha="left", va="center", fontsize=8.5, color=ICOL["wnpmi"], weight="bold", zorder=6)
    for name, (x, y) in SOI_POINTS.items():
        ax.plot(x, y, marker="*", ms=13, color=ICOL["soi"], mec="k", mew=0.6, transform=pc, zorder=7)
        ax.text(x + 2.5, y - 1.0, name, transform=pc, fontsize=8.5, color=ICOL["soi"], weight="bold",
                va="top", zorder=7)
    ax.plot([130.84, 210.4], [-12.46, -17.55], color=ICOL["soi"], lw=1.0, ls=(0, (4, 3)), transform=pc,
            zorder=4)
    ax.text(170, -17.6, "SOI = ความกดอากาศ ตาฮิติ − ดาร์วิน", transform=pc, ha="center", va="top",
            fontsize=8.5, color=ICOL["soi"], weight="bold", zorder=6)
    for st in SEAS:
        x, y = STATION_LL[st]
        ax.plot(x, y, "o", ms=9, color=COLOR[st], mec="k", mew=1.0, transform=pc, zorder=8)
    ax.annotate("สองทะเลของไทย\n● อันดามัน  ● อ่าวไทย", xy=(99, 10), xycoords=pc._as_mpl_transform(ax),
                xytext=(66, 27), textcoords=pc._as_mpl_transform(ax), fontsize=9, weight="bold",
                ha="center", arrowprops=dict(arrowstyle="->", color="k", lw=1.0), zorder=9,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.5", alpha=0.95))
    ax.text(282, 36, "ไม่อยู่ในแผนที่: PDO / TPI (แปซิฟิกเหนือ–ทั้งแอ่ง, คาบทศวรรษ) · AMO / NAO (แอตแลนติก)",
            transform=pc, ha="right", va="top", fontsize=8, color="0.3", zorder=6,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.75", alpha=0.9))
    ax.set_title("ดัชนีภูมิอากาศแต่ละตัว \"วัด\" อะไร ที่ไหน — สี่ตัวที่สัมพันธ์กับทะเลอันดามัน",
                 fontsize=11, loc="left")
    save(fig, "map01_indices")


@figure
def map02_two_seas():
    import cartopy.crs as ccrs
    pc = ccrs.PlateCarree()
    S, _ = load_sens()
    base = S["baseline"]
    n_var = len(S)
    sig_andaman = [k for k in ORDER if base["ko_taphao_noi"]["bands"]["ทั้งระนาบ"]["single"][k]["p"] < 0.05]
    robust = [k for k in sig_andaman
              if all(S[n]["ko_taphao_noi"]["bands"]["ทั้งระนาบ"]["single"].get(k, {"p": 1})["p"] < 0.05
                     for n in S)]
    gulf_none = all(all(v["p"] >= 0.05 for b in ("ทั้งระนาบ", "2–7 ปี")
                        for v in S[n]["ko_lak"]["bands"][b]["single"].values()) for n in S)

    fig = plt.figure(figsize=(8.6, 9.0))
    ax = fig.add_subplot(1, 1, 1, projection=pc)
    base_map(ax, (90.5, 106.5, 0.5, 17.5))
    ax.text(94.6, 11.9, "ทะเลอันดามัน", transform=pc, fontsize=15, color="#0e3e66", weight="bold",
            ha="center", style="italic", zorder=5)
    ax.text(101.6, 9.4, "อ่าวไทย", transform=pc, fontsize=15, color="#7a4310", weight="bold",
            ha="center", style="italic", zorder=5)
    ax.text(105.2, 4.8, "ทะเลจีนใต้", transform=pc, fontsize=10, color="0.35", ha="center",
            style="italic", zorder=5)
    ax.text(97.3, 3.4, "สุมาตรา", transform=pc, fontsize=9, color="0.35", ha="center", zorder=5)
    ax.text(100.0, 15.6, "ประเทศไทย", transform=pc, fontsize=10, color="0.35", ha="center", zorder=5)
    ax.text(101.6, 8.65, "ลึกเฉลี่ยราว 40 ม.\nแอ่งกึ่งปิดบนไหล่ทวีป", transform=pc, fontsize=8, color="#7a4310",
            ha="center", va="top", zorder=5)
    ax.text(94.6, 11.55, "ส่วนลึกเกิน 1,000–3,000 ม.\nเปิดสู่มหาสมุทรอินเดีย", transform=pc, fontsize=8,
            color="#0e3e66", ha="center", va="top", zorder=5)

    for st, mk, ms in (("ko_taphao_noi", "o", 12), ("ko_lak", "o", 12), ("fort_phrachula_chomklao", "s", 7)):
        x, y = STATION_LL[st]
        ax.plot(x, y, mk, ms=ms, color=COLOR.get(st, "0.5"), mec="k", mew=1.2, transform=pc, zorder=8)
    x, y = STATION_LL["fort_phrachula_chomklao"]
    ax.text(x - 0.3, y + 0.05, "ป้อมพระจุลฯ (หมายเหตุ)", transform=pc, fontsize=7.5, color="0.3",
            va="center", ha="right", zorder=8)

    txt_a = ("อันดามัน · เกาะตะเภาน้อย\n"
             f"สัมพันธ์กับ {' · '.join(NAME[k] for k in robust)}\n"
             f"ผ่านทุก {n_var} แบบทดสอบความไว\n"
             "สัญญาณมาจากเส้นศูนย์สูตร (ENSO–IOD)")
    txt_g = ("อ่าวไทย · เกาะหลัก\n"
             + ("ไม่สัมพันธ์กับดัชนีใดเลย\n" if gulf_none else "มีบางดัชนีเกิน noise บางแบบ\n")
             + f"0 จาก 8 ดัชนี · ทุก {n_var} แบบ\n"
             "ระดับน้ำตอบลมท้องถิ่นทันที")
    for (sx, sy), (tx, ty), txt, st in ((STATION_LL["ko_taphao_noi"], (93.35, 8.35), txt_a, "ko_taphao_noi"),
                                       (STATION_LL["ko_lak"], (104.0, 12.6), txt_g, "ko_lak")):
        ax.annotate(txt, xy=(sx, sy), xycoords=pc._as_mpl_transform(ax), xytext=(tx, ty),
                    textcoords=pc._as_mpl_transform(ax), fontsize=9, ha="center", va="center", zorder=10,
                    bbox=dict(boxstyle="round,pad=0.5", fc="white", ec=COLOR[st], lw=2.0),
                    arrowprops=dict(arrowstyle="-", color=COLOR[st], lw=1.8))

    coastal_arrow(ax, [(96.6, 0.6), (94.8, 4.2), (95.1, 6.0), (97.8, 7.3)], "#c0392b", 3.0,
                  alpha=0.85, head=(5, 8))
    ax.text(94.3, 2.0, "คลื่นเคลวิน\nเลียบชายฝั่ง\nจากศูนย์สูตร", transform=pc, fontsize=9, color="#c0392b",
            weight="bold", ha="right", zorder=7)
    ax.annotate("ช่องแคบมะละกาตื้น\nสัญญาณผ่านเข้าอ่าวไทยได้น้อย", xy=(100.4, 2.9), xycoords=pc._as_mpl_transform(ax),
                xytext=(104.2, 1.6), textcoords=pc._as_mpl_transform(ax), fontsize=7.5, color="0.25",
                ha="center", va="center", zorder=7, arrowprops=dict(arrowstyle="->", color="0.35", lw=0.9),
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.7", alpha=0.85))
    depth_legend(ax, loc="lower right" if False else "upper left")
    ax.set_title("สองทะเล สองคำตอบ", fontsize=13, loc="left", weight="bold")
    save(fig, "map02_two_seas")


@figure
def map03_mechanism():
    import cartopy.crs as ccrs
    pc = ccrs.PlateCarree()
    fig = plt.figure(figsize=(12.5, 6.6))
    ax = fig.add_subplot(1, 1, 1, projection=pc)
    base_map(ax, (42, 128, -14, 24))
    ax.plot([42, 128], [0, 0], color="0.4", lw=0.7, ls="--", transform=pc, zorder=2)
    ax.text(43, 0.4, "เส้นศูนย์สูตร", transform=pc, fontsize=8, color="0.3", zorder=2)
    ax.add_patch(Ellipse((60, -1), 18, 12, transform=pc, fc="#e74c3c", alpha=0.22, ec="none", zorder=2))
    ax.add_patch(Ellipse((101, -5), 18, 10, transform=pc, fc="#2e86c1", alpha=0.25, ec="none", zorder=2))
    ax.text(60, -6.5, "น้ำอุ่นผิดปกติ", transform=pc, ha="center", fontsize=8.5, color="#a93226", zorder=3)
    ax.text(101.5, -9.6, "น้ำเย็น/เทอร์โมไคลน์ยกตัว", transform=pc, ha="center", fontsize=8.5,
            color="#1b4f72", zorder=3)
    for x in (88, 80, 72):
        ax.add_patch(FancyArrowPatch((x + 5.5, 1.6), (x, 1.6), transform=pc,
                                     arrowstyle="-|>,head_width=4,head_length=6", lw=2.2, color="#555",
                                     zorder=5))
    kel = dict(arrowstyle="-|>,head_width=6,head_length=10", lw=4.0, color="#c0392b", zorder=6)
    ax.add_patch(FancyArrowPatch((70, -1.4), (96.8, -1.8), transform=pc, connectionstyle="arc3,rad=0.0", **kel))
    coastal_arrow(ax, [(97.2, -1.2), (95.0, 4.0), (95.0, 6.3), (97.7, 7.7)], "#c0392b", 4.0)
    wg = [(97.6, 9.5), (97.4, 15.5), (94.0, 18.5), (90.5, 22.0), (86.5, 20.5), (82.0, 16.5)]
    for a, b in zip(wg[:-1], wg[1:]):
        ax.add_patch(FancyArrowPatch(a, b, transform=pc, arrowstyle="-|>,head_width=3,head_length=5",
                                     lw=1.4, color="#c0392b", alpha=0.55, ls="--", zorder=5))
    ax.add_patch(FancyArrowPatch((127.5, 5.8), (112.5, 5.8), transform=pc,
                                 arrowstyle="-|>,head_width=5,head_length=8", lw=2.5, color="#7d3c98", zorder=5))
    x, y = STATION_LL["ko_taphao_noi"]
    ax.plot(x, y, "o", ms=12, color=COLOR["ko_taphao_noi"], mec="k", mew=1.2, transform=pc, zorder=9)
    x2, y2 = STATION_LL["ko_lak"]
    ax.plot(x2, y2, "o", ms=12, color=COLOR["ko_lak"], mec="k", mew=1.2, transform=pc, zorder=9)

    def step(n, x, y, text, color="k", ha="left", va="center"):
        ax.text(x, y, f"{n}  {text}", transform=pc, fontsize=9, ha=ha, va=va, ma="left", color=color, zorder=11,
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=color, lw=1.2, alpha=0.95))

    step("②", 43.5, 8.0, "El Niño หรือ IOD บวก → ลมตะวันออกผิดปกติ\nเหนือศูนย์สูตรมหาสมุทรอินเดียตะวันออก", "#333")
    step("③", 66, -10.6, "ลมสร้างคลื่นเคลวินแบบดูดน้ำขึ้น (upwelling)\nวิ่งไปทางตะวันออกตามศูนย์สูตร", "#c0392b")
    step("④", 104.2, 0.2, "ชนสุมาตรา → กลายเป็นคลื่นเคลวินชายฝั่ง\nวิ่งขึ้นเหนือเข้าทะเลอันดามัน\nภายในไม่ถึงสองสัปดาห์",
         "#c0392b")
    step("⑤", 93.4, 9.2, "ระดับน้ำภูเก็ตต่ำลง\n1997–98: ต่ำสุดราว 29 ซม. นาน 7 เดือน\nทช. บันทึกน้ำลงต่ำผิดปกติ 1997 · 2006 · 2019",
         COLOR["ko_taphao_noi"], ha="right", va="bottom")
    ax.annotate("", xy=(x - 0.3, y + 0.3), xycoords=pc._as_mpl_transform(ax), xytext=(93.5, 9.9),
                textcoords=pc._as_mpl_transform(ax),
                arrowprops=dict(arrowstyle="->", color=COLOR["ko_taphao_noi"], lw=1.3), zorder=10)
    step("⑥", 104.5, 19.5, "อ่าวไทย: แอ่งตื้น ระดับน้ำตาม curl ของลม\nท้องถิ่นทันที (r = −0.84, ไม่มีความหน่วง)\nไม่อยู่บนท่อนำคลื่นที่พาสัญญาณมา",
         COLOR["ko_lak"])
    ax.annotate("", xy=(x2 + 0.3, y2 + 0.3), xycoords=pc._as_mpl_transform(ax), xytext=(104.4, 18.3),
                textcoords=pc._as_mpl_transform(ax),
                arrowprops=dict(arrowstyle="->", color=COLOR["ko_lak"], lw=1.3), zorder=10)
    step("①", 127.4, 9.6, "จากแปซิฟิก: El Niño ย้าย Walker circulation\nกิ่งขาลงมาอยู่เหนือทะเลทวีป\n→ เกิดลมตะวันออกในข้อ ②",
         "#7d3c98", ha="right")
    ax.text(89.2, 16.0, "ท่อนำคลื่นรอบอ่าวเบงกอล\n(ทวนเข็มนาฬิกา)", transform=pc, fontsize=7.5, color="#c0392b",
            ha="center", zorder=7, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.75))
    ax.set_title("ทำไมอันดามันขยับตาม ENSO–IOD แต่อ่าวไทยไม่ (ปีที่ El Niño / IOD บวก — ปีตรงข้ามกลับทิศทุกลูกศร)",
                 fontsize=11, loc="left")
    save(fig, "map03_mechanism")


@figure
def fig10_scorecard():
    S, _ = load_sens()
    base = S["baseline"]
    cols = [(st, b) for st in SEAS for b in ("ทั้งระนาบ", "2–7 ปี")]
    fig, ax = plt.subplots(figsize=(8.2, 5.4))
    for j, (st, b) in enumerate(cols):
        for i, k in enumerate(ORDER):
            rec = base[st]["bands"][b]["single"][k]
            n_ok = sum(S[n][st]["bands"][b]["single"].get(k, {"p": 1})["p"] < 0.05
                       for n in S if k in S[n][st]["bands"][b]["single"])
            n_all = sum(k in S[n][st]["bands"][b]["single"] for n in S)
            sig = rec["p"] < 0.05
            strength = min(rec["pasc"] / 35, 1)
            fc = plt.matplotlib.colors.to_rgba(COLOR[st], 0.20 + 0.75 * strength) if sig else "#f1f1f1"
            ax.add_patch(Rectangle((j, i), 1, 1, fc=fc, ec="white", lw=2.5))
            dark = sig and strength > 0.45
            ax.text(j + 0.5, i + 0.40, f"{rec['pasc']:.1f}%" + (" ✓" if sig else ""), ha="center", va="center",
                    fontsize=10.5, weight="bold" if sig else "normal", color="white" if dark else "0.15")
            ax.text(j + 0.5, i + 0.75, f"ผ่าน {n_ok}/{n_all} แบบ", ha="center", va="center", fontsize=7.5,
                    color="white" if dark else "0.45")
    ax.set_xlim(0, len(cols)); ax.set_ylim(len(ORDER), 0)
    ax.set_yticks(np.arange(len(ORDER)) + 0.5); ax.set_yticklabels([NAME[k] for k in ORDER], fontsize=10)
    ax.set_xticks(np.arange(len(cols)) + 0.5)
    ax.set_xticklabels([f"{'อันดามัน' if st == 'ko_taphao_noi' else 'อ่าวไทย'}\n{b}" for st, b in cols], fontsize=9.5)
    ax.xaxis.tick_top()
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    ax.axvline(2, color="0.3", lw=1.5)
    ax.set_title("PASC = สัดส่วนพื้นที่ในระนาบเวลา–คาบที่ coherence เกินระดับ noise 95%\n"
                 "✓ = p < 0.05 ในแบบมาตรฐาน · \"ผ่าน n/8 แบบ\" = จำนวนแบบทดสอบความไวที่ยังได้ p < 0.05",
                 fontsize=9, loc="left", pad=46)
    save(fig, "fig10_scorecard")


def _running(x, w=12, min_real=9):
    ok = np.isfinite(x).astype(float)
    xs = np.where(ok > 0, x, 0.0)
    k = np.ones(w)
    num, den = np.convolve(xs, k, "same"), np.convolve(ok, k, "same")
    return np.where(den >= min_real, num / np.maximum(den, 1), np.nan)


@figure
def fig11_events():
    d = np.load(PROC / "series.npz", allow_pickle=True)
    meta = json.loads(str(d["meta"]))
    t, yn, xn = d["t"], [str(s) for s in d["y_names"]], [str(s) for s in d["x_names"]]
    fig, axes = plt.subplots(2, 1, figsize=(12, 6.4), sharex=True)
    rows = []
    for ax, st in zip(axes, SEAS):
        i = yn.index(st)
        mm = np.where(d["Y_fill"][i], np.nan, d["Y"][i]) * meta["stats"][st]["resid_std"]
        sm = _running(mm)
        ax.fill_between(t, 0, sm, where=sm >= 0, color="#2e86c1", alpha=0.55, lw=0, interpolate=True)
        ax.fill_between(t, 0, sm, where=sm < 0, color="#c0392b", alpha=0.55, lw=0, interpolate=True)
        ax.plot(t, sm, color="k", lw=0.6)
        gaps = d["Y_fill"][i]
        ax.fill_between(t, -1, 1, where=gaps, transform=ax.get_xaxis_transform(), color="0.85", lw=0, zorder=0)
        ax.set_ylabel("ระดับน้ำผิดปกติ (มม.)\nเฉลี่ย 12 เดือน")
        ax2 = ax.twinx()
        r_txt = []
        for k, c in (("nino34", "#7b241c"), ("dmi", "#6c3483")):
            x = -_running(d["X"][xn.index(k)])
            ax2.plot(t, x, color=c, lw=1.1, alpha=0.9, label=f"−{NAME[k]} (กลับด้าน)")
            ok = np.isfinite(sm) & np.isfinite(x)
            r = np.corrcoef(sm[ok], x[ok])[0, 1]
            r_txt.append(f"r(−{NAME[k]}) = {r:+.2f}")
            rows.append((st, k, r))
        ax2.set_ylabel("ดัชนี กลับด้าน (SD)"); ax2.set_ylim(-3, 3)
        lim = np.nanmax(np.abs(sm)) * 1.15
        ax.set_ylim(-lim, lim)
        ax.axhline(0, color="k", lw=0.5)
        ax.set_title(f"{'ทะเลอันดามัน · เกาะตะเภาน้อย' if st == 'ko_taphao_noi' else 'อ่าวไทย · เกาะหลัก'}"
                     f"   ({' · '.join(r_txt)} จากค่าเฉลี่ย 12 เดือน — บรรยาย ไม่ใช่การทดสอบ)",
                     loc="left", fontsize=9.5)
        if st == "ko_taphao_noi":
            ax2.legend(loc="upper left", fontsize=8, ncol=2, framealpha=0.9)
            for yr, txt in ((1997.8, "1997–98\nIOD บวก + El Niño"), (2006.8, "2006\nIOD บวก"),
                            (2019.8, "2019\nIOD บวก")):
                ax.annotate(txt, xy=(yr, -lim * 0.62), xytext=(yr, -lim * 0.97), ha="center", va="bottom",
                            fontsize=7.5, color="#7b241c",
                            arrowprops=dict(arrowstyle="-", color="#7b241c", lw=0.8))
    axes[-1].set_xlabel("ปี")
    fig.suptitle("ระดับน้ำทะเลระหว่างปี (ตัดแนวโน้มและฤดูกาลแล้ว) — แดง = ต่ำกว่าปกติ · น้ำเงิน = สูงกว่าปกติ · "
                 "แถบเทา = ช่วงไม่มีข้อมูล", fontsize=10, y=0.995)
    fig.tight_layout()
    save(fig, "fig11_events")
    for st, k, r in rows:
        print(f"     r {st:14s} vs −{k:6s} = {r:+.2f}")


EXPECTED = {"soi": (-30, 30, "หนักแน่น"), "nino34": (150, 210, "หนักแน่น"),
            "dmi": (150, 210, "หนักแน่น"), "wnpmi": (0, 60, "อนุมาน")}


@figure
def fig12_phase():
    r = np.load(PROC / "wtc_q1.npz", allow_pickle=True)
    st_, ix = [str(s) for s in r["stations"]], [str(s) for s in r["indices"]]
    per = r["periods"]; band = (per >= 2) & (per <= 7)
    si = st_.index("ko_taphao_noi")
    fig, axes = plt.subplots(1, 4, figsize=(14, 4.2), subplot_kw=dict(projection="polar"))
    fig.subplots_adjust(wspace=0.55)
    out = {}
    for ax, k in zip(axes, ("soi", "nino34", "dmi", "wnpmi")):
        xi = ix.index(k)
        m = r["sig"][si, xi] & r["valid"][si, xi] & band[:, None]
        th = r["phase"][si, xi][m].astype(float)
        P = (per[:, None] * np.ones(m.shape))[m]
        z = np.exp(1j * th).mean(); ang = np.angle(z)
        lo, hi, conf = EXPECTED[k]
        ax.bar(np.radians((lo + hi) / 2), 1.0, width=np.radians(hi - lo), color=ICOL[k], alpha=0.18,
               hatch=None if conf == "หนักแน่น" else "///", edgecolor=ICOL[k], lw=0.0)
        hist, edges = np.histogram(th, bins=36, range=(-np.pi, np.pi))
        ax.bar((edges[:-1] + edges[1:]) / 2, 0.85 * hist / hist.max(), width=2 * np.pi / 36, color="0.55",
               alpha=0.45)
        ax.annotate("", xy=(ang, abs(z)), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.5,head_length=0.9", color="k", lw=2.4))
        ax.set_ylim(0, 1); ax.set_yticks([])
        ax.set_xticks(np.radians([0, 90, 180, 270]))
        ax.set_xticklabels(["ไป\nด้วยกัน", "ระดับน้ำนำ", "สวน\nทาง", "ดัชนีนำ"], fontsize=8)
        deg = np.degrees(ang)
        ref = 0 if abs(deg) < 90 else (180 if deg > 0 else -180)
        lag = (deg - ref) / 360 * np.median(P) * 12
        ok = lo <= (deg if deg > -90 or lo < 0 else deg + 360) <= hi
        rel = "ระดับน้ำนำ" if lag > 0 else "ระดับน้ำตาม"
        out[k] = dict(theta=deg, R=abs(z), lag=lag, period=float(np.median(P)), inside=bool(ok))
        ax.set_title(f"{NAME[k]}\nθ = {deg:+.0f}° · {rel} ~{abs(lag):.0f} เดือน\n"
                     f"{'✓ ตรงทิศที่คาด' if ok else '✗ ไม่ตรงทิศที่คาด'} ({conf})", fontsize=9, pad=14,
                     color="#1e6b34" if ok else "#a93226")
    fig.suptitle("ทิศของความสัมพันธ์ที่อันดามัน (แถบ 2–7 ปี เฉพาะบริเวณมีนัยสำคัญ) — ลูกศรดำ = ทิศเฉลี่ย "
                 "(ยาว = สม่ำเสมอ) · พื้นสี = ทิศที่กลไกคาด (ลายเส้น = อนุมาน) · เทา = การกระจายของมุม",
                 fontsize=9.5, y=1.13)
    save(fig, "fig12_phase")
    (PROC / "phase_summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    for k, v in out.items():
        print(f"     {k:7s} θ={v['theta']:+6.1f}° R={v['R']:.2f} lag={v['lag']:+.1f} mo inside={v['inside']}")


def robustness_rows(S):
    A, G = "ko_taphao_noi", "ko_lak"
    one = lambda n, st, b: S[n][st]["bands"][b]
    top = lambda n, b: max(one(n, A, b)["single"].items(), key=lambda kv: kv[1]["pasc"])[0]
    return [
        ("อันดามันสัมพันธ์กับดัชนีภูมิอากาศ (ดัชนีเดี่ยว p < 0.05)",
         lambda n: 2 if any(v["p"] < 0.05 for v in one(n, A, "ทั้งระนาบ")["single"].values()) else 0),
        ("อ่าวไทยไม่มีดัชนีเดี่ยวใดเกิน noise",
         lambda n: 2 if all(v["p"] >= 0.05 for b in ("ทั้งระนาบ", "2–7 ปี")
                            for v in one(n, G, b)["single"].values()) else 0),
        ("SOI · DMI · WNPMI · Niño3.4 เกิน noise ทั้งสี่ตัว",
         lambda n: 2 if all(one(n, A, "ทั้งระนาบ")["single"][k]["p"] < 0.05
                            for k in ("soi", "dmi", "wnpmi", "nino34")) else 0),
        ("ดัชนีเดียวพอ (ทั้งระนาบ)", lambda n: 2 if one(n, A, "ทั้งระนาบ")["q_enough"] == 1 else 0),
        ("ดัชนีเดียวพอ (แถบ 2–7 ปี)", lambda n: 2 if one(n, A, "2–7 ปี")["q_enough"] == 1 else 0),
        ("WNPMI อันดับหนึ่งในแถบ 2–7 ปี",
         lambda n: (2 if top(n, "2–7 ปี") == "wnpmi" else 0)),
        ("ดัชนีภูมิภาคเพิ่มอำนาจอธิบาย (Q5, แถบ 2–7 ปี)",
         lambda n: (2 if one(n, A, "2–7 ปี")["q5_gain"]["p"] < 0.05
                    else 1 if one(n, A, "2–7 ปี")["q5_gain"]["p"] < 0.10 else 0)),
    ]


@figure
def fig13_robustness():
    S, M = load_sens()
    names = list(S)
    rows = robustness_rows(S)
    col = {2: "#27ae60", 1: "#f1c40f", 0: "#e74c3c"}
    sym = {2: "✓", 1: "~", 0: "✗"}
    fig, ax = plt.subplots(figsize=(12.5, 4.6))
    for i, (label, f) in enumerate(rows):
        vals = [f(n) for n in names]
        for j, v in enumerate(vals):
            ax.add_patch(plt.Circle((j + 0.5, i + 0.5), 0.33, fc=col[v], ec="white", lw=1.5))
            ax.text(j + 0.5, i + 0.5, sym[v], ha="center", va="center", color="white", fontsize=11, weight="bold")
        n_ok = sum(v == 2 for v in vals)
        ax.text(len(names) + 0.2, i + 0.5, f"{n_ok}/{len(names)}", va="center", fontsize=11, weight="bold",
                color="#1e6b34" if n_ok == len(names) else "#9a7d0a" if n_ok >= len(names) / 2 else "#a93226")
    ax.set_xlim(0, len(names) + 1.0); ax.set_ylim(len(rows), 0); ax.set_aspect("equal")
    ax.set_yticks(np.arange(len(rows)) + 0.5); ax.set_yticklabels([r[0] for r in rows], fontsize=9.5)
    ax.set_xticks(np.arange(len(names)) + 0.5)
    ax.set_xticklabels([M[n]["label"] for n in names], rotation=35, ha="left", fontsize=8.5)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("ข้อสรุปไหนอยู่รอดเมื่อเปลี่ยนวิธีเตรียมข้อมูล — เขียว = ผ่าน · เหลือง = ก้ำกึ่ง (p < 0.10) · แดง = ไม่ผ่าน",
                 fontsize=10, loc="left", y=-0.12)
    save(fig, "fig13_robustness")


KTN_EVENTS = [
    (1988.5, "PSMSL ยก datum 14 มม.", 0, "right"),
    (2004.98, "แผ่นดินไหว/สึนามิ\n26 ธ.ค. 2004", 0, "left"),
    (2005.78, "UHSLC เปลี่ยนไปใช้\nเรดาร์ของตัวเอง\n12 ต.ค. 2005", 1, "right"),
    (2012.25, "UHSLC บวก +10 ซม.\nให้ข้อมูลก่อน\n1 เม.ย. 2012", 0, "left"),
    (2013.55, "แท่นวัดถูกทำลาย\nก.ค. 2013", 1, "right"),
    (2016.17, "แท่นใหม่\nมี.ค. 2016", 0, "right"),
]


@figure
def fig14_ktn_datum():
    from wtc.loaders import read_psmsl
    from wtc.qc import apply_exclusions
    from wtc.series import RAW, q7_monthly
    tp, vp = read_psmsl(RAW / "psmsl" / "ko_taphao_noi_monthly.rlrdata")
    vp, _ = apply_exclusions("ko_taphao_noi", tp, vp)
    tu, vu = q7_monthly("ko_taphao_noi")
    key = lambda t: np.round((np.asarray(t) - 1 / 24) * 12).astype(int)
    up = dict(zip(key(tu), vu))
    diff = np.array([v - up.get(k, np.nan) for k, v in zip(key(tp), vp)])
    ref = np.nanmedian(diff[(tp >= 1990) & (tp < 2004)])
    diff = diff - ref
    keep = np.isfinite(diff)
    t, dd = tp[keep], diff[keep]
    fig, ax = plt.subplots(figsize=(12, 4.3))
    ax.axvspan(2005.78, 2020, color="#fdebd0", zorder=0)
    ax.scatter(t, dd, s=7, color="#1f6fb4", zorder=3, label="รายเดือน")
    yy = np.arange(int(t.min()), int(t.max()) + 1)
    med = [np.nanmedian(dd[(t >= y) & (t < y + 1)]) if ((t >= y) & (t < y + 1)).sum() >= 6 else np.nan for y in yy]
    ax.step(yy, med, where="post", color="k", lw=1.6, zorder=4, label="มัธยฐานรายปี")
    ax.axhline(0, color="0.4", lw=0.8)
    ylo, yhi = -150, 330
    for x, lab, tier, side in KTN_EVENTS:
        ax.axvline(x, color="#a93226", lw=1.0, ls="--", zorder=2)
        ax.text(x + (0.15 if side == "right" else -0.15), yhi - 5 - 75 * tier, lab, fontsize=7.3,
                color="#7b241c", va="top", ha="left" if side == "right" else "right", zorder=5,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    ax.set_ylim(ylo, yhi); ax.set_xlim(1984.5, 2020.2)
    ax.set_xlabel("ปี"); ax.set_ylabel("PSMSL − UHSLC (มม.)\nจัดศูนย์ที่ช่วง 1990–2003")
    ax.text(1985.0, ylo + 12, "ตรงกันระดับมิลลิเมตรจนถึงปี 2005", fontsize=9, color="#1e6b34", weight="bold")
    ax.text(2006.2, ylo + 12, "สองแหล่งแยกทาง: คนละเครื่องมือ · คนละการแก้ datum", fontsize=9, color="#a93226",
            weight="bold")
    ax.legend(loc="center left", fontsize=8)
    ax.set_title("สถานีเดียวกัน สองคลังข้อมูล — ผลต่างหลังปี 2005 มาจากเครื่องมือและ datum ที่มีเอกสารยืนยัน "
                 "(การทรุดตัวหลังแผ่นดินไหวหักล้างกันในผลต่าง)", fontsize=9.5, loc="left")
    save(fig, "fig14_ktn_datum")
    pre = dd[(t >= 1990) & (t < 2004)]
    late = dd[(t >= 2015) & (t < 2020)]
    print(f"     1990–2003: median {np.median(pre):+.1f} mm, MAD {np.median(np.abs(pre)):.1f} · "
          f"2015–2019: median {np.median(late):+.1f} mm")


def main() -> int:
    use_thai_font()
    want = sys.argv[1:]
    for name, fn in FIGS.items():
        if not want or any(name.startswith(w) for w in want):
            fn()
    return 0


if __name__ == "__main__":
    sys.exit(main())
