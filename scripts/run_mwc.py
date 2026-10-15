#!/usr/bin/env python3
"""Q3 · Q4 · Q5 — ค้น MWC ครบทุกชุดดัชนี (218 ชุด/สถานี) พร้อมนัยสำคัญ

    uv run python scripts/run_mwc.py                # ต้องรัน run_mwc_null.py มาก่อน
    uv run python scripts/run_mwc.py --no-exact     # ข้าม null เจาะจงชุด (ตอนพัฒนา)

ต่อสถานี
  1. cache spectrum ที่ smooth แล้วของทุกคู่ (1 + 8 + 36 = 45 อัน)
  2. MWC ของทุกชุดขนาด 1–5 จากดัชนี 8 ตัว ⇒ PASC/AWC สามแถบ
     - **pasc**        ใช้ threshold ของ q ตัวเอง (null รวมต่อ q จาก mwc_null.npz) ← ผลหลัก
     - **pasc_fixed**  ใช้ threshold ของ q=1 ตลอด ← ไว้เทียบกับเส้นของเปเปอร์ต้นทางเท่านั้น
  3. p-value ของ PASC ต่อชุด เทียบการกระจายของ PASC ใน null รวมต่อ q
     ⚠️ p นี้ตอบว่า "ชุดนี้ชุดเดียวเกิน noise ไหม" — **ไม่ได้ชดเชยการเลือกชุดที่ดีที่สุด**
        p ที่ชดเชยการเลือกมาจาก scripts/null_control.py (Q6)

คำถาม
  Q3  ต้องใช้ดัชนีกี่ตัว      PASC สูงสุดต่อ q + เกณฑ์ "เพิ่มอย่างน้อย 5 จุด" ของ Hu et al. (2017)
  Q4  ชุดไหนดีที่สุด          argmax + กฎความประหยัด (ชุดเล็กสุดที่อยู่ใน 1 จุดของค่าสูงสุด)
  Q5  ดัชนีภูมิภาคช่วยไหม     ชุดที่ดีที่สุดจาก 6 ตัวของเปเปอร์ เทียบจากทั้ง 8 ตัว ที่ q เท่ากัน

สถานีหลัก: รัน **null เจาะจงชุด** ให้ชุดที่ดีที่สุดต่อ q (PLAN.md §4) เพื่อยืนยันว่าตัวเลขที่จะรายงาน
ไม่ได้ขึ้นกับการใช้ null รวม

ผล -> data/processed/mwc_search.npz
"""
from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wtc.coherence import mwc_cached                                             # noqa: E402
from wtc.metrics import BANDS, pasc, significance                                # noqa: E402
from wtc.search import (all_subsets, best_per_q, evaluate_subsets, gains,        # noqa: E402
                        prepare_station, within_of_max)
from wtc.significance import empirical_p, fit_ar1, pasc_null_mwc, threshold_mwc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SERIES = ROOT / "data" / "processed" / "series.npz"
NULL = ROOT / "data" / "processed" / "mwc_null.npz"
OUT = ROOT / "data" / "processed" / "mwc_search.npz"
MAIN = "ko_taphao_noi"
PAPER6 = ("nino34", "pdo", "nao", "soi", "amo", "tpi")     # ดัชนีของเปเปอร์ต้นทาง
GAIN_RULE = 5.0          # จุดร้อยละ — Hu et al. (2017)
PRIMARY = ("ทั้งระนาบ", "2–7 ปี")                          # แถบที่ใช้ตัดสิน (8–16 ปีตอบไม่ได้ · Q1)


