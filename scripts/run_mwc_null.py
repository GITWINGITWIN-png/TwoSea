#!/usr/bin/env python3
"""null ของ MWC — threshold รวมต่อ (q, สถานี) + การกระจายของ PASC · ใช้ซ้ำใน W6

    uv run python scripts/run_mwc_null.py                 # 1000 surrogate ตามแผน (ผลจริง)
    uv run python scripts/run_mwc_null.py --nmc 200       # ตอนพัฒนา

ต่อสถานี:
  1. fit AR(1) ของ Y และดัชนีทั้ง 8 ตัว (เฉพาะคู่ข้อมูลจริง — เหมือน W4)
  2. threshold_mwc แบบ **รวมต่อ q** (q = 1..5): ทุก surrogate สุ่มชุดดัชนีขนาด q ใหม่จาก 8 ตัว
  3. pasc_null_mwc ด้วย surrogate ชุดใหม่ ⇒ ใช้คิด p-value ของ PASC ของทุกชุดใน W6

ตรวจความชอบธรรมของการรวม (เฉพาะสถานีหลัก): คำนวณ threshold แบบ **เจาะจงชุด** (exact)
ของชุดที่ความแดงสุดโต่งสองทาง แล้ววัดว่าห่างจากแบบรวมแค่ไหน
  แดงน้อยสุด  NAO (a≈0.18) · WNPMI (a≈0.11) [+ SOI ที่ q=3]
  แดงมากสุด   Niño3.4 (a≈0.94) · TPI (a≈0.96) [+ AMO ที่ q=3]
ถ้าห่างมาก ⇒ ต้องรัน null แบบเจาะจงกับชุดที่จะรายงานทุกชุด (PLAN.md §4 วางไว้แล้วว่าจะทำ)

ผล -> data/processed/mwc_null.npz
"""
from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wtc.metrics import BANDS                                               # noqa: E402
from wtc.significance import fit_ar1, pasc_null_mwc, threshold_mwc          # noqa: E402
from wtc.transform import cwt                                               # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SERIES = ROOT / "data" / "processed" / "series.npz"
OUT = ROOT / "data" / "processed" / "mwc_null.npz"
MAIN = "ko_taphao_noi"
QS = (1, 2, 3, 4, 5)
EXTREMES = {                       # ชุดที่ใช้ตรวจว่า null รวมต่อ q ใช้แทน null เจาะจงได้
    "แดงน้อย q=2": ("nao", "wnpmi"),
    "แดงมาก q=2": ("nino34", "tpi"),
    "แดงน้อย q=3": ("nao", "wnpmi", "soi"),
    "แดงมาก q=3": ("nino34", "tpi", "amo"),
}
MID = (0.5, 16.0)                  # ช่วงคาบที่ใช้สรุป "ระดับ" ของ threshold (ตัดสองปลายตัว U)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmc", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20261001)
    ap.add_argument("--workers", type=int, default=min(24, (os.cpu_count() or 2) - 2))
    args = ap.parse_args()

    d = np.load(SERIES, allow_pickle=True)
    Y, X, Yf, Xf = d["Y"], d["X"], d["Y_fill"], d["X_fill"]
    y_names = [str(s) for s in d["y_names"]]
    x_names = [str(s) for s in d["x_names"]]
    stations = [MAIN] + [s for s in y_names if s != MAIN]
    n = Y.shape[1]
    _, _, periods, _ = cwt(Y[0])
    mid = (periods >= MID[0]) & (periods <= MID[1])

    ax = [fit_ar1(x, f) for x, f in zip(X, Xf)]
    a_x, s_x = [a for a, _ in ax], [s for _, s in ax]
    print(f"{len(stations)} สถานี · q = {QS} · surrogate {args.nmc}+{args.nmc} ชุด/สถานี · "
          f"{args.workers} workers · seed {args.seed}")
    print("a ของดัชนี: " + " · ".join(f"{k} {a:.2f}" for k, a in zip(x_names, a_x)))

    thr_all, null_all, a_y_all, meta = {}, {}, {}, {}
    t0 = time.perf_counter()
    for i, st in enumerate(stations):
        iy = y_names.index(st)
        a_y, s_y = fit_ar1(Y[iy], Yf[iy])
        seed = args.seed + 100_000 * i
        thr = threshold_mwc(n, a_y, s_y, a_x, s_x, qs=QS, nmc=args.nmc, seed=seed,
                            workers=args.workers)
        null = pasc_null_mwc(thr, n, s_y, s_x, nmc=args.nmc, workers=args.workers)
        thr_all[st], null_all[st], a_y_all[st] = thr, null, a_y
        print(f"\n{st}  a_Y = {a_y:.3f}   ({time.perf_counter() - t0:.0f} s)")
        print(f"  {'q':>2s} │ {'threshold (คาบ 0.5–16 ปี)':>26s} │ " +
              " │ ".join(f"{b:^17s}" for b in BANDS) + " │ NaN ใน null")
        for q in QS:
            t = thr[q].per_scale[mid]
            cells = [f"{np.mean(null[q][b]):5.1f} / {np.percentile(null[q][b], 95):5.1f}"
                     for b in BANDS]
            print(f"  {q:2d} │ มัธยฐาน {np.nanmedian(t):.3f} ช่วง {np.nanmin(t):.3f}–{np.nanmax(t):.3f} │ "
                  + " │ ".join(f"{c:^17s}" for c in cells) + f" │ {thr[q].n_nan}")
        print("       (ช่อง PASC ของ null = ค่าเฉลี่ย / เปอร์เซ็นไทล์ที่ 95 · หน่วย %)")

    # --- ตรวจ: null รวมต่อ q ใช้แทน null เจาะจงชุดได้ไหม (สถานีหลักเท่านั้น) ------------
    iy = y_names.index(MAIN)
    a_y, s_y = fit_ar1(Y[iy], Yf[iy])
    print(f"\nตรวจการรวม null ที่ {MAIN} — threshold แบบเจาะจงชุด เทียบแบบรวมต่อ q")
    exact = {}
    for j, (label, subset) in enumerate(EXTREMES.items()):
        idx = [x_names.index(k) for k in subset]
        q = len(subset)
        e = threshold_mwc(n, a_y, s_y, [a_x[k] for k in idx], [s_x[k] for k in idx],
                          qs=(q,), nmc=args.nmc, seed=args.seed + 900_000 + j,
                          workers=args.workers)[q]
        diff = e.per_scale - thr_all[MAIN][q].per_scale
        exact[label] = dict(subset=list(subset), q=q, per_scale=e.per_scale.tolist(),
                            mid_median_diff=float(np.nanmedian(diff[mid])),
                            mid_max_abs_diff=float(np.nanmax(np.abs(diff[mid]))))
        print(f"  {label:12s} {'+'.join(subset):22s} เจาะจง−รวม: มัธยฐาน {np.nanmedian(diff[mid]):+.3f} · "
              f"มากสุด {np.nanmax(np.abs(diff[mid])):.3f}")

    # --- บันทึก --------------------------------------------------------------
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUT, stations=np.array(stations), indices=np.array(x_names), qs=np.array(QS),
        bands=np.array(list(BANDS)), periods=periods,
        threshold=np.array([[thr_all[s][q].per_scale for q in QS] for s in stations]),
        null=np.array([[[null_all[s][q][b] for b in BANDS] for q in QS] for s in stations]),
        n_nan=np.array([[thr_all[s][q].n_nan for q in QS] for s in stations]),
        a_y=np.array([a_y_all[s] for s in stations]), a_x=np.array(a_x), s_x=np.array(s_x),
        exact=json.dumps(exact, ensure_ascii=False),
        meta=json.dumps({"nmc": args.nmc, "seed": args.seed, "level": 0.95,
                         "pooled": "q < 8 ⇒ สุ่มชุดดัชนีใหม่ทุก surrogate จาก 8 ตัว",
                         "null_seed": "threshold seed + 10000"}, ensure_ascii=False))
    print(f"\n✅ เขียนแล้ว {OUT.relative_to(ROOT)} · ใช้เวลารวม {time.perf_counter() - t0:.0f} วินาที")
    return 0


if __name__ == "__main__":
    sys.exit(main())
