#!/usr/bin/env python3
"""รูปสุดท้ายสำหรับรายงาน — วาดจากไฟล์ผลใน data/processed/ เท่านั้น ไม่คำนวณผลใหม่

    uv run python scripts/make_figures.py            # ทุกรูป -> figures/report/
    uv run python scripts/make_figures.py fig04      # เฉพาะรูปที่ชื่อขึ้นต้นด้วย fig04

ทำไมแยกจากโน้ตบุ๊ก: โน้ตบุ๊กมีรูประหว่างทางไว้ตรวจกระบวนการ (figures/w*.png) ส่วนนี้คือรูปชุดเดียว
ที่เข้ารายงานและสไลด์ ⇒ สไตล์เดียวกัน ชื่อดัชนีเดียวกัน และ **ทุกตัวเลขในรูปมาจากไฟล์ผล** ถ้ารันสคริปต์
คำนวณใหม่ แล้วรันไฟล์นี้ซ้ำ รูปจะตามทันเองโดยไม่ต้องแก้มือ

รายงานสองทะเล (PLAN.md §1.4): อันดามัน = KO TAPHAO NOI · อ่าวไทย = KO LAK
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wtc.plotting import period_axis, plot_coherence, plot_filter_response, use_thai_font  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
OUT = ROOT / "figures" / "report"
SEAS = ("ko_taphao_noi", "ko_lak")
SEA = {"ko_taphao_noi": "อันดามัน · KO TAPHAO NOI", "ko_lak": "อ่าวไทย · KO LAK"}
COLOR = {"ko_taphao_noi": "#1f6fb4", "ko_lak": "#d17a22"}
NAME = {"nino34": "Niño3.4", "soi": "SOI", "pdo": "PDO", "amo": "AMO", "nao": "NAO",
        "tpi": "TPI", "dmi": "DMI", "wnpmi": "WNPMI"}
REGIONAL = ("dmi", "wnpmi")
PAPER_PASC = {1: 14.03, 2: 49.63, 3: 81.11, 4: 96.00}
lab = lambda s: "+".join(NAME[k] for k in s)
FIGS = {}


def figure(fn):
    FIGS[fn.__name__] = fn
    return fn


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✅ figures/report/{name}.png")


def pval(obs, null):
    return float((np.sum(null >= obs - 1e-9) + 1) / (len(null) + 1))


def bh(p):
    p = np.asarray(p, float); m = len(p); o = np.argsort(p)
    q = np.minimum.accumulate((p[o] * m / np.arange(1, m + 1))[::-1])[::-1]
    out = np.empty(m); out[o] = np.minimum(q, 1); return out


# ---------------------------------------------------------------------------
@figure
def fig01_series():
    """ระดับน้ำทะเลหลังตัดแนวโน้ม+ฤดูกาลของสองทะเล เทียบกับ WNPMI และ SOI (ค่าเฉลี่ยเคลื่อนที่ 12 เดือน)"""
    d = np.load(PROC / "series.npz", allow_pickle=True)
    t, yn, xn = d["t"], [str(s) for s in d["y_names"]], [str(s) for s in d["x_names"]]
    sm = lambda x: np.convolve(x, np.ones(12) / 12, mode="same")
    fig, axes = plt.subplots(3, 1, figsize=(11, 6.6), sharex=True)
    for ax, st in zip(axes[:2], SEAS):
        i = yn.index(st)
        y, f = d["Y"][i], d["Y_fill"][i]
        ax.plot(t, y, color=COLOR[st], lw=0.5, alpha=0.5)
        ax.plot(t, sm(y), color=COLOR[st], lw=1.6, label="เฉลี่ย 12 เดือน")
        ax.plot(t[f], y[f], ".", ms=2.5, color="crimson", label=f"ของเติม {f.mean():.1%}")
        ax.set_ylabel("anomaly (SD)"); ax.set_title(SEA[st], loc="left", fontsize=10)
        ax.legend(fontsize=8, loc="upper left", ncol=2)
    for k, c in (("wnpmi", "C2"), ("soi", "C4")):
        axes[2].plot(t, sm(d["X"][xn.index(k)]), color=c, lw=1.3, label=NAME[k])
    axes[2].set_ylabel("anomaly (SD)"); axes[2].set_title("ดัชนี (เฉลี่ย 12 เดือน)", loc="left", fontsize=10)
    axes[2].legend(fontsize=8, loc="upper left", ncol=2); axes[2].set_xlabel("ปี")
    for ax in axes:
        ax.axhline(0, color="k", lw=0.5)
    save(fig, "fig01_series")


@figure
def fig02_filter():
    """Q7 — ตัวกรอง anti-alias ที่ออกแบบเอง (Kaiser) พร้อมตำแหน่งน้ำขึ้นน้ำลง"""
    from wtc.multirate import TIDES_CPD, design_lowpass
    spec = json.loads(str(np.load(PROC / "decimation.npz", allow_pickle=True)["spec"]))
    design = design_lowpass(**spec)
    fig, ax = plt.subplots(figsize=(8.5, 3.6))
    plot_filter_response(ax, design, TIDES_CPD)
    ax.set_title(f"FIR Kaiser {design.numtaps} taps · วัดได้ {design.measured_stopband_db():.1f} dB ที่ stopband")
    save(fig, "fig02_filter")


@figure
def fig03_wtc_maps():
    """Q1/Q2 — WTC ของสองทะเลกับสามดัชนีหลัก + เส้นขอบนัยสำคัญ + ลูกศรเฟส"""
    r = np.load(PROC / "wtc_q1.npz", allow_pickle=True)
    st_ = [str(s) for s in r["stations"]]; ix = [str(s) for s in r["indices"]]
    t, per, coi = r["t"], r["periods"], r["coi"]
    show = ("wnpmi", "soi", "nino34")
    fig, axes = plt.subplots(2, 3, figsize=(15, 6.6), sharex=True, sharey=True)
    for i, st in enumerate(SEAS):
        for j, k in enumerate(show):
            si, xi = st_.index(st), ix.index(k)
            cf = plot_coherence(axes[i, j], t, per, r["R2"][si, xi].astype(float), coi,
                                phase=r["phase"][si, xi].astype(float),
                                sig_mask=r["sig"][si, xi] & r["valid"][si, xi],
                                title=f"{SEA[st].split(' · ')[0]} × {NAME[k]}")
            if j:
                axes[i, j].set_ylabel("")
            if i == 0:
                axes[i, j].set_xlabel("")
    fig.colorbar(cf, ax=axes, shrink=0.8, label="R² (WTC)")
    fig.suptitle("WTC — เส้นขาวล้อมพื้นที่ที่เกิน threshold 95% · ลูกศร: ขวา = ไปด้วยกัน · ซ้าย = สวนทาง · ขึ้น = ระดับน้ำนำดัชนี", y=0.98)
    save(fig, "fig03_wtc_maps")


@figure
def fig04_q1_pasc():
    """Q1/Q2 — PASC ของดัชนีเดี่ยวทั้ง 8 ตัว สองทะเล สองแถบ · ขีดดำ = 95% ของ null · ดาว = ผ่าน BH"""
    r = np.load(PROC / "wtc_q1.npz", allow_pickle=True)
    st_ = [str(s) for s in r["stations"]]; ix = [str(s) for s in r["indices"]]
    bands = [str(b) for b in r["bands"]]; S = json.loads(str(r["summary"]))
    show = ("ทั้งระนาบ", "2–7 ปี")
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2), sharey=False)
    for ax, b in zip(axes, show):
        kb = bands.index(b)
        order = sorted(ix, key=lambda k: -S["ko_taphao_noi"][k][b]["pasc"])
        for s_i, st in enumerate(SEAS):
            p_all = [S[st][k][bb]["p"] for k in ix for bb in bands]
            q_all = dict(zip([(k, bb) for k in ix for bb in bands], bh(p_all)))
            xs = np.arange(len(order)) + (s_i - 0.5) * 0.38
            vals = [S[st][k][b]["pasc"] for k in order]
            ax.bar(xs, vals, width=0.36, color=COLOR[st], label=SEA[st],
                   edgecolor=["k" if k in REGIONAL else "none" for k in order], linewidth=1.2)
            null95 = [np.percentile(r["null"][st_.index(st), ix.index(k), kb], 95) for k in order]
            ax.hlines(null95, xs - 0.17, xs + 0.17, color="k", lw=1.6)
            for x, v, k in zip(xs, vals, order):
                if q_all[(k, b)] < 0.05:
                    ax.text(x, v + 0.6, "★", ha="center", fontsize=10, color=COLOR[st])
        ax.set_xticks(range(len(order))); ax.set_xticklabels([NAME[k] for k in order])
        ax.set_title(f"แถบ {b}"); ax.set_ylabel("PASC (%)")
    axes[0].legend(fontsize=8.5)
    fig.suptitle("ดัชนีเดี่ยว — ขีดดำ = 95% ของ PASC ใน null · ★ = ผ่านการปรับ BH (24 การทดสอบต่อสถานี) · "
                 "กรอบดำ = ดัชนีภูมิภาคที่เราเพิ่ม", fontsize=10, y=1.02)
    save(fig, "fig04_q1_pasc")


@figure
def fig05_threshold_vs_q():
    """W5 — threshold ของ MWC สูงขึ้นตามจำนวนดัชนี (สถานีอันดามัน · สามสถานีแทบทับกัน)"""
    n = np.load(PROC / "mwc_null.npz", allow_pickle=True)
    per, qs = n["periods"], [int(q) for q in n["qs"]]
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    for q, c in zip(qs, plt.cm.viridis(np.linspace(0, 0.9, len(qs)))):
        ax.plot(per, n["threshold"][0, qs.index(q)], color=c, lw=1.8, label=f"q = {q}")
    ax.set_xscale("log", base=2)
    ticks = [v for v in (0.25, 0.5, 1, 2, 4, 8, 16, 32) if per.min() <= v <= per.max()]
    ax.set_xticks(ticks); ax.set_xticklabels([f"{v:g}" for v in ticks]); ax.minorticks_off()
    ax.axvspan(2, 7, color="0.92", zorder=0)
    ax.set_ylim(0.4, 1.0); ax.set_xlabel("คาบ (ปี)"); ax.set_ylabel("threshold 95% ของ ρ²")
    ax.set_title("noise ล้วน q ตัว ทำให้ ρ² สูงได้แค่ไหน — threshold ต้องปรับตามจำนวนดัชนี")
    ax.legend(ncol=5, fontsize=8, loc="lower right")
    save(fig, "fig05_threshold_vs_q")


@figure
def fig06_q6_false_floor():
    """Q6 — PASC เฉลี่ยทุกชุดขนาด q: ดัชนีจริง vs ดัชนีปลอม · ปรับ / ไม่ปรับ threshold · เทียบเปเปอร์"""
    s = np.load(PROC / "mwc_search.npz", allow_pickle=True)
    nc = np.load(PROC / "null_control.npz", allow_pickle=True)
    q = s["q"]; qs = sorted(set(int(v) for v in q)); kb = [str(b) for b in s["bands"]].index("ทั้งระนาบ")
    dx = [str(x) for x in nc["designs"]].index("fake_x")
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2), sharey=True)
    for ax, st in zip(axes, SEAS):
        si = [str(x) for x in s["stations"]].index(st); ni = [str(x) for x in nc["stations"]].index(st)
        m = lambda a: [np.nanmean(a[..., q == k]) for k in qs]
        ax.plot(qs, m(nc["pasc_fixed"][ni, dx][:, :, kb]), "o--", color="C3", label="ดัชนีปลอม · ไม่ปรับ threshold")
        ax.plot(qs, m(s["pasc_fixed"][si][:, kb]), "o-", color="C3", label="ดัชนีจริง · ไม่ปรับ threshold")
        ax.plot(qs, m(nc["pasc"][ni, dx][:, :, kb]), "s--", color="C0", label="ดัชนีปลอม · ปรับตาม q")
        ax.plot(qs, m(s["pasc"][si][:, kb]), "s-", color="C0", label="ดัชนีจริง · ปรับตาม q (ของเรา)")
        ax.plot(list(PAPER_PASC), list(PAPER_PASC.values()), "k^", mfc="none", ms=8,
                label="เปเปอร์ต้นทาง (82 สถานี อเมริกาเหนือ)")
        ax.set_xticks(qs); ax.set_xlabel("จำนวนดัชนีในชุด (q)"); ax.set_title(SEA[st]); ax.set_ylim(0, 105)
    axes[0].set_ylabel("PASC ทั้งระนาบ เฉลี่ยทุกชุดขนาด q (%)"); axes[0].legend(fontsize=7.8, loc="center right")
    fig.suptitle("Q6 — เส้นที่พุ่งขึ้นตามจำนวนดัชนีเกิดได้จาก noise ล้วน ถ้าไม่ปรับ threshold", y=1.01)
    save(fig, "fig06_q6_false_floor")


@figure
def fig07_q3_best_per_q():
    """Q3 — PASC ของชุดที่ดีที่สุดต่อ q เทียบ null ของค่าสูงสุด (Y ปลอม) · สองทะเล × สองแถบ"""
    s = np.load(PROC / "mwc_search.npz", allow_pickle=True)
    nc = np.load(PROC / "null_control.npz", allow_pickle=True)
    q = s["q"]; qs = sorted(set(int(v) for v in q)); bands = [str(b) for b in s["bands"]]
    subsets = [tuple(x) for x in json.loads(str(s["subsets"]))]
    dy = [str(x) for x in nc["designs"]].index("fake_y")
    fig, axes = plt.subplots(2, 2, figsize=(13, 7.2), sharex=True)
    for i, st in enumerate(SEAS):
        si = [str(x) for x in s["stations"]].index(st); ni = [str(x) for x in nc["stations"]].index(st)
        for j, b in enumerate(("ทั้งระนาบ", "2–7 ปี")):
            ax, kb = axes[i, j], bands.index(b)
            v = s["pasc"][si][:, kb]
            best = [int(np.flatnonzero(q == k)[np.nanargmax(v[q == k])]) for k in qs]
            nmax = [np.nanmax(nc["pasc"][ni, dy][:, q == k, kb], axis=1) for k in qs]
            ax.fill_between(qs, [np.median(x) for x in nmax], [np.percentile(x, 95) for x in nmax],
                            color="0.6", alpha=0.35, label="null ของค่าสูงสุด: มัธยฐาน–95%")
            ax.plot(qs, v[best], "o-", color=COLOR[st], lw=2, label="ชุดที่ดีที่สุดต่อ q")
            for k, jj in zip(qs, best):
                ax.annotate(lab(subsets[jj]), (k, v[jj]), textcoords="offset points", xytext=(0, 7),
                            ha="center", fontsize=6.5)
            ax.set_title(f"{SEA[st]} · แถบ {b}", fontsize=10); ax.set_ylim(0, max(v[best].max(), 25) * 1.3)
            ax.set_xticks(qs)
            if j == 0:
                ax.set_ylabel("PASC (%) · threshold ปรับตาม q")
            if i == 1:
                ax.set_xlabel("จำนวนดัชนีในชุด (q)")
    axes[0, 0].legend(fontsize=8, loc="lower left")
    fig.suptitle("Q3 — เพิ่มดัชนีแล้วชุดที่ดีที่สุดไม่ดีขึ้น (อันดามัน) · ไม่มีชุดไหนเกิน null เลย (อ่าวไทย)", y=1.0)
    save(fig, "fig07_q3_best_per_q")


@figure
def fig08_q5_regional():
    """Q5 — ชุดที่ดีที่สุดจาก 8 ตัว vs จาก 6 ตัวของเปเปอร์ · แถบ 2–7 ปี · สองทะเล"""
    s = np.load(PROC / "mwc_search.npz", allow_pickle=True)
    q = s["q"]; qs = sorted(set(int(v) for v in q)); in6 = s["in_paper6"]
    kb = [str(b) for b in s["bands"]].index("2–7 ปี")
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.9), sharey=True)
    for ax, st in zip(axes, SEAS):
        v = s["pasc"][[str(x) for x in s["stations"]].index(st)][:, kb]
        ax.plot(qs, [np.nanmax(v[q == k]) for k in qs], "o-", color=COLOR[st], lw=2,
                label="ดีที่สุดจาก 8 ดัชนี (รวม DMI, WNPMI)")
        ax.plot(qs, [np.nanmax(v[(q == k) & in6]) for k in qs], "s--", color="0.35",
                label="ดีที่สุดจาก 6 ดัชนีของเปเปอร์")
        ax.set_xticks(qs); ax.set_xlabel("จำนวนดัชนีในชุด (q)"); ax.set_title(SEA[st]); ax.set_ylim(0, None)
    axes[0].set_ylabel("PASC แถบ 2–7 ปี (%)"); axes[0].legend(fontsize=8)
    fig.suptitle("Q5 — ดัชนีภูมิภาคเพิ่มอำนาจอธิบายในแถบ ENSO ที่อันดามัน", y=1.02)
    save(fig, "fig08_q5_regional")


@figure
def fig09_sensitivity():
    """W7 — ข้อสรุปหลักภายใต้การเตรียมข้อมูลแต่ละแบบ (สองทะเล)"""
    from wtc.series import VARIANTS
    files = {n: PROC / f"sens_{n}.npz" for n in VARIANTS}
    have = {n: f for n, f in files.items() if f.exists()}
    if not have:
        print("  ⏭  ข้าม fig09 — ยังไม่มี sens_*.npz (รัน scripts/sensitivity.py ก่อน)")
        return
    S = {n: json.loads(str(np.load(f, allow_pickle=True)["summary"])) for n, f in have.items()}
    M = {n: json.loads(str(np.load(f, allow_pickle=True)["meta"])) for n, f in have.items()}
    names = list(have)
    metrics = (("2–7 ปี", "wnpmi", "WNPMI · แถบ 2–7 ปี"), ("2–7 ปี", "soi", "SOI · แถบ 2–7 ปี"),
               ("2–7 ปี", "nino34", "Niño3.4 · แถบ 2–7 ปี"), ("ทั้งระนาบ", "soi", "SOI · ทั้งระนาบ"))
    fig, axes = plt.subplots(1, len(metrics), figsize=(4.0 * len(metrics), 0.55 * len(names) + 1.6), sharey=True)
    y = np.arange(len(names))
    for ax, (b, k, title) in zip(axes, metrics):
        for o, st in zip((-0.15, 0.15), SEAS):
            vals, sig = [], []
            for n in names:
                rec = S[n].get(st, {}).get("bands", {}).get(b, {}).get("single", {}).get(k)
                vals.append(np.nan if rec is None else rec["pasc"])
                sig.append(rec is not None and rec["p"] < 0.05)
            ax.scatter(vals, y + o, color=COLOR[st], s=[46 if g else 18 for g in sig],
                       edgecolor=["k" if g else "none" for g in sig], label=SEA[st], zorder=3)
        ax.set_title(title, fontsize=10); ax.set_xlabel("PASC (%)"); ax.grid(axis="x", alpha=0.3)
    axes[0].set_yticks(y); axes[0].set_yticklabels([M[n]["label"] for n in names]); axes[0].invert_yaxis()
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, fontsize=8.5, bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("การทดสอบความไว — จุดใหญ่ขอบดำ = p < 0.05 (null ของแบบนั้นเอง)", y=1.02)
    save(fig, "fig09_sensitivity")


def main() -> int:
    use_thai_font()
    want = sys.argv[1:]
    for name, fn in FIGS.items():
        if not want or any(name.startswith(w) for w in want):
            fn()
    return 0


if __name__ == "__main__":
    sys.exit(main())