def bh_qvalues(p: np.ndarray) -> np.ndarray:
    """Benjamini–Hochberg — q_(i) = min_{k>=i} p_(k) m / k (NaN ถูกข้าม)"""
    p = np.asarray(p, float)
    out = np.full(p.shape, np.nan)
    ok = np.isfinite(p)
    v = p[ok]
    order = np.argsort(v)
    qv = v[order] * len(v) / np.arange(1, len(v) + 1)
    qv = np.minimum.accumulate(qv[::-1])[::-1]
    res = np.empty(len(v))
    res[order] = np.minimum(qv, 1.0)
    out[ok] = res
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-exact", action="store_true")
    ap.add_argument("--workers", type=int, default=min(24, (os.cpu_count() or 2) - 2))
    args = ap.parse_args()

    d = np.load(SERIES, allow_pickle=True)
    nul = np.load(NULL, allow_pickle=True)
    nmeta = json.loads(str(nul["meta"]))
    x_names = [str(s) for s in d["x_names"]]
    stations = [str(s) for s in nul["stations"]]
    QS = [int(q) for q in nul["qs"]]
    bands = list(BANDS)
    assert [str(b) for b in nul["bands"]] == bands and [str(s) for s in nul["indices"]] == x_names
    subsets = all_subsets(x_names, max(QS))
    label = lambda s: "+".join(s)
    in6 = np.array([set(s) <= set(PAPER6) for s in subsets])
    print(f"{len(stations)} สถานี × {len(subsets)} ชุด (q = 1..{max(QS)} จาก {len(x_names)} ดัชนี) · "
          f"null รวมต่อ q {nmeta['nmc']} surrogate")

    tables, P, Qv, summary = {}, {}, {}, {}
    t0 = time.perf_counter()
    for si, st in enumerate(stations):
        cache, periods, coi, scales, inside, ok = prepare_station(d, st)
        thr = {q: nul["threshold"][si, i] for i, q in enumerate(QS)}
        null = {q: {b: nul["null"][si, i, k] for k, b in enumerate(bands)} for i, q in enumerate(QS)}
        tab = evaluate_subsets(cache, "y", subsets, thr, periods, inside, ok)
        p = np.array([[empirical_p(tab.pasc[i, k], null[int(tab.q[i])][b])
                       for k, b in enumerate(bands)] for i in range(len(subsets))])
        qv = bh_qvalues(p.ravel()).reshape(p.shape)        # BH บน 218 × 3 การทดสอบของสถานีนี้
        tables[st], P[st], Qv[st] = tab, p, qv

        tag = "← รายงานหลัก" if st == MAIN else "(สำรอง)"
        print(f"\n{'=' * 100}\n{st}  {tag}   ({time.perf_counter() - t0:.0f} s)")
        print(f"  จุด NaN ในกรวยรวมทุกชุด {int(tab.n_nan.sum())} · cond สูงสุดในกรวย {np.nanmax(tab.cond_max):.0f} "
              f"({label(subsets[int(np.nanargmax(tab.cond_max))])})")
        n_p = {b: int((p[:, k] < 0.05).sum()) for k, b in enumerate(bands)}
        n_q = {b: int((qv[:, k] < 0.05).sum()) for k, b in enumerate(bands)}
        print("  ชุดที่ p < 0.05: " + " · ".join(f"{b} {n_p[b]}" for b in bands) +
              "   |   ผ่าน BH (q < 0.05): " + " · ".join(f"{b} {n_q[b]}" for b in bands) +
              f"   (จาก {len(subsets)} ชุด)")

        summ = {"n_p05": n_p, "n_bh05": n_q, "bands": {}}
        for b in PRIMARY:
            k = bands.index(b)
            v = tab.pasc[:, k]
            best8 = best_per_q(tab.q, v)
            best6 = best_per_q(tab.q, v, in6)
            gain = gains(best8)
            # Q3: จำนวนดัชนีที่ "พอ" = q ใหญ่สุดที่การเพิ่มขั้นสุดท้ายยังได้ >= 5 จุด (เริ่มนับที่ 1)
            q_enough = 1
            for q in sorted(gain):
                if gain[q] >= GAIN_RULE and q == q_enough + 1:
                    q_enough = q
            top = int(np.nanargmax(v))
            pars = within_of_max(v, tab.q, 1.0)
            print(f"\n  ── แถบ {b} ──")
            print(f"  {'q':>2s} │ {'ชุดที่ดีที่สุด (จาก 8 ตัว)':34s} {'PASC':>6s} {'เพิ่ม':>6s} {'p':>6s} {'ไม่ปรับ':>7s} │ "
                  f"{'ดีที่สุดจาก 6 ตัวของเปเปอร์':30s} {'PASC':>6s} │ {'8−6':>6s}")
            for q in QS:
                j8, v8 = best8[q]
                j6, v6 = best6[q]
                g = f"{gain[q]:+6.1f}" if q in gain else "     —"
                print(f"  {q:2d} │ {label(subsets[j8]):34s} {v8:6.1f} {g} {p[j8, k]:6.3f} "
                      f"{tab.pasc_fixed[j8, k]:7.1f} │ {label(subsets[j6]):30s} {v6:6.1f} │ {v8 - v6:+6.1f}")
            print(f"  Q3 ดัชนีที่พอตามเกณฑ์ +{GAIN_RULE:g} จุด: {q_enough} ตัว"
                  f"   ·   Q4 สูงสุด {label(subsets[top])} ({v[top]:.1f}%) · "
                  f"ประหยัดสุดใน 1 จุด {label(subsets[pars])} ({v[pars]:.1f}%)")
            summ["bands"][b] = {
                "best8": {q: {"subset": list(subsets[j]), "pasc": val, "p": float(p[j, k]),
                              "pasc_fixed": float(tab.pasc_fixed[j, k]), "awc": float(tab.awc[j, k])}
                          for q, (j, val) in best8.items()},
                "best6": {q: {"subset": list(subsets[j]), "pasc": val, "p": float(p[j, k])}
                          for q, (j, val) in best6.items()},
                "gain": gain, "q_enough": q_enough,
                "top": {"subset": list(subsets[top]), "pasc": float(v[top])},
                "parsimonious": {"subset": list(subsets[pars]), "pasc": float(v[pars])},
            }
        summary[st] = summ

    # --- null เจาะจงชุด ให้ชุดที่ดีที่สุดต่อ q ของสถานีหลัก ---------------------------
    exact = {}
    if not args.no_exact:
        y_names = [str(s) for s in d["y_names"]]
        iy = y_names.index(MAIN)
        a_y, s_y = fit_ar1(d["Y"][iy], d["Y_fill"][iy])
        ar = {k: fit_ar1(x, f) for k, x, f in zip(x_names, d["X"], d["X_fill"])}
        cache, periods, coi, scales, inside, ok = prepare_station(d, MAIN)
        tab = tables[MAIN]
        todo = sorted({tuple(summary[MAIN]["bands"][b]["best8"][q]["subset"])
                       for b in PRIMARY for q in QS if q > 1}, key=lambda s: (len(s), s))
        print(f"\n{'=' * 100}\nnull เจาะจงชุด ที่ {MAIN} — {len(todo)} ชุด × {nmeta['nmc']}+{nmeta['nmc']} surrogate")
        print(f"  {'ชุด':34s} │ " + " │ ".join(f"{b + ': รวม → เจาะจง (p)':^34s}" for b in PRIMARY))
        for j, s in enumerate(todo):
            q = len(s)
            e = threshold_mwc(d["Y"].shape[1], a_y, s_y, [ar[k][0] for k in s], [ar[k][1] for k in s],
                              qs=(q,), nmc=nmeta["nmc"], seed=nmeta["seed"] + 500_000 + 100 * j,
                              workers=args.workers)
            en = pasc_null_mwc(e, d["Y"].shape[1], s_y, [ar[k][1] for k in s], workers=args.workers)[q]
            R2, _ = mwc_cached(cache, "y", s, where=inside)
            valid = inside & np.isfinite(R2) & ok["y"]
            for k in s:
                valid &= ok[k]
            sig = significance(R2, e[q].per_scale)
            i = subsets.index(s)
            rec, cells = {"q": q}, []
            for b in PRIMARY:
                kb = bands.index(b)
                pe = pasc(sig, valid, periods, BANDS[b])
                rec[b] = {"pasc_pooled": float(tab.pasc[i, kb]), "p_pooled": float(P[MAIN][i, kb]),
                          "pasc_exact": pe, "p_exact": empirical_p(pe, en[b])}
                cells.append(f"{tab.pasc[i, kb]:5.1f} ({P[MAIN][i, kb]:.3f}) → {pe:5.1f} ({rec[b]['p_exact']:.3f})")
            exact[label(s)] = rec
            print(f"  {label(s):34s} │ " + " │ ".join(f"{c:^34s}" for c in cells), flush=True)

    stack = lambda f: np.array([f(tables[s]) for s in stations])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUT, stations=np.array(stations), indices=np.array(x_names), bands=np.array(bands),
        subsets=json.dumps([list(s) for s in subsets]), q=tables[MAIN].q, in_paper6=in6,
        pasc=stack(lambda t: t.pasc), pasc_fixed=stack(lambda t: t.pasc_fixed),
        awc=stack(lambda t: t.awc), mean_r2=stack(lambda t: t.mean_r2),
        n_valid=stack(lambda t: t.n_valid), n_nan=stack(lambda t: t.n_nan),
        cond_max=stack(lambda t: t.cond_max),
        p=np.array([P[s] for s in stations]), bh=np.array([Qv[s] for s in stations]),
        summary=json.dumps(summary, ensure_ascii=False), exact=json.dumps(exact, ensure_ascii=False),
        meta=json.dumps({"null_nmc": nmeta["nmc"], "null_seed": nmeta["seed"], "gain_rule": GAIN_RULE,
                         "paper6": list(PAPER6), "primary_bands": list(PRIMARY)}, ensure_ascii=False))
    print(f"\n✅ เขียนแล้ว {OUT.relative_to(ROOT)} · ใช้เวลารวม {time.perf_counter() - t0:.0f} วินาที")
    return 0


if __name__ == "__main__":
    sys.exit(main())
